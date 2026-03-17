# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MedTechPackagingBatch(models.Model):
    _name = 'medtech.packaging.batch'
    _description = 'Packaging Batch'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = [
        'state', 'operator_id', 'packaging_at', 'dropper_cap_inserted',
        'leaflet_inserted', 'carton_box_applied', 'final_inspection_result'
    ]

    name = fields.Char(string='Packaging Batch Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    filling_batch_id = fields.Many2one('medtech.filling.batch', string='Filling Batch', tracking=True)

    product_id = fields.Many2one(related='production_id.product_id', string='Finished Product', store=True, readonly=True)
    product_qty = fields.Float(related='production_id.product_qty', string='MO Qty', store=True, readonly=True)
    unit_count = fields.Integer(string='Units to Package', default=20, required=True)
    finished_lot_id = fields.Many2one('stock.lot', string='Finished Product Lot', readonly=True)

    operator_id = fields.Many2one('res.users', string='Operator', tracking=True)
    packaging_at = fields.Datetime(string='Packaging Time', tracking=True)

    dropper_cap_inserted = fields.Boolean(string='Dropper Cap Inserted', tracking=True)
    leaflet_inserted = fields.Boolean(string='Leaflet Inserted', tracking=True)
    carton_box_applied = fields.Boolean(string='Carton Box Applied', tracking=True)

    final_inspection_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Final Packaging Inspection', tracking=True)

    qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='Packaging QC', default='pending', tracking=True)

    nonconformance_id = fields.Many2one('medtech.nonconformance', string='Nonconformance', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('qc_passed', 'QC Passed'),
        ('qc_failed', 'QC Failed'),
        ('moved', 'Moved to FG Quarantine'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.packaging.batch') or _('New')
        records = super().create(vals_list)
        for record in records.filtered(lambda r: r.production_id and not r.production_id.medtech_packaging_batch_id):
            record.production_id.medtech_packaging_batch_id = record.id
        return records

    def action_start_packaging(self):
        self.ensure_one()
        if self.filling_batch_id and self.filling_batch_id.state not in ['moved', 'qc_passed']:
            raise ValidationError(_('Filling batch must be QC passed/moved before packaging starts.'))

        if self.filling_batch_id and self.filling_batch_id.finished_lot_id:
            self.finished_lot_id = self.filling_batch_id.finished_lot_id.id

        self.write({
            'state': 'in_progress',
            'operator_id': self.env.user.id,
            'packaging_at': fields.Datetime.now(),
        })
        return True

    def action_packaging_qc_pass(self):
        self.ensure_one()
        if self.unit_count != 20:
            raise ValidationError(_('This demo scenario requires exactly 20 units.'))
        if not (self.dropper_cap_inserted and self.leaflet_inserted and self.carton_box_applied):
            raise ValidationError(_('All packaging checklist items must be completed before QC pass.'))
        if self.final_inspection_result != 'pass':
            raise ValidationError(_('Final packaging inspection must be Pass.'))

        self.write({
            'qc_status': 'passed',
            'state': 'qc_passed',
        })
        return True

    def action_packaging_qc_fail(self):
        self.ensure_one()
        if self.final_inspection_result != 'fail':
            raise ValidationError(_('Set final packaging inspection result to Fail first.'))

        nc = self.nonconformance_id
        if not nc:
            nc = self.env['medtech.nonconformance'].create({
                'source': 'manufacturing',
                'severity': 'medium',
                'description': _('Packaging inspection failed in %(batch)s for MO %(mo)s') % {
                    'batch': self.name,
                    'mo': self.production_id.name,
                },
                'affected_product_ids': [(4, self.product_id.id)],
                'state': 'investigation',
            })
            self.nonconformance_id = nc.id

        self.write({
            'qc_status': 'failed',
            'state': 'qc_failed',
        })
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

    def action_move_to_fg_quarantine(self):
        self.ensure_one()
        if self.state != 'qc_passed':
            raise ValidationError(_('Only QC-passed packaging batches can move to Finished Goods / Quarantine.'))

        if not self.finished_lot_id and self.filling_batch_id and self.filling_batch_id.finished_lot_id:
            self.finished_lot_id = self.filling_batch_id.finished_lot_id.id

        source_location = self.env.ref('medtech_quality_capa.location_wip_packaging', raise_if_not_found=False)
        dest_location = self.env.ref('medtech_quality_capa.location_finished_goods_quarantine', raise_if_not_found=False)
        if not source_location or not dest_location:
            raise ValidationError(_('Required locations WIP/Packaging or Finished Goods/Quarantine are missing.'))

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
                'lot_id': self.finished_lot_id.id,
            }
            if 'quantity' in self.env['stock.move.line']._fields:
                vals['quantity'] = self.unit_count
            elif 'qty_done' in self.env['stock.move.line']._fields:
                vals['qty_done'] = self.unit_count
            self.env['stock.move.line'].create(vals)

        for line in move.move_line_ids:
            values = {'lot_id': self.finished_lot_id.id}
            if 'quantity' in line._fields:
                values['quantity'] = self.unit_count
            elif 'qty_done' in line._fields:
                values['qty_done'] = self.unit_count
            line.write(values)

        picking.button_validate()
        self.state = 'moved'
        return True
