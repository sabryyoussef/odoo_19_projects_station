# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MedTechMaintenancePlan(models.Model):
    """Preventive Maintenance Plans for Medical Devices"""
    _name = 'medtech.maintenance.plan'
    _description = 'Maintenance Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'next_service_date'
    _rec_name = 'display_name'
    
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    
    # Device & Customer
    device_serial_id = fields.Many2one('stock.lot', string='Device Serial/Lot', required=True, tracking=True)
    device_product_id = fields.Many2one(related='device_serial_id.product_id', string='Device Product', store=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    
    # Schedule
    frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('biennial', 'Every 2 Years'),
    ], string='Maintenance Frequency', required=True, default='annual', tracking=True)
    
    last_service_date = fields.Date(string='Last Service Date')
    next_service_date = fields.Date(string='Next Service Date', required=True, tracking=True, index=True)
    
    # Service Details
    service_type = fields.Selection([
        ('preventive', 'Preventive Maintenance'),
        ('calibration', 'Calibration'),
        ('inspection', 'Inspection'),
    ], string='Service Type', default='preventive')
    
    service_checklist = fields.Text(string='Service Checklist',
                                   help='Standard checklist for this maintenance')
    technician_id = fields.Many2one('res.users', string='Assigned Technician')
    
    # Status
    active = fields.Boolean(string='Active', default=True, tracking=True)
    status = fields.Selection([
        ('current', 'Current'),
        ('overdue', 'Overdue'),
        ('inactive', 'Inactive'),
    ], string='Status', compute='_compute_status', store=True)
    
    # History
    service_visit_ids = fields.One2many('medtech.service.visit', 'maintenance_plan_id', string='Service Visits')
    visit_count = fields.Integer(string='Service Visits', compute='_compute_visit_count')
    
    @api.depends('device_serial_id', 'customer_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.device_product_id.name or 'Device'} - {record.customer_id.name}"
    
    @api.depends('next_service_date', 'active')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if not record.active:
                record.status = 'inactive'
            elif record.next_service_date < today:
                record.status = 'overdue'
            else:
                record.status = 'current'
    
    @api.depends('service_visit_ids')
    def _compute_visit_count(self):
        for record in self:
            record.visit_count = len(record.service_visit_ids)
    
    def action_create_service_visit(self):
        """Create service visit from maintenance plan"""
        self.ensure_one()
        
        visit = self.env['medtech.service.visit'].create({
            'device_serial_id': self.device_serial_id.id,
            'customer_id': self.customer_id.id,
            'service_type': 'maintenance',
            'maintenance_plan_id': self.id,
            'technician_id': self.technician_id.id,
            'scheduled_date': self.next_service_date,
            'work_description': f"Scheduled {self.frequency} maintenance\n{self.service_checklist or ''}",
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Visit',
            'res_model': 'medtech.service.visit',
            'res_id': visit.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_reschedule(self):
        """Reschedule next service based on frequency"""
        self.ensure_one()
        
        if not self.last_service_date:
            self.last_service_date = fields.Date.today()
        
        # Calculate next date based on frequency
        from dateutil.relativedelta import relativedelta
        
        if self.frequency == 'weekly':
            delta = relativedelta(weeks=1)
        elif self.frequency == 'monthly':
            delta = relativedelta(months=1)
        elif self.frequency == 'quarterly':
            delta = relativedelta(months=3)
        elif self.frequency == 'semi_annual':
            delta = relativedelta(months=6)
        elif self.frequency == 'annual':
            delta = relativedelta(years=1)
        elif self.frequency == 'biennial':
            delta = relativedelta(years=2)
        else:
            delta = relativedelta(years=1)
        
        self.next_service_date = self.last_service_date + delta
        
        return True
    
    @api.model
    def _cron_check_due_maintenance(self):
        """Cron job to create activities for due maintenance"""
        # Find plans due in next 7 days
        due_date = fields.Date.add(fields.Date.today(), days=7)
        
        plans = self.search([
            ('active', '=', True),
            ('next_service_date', '<=', due_date),
            ('next_service_date', '>=', fields.Date.today()),
        ])
        
        for plan in plans:
            # Check if activity already exists
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'medtech.maintenance.plan'),
                ('res_id', '=', plan.id),
                ('date_deadline', '=', plan.next_service_date),
            ])
            
            if not existing:
                # Create activity
                plan.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=plan.technician_id.id if plan.technician_id else self.env.user.id,
                    summary='Scheduled Maintenance Due',
                    note=f'Device: {plan.device_product_id.name}\nCustomer: {plan.customer_id.name}',
                    date_deadline=plan.next_service_date,
                )
        
        return True
