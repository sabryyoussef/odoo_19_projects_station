# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_elevator_floors = fields.Integer(
        string='Number of Floors',
        help='Number of floors from technical survey.',
    )
    x_elevator_shaft_height = fields.Float(
        string='Shaft Height (m)',
        help='Shaft dimension: height in meters.',
    )
    x_elevator_shaft_width = fields.Float(
        string='Shaft Width (m)',
        help='Shaft dimension: width in meters.',
    )
    x_elevator_shaft_depth = fields.Float(
        string='Shaft Depth (m)',
        help='Shaft dimension: depth in meters.',
    )
    x_elevator_passenger_capacity = fields.Integer(
        string='Passenger Capacity',
        help='Passenger capacity from technical survey.',
    )
