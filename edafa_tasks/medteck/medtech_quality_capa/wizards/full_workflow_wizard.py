# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedTechFullWorkflowWizard(models.TransientModel):
    _name = 'medtech.full.workflow.wizard'
    _description = 'Demo Full Workflow Wizard - Eye Drops 10ml'

    name = fields.Char(string='Workflow Run', default=lambda self: _('Eye Drops 10ml Demo Workflow'))

    product_id = fields.Many2one('product.product', string='Finished Product', required=True)
    target_units = fields.Integer(string='Target Units', default=20, required=True)

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=True)
    finished_lot_id = fields.Many2one('stock.lot', string='Finished Product Lot', readonly=True)
    recall_record_id = fields.Integer(string='Recall Record ID', readonly=True)
    recall_name = fields.Char(string='Recall Reference', readonly=True)

    state = fields.Selection([
        ('stage1', 'Stage 1 - Intake'),
        ('stage2', 'Stage 2 - Weighing'),
        ('stage3', 'Stage 3 - Compounding'),
        ('stage4', 'Stage 4 - Sterilization'),
        ('stage5', 'Stage 5 - Filling'),
        ('stage6', 'Stage 6 - Packaging'),
        ('quality', 'Quality + Release'),
        ('traceability', 'Traceability + Recall'),
        ('done', 'Completed'),
    ], string='Workflow Stage', default='stage1', required=True)

    stage1_at = fields.Datetime(string='Stage 1 Completed At', readonly=True)
    stage2_at = fields.Datetime(string='Stage 2 Completed At', readonly=True)
    stage3_at = fields.Datetime(string='Stage 3 Completed At', readonly=True)
    stage4_at = fields.Datetime(string='Stage 4 Completed At', readonly=True)
    stage5_at = fields.Datetime(string='Stage 5 Completed At', readonly=True)
    stage6_at = fields.Datetime(string='Stage 6 Completed At', readonly=True)
    final_release_at = fields.Datetime(string='Final Release At', readonly=True)

    incoming_qc_done = fields.Boolean(string='Incoming Raw Material Inspection', default=False, readonly=True)
    inprocess_qc_done = fields.Boolean(string='In-Process QC', default=False, readonly=True)
    sterility_qc_done = fields.Boolean(string='Sterility Control', default=False, readonly=True)
    final_release_done = fields.Boolean(string='Final Release Approval', default=False, readonly=True)

    traceability_done = fields.Boolean(string='Traceability Verified', default=False, readonly=True)
    recall_ready_done = fields.Boolean(string='Recall Simulation Ready', default=False, readonly=True)
    docs_generated = fields.Boolean(string='Compliance Docs Prepared', default=False, readonly=True)

    notes = fields.Text(string='Run Notes')

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        product = self.env['product.product'].search([('name', 'ilike', 'Eye Drops 10ml')], limit=1)
        if product:
            vals['product_id'] = product.id
        return vals

    def _ensure_mo(self):
        self.ensure_one()
        if self.production_id:
            return self.production_id
        if self.target_units != 20:
            raise ValidationError(_('This workflow is designed for 20 units.'))

        bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('type', '=', 'normal'),
        ], limit=1)

        mo_vals = {
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'product_qty': float(self.target_units),
            'origin': self.name,
        }
        if bom:
            mo_vals['bom_id'] = bom.id

        mo = self.env['mrp.production'].create(mo_vals)
        self.production_id = mo.id
        return mo

    def action_stage1_complete(self):
        self.ensure_one()
        self.write({
            'incoming_qc_done': True,
            'stage1_at': fields.Datetime.now(),
            'state': 'stage2',
        })
        return True

    def action_open_incoming_qc(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Incoming QC',
            'res_model': 'medtech.incoming.qc',
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_stage2_open_weighing(self):
        self.ensure_one()
        mo = self._ensure_mo()
        return mo.action_open_medtech_weighing_batch()

    def action_stage2_complete(self):
        self.ensure_one()
        self.write({
            'inprocess_qc_done': True,
            'stage2_at': fields.Datetime.now(),
            'state': 'stage3',
        })
        return True

    def action_stage3_open_compounding(self):
        self.ensure_one()
        mo = self._ensure_mo()
        return mo.action_open_medtech_compounding_batch()

    def action_stage3_complete(self):
        self.ensure_one()
        self.write({
            'stage3_at': fields.Datetime.now(),
            'state': 'stage4',
        })
        return True

    def action_stage4_open_sterilization(self):
        self.ensure_one()
        mo = self._ensure_mo()
        return mo.action_open_medtech_sterilization_batch()

    def action_stage4_complete(self):
        self.ensure_one()
        self.write({
            'sterility_qc_done': True,
            'stage4_at': fields.Datetime.now(),
            'state': 'stage5',
        })
        return True

    def action_stage5_open_filling(self):
        self.ensure_one()
        mo = self._ensure_mo()
        return mo.action_open_medtech_filling_batch()

    def action_stage5_complete(self):
        self.ensure_one()
        filling_batch = self.env['medtech.filling.batch'].search([('production_id', '=', self.production_id.id)], limit=1)
        if filling_batch and filling_batch.finished_lot_id:
            self.finished_lot_id = filling_batch.finished_lot_id.id

        self.write({
            'stage5_at': fields.Datetime.now(),
            'state': 'stage6',
        })
        return True

    def action_stage6_complete(self):
        self.ensure_one()
        packaging_batch = self.env['medtech.packaging.batch'].search([('production_id', '=', self.production_id.id)], limit=1)
        if packaging_batch and packaging_batch.finished_lot_id:
            self.finished_lot_id = packaging_batch.finished_lot_id.id

        self.write({
            'stage6_at': fields.Datetime.now(),
            'state': 'quality',
        })
        return True

    def action_stage6_open_packaging(self):
        self.ensure_one()
        mo = self._ensure_mo()
        return mo.action_open_medtech_packaging_batch()

    def action_quality_release_complete(self):
        self.ensure_one()
        release_batch = self.env['medtech.final.release.batch'].search([('production_id', '=', self.production_id.id)], limit=1)
        if release_batch and release_batch.state != 'released':
            raise ValidationError(_('Final release batch must be in Released state first.'))

        self.write({
            'final_release_done': True,
            'final_release_at': fields.Datetime.now(),
            'state': 'traceability',
        })
        return True

    def action_open_final_release(self):
        self.ensure_one()
        mo = self._ensure_mo()
        return mo.action_open_medtech_final_release_batch()

    def action_open_capa(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'CAPAs',
            'res_model': 'medtech.capa',
            'view_mode': 'kanban,list,form',
            'target': 'current',
        }

    def action_open_batch_search(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Instant Batch Search',
            'res_model': 'medtech.batch.search.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_open_expiry_monitoring(self):
        monitor = self.env['medtech.lot.expiry.monitor']
        monitor.refresh_monitor_table()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expiry Monitoring',
            'res_model': 'medtech.lot.expiry.monitor',
            'view_mode': 'list',
            'target': 'current',
        }

    def action_open_recall_simulation(self):
        self.ensure_one()
        if 'medtech.recall' not in self.env:
            raise ValidationError(_('Install/upgrade module "medtech_recall" to use recall simulation.'))

        recall_model = self.env['medtech.recall']
        recall = recall_model.browse(self.recall_record_id).exists() if self.recall_record_id else recall_model
        if recall:
            recall = recall[0]
        else:
            affected_method = 'by_lot' if self.finished_lot_id else 'by_product'
            vals = {
                'classification': 'class_ii',
                'severity': 'high',
                'recall_type': 'quality',
                'trigger_source': 'internal_testing',
                'description': _('Demo recall simulation for workflow run %(run)s') % {'run': self.name},
                'affected_determination': affected_method,
                'affected_product_ids': [(6, 0, [self.product_id.id])],
            }
            if self.finished_lot_id:
                vals['affected_lot_ids'] = [(6, 0, [self.finished_lot_id.id])]
            recall = recall_model.create(vals)
            self.recall_record_id = recall.id
            self.recall_name = recall.name

        return {
            'type': 'ir.actions.act_window',
            'name': 'Recall Simulation',
            'res_model': 'medtech.recall',
            'res_id': recall.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_run_recall_simulation(self):
        self.ensure_one()
        if 'medtech.recall' not in self.env:
            raise ValidationError(_('Install/upgrade module "medtech_recall" to use recall simulation.'))
        if not self.recall_record_id:
            self.action_open_recall_simulation()
        recall = self.env['medtech.recall'].browse(self.recall_record_id).exists()
        if not recall:
            raise ValidationError(_('Recall record is missing. Re-open recall simulation first.'))
        recall.action_run_recall_simulation()
        self.recall_name = recall.name
        self.recall_ready_done = True
        return True

    def action_generate_recall_docs(self):
        self.ensure_one()
        if 'medtech.recall' not in self.env:
            raise ValidationError(_('Install/upgrade module "medtech_recall" to generate regulatory pack.'))
        if not self.recall_record_id:
            raise ValidationError(_('Create/open recall simulation first.'))
        recall = self.env['medtech.recall'].browse(self.recall_record_id).exists()
        if not recall:
            raise ValidationError(_('Recall record is missing. Re-open recall simulation first.'))
        action = recall.action_generate_regulatory_pack()
        self.recall_name = recall.name
        self.docs_generated = True
        return action

    def action_mark_traceability_ready(self):
        self.ensure_one()
        self.write({'traceability_done': True})
        return True

    def action_mark_recall_ready(self):
        self.ensure_one()
        self.write({'recall_ready_done': True})
        return True

    def action_mark_docs_generated(self):
        self.ensure_one()
        self.write({'docs_generated': True})
        return True

    def action_complete_workflow(self):
        self.ensure_one()
        if not self.final_release_done:
            raise ValidationError(_('Final release must be completed first.'))
        if not self.traceability_done:
            raise ValidationError(_('Mark traceability as verified before completing workflow.'))
        if not self.recall_ready_done:
            raise ValidationError(_('Recall simulation must be completed before workflow completion.'))
        if not self.docs_generated:
            raise ValidationError(_('Generate recall/compliance documentation before workflow completion.'))
        self.state = 'done'
        return True
