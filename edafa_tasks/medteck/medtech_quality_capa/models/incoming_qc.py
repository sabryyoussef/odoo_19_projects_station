# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MedTechIncomingQC(models.Model):
    _name = 'medtech.incoming.qc'
    _description = 'Incoming Raw Material QC'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = ['state', 'result', 'checked_by_id', 'checked_at', 'notes']

    name = fields.Char(
        string='Inspection Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    result = fields.Selection([
        ('pending', 'Pending'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Result', default='pending', required=True, tracking=True)

    product_id = fields.Many2one('product.product', string='Material', required=True, tracking=True)
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot Number',
        required=True,
        tracking=True,
        domain="[('product_id', '=', product_id)]",
    )
    expiration_date = fields.Date(string='Expiry Date', compute='_compute_expiration_date', store=True, readonly=True)

    quantity_inspected = fields.Float(string='Quantity Inspected', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id', readonly=True, store=True)

    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)])
    receipt_picking_id = fields.Many2one('stock.picking', string='Receipt')
    nonconformance_id = fields.Many2one('medtech.nonconformance', string='Related Nonconformance', readonly=True)

    quarantine_location_id = fields.Many2one(
        'stock.location',
        string='Quarantine Location',
        required=True,
        default=lambda self: self._default_quarantine_location(),
    )
    released_location_id = fields.Many2one(
        'stock.location',
        string='Released Location',
        required=True,
        default=lambda self: self._default_released_location(),
    )

    checked_by_id = fields.Many2one('res.users', string='Checked By', tracking=True)
    checked_at = fields.Datetime(string='Checked At', tracking=True)
    notes = fields.Text(string='Inspection Notes', tracking=True)

    @api.depends('lot_id', 'lot_id.write_date')
    def _compute_expiration_date(self):
        for record in self:
            if not record.lot_id:
                record.expiration_date = False
                continue

            lot = record.lot_id
            lot_fields = lot._fields
            if 'expiration_date' in lot_fields:
                record.expiration_date = lot.expiration_date
            elif 'use_date' in lot_fields:
                record.expiration_date = lot.use_date
            elif 'life_date' in lot_fields:
                record.expiration_date = lot.life_date
            else:
                record.expiration_date = False

    @api.model
    def _default_quarantine_location(self):
        return self.env.ref('medtech_quality_capa.location_raw_material_quarantine', raise_if_not_found=False)

    @api.model
    def _default_released_location(self):
        return self.env.ref('medtech_quality_capa.location_raw_material_released', raise_if_not_found=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.incoming.qc') or _('New')
        return super().create(vals_list)

    def _get_internal_picking_type(self):
        self.ensure_one()
        company_id = self.env.company.id
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            '|', ('warehouse_id.company_id', '=', company_id), ('warehouse_id', '=', False),
        ], limit=1)
        if not picking_type:
            raise UserError(_('No internal transfer operation type found for the current company.'))
        return picking_type

    def _create_release_transfer(self):
        self.ensure_one()
        picking_type = self._get_internal_picking_type()

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.quarantine_location_id.id,
            'location_dest_id': self.released_location_id.id,
            'origin': self.name,
        })

        move = self.env['stock.move'].create({
            'name': self.product_id.display_name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity_inspected,
            'product_uom': self.uom_id.id,
            'location_id': self.quarantine_location_id.id,
            'location_dest_id': self.released_location_id.id,
            'picking_id': picking.id,
        })

        move._action_confirm()
        move._action_assign()

        if not move.move_line_ids:
            self.env['stock.move.line'].create({
                'move_id': move.id,
                'picking_id': picking.id,
                'product_id': self.product_id.id,
                'product_uom_id': self.uom_id.id,
                'location_id': self.quarantine_location_id.id,
                'location_dest_id': self.released_location_id.id,
                'lot_id': self.lot_id.id,
            })

        for line in move.move_line_ids:
            values = {'lot_id': self.lot_id.id}
            if 'quantity' in line._fields:
                values['quantity'] = self.quantity_inspected
            elif 'qty_done' in line._fields:
                values['qty_done'] = self.quantity_inspected
            line.write(values)

        picking.button_validate()
        return picking

    def action_pass(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Only draft inspections can be passed.'))
        if self.quantity_inspected <= 0:
            raise ValidationError(_('Quantity inspected must be greater than zero.'))

        self._create_release_transfer()
        self.lot_id.write({
            'medtech_qc_status': 'released',
            'medtech_qc_released_at': fields.Datetime.now(),
            'medtech_qc_released_by_id': self.env.user.id,
        })
        self.write({
            'state': 'passed',
            'result': 'pass',
            'checked_by_id': self.env.user.id,
            'checked_at': fields.Datetime.now(),
        })
        self._track_changes('write', context_info='Incoming QC passed and lot moved to Released')
        self.message_post(body=_('Incoming QC passed. Lot moved to Raw Material / Released.'))
        return True

    def action_fail(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Only draft inspections can be failed.'))

        if not self.nonconformance_id:
            nc = self.env['medtech.nonconformance'].create({
                'source': 'incoming',
                'severity': 'medium',
                'description': self.notes or _('Incoming QC failed for lot %s') % self.lot_id.name,
                'affected_lot_ids': [(4, self.lot_id.id)],
                'affected_product_ids': [(4, self.product_id.id)],
                'supplier_id': self.vendor_id.id,
                'state': 'investigation',
            })
            self.nonconformance_id = nc.id

        self.lot_id.write({'medtech_qc_status': 'quarantine'})
        self.write({
            'state': 'failed',
            'result': 'fail',
            'checked_by_id': self.env.user.id,
            'checked_at': fields.Datetime.now(),
        })
        self._track_changes('write', context_info='Incoming QC failed')
        self.message_post(body=_('Incoming QC failed. Lot remains in quarantine and NC was created.'))
        return True

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'passed':
            raise ValidationError(_('Passed inspections cannot be reset to draft.'))
        self.write({
            'state': 'draft',
            'result': 'pending',
            'checked_by_id': False,
            'checked_at': False,
        })
        return True
