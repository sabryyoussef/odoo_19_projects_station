# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class MedTechAuditMixin(models.AbstractModel):
    """Mixin to add automatic audit trail to any model"""
    _name = 'medtech.audit.mixin'
    _description = 'MedTech Audit Trail Mixin'

    audit_event_ids = fields.One2many('medtech.audit.event', compute='_compute_audit_events', string='Audit Trail')
    audit_count = fields.Integer(string='Audit Events', compute='_compute_audit_events')
    
    # Fields to track (can be overridden in inheriting models)
    _audit_tracked_fields = []  # List of field names to track
    
    @api.depends()
    def _compute_audit_events(self):
        """Compute audit events for this record"""
        for record in self:
            events = self.env['medtech.audit.event'].search([
                ('model', '=', record._name),
                ('res_id', '=', record.id)
            ])
            record.audit_event_ids = events
            record.audit_count = len(events)
    
    def _track_changes(self, operation, old_values=None, new_values=None, context_info=None):
        """Track changes in audit trail"""
        self.ensure_one()
        if self.id:  # Only track if record is saved
            return self.env['medtech.audit.event']._create_audit_event(
                model=self._name,
                res_id=self.id,
                operation=operation,
                old_vals=old_values,
                new_vals=new_values,
                context_info=context_info
            )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add audit trail"""
        records = super().create(vals_list)
        for record in records:
            if record._audit_tracked_fields:
                tracked_vals = {k: v for k, v in vals_list[0].items() if k in record._audit_tracked_fields}
                record._track_changes('create', old_values=None, new_values=tracked_vals, context_info='Record created')
        return records
    
    def write(self, vals):
        """Override write to add audit trail"""
        if self._audit_tracked_fields:
            for record in self:
                old_values = {}
                new_values = {}
                for field in record._audit_tracked_fields:
                    if field in vals:
                        old_values[field] = record[field] if hasattr(record, field) else None
                        new_values[field] = vals[field]
                
                result = super(MedTechAuditMixin, record).write(vals)
                
                if old_values or new_values:
                    record._track_changes('write', old_values=old_values, new_values=new_values, context_info='Record updated')
                
                return result
        return super().write(vals)
    
    def unlink(self):
        """Override unlink to add audit trail"""
        for record in self:
            if record._audit_tracked_fields:
                old_values = {field: record[field] for field in record._audit_tracked_fields if hasattr(record, field)}
                record._track_changes('unlink', old_values=old_values, context_info='Record deleted')
        return super().unlink()
    
    def action_view_audit_trail(self):
        """Smart button action to view audit trail"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Audit Trail',
            'res_model': 'medtech.audit.event',
            'view_mode': 'tree,form',
            'domain': [('model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_model': self._name, 'default_res_id': self.id},
        }
