# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_fleet_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        help='Vehicle assigned for transport of components to site.',
    )
    x_final_shaft_height = fields.Float(
        string='Final Shaft Height (m)',
        help='Final site measurement: shaft height.',
    )
    x_final_shaft_width = fields.Float(
        string='Final Shaft Width (m)',
        help='Final site measurement: shaft width.',
    )
    x_final_shaft_depth = fields.Float(
        string='Final Shaft Depth (m)',
        help='Final site measurement: shaft depth.',
    )
    x_sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        index=True,
        help='Linked sale order (implementation task).',
    )
