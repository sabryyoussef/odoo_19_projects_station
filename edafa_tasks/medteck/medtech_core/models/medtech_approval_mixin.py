# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MedTechApprovalHistory(models.Model):
    """Track approval history for records"""
    _name = 'medtech.approval.history'
    _description = 'Approval History'
    _order = 'timestamp desc'
    
    model = fields.Char(string='Model', required=True)
    res_id = fields.Integer(string='Record ID', required=True)
    stage = fields.Char(string='Stage', required=True)
    action = fields.Selection([
        ('request', 'Approval Requested'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Action', required=True)
    
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    timestamp = fields.Datetime(string='Timestamp', required=True, default=fields.Datetime.now)
    comments = fields.Text(string='Comments')


class MedTechApprovalMixin(models.AbstractModel):
    """Mixin to add multi-stage approval workflow"""
    _name = 'medtech.approval.mixin'
    _description = 'MedTech Approval Workflow Mixin'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']

    approval_stage = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Approval Stage', default='draft', tracking=True, index=True)
    
    approval_history_ids = fields.One2many('medtech.approval.history', compute='_compute_approval_history', string='Approval History')
    current_approver_id = fields.Many2one('res.users', string='Current Approver', tracking=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    rejected_by_id = fields.Many2one('res.users', string='Rejected By', readonly=True)
    rejected_date = fields.Datetime(string='Rejected Date', readonly=True)
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)
    
    @api.depends()
    def _compute_approval_history(self):
        """Compute approval history for this record"""
        for record in self:
            history = self.env['medtech.approval.history'].search([
                ('model', '=', record._name),
                ('res_id', '=', record.id)
            ])
            record.approval_history_ids = history
    
    def request_approval(self, approver=None, comments=None):
        """Request approval for this record"""
        self.ensure_one()
        if self.approval_stage not in ['draft', 'rejected']:
            raise UserError(_('Can only request approval from Draft or Rejected stage.'))
        
        self.write({
            'approval_stage': 'pending',
            'current_approver_id': approver.id if approver else False,
        })
        
        # Create approval history
        self.env['medtech.approval.history'].create({
            'model': self._name,
            'res_id': self.id,
            'stage': self.approval_stage,
            'action': 'request',
            'comments': comments,
        })
        
        # Track in audit trail
        self._track_changes('approve', context_info='Approval requested')
        
        # Post message
        self.message_post(body=_('Approval requested by %s') % self.env.user.name)
        
        return True
    
    def approve(self, comments=None):
        """Approve this record"""
        self.ensure_one()
        if self.approval_stage != 'pending':
            raise UserError(_('Can only approve records in Pending stage.'))
        
        self.write({
            'approval_stage': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': fields.Datetime.now(),
            'current_approver_id': False,
        })
        
        # Create approval history
        self.env['medtech.approval.history'].create({
            'model': self._name,
            'res_id': self.id,
            'stage': self.approval_stage,
            'action': 'approve',
            'comments': comments,
        })
        
        # Track in audit trail
        self._track_changes('approve', context_info=f'Approved by {self.env.user.name}')
        
        # Post message
        self.message_post(body=_('Approved by %s') % self.env.user.name)
        
        return True
    
    def reject(self, reason=None):
        """Reject this record"""
        self.ensure_one()
        if self.approval_stage != 'pending':
            raise UserError(_('Can only reject records in Pending stage.'))
        
        if not reason:
            raise UserError(_('Please provide a rejection reason.'))
        
        self.write({
            'approval_stage': 'rejected',
            'rejected_by_id': self.env.user.id,
            'rejected_date': fields.Datetime.now(),
            'rejection_reason': reason,
            'current_approver_id': False,
        })
        
        # Create approval history
        self.env['medtech.approval.history'].create({
            'model': self._name,
            'res_id': self.id,
            'stage': self.approval_stage,
            'action': 'reject',
            'comments': reason,
        })
        
        # Track in audit trail
        self._track_changes('reject', context_info=f'Rejected by {self.env.user.name}: {reason}')
        
        # Post message
        self.message_post(body=_('Rejected by %s: %s') % (self.env.user.name, reason))
        
        return True
    
    def action_view_approval_history(self):
        """Smart button action to view approval history"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval History',
            'res_model': 'medtech.approval.history',
            'view_mode': 'tree,form',
            'domain': [('model', '=', self._name), ('res_id', '=', self.id)],
        }
