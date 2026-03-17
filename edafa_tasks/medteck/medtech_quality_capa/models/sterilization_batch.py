# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MedTechSterilizationBatch(models.Model):
    _name = 'medtech.sterilization.batch'
    _description = 'Sterilization / Filtration Batch'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = [
        'state', 'operator_id', 'start_at', 'end_at', 'filter_batch', 'sterility_result', 'qc_status'
    ]

    name = fields.Char(string='Sterilization Batch Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    compounding_batch_id = fields.Many2one('medtech.compounding.batch', string='Compounding Batch', tracking=True)

    product_id = fields.Many2one(related='production_id.product_id', string='Finished Product', store=True, readonly=True)
    product_qty = fields.Float(related='production_id.product_qty', string='MO Qty', store=True, readonly=True)

    operator_id = fields.Many2one('res.users', string='Operator', tracking=True)
    start_at = fields.Datetime(string='Start Time', tracking=True)
    end_at = fields.Datetime(string='End Time', tracking=True)

    filter_batch = fields.Char(string='Filter Batch', tracking=True)
    filter_lot_id = fields.Many2one('stock.lot', string='Filter Lot', tracking=True)
    sterility_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Sterility Test Result', tracking=True)

    qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='QC Status', default='pending', tracking=True)

    decision = fields.Selection([
        ('to_filling', 'Move to Filling'),
        ('to_scrap', 'Scrap'),
        ('to_capa', 'Open CAPA'),
    ], string='Failure/Release Decision', tracking=True)

    nonconformance_id = fields.Many2one('medtech.nonconformance', string='Nonconformance', readonly=True)
    capa_id = fields.Many2one('medtech.capa', string='CAPA', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('qc_passed', 'QC Passed'),
        ('qc_failed', 'QC Failed'),
        ('moved', 'Moved to Filling'),
        ('scrapped', 'Scrapped'),
        ('capa_opened', 'CAPA Opened'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.sterilization.batch') or _('New')
        records = super().create(vals_list)
        for record in records.filtered(lambda r: r.production_id and not r.production_id.medtech_sterilization_batch_id):
            record.production_id.medtech_sterilization_batch_id = record.id
        return records

    def action_start_sterilization(self):
        self.ensure_one()
        if self.compounding_batch_id and self.compounding_batch_id.state not in ['moved', 'qc_passed']:
            raise ValidationError(_('Compounding batch must be QC passed/moved before sterilization starts.'))

        self.write({
            'state': 'in_progress',
            'operator_id': self.env.user.id,
            'start_at': fields.Datetime.now(),
        })
        return True

    def action_mark_passed(self):
        self.ensure_one()
        if not self.filter_batch:
            raise ValidationError(_('Filter batch is required.'))
        if self.sterility_result != 'pass':
            raise ValidationError(_('Sterility test result must be Pass to mark batch as passed.'))

        self.end_at = self.end_at or fields.Datetime.now()
        self.write({
            'qc_status': 'passed',
            'state': 'qc_passed',
            'decision': 'to_filling',
        })
        if self.production_id:
            self.production_id.medtech_inprocess_qc_status = 'passed'
        return True

    def action_mark_failed(self):
        self.ensure_one()
        if self.sterility_result != 'fail':
            raise ValidationError(_('Sterility test result must be Fail to mark batch as failed.'))

        self.end_at = self.end_at or fields.Datetime.now()
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

    def _create_internal_transfer(self, source_location, dest_location, qty):
        self.ensure_one()
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
            'product_uom_qty': qty,
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
            }
            if 'quantity' in self.env['stock.move.line']._fields:
                vals['quantity'] = qty
            elif 'qty_done' in self.env['stock.move.line']._fields:
                vals['qty_done'] = qty
            self.env['stock.move.line'].create(vals)

        for line in move.move_line_ids:
            if 'quantity' in line._fields:
                line.quantity = qty
            elif 'qty_done' in line._fields:
                line.qty_done = qty

        picking.button_validate()
        return picking

    def action_move_to_filling(self):
        self.ensure_one()
        if self.state != 'qc_passed':
            raise ValidationError(_('Only QC-passed sterilization batches can move to filling.'))

        source_location = self.env.ref('medtech_quality_capa.location_wip_sterilization', raise_if_not_found=False)
        dest_location = self.env.ref('medtech_quality_capa.location_wip_filling', raise_if_not_found=False)
        if not source_location or not dest_location:
            raise ValidationError(_('Required locations WIP/Sterilization or WIP/Filling are missing.'))

        self._create_internal_transfer(source_location, dest_location, self.product_qty)
        self.write({'state': 'moved', 'decision': 'to_filling'})
        return True

    def action_fail_to_scrap(self):
        self.ensure_one()
        if self.state != 'qc_failed':
            raise ValidationError(_('Batch must be in QC Failed state.'))

        source_location = self.env.ref('medtech_quality_capa.location_wip_sterilization', raise_if_not_found=False)
        scrap_location = self.env.ref('stock.stock_location_scrapped', raise_if_not_found=False)
        if not source_location or not scrap_location:
            raise ValidationError(_('Required source or scrap location is missing.'))

        self._create_internal_transfer(source_location, scrap_location, self.product_qty)
        self.write({'state': 'scrapped', 'decision': 'to_scrap'})
        return True

    def action_fail_open_capa(self):
        self.ensure_one()
        if self.state != 'qc_failed':
            raise ValidationError(_('Batch must be in QC Failed state.'))

        nc = self.nonconformance_id
        if not nc:
            nc = self.env['medtech.nonconformance'].create({
                'source': 'manufacturing',
                'severity': 'high',
                'description': _('Sterility failure in %(batch)s for MO %(mo)s') % {
                    'batch': self.name,
                    'mo': self.production_id.name,
                },
                'affected_product_ids': [(4, self.product_id.id)],
                'state': 'investigation',
            })
            self.nonconformance_id = nc.id

        capa = self.capa_id
        if not capa:
            capa = self.env['medtech.capa'].create({
                'source': 'nonconformance',
                'description': _('CAPA opened from sterility failure in %(batch)s') % {'batch': self.name},
                'nonconformance_ids': [(4, nc.id)],
                'affected_product_ids': [(4, self.product_id.id)],
            })
            self.capa_id = capa.id

        self.write({'state': 'capa_opened', 'decision': 'to_capa'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'CAPA',
            'res_model': 'medtech.capa',
            'res_id': capa.id,
            'view_mode': 'form',
            'target': 'current',
        }
