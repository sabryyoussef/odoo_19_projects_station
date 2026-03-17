# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MedTechCompoundingBatch(models.Model):
    _name = 'medtech.compounding.batch'
    _description = 'Compounding Batch'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = [
        'state', 'operator_id', 'start_at', 'end_at', 'ph_result', 'clarity_result', 'qc_status'
    ]

    name = fields.Char(string='Compounding Batch Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    weighing_batch_id = fields.Many2one('medtech.weighing.batch', string='Weighing Batch', tracking=True)

    product_id = fields.Many2one(related='production_id.product_id', string='Finished Product', store=True, readonly=True)
    product_qty = fields.Float(related='production_id.product_qty', string='MO Qty', store=True, readonly=True)

    operator_id = fields.Many2one('res.users', string='Operator', tracking=True)
    start_at = fields.Datetime(string='Start Time', tracking=True)
    end_at = fields.Datetime(string='End Time', tracking=True)

    ph_result = fields.Float(string='pH Result', tracking=True)
    ph_min = fields.Float(string='Min pH', default=6.5)
    ph_max = fields.Float(string='Max pH', default=7.5)
    clarity_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Clarity Result', tracking=True)

    qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='QC Status', default='pending', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('qc_pending', 'QC Pending'),
        ('qc_passed', 'QC Passed'),
        ('qc_failed', 'QC Failed'),
        ('moved', 'Moved to Sterilization'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.compounding.batch') or _('New')
        records = super().create(vals_list)
        for record in records.filtered(lambda r: r.production_id and not r.production_id.medtech_compounding_batch_id):
            record.production_id.medtech_compounding_batch_id = record.id
        return records

    def action_start_compounding(self):
        self.ensure_one()
        if self.weighing_batch_id and self.weighing_batch_id.state not in ['moved', 'qc_passed']:
            raise ValidationError(_('Weighing batch must be QC passed/moved before compounding starts.'))

        self.write({
            'state': 'in_progress',
            'operator_id': self.env.user.id,
            'start_at': fields.Datetime.now(),
        })
        return True

    def action_submit_qc(self):
        self.ensure_one()
        if self.state not in ['in_progress', 'draft']:
            raise ValidationError(_('QC can only be submitted from Draft/In Progress states.'))
        if self.ph_result <= 0:
            raise ValidationError(_('pH test result is required.'))
        if not self.clarity_result:
            raise ValidationError(_('Clarity test result is required.'))

        self.end_at = self.end_at or fields.Datetime.now()

        ph_passed = self.ph_min <= self.ph_result <= self.ph_max
        clarity_passed = self.clarity_result == 'pass'

        if ph_passed and clarity_passed:
            self.write({
                'qc_status': 'passed',
                'state': 'qc_passed',
            })
            if self.production_id:
                self.production_id.medtech_inprocess_qc_status = 'passed'
        else:
            self.write({
                'qc_status': 'failed',
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

    def action_move_to_sterilization(self):
        self.ensure_one()
        if self.state != 'qc_passed':
            raise ValidationError(_('Only QC-passed compounding batches can move to sterilization.'))

        source_location = self.env.ref('medtech_quality_capa.location_wip_compounding', raise_if_not_found=False)
        dest_location = self.env.ref('medtech_quality_capa.location_wip_sterilization', raise_if_not_found=False)
        if not source_location or not dest_location:
            raise ValidationError(_('Required locations WIP/Compounding or WIP/Sterilization are missing.'))

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
            'product_uom_qty': self.product_qty,
            'product_uom': self.product_id.uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': dest_location.id,
            'picking_id': picking.id,
        })
        move._action_confirm()
        move._action_assign()

        for move_line in move.move_line_ids:
            if 'quantity' in move_line._fields:
                move_line.quantity = self.product_qty
            elif 'qty_done' in move_line._fields:
                move_line.qty_done = self.product_qty

        if not move.move_line_ids:
            vals = {
                'move_id': move.id,
                'picking_id': picking.id,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
            }
            if 'quantity' in self.env['stock.move.line']._fields:
                vals['quantity'] = self.product_qty
            elif 'qty_done' in self.env['stock.move.line']._fields:
                vals['qty_done'] = self.product_qty
            self.env['stock.move.line'].create(vals)

        picking.button_validate()
        self.state = 'moved'
        return True
