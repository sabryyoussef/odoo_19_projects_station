# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MedTechRecallNotification(models.Model):
    """Customer notification for recalls"""
    _name = 'medtech.recall.notification'
    _description = 'Recall Customer Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'
    
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    
    recall_id = fields.Many2one('medtech.recall', string='Recall', required=True, ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    
    # Affected Items for this customer
    affected_serial_ids = fields.Many2many('stock.lot', string='Affected Serials at Customer')
    affected_count = fields.Integer(string='Affected Units', compute='_compute_affected_count')
    
    # Notification
    notification_method = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('letter', 'Letter'),
        ('in_person', 'In-Person'),
        ('regulatory', 'Regulatory Authority Notification'),
    ], string='Notification Method', default='email', tracking=True)
    
    notification_date = fields.Datetime(string='Notification Date', tracking=True)
    notified_by_id = fields.Many2one('res.users', string='Notified By')
    
    # Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('acknowledged', 'Acknowledged by Customer'),
        ('action_taken', 'Customer Action Taken'),
        ('completed', 'Completed'),
    ], string='Status', default='pending', required=True, tracking=True)
    
    # Customer Response
    customer_acknowledgment_date = fields.Date(string='Customer Acknowledged')
    customer_contact_person = fields.Char(string='Customer Contact Person')
    customer_contact_email = fields.Char(string='Customer Email')
    customer_contact_phone = fields.Char(string='Customer Phone')
    
    # Actions
    action_required = fields.Text(string='Action Required from Customer')
    action_completed_date = fields.Date(string='Action Completed Date')
    action_notes = fields.Text(string='Action Notes')
    
    # Follow-up
    followup_required = fields.Boolean(string='Follow-up Required', default=True)
    followup_date = fields.Date(string='Follow-up Date')
    followup_notes = fields.Text(string='Follow-up Notes')
    
    @api.depends('recall_id', 'customer_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.recall_id.name} - {record.customer_id.name}"
    
    @api.depends('affected_serial_ids')
    def _compute_affected_count(self):
        for record in self:
            record.affected_count = len(record.affected_serial_ids)
    
    def action_mark_sent(self):
        """Mark notification as sent"""
        self.ensure_one()
        self.write({
            'status': 'sent',
            'notification_date': fields.Datetime.now(),
            'notified_by_id': self.env.user.id,
        })
        self.message_post(body=_('Notification sent to customer by %s') % self.env.user.name)
        return True
    
    def action_mark_acknowledged(self):
        """Customer acknowledged the notification"""
        self.ensure_one()
        self.write({
            'status': 'acknowledged',
            'customer_acknowledgment_date': fields.Date.today(),
        })
        self.message_post(body=_('Customer acknowledgment recorded by %s') % self.env.user.name)
        return True
    
    def action_send_email(self):
        """Send recall notification email to customer"""
        self.ensure_one()
        
        template = self.env.ref('medtech_recall.email_template_recall_notification', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.action_mark_sent()
        
        return True
