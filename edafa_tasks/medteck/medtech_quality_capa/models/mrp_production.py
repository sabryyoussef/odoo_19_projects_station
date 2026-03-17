# -*- coding: utf-8 -*-
from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    medtech_weighing_batch_id = fields.Many2one('medtech.weighing.batch', string='Weighing Batch')
    medtech_compounding_batch_id = fields.Many2one('medtech.compounding.batch', string='Compounding Batch')
    medtech_sterilization_batch_id = fields.Many2one('medtech.sterilization.batch', string='Sterilization Batch')
    medtech_filling_batch_id = fields.Many2one('medtech.filling.batch', string='Filling Batch')
    medtech_packaging_batch_id = fields.Many2one('medtech.packaging.batch', string='Packaging Batch')
    medtech_final_release_batch_id = fields.Many2one('medtech.final.release.batch', string='Final Release Batch')
    medtech_inprocess_qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='In-Process QC Status', default='pending', tracking=True)

    def action_open_medtech_weighing_batch(self):
        self.ensure_one()
        batch = self.medtech_weighing_batch_id
        if not batch:
            batch = self.env['medtech.weighing.batch'].create({
                'production_id': self.id,
            })
            self.medtech_weighing_batch_id = batch.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Weighing & Dispensing',
            'res_model': 'medtech.weighing.batch',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_medtech_compounding_batch(self):
        self.ensure_one()
        batch = self.medtech_compounding_batch_id
        if not batch:
            batch = self.env['medtech.compounding.batch'].create({
                'production_id': self.id,
                'weighing_batch_id': self.medtech_weighing_batch_id.id,
            })
            self.medtech_compounding_batch_id = batch.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Compounding',
            'res_model': 'medtech.compounding.batch',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_medtech_sterilization_batch(self):
        self.ensure_one()
        batch = self.medtech_sterilization_batch_id
        if not batch:
            batch = self.env['medtech.sterilization.batch'].create({
                'production_id': self.id,
                'compounding_batch_id': self.medtech_compounding_batch_id.id,
            })
            self.medtech_sterilization_batch_id = batch.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sterilization / Filtration',
            'res_model': 'medtech.sterilization.batch',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_medtech_filling_batch(self):
        self.ensure_one()
        batch = self.medtech_filling_batch_id
        if not batch:
            batch = self.env['medtech.filling.batch'].create({
                'production_id': self.id,
                'sterilization_batch_id': self.medtech_sterilization_batch_id.id,
            })
            self.medtech_filling_batch_id = batch.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Filling',
            'res_model': 'medtech.filling.batch',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_medtech_packaging_batch(self):
        self.ensure_one()
        batch = self.medtech_packaging_batch_id
        if not batch:
            batch = self.env['medtech.packaging.batch'].create({
                'production_id': self.id,
                'filling_batch_id': self.medtech_filling_batch_id.id,
            })
            self.medtech_packaging_batch_id = batch.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Packaging',
            'res_model': 'medtech.packaging.batch',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_medtech_final_release_batch(self):
        self.ensure_one()
        batch = self.medtech_final_release_batch_id
        if not batch:
            batch = self.env['medtech.final.release.batch'].create({
                'production_id': self.id,
                'packaging_batch_id': self.medtech_packaging_batch_id.id,
            })
            self.medtech_final_release_batch_id = batch.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Final Release',
            'res_model': 'medtech.final.release.batch',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }
