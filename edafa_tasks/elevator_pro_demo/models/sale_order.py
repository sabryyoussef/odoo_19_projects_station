from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    engineering_approved = fields.Boolean(string="Engineering Approved", default=False)
    elevator_lead_id = fields.Many2one("crm.lead", string="Elevator Lead")
    elevator_installation_task_id = fields.Many2one(
        "project.task", string="Installation Task", copy=False
    )
    elevator_equipment_id = fields.Many2one(
        "maintenance.equipment", string="Maintenance Equipment", copy=False
    )

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            order._create_installation_task_if_needed()
            if order.elevator_lead_id:
                order.elevator_lead_id.elevator_flow_stage = "manufacturing"
        return result

    def _create_installation_task_if_needed(self):
        for order in self:
            if order.elevator_installation_task_id:
                continue
            project = self.env["project.project"].search(
                [("name", "=", "Elevator Operations")], limit=1
            )
            if not project:
                project = self.env["project.project"].create({"name": "Elevator Operations"})

            task = self.env["project.task"].create(
                {
                    "name": f"Installation - {order.name}",
                    "project_id": project.id,
                    "partner_id": order.partner_id.id,
                    "elevator_task_type": "installation",
                    "elevator_sale_order_id": order.id,
                    "elevator_lead_id": order.elevator_lead_id.id,
                }
            )
            order.elevator_installation_task_id = task.id
            if order.elevator_lead_id:
                order.elevator_lead_id.elevator_flow_stage = "installation"

    def _create_maintenance_equipment_if_needed(self):
        for order in self:
            if order.elevator_equipment_id:
                continue
            product = order.order_line.filtered(lambda l: not l.display_type and l.product_id)[:1].product_id
            equipment = self.env["maintenance.equipment"].create(
                {
                    "name": f"{order.name} - Elevator",
                    "partner_id": order.partner_id.id,
                    "owner_user_id": order.user_id.id,
                    "category_id": False,
                    "serial_no": order.client_order_ref or order.name,
                    "technician_user_id": order.user_id.id,
                    "model": product.name if product else "Elevator",
                }
            )
            order.elevator_equipment_id = equipment.id
            if order.elevator_lead_id:
                order.elevator_lead_id.elevator_flow_stage = "live"
