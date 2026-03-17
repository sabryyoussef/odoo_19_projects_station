# -*- coding: utf-8 -*-
from odoo import models, fields


class StockLot(models.Model):
    _inherit = 'stock.lot'

    medtech_qc_status = fields.Selection([
        ('quarantine', 'Quarantine'),
        ('released', 'Released'),
        ('rejected', 'Rejected'),
    ], string='QC Status', default='quarantine', index=True)
    medtech_qc_released_at = fields.Datetime(string='QC Released At')
    medtech_qc_released_by_id = fields.Many2one('res.users', string='QC Released By')
