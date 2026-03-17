# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MedTechCAPA(models.Model):
    """Corrective and Preventive Action with stage gate workflow"""
    _name = 'medtech.capa'
    _description = 'CAPA (Corrective & Preventive Action)'
    _inherit = ['medtech.approval.mixin', 'medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    _audit_tracked_fields = ['stage', 'investigation', 'root_cause_analysis', 'action_plan', 
                             'implementation_status', 'effectiveness_result']

    name = fields.Char(string='CAPA Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    
    # Source
    source = fields.Selection([
        ('nonconformance', 'Nonconformance'),
        ('recall', 'Recall'),
        ('complaint', 'Customer Complaint'),
        ('audit', 'Audit Finding'),
        ('risk_assessment', 'Risk Assessment'),
        ('other', 'Other'),
    ], string='Source', required=True, default='nonconformance', tracking=True)
    
    description = fields.Text(string='Problem Description', required=True, tracking=True)
    
    # Links
    nonconformance_ids = fields.Many2many('medtech.nonconformance', string='Related Nonconformances')
    # recall_ids = fields.Many2many('medtech.recall', string='Related Recalls')
    affected_serial_lot_ids = fields.Many2many('stock.lot', string='Affected Serials/Lots')
    affected_product_ids = fields.Many2many('product.product', string='Affected Products')
    
    # Stage Workflow
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('investigation', 'Investigation'),
        ('containment', 'Containment'),
        ('root_cause', 'Root Cause Analysis'),
        ('action_plan', 'Action Plan'),
        ('implementation', 'Implementation'),
        ('effectiveness', 'Effectiveness Check'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Stage', default='draft', required=True, tracking=True, index=True)
    
    # Stage 1: Investigation
    investigation = fields.Text(string='Investigation Details', tracking=True,
                                help='Detailed investigation of the problem')
    investigation_date = fields.Date(string='Investigation Completed')
    investigator_id = fields.Many2one('res.users', string='Investigator')
    
    # Stage 2: Containment
    containment_action = fields.Text(string='Containment Action', tracking=True,
                                     help='Immediate actions to prevent further occurrence')
    containment_date = fields.Date(string='Containment Completed')
    containment_verified = fields.Boolean(string='Containment Verified')
    
    # Stage 3: Root Cause Analysis
    root_cause_analysis = fields.Text(string='Root Cause Analysis', tracking=True,
                                      help='5 Whys, Fishbone, or other RCA method')
    root_cause_method = fields.Selection([
        ('5_whys', '5 Whys'),
        ('fishbone', 'Fishbone Diagram'),
        ('fmea', 'FMEA'),
        ('other', 'Other'),
    ], string='RCA Method')
    root_cause_date = fields.Date(string='RCA Completed')
    
    # Stage 4: Action Plan
    action_plan = fields.Text(string='Corrective/Preventive Action Plan', required=True, tracking=True)
    action_type = fields.Selection([
        ('corrective', 'Corrective Action'),
        ('preventive', 'Preventive Action'),
        ('both', 'Both Corrective & Preventive'),
    ], string='Action Type', default='corrective', tracking=True)
    
    responsible_id = fields.Many2one('res.users', string='Responsible Person', tracking=True,
                                     help='Person responsible for implementation')
    target_completion_date = fields.Date(string='Target Completion Date', tracking=True)
    
    # Stage 5: Implementation
    implementation_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Implementation Status', default='not_started', tracking=True)
    
    implementation_date = fields.Date(string='Implementation Completed')
    implementation_evidence = fields.Binary(string='Implementation Evidence', attachment=True)
    implementation_evidence_filename = fields.Char(string='Evidence Filename')
    implementation_notes = fields.Text(string='Implementation Notes')
    
    # Stage 6: Effectiveness Check
    effectiveness_check_date = fields.Date(string='Effectiveness Check Date', tracking=True,
                                           help='Date when effectiveness will be/was checked')
    effectiveness_check_required = fields.Boolean(string='Effectiveness Check Required', default=True)
    effectiveness_result = fields.Selection([
        ('effective', 'Effective'),
        ('not_effective', 'Not Effective'),
        ('partially_effective', 'Partially Effective'),
    ], string='Effectiveness Result', tracking=True)
    effectiveness_notes = fields.Text(string='Effectiveness Check Notes')
    effectiveness_checked_by_id = fields.Many2one('res.users', string='Checked By')
    
    # Approvals
    qa_approval_required = fields.Boolean(string='QA Approval Required', default=True)
    qa_approved_by_id = fields.Many2one('res.users', string='QA Approved By', readonly=True)
    qa_approved_date = fields.Date(string='QA Approval Date', readonly=True)
    
    regulatory_approval_required = fields.Boolean(string='Regulatory Approval Required')
    regulatory_approved_by_id = fields.Many2one('res.users', string='Regulatory Approved By', readonly=True)
    regulatory_approved_date = fields.Date(string='Regulatory Approval Date', readonly=True)
    
    # Closure
    closed_date = fields.Date(string='Closed Date', readonly=True)
    closed_by_id = fields.Many2one('res.users', string='Closed By', readonly=True)
    
    # Computed
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_overdue')
    days_open = fields.Integer(string='Days Open', compute='_compute_days_open')
    color = fields.Integer(string='Color Index', compute='_compute_color', store=True)
    
    @api.depends('stage', 'is_overdue')
    def _compute_color(self):
        """Set color based on stage and overdue status for kanban view"""
        for record in self:
            if record.stage == 'closed':
                record.color = 10  # Green
            elif record.stage == 'cancelled':
                record.color = 7   # Gray
            elif record.is_overdue:
                record.color = 1   # Red
            elif record.stage in ['draft', 'investigation']:
                record.color = 4   # Blue
            elif record.stage in ['implementation', 'effectiveness']:
                record.color = 3   # Orange
            else:
                record.color = 0   # White
    
    @api.depends('target_completion_date')
    def _compute_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (record.target_completion_date and 
                                record.target_completion_date < today and 
                                record.stage not in ['closed', 'cancelled'])
    
    @api.depends('create_date', 'closed_date')
    def _compute_days_open(self):
        for record in self:
            if record.closed_date:
                delta = record.closed_date - record.create_date.date()
                record.days_open = delta.days
            else:
                delta = fields.Date.today() - record.create_date.date()
                record.days_open = delta.days
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.capa') or _('New')
        return super().create(vals_list)
    
    def _check_stage_requirements(self, new_stage):
        """Enforce required fields per stage"""
        self.ensure_one()
        
        if new_stage == 'investigation' and not self.description:
            raise ValidationError(_('Problem description is required to start investigation.'))
        
        if new_stage == 'containment' and not self.investigation:
            raise ValidationError(_('Investigation details are required before containment.'))
        
        if new_stage == 'root_cause' and not self.containment_action:
            raise ValidationError(_('Containment action is required before root cause analysis.'))
        
        if new_stage == 'action_plan' and not self.root_cause_analysis:
            raise ValidationError(_('Root cause analysis is required before creating action plan.'))
        
        if new_stage == 'implementation' and not self.action_plan:
            raise ValidationError(_('Action plan is required before implementation.'))
        
        if new_stage == 'effectiveness':
            if not self.implementation_date:
                raise ValidationError(_('Implementation must be completed before effectiveness check.'))
            if self.qa_approval_required and not self.qa_approved_by_id:
                raise ValidationError(_('QA approval is required before effectiveness check.'))
        
        if new_stage == 'closed':
            if self.effectiveness_check_required and not self.effectiveness_result:
                raise ValidationError(_('Effectiveness check is required before closure.'))
            if self.effectiveness_result == 'not_effective':
                raise ValidationError(_('Cannot close CAPA with "Not Effective" result. Create new action plan.'))
        
        return True
    
    def action_progress_stage(self):
        """Move to next stage"""
        self.ensure_one()
        
        stage_sequence = ['draft', 'investigation', 'containment', 'root_cause', 
                         'action_plan', 'implementation', 'effectiveness', 'closed']
        
        current_index = stage_sequence.index(self.stage)
        if current_index < len(stage_sequence) - 1:
            next_stage = stage_sequence[current_index + 1]
            
            # Check requirements
            self._check_stage_requirements(next_stage)
            
            # Update stage
            self.stage = next_stage
            
            # Log
            self.message_post(body=_('Stage progressed to %s by %s') % (next_stage.replace('_', ' ').title(), self.env.user.name))
            self._track_changes('write', context_info=f'Stage progressed to {next_stage}')
            
            return True
        else:
            raise UserError(_('Already at final stage.'))
    
    def action_request_qa_approval(self):
        """Request QA approval"""
        self.ensure_one()
        if self.stage not in ['action_plan', 'implementation']:
            raise UserError(_('QA approval can be requested during Action Plan or Implementation stage.'))
        
        self.message_post(body=_('QA approval requested by %s') % self.env.user.name)
        # Create activity for QA manager
        qa_group = self.env.ref('medtech_core.group_medtech_quality_manager')
        if qa_group.users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=qa_group.users[0].id,
                summary='QA Approval Required',
                note=f'Please review and approve CAPA: {self.name}'
            )
        return True
    
    def action_qa_approve(self):
        """QA Manager approves"""
        self.ensure_one()
        if not self.env.user.has_group('medtech_core.group_medtech_quality_manager'):
            raise UserError(_('Only QA Manager can approve.'))
        
        self.write({
            'qa_approved_by_id': self.env.user.id,
            'qa_approved_date': fields.Date.today(),
        })
        
        self.message_post(body=_('QA approved by %s') % self.env.user.name)
        self._track_changes('approve', context_info='QA approved')
        return True
    
    def action_regulatory_approve(self):
        """Regulatory Manager approves"""
        self.ensure_one()
        if not self.env.user.has_group('medtech_core.group_medtech_regulatory_manager'):
            raise UserError(_('Only Regulatory Manager can approve.'))
        
        self.write({
            'regulatory_approved_by_id': self.env.user.id,
            'regulatory_approved_date': fields.Date.today(),
        })
        
        self.message_post(body=_('Regulatory approved by %s') % self.env.user.name)
        self._track_changes('approve', context_info='Regulatory approved')
        return True
    
    def action_mark_effective(self):
        """Mark effectiveness check as effective and close"""
        self.ensure_one()
        if self.stage != 'effectiveness':
            raise ValidationError(_('Must be in Effectiveness Check stage.'))
        
        self.write({
            'effectiveness_result': 'effective',
            'effectiveness_checked_by_id': self.env.user.id,
            'stage': 'closed',
            'closed_date': fields.Date.today(),
            'closed_by_id': self.env.user.id,
        })
        
        self.message_post(body=_('CAPA marked effective and closed by %s') % self.env.user.name)
        self._track_changes('write', context_info='Marked effective and closed')
        return True
    
    def action_mark_not_effective(self):
        """Mark as not effective - requires new action plan"""
        self.ensure_one()
        if self.stage != 'effectiveness':
            raise ValidationError(_('Must be in Effectiveness Check stage.'))
        
        self.write({
            'effectiveness_result': 'not_effective',
            'effectiveness_checked_by_id': self.env.user.id,
            'stage': 'action_plan',  # Go back to action plan
        })
        
        self.message_post(body=_('CAPA marked not effective by %s. Requires new action plan.') % self.env.user.name)
        self._track_changes('write', context_info='Marked not effective - returned to action plan')
        return True
