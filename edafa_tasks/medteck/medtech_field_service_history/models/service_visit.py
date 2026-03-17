# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedTechServiceVisit(models.Model):
    """Field Service Visit Records"""
    _name = 'medtech.service.visit'
    _description = 'Service Visit'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'visit_date desc'
    _rec_name = 'name'
    
    _audit_tracked_fields = ['service_type', 'state', 'device_serial_id', 'technician_id']

    name = fields.Char(string='Service Visit Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    
    # Device & Customer
    device_serial_id = fields.Many2one('stock.lot', string='Device Serial/Lot', required=True, 
                                       tracking=True, index=True,
                                       help='Serial or lot number of the device being serviced')
    device_product_id = fields.Many2one(related='device_serial_id.product_id', string='Device Product', store=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    customer_location = fields.Text(string='Service Location')
    
    # Service Details
    service_type = fields.Selection([
        ('maintenance', 'Preventive Maintenance'),
        ('repair', 'Repair'),
        ('calibration', 'Calibration'),
        ('firmware_update', 'Firmware Update'),
        ('recall_action', 'Recall Correction'),
        ('installation', 'Installation/Setup'),
        ('decommission', 'Decommission/Removal'),
        ('inspection', 'Inspection'),
    ], string='Service Type', required=True, default='maintenance', tracking=True)
    
    visit_date = fields.Datetime(string='Visit Date', required=True, default=fields.Datetime.now, tracking=True)
    scheduled_date = fields.Datetime(string='Scheduled Date')
    completion_date = fields.Datetime(string='Completion Date')
    
    # Technician
    technician_id = fields.Many2one('res.users', string='Technician', 
                                    domain=[('groups_id', 'in', [('medtech_core.group_medtech_service_technician')])],
                                    default=lambda self: self.env.user, tracking=True)
    
    # Work Performed
    work_description = fields.Text(string='Work Description', required=True)
    problem_reported = fields.Text(string='Problem Reported by Customer')
    root_cause = fields.Text(string='Root Cause Found')
    corrective_action = fields.Text(string='Corrective Action Taken')
    
    # Parts Replaced
    parts_replaced_ids = fields.One2many('medtech.service.visit.part', 'service_visit_id', string='Parts Replaced')
    parts_count = fields.Integer(string='Parts Replaced', compute='_compute_parts_count')
    
    # Firmware Update
    firmware_version_old = fields.Char(string='Firmware Version (Before)')
    firmware_version_new = fields.Char(string='Firmware Version (After)')
    software_changes = fields.Text(string='Software/Firmware Changes')
    
    # Measurements/Calibration
    calibration_results = fields.Text(string='Calibration Results')
    test_results = fields.Text(string='Test Results')
    device_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('failed', 'Failed'),
    ], string='Device Condition After Service')
    
    # Documentation
    signature = fields.Binary(string='Technician Signature', attachment=True)
    customer_signature = fields.Binary(string='Customer Signature', attachment=True)
    photos = fields.Many2many('ir.attachment', string='Photos/Evidence')
    photo_count = fields.Integer(string='Photos', compute='_compute_photo_count')
    
    # Recall Link
    # recall_id = fields.Many2one('medtech.recall', string='Related Recall')
    # is_recall_action = fields.Boolean(string='Is Recall Action', compute='_compute_is_recall_action', store=True)
    
    # State
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='scheduled', required=True, tracking=True)
    
    # Follow-up
    followup_required = fields.Boolean(string='Follow-up Required')
    followup_date = fields.Date(string='Follow-up Date')
    followup_notes = fields.Text(string='Follow-up Notes')
    
    # Maintenance Plan Link
    maintenance_plan_id = fields.Many2one('medtech.maintenance.plan', string='Maintenance Plan')
    
    # DHR Link
    dhr_id = fields.Many2one('medtech.dhr', string='Device History Record', 
                            compute='_compute_dhr_id', store=True)
    
    @api.depends('parts_replaced_ids')
    def _compute_parts_count(self):
        for record in self:
            record.parts_count = len(record.parts_replaced_ids)
    
    @api.depends('photos')
    def _compute_photo_count(self):
        for record in self:
            record.photo_count = len(record.photos)
    
    # @api.depends('service_type', 'recall_id')
    # def _compute_is_recall_action(self):
    #     for record in self:
    #         record.is_recall_action = (record.service_type == 'recall_action' or bool(record.recall_id))
    
    @api.depends('device_serial_id')
    def _compute_dhr_id(self):
        for record in self:
            if record.device_serial_id:
                dhr = self.env['medtech.dhr'].search([
                    ('serial_lot_id', '=', record.device_serial_id.id)
                ], limit=1)
                record.dhr_id = dhr.id if dhr else False
            else:
                record.dhr_id = False
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.service.visit') or _('New')
        return super().create(vals_list)
    
    def action_start_visit(self):
        """Start service visit"""
        self.ensure_one()
        if self.state != 'scheduled':
            raise ValidationError(_('Can only start scheduled visits.'))
        
        self.state = 'in_progress'
        self.visit_date = fields.Datetime.now()
        self.message_post(body=_('Service visit started by %s') % self.env.user.name)
        return True
    
    def action_complete_visit(self):
        """Complete service visit"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_('Can only complete visits in progress.'))
        
        if not self.work_description:
            raise ValidationError(_('Work description is required to complete visit.'))
        
        self.write({
            'state': 'completed',
            'completion_date': fields.Datetime.now(),
        })
        
        self.message_post(body=_('Service visit completed by %s') % self.env.user.name)
        self._track_changes('write', context_info='Service visit completed')
        
        # Update DHR if exists
        if self.dhr_id:
            self.dhr_id.message_post(
                body=_('Service visit %s completed: %s') % (self.name, self.work_description[:100])
            )
        
        return True
    
    def action_view_dhr(self):
        """View Device History Record"""
        self.ensure_one()
        if not self.dhr_id:
            raise ValidationError(_('No DHR found for this device.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Device History Record',
            'res_model': 'medtech.dhr',
            'res_id': self.dhr_id.id,
            'view_mode': 'form',
        }


class MedTechServiceVisitPart(models.Model):
    """Parts replaced during service visit"""
    _name = 'medtech.service.visit.part'
    _description = 'Service Visit Part Replacement'
    _order = 'create_date'
    
    service_visit_id = fields.Many2one('medtech.service.visit', string='Service Visit', 
                                       required=True, ondelete='cascade')
    
    # Part Details
    product_id = fields.Many2one('product.product', string='Part', required=True)
    old_serial_id = fields.Many2one('stock.lot', string='Old Part Serial/Lot',
                                    help='Serial/lot of part being removed')
    new_serial_id = fields.Many2one('stock.lot', string='New Part Serial/Lot', required=True,
                                    help='Serial/lot of replacement part')
    
    quantity = fields.Float(string='Quantity', default=1.0)
    reason = fields.Text(string='Replacement Reason')
    
    # Traceability
    old_part_condition = fields.Selection([
        ('failed', 'Failed'),
        ('worn', 'Worn Out'),
        ('damaged', 'Damaged'),
        ('recall', 'Recall'),
        ('upgrade', 'Upgrade'),
    ], string='Old Part Condition')
    
    old_part_disposition = fields.Selection([
        ('returned', 'Returned to Warehouse'),
        ('scrapped', 'Scrapped on Site'),
        ('customer_kept', 'Left with Customer'),
    ], string='Old Part Disposition')
