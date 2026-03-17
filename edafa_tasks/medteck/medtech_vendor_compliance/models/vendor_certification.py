# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class MedTechVendorCertification(models.Model):
    """Vendor/Supplier Certifications Management"""
    _name = 'medtech.vendor.certification'
    _description = 'Vendor Certification'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date, partner_id'
    _rec_name = 'display_name'
    
    _audit_tracked_fields = ['certification_type', 'status', 'expiry_date']

    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    
    partner_id = fields.Many2one('res.partner', string='Vendor/Supplier', required=True, 
                                 domain=[('supplier_rank', '>', 0)], tracking=True)
    
    # Certification Details
    certification_type = fields.Selection([
        ('iso_9001', 'ISO 9001 - Quality Management'),
        ('iso_13485', 'ISO 13485 - Medical Devices QMS'),
        ('iso_14001', 'ISO 14001 - Environmental Management'),
        ('quality_agreement', 'Quality Agreement'),
        ('vendor_audit', 'Vendor Audit Report'),
        ('ce_mark', 'CE Mark'),
        ('fda_registration', 'FDA Registration'),
        ('other', 'Other'),
    ], string='Certification Type', required=True, tracking=True)
    
    certificate_number = fields.Char(string='Certificate Number', tracking=True)
    issuing_body = fields.Char(string='Issuing Body/Authority')
    
    # Dates
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', required=True, tracking=True, index=True,
                             help='Date when certification expires')
    next_audit_date = fields.Date(string='Next Audit Date')
    
    # Status
    status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('pending', 'Pending Renewal'),
        ('suspended', 'Suspended'),
    ], string='Status', compute='_compute_status', store=True, index=True)
    
    days_to_expiry = fields.Integer(string='Days to Expiry', compute='_compute_days_to_expiry')
    
    # Documentation
    attachment_id = fields.Many2one('ir.attachment', string='Certificate Document')
    attachment_filename = fields.Char(related='attachment_id.name', string='Filename')
    notes = fields.Text(string='Notes')
    
    # Required for PO
    required_for_po = fields.Boolean(string='Required for Purchase Orders', default=True,
                                     help='If checked, valid certification is required to confirm POs with this vendor')
    product_category_ids = fields.Many2many('product.category', string='Applies to Product Categories',
                                           help='If specified, certification only required for these product categories')
    
    @api.depends('partner_id', 'certification_type', 'certificate_number')
    def _compute_display_name(self):
        for record in self:
            cert_type = dict(self._fields['certification_type'].selection).get(record.certification_type, '')
            if record.certificate_number:
                record.display_name = f"{record.partner_id.name} - {cert_type} ({record.certificate_number})"
            else:
                record.display_name = f"{record.partner_id.name} - {cert_type}"
    
    @api.depends('expiry_date')
    def _compute_status(self):
        """Auto-compute status based on expiry date"""
        today = date.today()
        for record in self:
            if not record.expiry_date:
                record.status = 'pending'
            elif record.expiry_date < today:
                record.status = 'expired'
            elif (record.expiry_date - today).days <= 30:  # Expiring within 30 days
                record.status = 'expiring_soon'
            else:
                record.status = 'valid'
    
    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = date.today()
        for record in self:
            if record.expiry_date:
                delta = record.expiry_date - today
                record.days_to_expiry = delta.days
            else:
                record.days_to_expiry = 0
    
    @api.constrains('expiry_date', 'issue_date')
    def _check_dates(self):
        for record in self:
            if record.issue_date and record.expiry_date and record.issue_date > record.expiry_date:
                raise ValidationError(_('Issue date cannot be after expiry date.'))
    
    def action_renew(self):
        """Create renewal reminder"""
        self.ensure_one()
        # Create activity for purchasing team
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=f'Renew {self.certification_type}',
            note=f'Vendor certification expiring on {self.expiry_date}. Please obtain renewed certificate.',
            date_deadline=self.expiry_date,
        )
        return True
    
    @api.model
    def _cron_check_expiring_certifications(self):
        """Cron job to create alerts for expiring certifications"""
        # Find certifications expiring in 30 days
        expiring = self.search([
            ('expiry_date', '<=', fields.Date.add(fields.Date.today(), days=30)),
            ('expiry_date', '>=', fields.Date.today()),
            ('status', '=', 'expiring_soon'),
        ])
        
        for cert in expiring:
            # Create activity if not already exists
            existing_activity = self.env['mail.activity'].search([
                ('res_model', '=', 'medtech.vendor.certification'),
                ('res_id', '=', cert.id),
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
            ])
            
            if not existing_activity:
                cert.action_renew()
        
        return True
