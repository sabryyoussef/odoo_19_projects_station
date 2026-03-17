# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_nationality_id = fields.Many2one(
        'res.country',
        string='Document Nationality',
        help='Fallback nationality for HR document printing when contract/version nationality is not set.',
        groups='hr.group_hr_user',
    )
    document_id_iqama = fields.Char(
        string='Document ID / Iqama',
        help='Fallback ID/Iqama for HR document printing when contract/version ID is not set.',
        groups='hr.group_hr_user',
    )

    def action_print_work_commencement_notice(self):
        self.ensure_one()
        return self.env.ref(
            'hr_employee_document_prints.action_report_work_commencement_notice'
        ).report_action(self)
