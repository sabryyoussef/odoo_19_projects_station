# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MedTechWeighingBatch(models.Model):
    _name = 'medtech.weighing.batch'
    _description = 'Weighing & Dispensing Batch'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = ['state', 'operator_id', 'weighed_at', 'production_id']

    name = fields.Char(string='Batch Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    product_id = fields.Many2one(related='production_id.product_id', string='Finished Product', store=True, readonly=True)
    product_qty = fields.Float(related='production_id.product_qty', string='MO Qty', store=True, readonly=True)

    operator_id = fields.Many2one('res.users', string='Operator', tracking=True)
    weighed_at = fields.Datetime(string='Weighing Timestamp', tracking=True)

    line_ids = fields.One2many('medtech.weighing.batch.line', 'batch_id', string='Weighing Lines')
    line_count = fields.Integer(string='Line Count', compute='_compute_line_count')

    inprocess_qc_id = fields.Many2one('medtech.inprocess.qc', string='In-Process QC', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('qc_pending', 'QC Pending'),
        ('qc_passed', 'QC Passed'),
        ('qc_failed', 'QC Failed'),
        ('moved', 'Moved to Compounding'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.weighing.batch') or _('New')
        batches = super().create(vals_list)
        for batch in batches.filtered(lambda b: b.production_id and not b.production_id.medtech_weighing_batch_id):
            batch.production_id.medtech_weighing_batch_id = batch.id
        return batches

    def action_prepare_lines(self):
        self.ensure_one()
        if not self.production_id:
            raise ValidationError(_('Manufacturing Order is required.'))

        self.line_ids.unlink()
        for move in self.production_id.move_raw_ids.filtered(lambda m: m.state not in ['cancel', 'done']):
            reserved_lot = False
            reserved_qty = 0.0
            move_line = move.move_line_ids[:1]
            if move_line:
                reserved_lot = move_line.lot_id
                if 'quantity' in move_line._fields:
                    reserved_qty = move_line.quantity
                elif 'qty_done' in move_line._fields:
                    reserved_qty = move_line.qty_done

            self.env['medtech.weighing.batch.line'].create({
                'batch_id': self.id,
                'product_id': move.product_id.id,
                'uom_id': move.product_uom.id,
                'required_qty': move.product_uom_qty,
                'reserved_qty': reserved_qty,
                'lot_id': reserved_lot.id if reserved_lot else False,
                'stock_move_id': move.id,
            })

        if self.state == 'draft':
            self.state = 'in_progress'
        return True

    def action_start_weighing(self):
        self.ensure_one()
        if not self.line_ids:
            self.action_prepare_lines()
        self.write({
            'state': 'in_progress',
            'operator_id': self.env.user.id,
            'weighed_at': fields.Datetime.now(),
        })
        return True

    def action_submit_for_qc(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_('No weighing lines found. Prepare lines first.'))

        for line in self.line_ids:
            if line.actual_qty <= 0:
                raise ValidationError(_('Actual weighed quantity must be greater than zero for all lines.'))
            if not line.lot_id:
                raise ValidationError(_('Lot number is required for all weighed lines.'))

        qc = self.inprocess_qc_id
        if not qc:
            qc = self.env['medtech.inprocess.qc'].create({
                'check_type': 'weighing_dispensing',
                'production_id': self.production_id.id,
                'weighing_batch_id': self.id,
                'notes': _('In-process QC created from Weighing & Dispensing batch.'),
            })
            self.inprocess_qc_id = qc.id

        self.state = 'qc_pending'
        self.production_id.medtech_inprocess_qc_status = 'pending'
        return {
            'type': 'ir.actions.act_window',
            'name': 'In-Process QC',
            'res_model': 'medtech.inprocess.qc',
            'res_id': qc.id,
            'view_mode': 'form',
            'target': 'current',
        }

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

    def action_move_to_compounding(self):
        self.ensure_one()
        if self.state != 'qc_passed':
            raise ValidationError(_('Batch can only move to compounding after QC pass.'))

        source_location = self.env.ref('medtech_quality_capa.location_raw_material_released', raise_if_not_found=False)
        dest_location = self.env.ref('medtech_quality_capa.location_wip_compounding', raise_if_not_found=False)
        if not source_location or not dest_location:
            raise ValidationError(_('Required locations Raw Material/Released or WIP/Compounding are missing.'))

        picking_type = self._get_internal_picking_type()
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': source_location.id,
            'location_dest_id': dest_location.id,
            'origin': self.name,
        })

        for line in self.line_ids:
            move = self.env['stock.move'].create({
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.actual_qty,
                'product_uom': line.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
                'picking_id': picking.id,
            })
            move._action_confirm()
            move._action_assign()

            if not move.move_line_ids:
                self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'picking_id': picking.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.uom_id.id,
                    'location_id': source_location.id,
                    'location_dest_id': dest_location.id,
                    'lot_id': line.lot_id.id,
                })

            for move_line in move.move_line_ids:
                values = {'lot_id': line.lot_id.id}
                if 'quantity' in move_line._fields:
                    values['quantity'] = line.actual_qty
                elif 'qty_done' in move_line._fields:
                    values['qty_done'] = line.actual_qty
                move_line.write(values)

        picking.button_validate()
        self.state = 'moved'
        return True


class MedTechWeighingBatchLine(models.Model):
    _name = 'medtech.weighing.batch.line'
    _description = 'Weighing & Dispensing Line'
    _order = 'id'

    batch_id = fields.Many2one('medtech.weighing.batch', string='Batch', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Raw Material', required=True)
    lot_id = fields.Many2one('stock.lot', string='Lot Number', domain="[('product_id', '=', product_id)]")
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True)

    required_qty = fields.Float(string='Required Qty', required=True)
    reserved_qty = fields.Float(string='Reserved Qty')
    actual_qty = fields.Float(string='Actual Weighed Qty', required=True, default=0.0)

    stock_move_id = fields.Many2one('stock.move', string='MO Raw Move', readonly=True)
