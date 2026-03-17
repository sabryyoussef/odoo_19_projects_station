# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Compliance Configuration
    medtech_compliance_enabled = fields.Boolean(string='Enable MedTech Compliance', config_parameter='medtech_core.compliance_enabled')
    medtech_regulatory_region = fields.Selection([
        ('fda', 'FDA (USA)'),
        ('eu_mdr', 'EU MDR'),
        ('both', 'FDA + EU MDR'),
    ], string='Regulatory Region', config_parameter='medtech_core.regulatory_region')
    
    medtech_enforce_udi = fields.Boolean(string='Enforce UDI on Shipments', config_parameter='medtech_core.enforce_udi', default=True)
    medtech_enforce_fefo = fields.Boolean(string='Enforce FEFO (First Expired First Out)', config_parameter='medtech_core.enforce_fefo', default=True)
    medtech_vendor_cert_blocking = fields.Boolean(string='Block PO without Valid Vendor Certs', config_parameter='medtech_core.vendor_cert_blocking', default=True)
    
    # Audit Settings
    medtech_audit_retention_days = fields.Integer(string='Audit Log Retention (Days)', config_parameter='medtech_core.audit_retention_days', default=2555)  # 7 years
    
    # Approval Settings
    medtech_qa_approval_required = fields.Boolean(string='QA Approval Required for CAPAs', config_parameter='medtech_core.qa_approval_required', default=True)
    medtech_regulatory_approval_required = fields.Boolean(string='Regulatory Approval Required', config_parameter='medtech_core.regulatory_approval_required', default=True)
