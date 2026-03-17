# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MedTechQuarantine(models.Model):
    """Quarantine records for recalled or suspect items"""
    _name = 'medtech.quarantine'
    _description = 'Quarantine Record'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'quarantine_date desc'
    _rec_name = 'display_name'
    
    _audit_tracked_fields = ['status', 'disposition']

    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    
    # Linked Records
    recall_id = fields.Many2one('medtech.recall', string='Recall', tracking=True, ondelete='cascade')
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial', required=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    
    # Location
    location_id = fields.Many2one('stock.location', string='Quarantine Location', required=True, tracking=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    
    # Quarantine Info
    quarantine_date = fields.Datetime(string='Quarantine Date', required=True, default=fields.Datetime.now)
    quarantined_by_id = fields.Many2one('res.users', string='Quarantined By', default=lambda self: self.env.user)
    reason = fields.Text(string='Quarantine Reason', required=True)
    
    # Status
    status = fields.Selection([
        ('quarantined', 'Quarantined'),
        ('returned', 'Returned to Supplier'),
        ('reworked', 'Reworked'),
        ('destroyed', 'Destroyed'),
        ('released', 'Released (Approved)'),
    ], string='Status', default='quarantined', required=True, tracking=True)
    
    # Disposition
    disposition = fields.Selection([
        ('pending', 'Pending Disposition'),
        ('return_customer', 'Return to Customer'),
        ('scrap', 'Scrap'),
        ('rework', 'Rework'),
        ('use_as_is', 'Use As-Is (Approved)'),
    ], string='Disposition', default='pending', tracking=True)
    
    disposition_date = fields.Date(string='Disposition Date')
    disposition_approved_by_id = fields.Many2one('res.users', string='Disposition Approved By')
    disposition_notes = fields.Text(string='Disposition Notes')
    
    # Release (if approved)
    released_date = fields.Datetime(string='Released Date')
    released_by_id = fields.Many2one('res.users', string='Released By')
    release_approval = fields.Text(string='Release Approval Justification')
    
    @api.depends('lot_id', 'product_id', 'recall_id')
    def _compute_display_name(self):
        for record in self:
            if record.recall_id:
                record.display_name = f"{record.recall_id.name} - {record.lot_id.name if record.lot_id else 'No lot'}"
            else:
                record.display_name = f"Quarantine - {record.lot_id.name if record.lot_id else 'No lot'}"
    
    def action_release(self, justification=None):
        """Release from quarantine (requires approval)"""
        self.ensure_one()
        
        if not self.env.user.has_group('medtech_core.group_medtech_quality_manager'):
            raise UserError(_('Only Quality Manager can release quarantined items.'))
        
        if not justification:
            raise ValidationError(_('Release justification is required.'))
        
        # Update stock quant
        quant = self.env['stock.quant'].search([
            ('lot_id', '=', self.lot_id.id),
            ('location_id', '=', self.location_id.id),
        ], limit=1)
        
        if quant:
            quant.write({
                'is_quarantined': False,
                'quarantine_reason': False,
            })
        
        # Update quarantine status
        self.write({
            'status': 'released',
            'disposition': 'use_as_is',
            'released_date': fields.Datetime.now(),
            'released_by_id': self.env.user.id,
            'release_approval': justification,
            'disposition_date': fields.Date.today(),
            'disposition_approved_by_id': self.env.user.id,
        })
        
        self.message_post(body=_('Released from quarantine by %s: %s') % (self.env.user.name, justification))
        self._track_changes('release', context_info=f'Released: {justification}')
        
        return True
    
    def action_scrap(self):
        """Mark as scrapped/destroyed"""
        self.ensure_one()
        
        self.write({
            'status': 'destroyed',
            'disposition': 'scrap',
            'disposition_date': fields.Date.today(),
            'disposition_approved_by_id': self.env.user.id,
        })
        
        self.message_post(body=_('Marked for scrap by %s') % self.env.user.name)
        return True


class StockQuant(models.Model):
    """Extend stock quant to support quarantine"""
    _inherit = 'stock.quant'
    
    is_quarantined = fields.Boolean(string='Quarantined', default=False, index=True)
    quarantine_reason = fields.Char(string='Quarantine Reason')
    quarantine_date = fields.Datetime(string='Quarantine Date')
    
    def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
        """Override to exclude quarantined stock from available quantity"""
        # Call super first
        available_qty = super()._get_available_quantity(
            product_id, location_id, lot_id=lot_id, package_id=package_id, 
            owner_id=owner_id, strict=strict, allow_negative=allow_negative
        )
        
        # Subtract quarantined stock
        if lot_id:
            quarantined_quants = self.search([
                ('product_id', '=', product_id.id),
                ('location_id', '=', location_id.id),
                ('lot_id', '=', lot_id.id),
                ('is_quarantined', '=', True),
            ])
            quarantined_qty = sum(quarantined_quants.mapped('quantity'))
            available_qty -= quarantined_qty
        
        return available_qty
