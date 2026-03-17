# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    """Extend Purchase Order to enforce vendor certification compliance"""
    _inherit = 'purchase.order'
    
    vendor_certification_ids = fields.Many2many('medtech.vendor.certification', 
                                                string='Vendor Certifications')
    
    @api.onchange('partner_id')
    def _onchange_partner_id_vendor_certifications(self):
        for order in self:
            if order.partner_id:
                certs = self.env['medtech.vendor.certification'].search([
                    ('partner_id', '=', order.partner_id.id)
                ])
                order.vendor_certification_ids = [(6, 0, certs.ids)]
            else:
                order.vendor_certification_ids = [(5, 0, 0)]
    
    vendor_compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('warning', 'Warning - Expiring Soon'),
        ('not_applicable', 'Not Applicable'),
    ], string='Compliance Status', compute='_compute_compliance_status', store=True)
    
    compliance_override = fields.Boolean(string='Compliance Override', 
                                        help='Allow PO confirmation even without valid certifications',
                                        tracking=True)
    compliance_override_reason = fields.Text(string='Override Reason')
    compliance_override_approved_by_id = fields.Many2one('res.users', string='Override Approved By')

    @api.depends('vendor_certification_ids', 'vendor_certification_ids.status', 'order_line.product_id')
    def _compute_compliance_status(self):
        for order in self:
            if not order.partner_id:
                order.vendor_compliance_status = 'not_applicable'
                continue
            
            # Check if vendor certification check is enabled
            config_enabled = self.env['ir.config_parameter'].sudo().get_param(
                'medtech_core.vendor_cert_blocking', default=True
            )
            
            if not config_enabled:
                order.vendor_compliance_status = 'not_applicable'
                continue
            
            # Get required certifications
            required_certs = order.vendor_certification_ids.filtered(lambda c: c.required_for_po)
            
            if not required_certs:
                order.vendor_compliance_status = 'not_applicable'
                continue
            
            # Check for product category specific requirements
            product_categories = order.order_line.mapped('product_id.categ_id')
            
            # Filter certifications applicable to these product categories
            applicable_certs = required_certs.filtered(
                lambda c: not c.product_category_ids or 
                         any(cat in c.product_category_ids for cat in product_categories)
            )
            
            if not applicable_certs:
                order.vendor_compliance_status = 'not_applicable'
                continue
            
            # Check statuses
            if any(cert.status == 'expired' for cert in applicable_certs):
                order.vendor_compliance_status = 'non_compliant'
            elif any(cert.status == 'expiring_soon' for cert in applicable_certs):
                order.vendor_compliance_status = 'warning'
            elif all(cert.status == 'valid' for cert in applicable_certs):
                order.vendor_compliance_status = 'compliant'
            else:
                order.vendor_compliance_status = 'non_compliant'
    
    def button_confirm(self):
        """Override to check vendor certification compliance"""
        for order in self:
            # Check compliance
            if order.vendor_compliance_status == 'non_compliant':
                if not order.compliance_override:
                    raise UserError(_(
                        'Cannot confirm Purchase Order: Vendor "%s" has expired or invalid certifications.\n\n'
                        'Required certifications:\n%s\n\n'
                        'Please ensure all certifications are valid or request an override approval.'
                    ) % (
                        order.partner_id.name,
                        '\n'.join([f"- {cert.display_name} (Status: {cert.status})" 
                                  for cert in order.vendor_certification_ids.filtered(lambda c: c.required_for_po)])
                    ))
                else:
                    # Log override in audit trail
                    self.env['medtech.audit.event']._create_audit_event(
                        model='purchase.order',
                        res_id=order.id,
                        operation='approve',
                        new_vals={'compliance_override': True},
                        context_info=f'Compliance override: {order.compliance_override_reason}'
                    )
                    
                    # Post message
                    order.message_post(
                        body=_('⚠️ Compliance Override Applied by %s\nReason: %s') % 
                             (order.compliance_override_approved_by_id.name or self.env.user.name,
                              order.compliance_override_reason or 'Not specified')
                    )
            
            elif order.vendor_compliance_status == 'warning':
                # Just warn, don't block
                order.message_post(
                    body=_('⚠️ Warning: Some vendor certifications are expiring soon. Please renew.')
                )
        
        return super().button_confirm()
    
    def action_request_compliance_override(self):
        """Request compliance override approval"""
        self.ensure_one()
        
        # Create wizard to get override reason
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request Compliance Override',
            'res_model': 'medtech.vendor.compliance.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id},
        }
    
    def action_grant_override(self, reason):
        """Quality Manager grants override"""
        self.ensure_one()
        
        if not self.env.user.has_group('medtech_core.group_medtech_quality_manager'):
            raise UserError(_('Only Quality Manager can approve compliance overrides.'))
        
        if not reason:
            raise ValidationError(_('Override reason is required.'))
        
        self.write({
            'compliance_override': True,
            'compliance_override_reason': reason,
            'compliance_override_approved_by_id': self.env.user.id,
        })
        
        self.message_post(
            body=_('Compliance override approved by %s\nReason: %s') % (self.env.user.name, reason)
        )
        
        return True
    
    def action_view_vendor_certifications(self):
        """Smart button to view vendor certifications"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Certifications',
            'res_model': 'medtech.vendor.certification',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_partner_id': self.partner_id.id},
        }
