from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    elevator_task_type = fields.Selection(
        selection=[
            ("inspection", "Inspection"),
            ("installation", "Installation"),
            ("quality", "Quality"),
        ],
        string="Elevator Task Type",
    )
    elevator_lead_id = fields.Many2one("crm.lead", string="Elevator Lead", copy=False)
    elevator_sale_order_id = fields.Many2one("sale.order", string="Sale Order", copy=False)
    inspection_status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("completed", "Completed"),
        ],
        string="Inspection Status",
        default="draft",
    )
    quality_passed = fields.Boolean(string="Quality Passed", copy=False)

    def action_set_inspection_draft(self):
        self.filtered(lambda task: task.elevator_task_type == "inspection").write(
            {"inspection_status": "draft"}
        )

    def action_set_inspection_scheduled(self):
        self.filtered(lambda task: task.elevator_task_type == "inspection").write(
            {"inspection_status": "scheduled"}
        )

    def action_set_inspection_completed(self):
        tasks = self.filtered(lambda task: task.elevator_task_type == "inspection")
        tasks.write({"inspection_status": "completed"})
        for task in tasks:
            if task.elevator_lead_id:
                task.elevator_lead_id.elevator_flow_stage = "manufacturing"

    def action_quality_pass(self):
        for task in self:
            task.quality_passed = True
            if task.elevator_lead_id:
                task.elevator_lead_id.elevator_flow_stage = "live"
            if task.elevator_sale_order_id:
                task.elevator_sale_order_id._create_maintenance_equipment_if_needed()
