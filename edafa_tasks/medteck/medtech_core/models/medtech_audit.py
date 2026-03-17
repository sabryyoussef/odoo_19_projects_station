# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class MedTechAuditEvent(models.Model):
    """Compliance-grade audit trail for all critical operations"""
    _name = 'medtech.audit.event'
    _description = 'MedTech Audit Event'
    _order = 'timestamp desc'
    _rec_name = 'model'

    model = fields.Char(string='Model', required=True, index=True)
    res_id = fields.Integer(string='Record ID', required=True, index=True)
    operation = fields.Selection([
        ('create', 'Create'),
        ('write', 'Update'),
        ('unlink', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('quarantine', 'Quarantine'),
        ('release', 'Release'),
    ], string='Operation', required=True, index=True)
    
    user_id = fields.Many2one('res.users', string='User', required=True, index=True, default=lambda self: self.env.user)
    timestamp = fields.Datetime(string='Timestamp', required=True, index=True, default=fields.Datetime.now)
    
    old_values = fields.Text(string='Old Values (JSON)')
    new_values = fields.Text(string='New Values (JSON)')
    context_info = fields.Text(string='Context Information')
    
    record_reference = fields.Char(string='Record Reference', compute='_compute_record_reference', store=True)
    change_summary = fields.Char(string='Change Summary', compute='_compute_change_summary')
    ip_address = fields.Char(string='IP Address')
    session_id = fields.Char(string='Session ID')
    
    @api.depends('model', 'res_id')
    def _compute_record_reference(self):
        for record in self:
            record.record_reference = f"{record.model},{record.res_id}" if record.model and record.res_id else False
    
    @api.depends('operation', 'old_values', 'new_values')
    def _compute_change_summary(self):
        for record in self:
            if record.operation == 'create':
                record.change_summary = 'Record created'
            elif record.operation == 'unlink':
                record.change_summary = 'Record deleted'
            elif record.operation in ('write', 'approve', 'reject'):
                try:
                    changes = json.loads(record.new_values) if record.new_values else {}
                    if changes:
                        record.change_summary = ', '.join([f"{k}: {v}" for k, v in list(changes.items())[:3]])
                    else:
                        record.change_summary = f'{record.operation.capitalize()} operation'
                except:
                    record.change_summary = f'{record.operation.capitalize()} operation'
            else:
                record.change_summary = record.operation or 'Unknown operation'
    
    def _create_audit_event(self, model, res_id, operation, old_vals=None, new_vals=None, context_info=None):
        """Helper method to create audit events"""
        return self.create({
            'model': model,
            'res_id': res_id,
            'operation': operation,
            'old_values': json.dumps(old_vals) if old_vals else False,
            'new_values': json.dumps(new_vals) if new_vals else False,
            'context_info': context_info,
        })
