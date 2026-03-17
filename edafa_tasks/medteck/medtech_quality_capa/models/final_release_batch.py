# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MedTechFinalReleaseBatch(models.Model):
    _name = 'medtech.final.release.batch'
    _description = 'Final Release Batch'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _audit_tracked_fields = ['state', 'requested_by_id', 'approved_by_id', 'approved_at']

    name = fields.Char(string='Final Release Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, tracking=True)
    packaging_batch_id = fields.Many2one('medtech.packaging.batch', string='Packaging Batch', tracking=True)

    product_id = fields.Many2one(related='production_id.product_id', string='Finished Product', store=True, readonly=True)
    release_qty = fields.Integer(string='Release Qty', default=20, required=True)
    finished_lot_id = fields.Many2one('stock.lot', string='Finished Product Lot', tracking=True)

    requested_by_id = fields.Many2one('res.users', string='Requested By', readonly=True)
    requested_at = fields.Datetime(string='Requested At', readonly=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_at = fields.Datetime(string='Approved At', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_qa', 'Pending QA Approval'),
        ('approved', 'Approved'),
        ('released', 'Released to FG'),
    ], string='State', default='draft', required=True, tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.final.release.batch') or _('New')
        records = super().create(vals_list)
        for record in records.filtered(lambda r: r.production_id and not r.production_id.medtech_final_release_batch_id):
            record.production_id.medtech_final_release_batch_id = record.id
        return records

    def action_request_qa_approval(self):
        self.ensure_one()
        if self.release_qty != 20:
            raise ValidationError(_('This demo workflow requires release quantity of 20 units.'))

        if not self.finished_lot_id and self.packaging_batch_id and self.packaging_batch_id.finished_lot_id:
            self.finished_lot_id = self.packaging_batch_id.finished_lot_id.id

        if not self.finished_lot_id:
            raise ValidationError(_('Finished lot is required before requesting final release approval.'))

        self.write({
            'state': 'pending_qa',
            'requested_by_id': self.env.user.id,
            'requested_at': fields.Datetime.now(),
        })
        return True

    def action_approve_release(self):
        self.ensure_one()
        if self.state != 'pending_qa':
            raise ValidationError(_('Release must be in Pending QA Approval state.'))
        if not self.env.user.has_group('medtech_core.group_medtech_quality_manager'):
            raise UserError(_('Only Quality Manager can approve final release.'))

        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_at': fields.Datetime.now(),
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

    def action_release_to_fg(self):
        self.ensure_one()
        if self.state != 'approved':
            raise ValidationError(_('Batch must be approved before release to Finished Goods/Released.'))
        if not self.finished_lot_id:
            raise ValidationError(_('Finished lot is required.'))

        source_location = self.env.ref('medtech_quality_capa.location_finished_goods_quarantine', raise_if_not_found=False)
        dest_location = self.env.ref('medtech_quality_capa.location_finished_goods_released', raise_if_not_found=False)
        if not source_location or not dest_location:
            raise ValidationError(_('Required locations Finished Goods/Quarantine or Finished Goods/Released are missing.'))

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
            'product_uom_qty': self.release_qty,
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
                vals['quantity'] = self.release_qty
            elif 'qty_done' in self.env['stock.move.line']._fields:
                vals['qty_done'] = self.release_qty
            self.env['stock.move.line'].create(vals)

        for line in move.move_line_ids:
            values = {'lot_id': self.finished_lot_id.id}
            if 'quantity' in line._fields:
                values['quantity'] = self.release_qty
            elif 'qty_done' in line._fields:
                values['qty_done'] = self.release_qty
            line.write(values)

        picking.button_validate()

        self.finished_lot_id.write({
            'medtech_qc_status': 'released',
            'medtech_qc_released_at': fields.Datetime.now(),
            'medtech_qc_released_by_id': self.approved_by_id.id or self.env.user.id,
        })

        self.state = 'released'
        return True
