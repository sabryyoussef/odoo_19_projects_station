# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta


class CrmLead(models.Model):
    """
    Extends the CRM Lead model to add audit tracking functionality.
    
    This extension adds two custom fields:
    - x_is_audited: Boolean flag indicating if the lead has been audited
    - x_last_audit_date: Datetime tracking when the last audit occurred
    
    These fields are used by external automation scripts to track and manage
    leads that remain stale (no activities) for extended periods.
    """
    _inherit = 'crm.lead'
    
    # Audit tracking fields
    x_is_audited = fields.Boolean(
        string='Is Audited',
        default=False,
        tracking=True,
        help='Indicates whether this lead has been audited by the automated system. '
             'Automatically set to True when an audit activity is created for stale leads.',
        groups='sales_team.group_sale_manager',
    )
    
    x_last_audit_date = fields.Datetime(
        string='Last Audit Date',
        readonly=True,
        tracking=True,
        help='Timestamp of the last automated audit performed on this lead. '
             'Used for reporting and audit trail purposes.',
        groups='sales_team.group_sale_manager',
    )
    
    # Computed field to show if lead is potentially stale (optional helper)
    x_is_stale = fields.Boolean(
        string='Is Stale',
        compute='_compute_is_stale',
        store=False,
        help='Indicates if this lead is older than 48 hours without any scheduled activities. '
             'This is a computed field for quick identification of potentially stale leads.',
    )
    
    @api.depends('create_date', 'activity_ids', 'x_is_audited')
    def _compute_is_stale(self):
        """
        Computes whether a lead is considered "stale" based on:
        - Created more than 48 hours ago
        - Has no scheduled activities
        - Has not been audited yet
        - Is still a lead (not opportunity)
        - Not won (probability < 100)
        """
        threshold_date = datetime.now() - timedelta(hours=48)
        
        for lead in self:
            is_old_enough = lead.create_date and lead.create_date < threshold_date
            has_no_activities = not lead.activity_ids
            not_audited = not lead.x_is_audited
            is_lead = lead.type == 'lead'
            not_won = lead.probability < 100
            
            lead.x_is_stale = (
                is_old_enough and 
                has_no_activities and 
                not_audited and 
                is_lead and 
                not_won
            )
    
    def action_reset_audit_flag(self):
        """
        Action to manually reset the audit flag.
        
        This can be useful when:
        - Lead stage changes
        - New activities are added
        - Lead ownership changes
        - Manual override is needed
        
        Can be called from a button or automated action.
        """
        for lead in self:
            lead.write({
                'x_is_audited': False,
            })
        return True
    
    def mark_as_audited(self):
        """
        Marks the lead as audited with current timestamp.
        
        This method should be called by the automation script after
        creating an audit activity for the lead.
        
        Returns:
            bool: True if successful
        """
        for lead in self:
            lead.write({
                'x_is_audited': True,
                'x_last_audit_date': fields.Datetime.now(),
            })
        return True
    
    @api.model
    def get_stale_leads(self, hours=48, limit=500):
        """
        Searches for stale leads based on configurable criteria.
        
        This method can be called by external scripts or scheduled actions
        to retrieve leads that need auditing.
        
        Args:
            hours (int): Number of hours to consider a lead stale (default: 48)
            limit (int): Maximum number of leads to return (default: 500)
        
        Returns:
            recordset: CRM Lead records matching the stale criteria
        """
        threshold_date = fields.Datetime.now() - timedelta(hours=hours)
        
        domain = [
            ('type', '=', 'lead'),
            ('probability', '<', 100),
            ('x_is_audited', '=', False),
            ('create_date', '<', threshold_date),
            ('activity_ids', '=', False),  # No activities scheduled
        ]
        
        return self.search(domain, limit=limit, order='create_date asc')
    
    def write(self, vals):
        """
        Override write to automatically reset audit flag on certain field changes.
        
        The audit flag is reset when:
        - Stage changes
        - Lead type changes (lead to opportunity)
        - Priority changes
        - New activities are scheduled
        
        This ensures leads are re-audited after significant changes.
        """
        # Fields that should trigger audit flag reset
        significant_fields = ['stage_id', 'type', 'priority']
        
        # Check if any significant field is being updated
        if any(field in vals for field in significant_fields):
            # Only reset if currently audited
            if not vals.get('x_is_audited'):  # Don't override if explicitly setting it
                for lead in self:
                    if lead.x_is_audited:
                        vals['x_is_audited'] = False
        
        return super(CrmLead, self).write(vals)
