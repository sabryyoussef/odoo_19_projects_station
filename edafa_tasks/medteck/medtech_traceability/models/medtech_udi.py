# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedTechUDI(models.Model):
    """UDI (Unique Device Identification) Registry"""
    _name = 'medtech.udi'
    _description = 'UDI Registry'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'manufacture_date desc, serial_number'
    _rec_name = 'display_name'
    
    # Track all fields for audit
    _audit_tracked_fields = ['udi_di', 'udi_pi', 'serial_number', 'lot_id', 'manufacture_date', 'expiry_date', 'status']

    # UDI Components
    udi_di = fields.Char(string='UDI-DI (Device Identifier)', required=True, index=True, tracking=True, 
                         help='Device Identifier - identifies the specific version or model of a device')
    udi_pi = fields.Char(string='UDI-PI (Production Identifier)', compute='_compute_udi_pi', store=True, 
                         help='Production Identifier - serial number, lot, manufacturing & expiry dates')
    
    # Production Identifiers
    serial_number = fields.Char(string='Serial Number', index=True, tracking=True)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial', index=True, tracking=True, 
                             help='Link to Odoo stock lot/serial number')
    manufacture_date = fields.Date(string='Manufacturing Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    
    # Device Info
    device_master_id = fields.Many2one('product.template', string='Device Master', 
                                       domain=[('is_medical_device', '=', True)], tracking=True)
    product_id = fields.Many2one('product.product', string='Product Variant', tracking=True)
    
    # Status
    status = fields.Selection([
        ('active', 'Active'),
        ('quarantined', 'Quarantined'),
        ('recalled', 'Recalled'),
        ('returned', 'Returned'),
        ('destroyed', 'Destroyed'),
    ], string='Status', default='active', required=True, index=True, tracking=True)
    
    # Display
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    
    # Links
    dhr_id = fields.Many2one('medtech.dhr', string='Device History Record', compute='_compute_dhr_id')
    shipment_ids = fields.Many2many('stock.picking', string='Shipments')
    
    # Location
    current_location = fields.Char(string='Current Location', compute='_compute_current_location')
    customer_id = fields.Many2one('res.partner', string='Customer', compute='_compute_customer')
    
    @api.depends('udi_di', 'serial_number', 'lot_id.name', 'manufacture_date', 'expiry_date')
    def _compute_udi_pi(self):
        """Construct UDI-PI from production identifiers"""
        for record in self:
            pi_parts = []
            if record.serial_number:
                pi_parts.append(f"SN:{record.serial_number}")
            if record.lot_id:
                pi_parts.append(f"LOT:{record.lot_id.name}")
            if record.manufacture_date:
                pi_parts.append(f"MFG:{record.manufacture_date.strftime('%Y%m%d')}")
            if record.expiry_date:
                pi_parts.append(f"EXP:{record.expiry_date.strftime('%Y%m%d')}")
            record.udi_pi = " ".join(pi_parts) if pi_parts else False
    
    @api.depends('udi_di', 'serial_number', 'lot_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.serial_number:
                record.display_name = f"{record.udi_di} / SN:{record.serial_number}"
            elif record.lot_id:
                record.display_name = f"{record.udi_di} / LOT:{record.lot_id.name}"
            else:
                record.display_name = record.udi_di or 'New UDI'
    
    @api.depends('lot_id')
    def _compute_dhr_id(self):
        """Link to Device History Record"""
        for record in self:
            if record.lot_id:
                dhr = self.env['medtech.dhr'].search([('serial_lot_id', '=', record.lot_id.id)], limit=1)
                record.dhr_id = dhr.id if dhr else False
            else:
                record.dhr_id = False
    
    def _compute_current_location(self):
        """Get current physical location from stock"""
        for record in self:
            if record.lot_id:
                quants = self.env['stock.quant'].search([
                    ('lot_id', '=', record.lot_id.id),
                    ('quantity', '>', 0)
                ], limit=1)
                record.current_location = quants.location_id.complete_name if quants else 'Unknown'
            else:
                record.current_location = 'Unknown'
    
    def _compute_customer(self):
        """Get customer from last delivery"""
        for record in self:
            if record.lot_id:
                # Find last outgoing delivery
                pickings = self.env['stock.picking'].search([
                    ('picking_type_code', '=', 'outgoing'),
                    ('state', '=', 'done'),
                    ('move_ids.lot_ids', 'in', record.lot_id.id)
                ], order='date_done desc', limit=1)
                record.customer_id = pickings.partner_id.id if pickings else False
            else:
                record.customer_id = False
    
    @api.constrains('udi_di')
    def _check_udi_di(self):
        for record in self:
            if record.udi_di and len(record.udi_di) < 5:
                raise ValidationError(_('UDI-DI must be at least 5 characters long'))
    
    def action_view_dhr(self):
        """Navigate to Device History Record"""
        self.ensure_one()
        if not self.dhr_id:
            # Create DHR if it doesn't exist
            dhr = self.env['medtech.dhr'].create({
                'serial_lot_id': self.lot_id.id,
                'device_master_id': self.device_master_id.id,
            })
            self.dhr_id = dhr.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Device History Record',
            'res_model': 'medtech.dhr',
            'res_id': self.dhr_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_quarantine(self):
        """Quarantine this device"""
        self.ensure_one()
        self.status = 'quarantined'
        self._track_changes('quarantine', context_info='Device quarantined manually')
        return True
    
    def action_release_quarantine(self):
        """Release from quarantine"""
        self.ensure_one()
        self.status = 'active'
        self._track_changes('release', context_info='Device released from quarantine')
        return True
