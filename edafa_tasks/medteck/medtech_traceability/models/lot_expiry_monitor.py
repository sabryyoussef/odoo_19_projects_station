# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MedTechLotExpiryMonitor(models.Model):
    _name = 'medtech.lot.expiry.monitor'
    _description = 'Lot Expiry Monitor'
    _order = 'expiry_date asc'

    lot_id = fields.Many2one('stock.lot', string='Lot', required=True, index=True)
    product_id = fields.Many2one(related='lot_id.product_id', string='Product', store=True, readonly=True)
    expiry_date = fields.Date(string='Expiry Date', required=True, index=True)
    days_to_expiry = fields.Integer(string='Days to Expiry', compute='_compute_days_to_expiry', store=False)
    status = fields.Selection([
        ('expired', 'Expired'),
        ('critical', 'Critical (<= 30 days)'),
        ('warning', 'Warning (<= 90 days)'),
        ('ok', 'OK'),
    ], string='Status', compute='_compute_status', store=True)

    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for record in self:
            if record.expiry_date:
                record.days_to_expiry = (record.expiry_date - today).days
            else:
                record.days_to_expiry = 0

    @api.depends('expiry_date')
    def _compute_status(self):
        for record in self:
            days_to_expiry = 0
            if record.expiry_date:
                days_to_expiry = (record.expiry_date - fields.Date.today()).days
            if days_to_expiry < 0:
                record.status = 'expired'
            elif days_to_expiry <= 30:
                record.status = 'critical'
            elif days_to_expiry <= 90:
                record.status = 'warning'
            else:
                record.status = 'ok'

    @api.model
    def refresh_monitor_table(self):
        self.search([]).unlink()

        lots = self.env['stock.lot'].search([])
        for lot in lots:
            expiry = False
            if 'expiration_date' in lot._fields:
                expiry = lot.expiration_date
            elif 'use_date' in lot._fields:
                expiry = lot.use_date
            elif 'life_date' in lot._fields:
                expiry = lot.life_date

            if expiry:
                self.create({
                    'lot_id': lot.id,
                    'expiry_date': expiry,
                })
        return True
