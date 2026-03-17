# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_project_task_ids = fields.One2many(
        'project.task',
        'x_sale_order_id',
        string='Implementation Tasks',
        help='Project/Field Service tasks created from this order.',
    )
    x_project_task_count = fields.Integer(
        string='Task Count',
        compute='_compute_x_project_task_count',
    )

    def _compute_x_project_task_count(self):
        for order in self:
            order.x_project_task_count = len(order.x_project_task_ids)

    def action_view_project_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Implementation Tasks',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('x_sale_order_id', '=', self.id)],
            'context': {'default_x_sale_order_id': self.id},
        }
