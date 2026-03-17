# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MedTechFillingBatch(models.Model):
    _name = 'medtech.filling.batch'
    _description = 'Filling Batch'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = [
        'state', 'operator_id', 'filling_at', 'finished_lot_id', 'unit_count',
        'measured_volume_ml', 'volume_qc_status'
    ]

    name = fields.Char(string='Filling Batch Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    sterilization_batch_id = fields.Many2one('medtech.sterilization.batch', string='Sterilization Batch', tracking=True)

    product_id = fields.Many2one(related='production_id.product_id', string='Finished Product', store=True, readonly=True)
    product_qty = fields.Float(related='production_id.product_qty', string='MO Qty', store=True, readonly=True)

    operator_id = fields.Many2one('res.users', string='Operator', tracking=True)
    filling_at = fields.Datetime(string='Filling Time', tracking=True)

    unit_count = fields.Integer(string='Units Filled', default=20, required=True, tracking=True)
    finished_lot_id = fields.Many2one(
        'stock.lot',
        string='Finished Product Lot',
        domain="[('product_id', '=', product_id)]",
        tracking=True,
    )

    target_volume_ml = fields.Float(string='Target Volume (ml)', default=10.0, required=True)
    measured_volume_ml = fields.Float(string='Measured Fill Volume (ml)', tracking=True)
    min_volume_ml = fields.Float(string='Min Volume (ml)', default=9.8)
    max_volume_ml = fields.Float(string='Max Volume (ml)', default=10.2)

    volume_qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='Fill Volume QC', default='pending', tracking=True)

    nonconformance_id = fields.Many2one('medtech.nonconformance', string='Nonconformance', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('qc_passed', 'QC Passed'),
        ('qc_failed', 'QC Failed'),
        ('moved', 'Moved to Packaging'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.filling.batch') or _('New')
        records = super().create(vals_list)
        for record in records.filtered(lambda r: r.production_id and not r.production_id.medtech_filling_batch_id):
            record.production_id.medtech_filling_batch_id = record.id
        return records

    def action_start_filling(self):
        self.ensure_one()
        if self.sterilization_batch_id and self.sterilization_batch_id.state not in ['moved', 'qc_passed']:
            raise ValidationError(_('Sterilization batch must be QC passed/moved before filling starts.'))

        self.write({
            'state': 'in_progress',
            'operator_id': self.env.user.id,
            'filling_at': fields.Datetime.now(),
        })
        return True

    def _ensure_finished_lot(self):
        self.ensure_one()
        if self.finished_lot_id:
            return self.finished_lot_id

        lot = self.env['stock.lot'].create({
            'name': self.name,
            'product_id': self.product_id.id,
            'company_id': self.env.company.id,
        })
        self.finished_lot_id = lot.id
        return lot

    def action_volume_qc_pass(self):
        self.ensure_one()
        if self.state not in ['draft', 'in_progress']:
            raise ValidationError(_('Fill-volume QC can only be evaluated from Draft/In Progress states.'))
        if self.unit_count != 20:
            raise ValidationError(_('This demo scenario requires exactly 20 filled units.'))

        self._ensure_finished_lot()

        if not (self.min_volume_ml <= self.measured_volume_ml <= self.max_volume_ml):
            raise ValidationError(_('Measured volume is out of tolerance. Use Fail action or adjust value.'))

        self.write({
            'volume_qc_status': 'passed',
            'state': 'qc_passed',
        })
        if self.production_id:
            self.production_id.medtech_inprocess_qc_status = 'passed'
        return True

    def action_volume_qc_fail(self):
        self.ensure_one()
        if self.state not in ['draft', 'in_progress']:
            raise ValidationError(_('Fill-volume QC can only be evaluated from Draft/In Progress states.'))

        nc = self.nonconformance_id
        if not nc:
            nc = self.env['medtech.nonconformance'].create({
                'source': 'manufacturing',
                'severity': 'medium',
                'description': _('Fill-volume QC failed in %(batch)s for MO %(mo)s') % {
                    'batch': self.name,
                    'mo': self.production_id.name,
                },
                'affected_product_ids': [(4, self.product_id.id)],
                'state': 'investigation',
            })
            self.nonconformance_id = nc.id

        self.write({
            'volume_qc_status': 'failed',
            'state': 'qc_failed',
        })
        if self.production_id:
            self.production_id.medtech_inprocess_qc_status = 'failed'
        return True

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

    def action_move_to_packaging(self):
        self.ensure_one()
        if self.state != 'qc_passed':
            raise ValidationError(_('Only QC-passed filling batches can move to packaging.'))
        if self.unit_count != 20:
            raise ValidationError(_('This demo scenario requires exactly 20 filled units before packaging.'))

        finished_lot = self._ensure_finished_lot()

        source_location = self.env.ref('medtech_quality_capa.location_wip_filling', raise_if_not_found=False)
        dest_location = self.env.ref('medtech_quality_capa.location_wip_packaging', raise_if_not_found=False)
        if not source_location or not dest_location:
            raise ValidationError(_('Required locations WIP/Filling or WIP/Packaging are missing.'))

        picking_type = self._get_internal_picking_type()
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': source_location.id,
            'location_dest_id': dest_location.id,
            'origin': self.name,
        })

        move = self.env['stock.move'].create({
            'name': self.product_id.display_name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.unit_count,
            'product_uom': self.product_id.uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': dest_location.id,
            'picking_id': picking.id,
        })
        move._action_confirm()
        move._action_assign()

        if not move.move_line_ids:
            vals = {
                'move_id': move.id,
                'picking_id': picking.id,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
                'lot_id': finished_lot.id,
            }
            if 'quantity' in self.env['stock.move.line']._fields:
                vals['quantity'] = self.unit_count
            elif 'qty_done' in self.env['stock.move.line']._fields:
                vals['qty_done'] = self.unit_count
            self.env['stock.move.line'].create(vals)

        for line in move.move_line_ids:
            values = {'lot_id': finished_lot.id}
            if 'quantity' in line._fields:
                values['quantity'] = self.unit_count
            elif 'qty_done' in line._fields:
                values['qty_done'] = self.unit_count
            line.write(values)

        picking.button_validate()
        self.state = 'moved'
        return True
