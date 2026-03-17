from odoo import _, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    elevator_flow_stage = fields.Selection(
        selection=[
            ("new", "New"),
            ("inspection", "Inspection"),
            ("manufacturing", "Manufacturing"),
            ("installation", "Installation"),
            ("qc", "QC"),
            ("live", "Live"),
        ],
        default="new",
        tracking=True,
    )
    shaft_height = fields.Float(string="Shaft Height (m)")
    shaft_width = fields.Float(string="Shaft Width (m)")
    shaft_depth = fields.Float(string="Shaft Depth (m)")
    floors_count = fields.Integer(string="Floors")
    passengers_capacity = fields.Integer(string="Passengers Capacity")
    elevator_speed = fields.Float(string="Speed (m/s)")
    machine_room_required = fields.Boolean(string="Machine Room Required")
    site_inspection_task_id = fields.Many2one(
        "project.task", string="Site Inspection Task", copy=False
    )

    def action_create_site_inspection(self):
        self.ensure_one()
        if self.site_inspection_task_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "project.task",
                "res_id": self.site_inspection_task_id.id,
                "view_mode": "form",
            }

        project = self.env["project.project"].search(
            [("name", "=", "Elevator Operations")], limit=1
        )
        if not project:
            project = self.env["project.project"].create({"name": "Elevator Operations"})

        inspection_stage = self.env["project.task.type"].search(
            [("name", "=", "Inspection")], limit=1
        )

        task = self.env["project.task"].create(
            {
                "name": _("Site Inspection - %s") % self.name,
                "project_id": project.id,
                "stage_id": inspection_stage.id,
                "partner_id": self.partner_id.id,
                "elevator_lead_id": self.id,
                "elevator_task_type": "inspection",
                "inspection_status": "draft",
            }
        )
        self.site_inspection_task_id = task.id
        self.elevator_flow_stage = "inspection"

        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "res_id": task.id,
            "view_mode": "form",
        }
