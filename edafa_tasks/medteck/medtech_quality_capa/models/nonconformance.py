# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedTechNonconformance(models.Model):
    """Nonconformance records from various sources"""
    _name = 'medtech.nonconformance'
    _description = 'Nonconformance'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    _audit_tracked_fields = ['source', 'description', 'root_cause', 'containment_action', 'state']

    name = fields.Char(string='NC Number', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'), index=True)
    
    # Source & Classification
    source = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('incoming', 'Incoming Inspection'),
        ('complaint', 'Customer Complaint'),
        ('service', 'Field Service'),
        ('audit', 'Internal Audit'),
        ('supplier', 'Supplier Issue'),
    ], string='Source', required=True, tracking=True, index=True)
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Severity', required=True, default='medium', tracking=True)
    
    # Description
    description = fields.Text(string='Description', required=True, tracking=True)
    detection_date = fields.Date(string='Detection Date', default=fields.Date.today, tracking=True)
    detected_by_id = fields.Many2one('res.users', string='Detected By', default=lambda self: self.env.user, tracking=True)
    
    # Affected Items
    affected_lot_ids = fields.Many2many('stock.lot', string='Affected Lots/Serials')
    affected_product_ids = fields.Many2many('product.product', string='Affected Products')
    affected_location_id = fields.Many2one('stock.location', string='Location')
    
    # Manufacturing Context
    # production_order_id = fields.Many2one('mrp.production', string='Manufacturing Order')  # Requires mrp module
    # work_order_id = fields.Many2one('mrp.workorder', string='Work Order')  # Requires mrp module
    
    # Supplier Context
    supplier_id = fields.Many2one('res.partner', string='Supplier', domain=[('supplier_rank', '>', 0)])
    # purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')  # Requires purchase module
    
    # Customer Context
    customer_id = fields.Many2one('res.partner', string='Customer')
    # sale_order_id = fields.Many2one('sale.order', string='Sales Order')  # Requires sale module
    
    # Analysis
    root_cause = fields.Text(string='Root Cause Analysis', tracking=True)
    containment_action = fields.Text(string='Immediate Containment Action', tracking=True,
                                     help='Immediate actions taken to contain the problem')
    
    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('investigation', 'Under Investigation'),
        ('contained', 'Contained'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True, index=True)
    
    # CAPA Link
    capa_ids = fields.One2many('medtech.capa', 'nonconformance_ids', string='CAPAs')
    capa_count = fields.Integer(string='CAPA Count', compute='_compute_capa_count')
    
    # Closure
    closed_date = fields.Date(string='Closed Date', readonly=True)
    closed_by_id = fields.Many2one('res.users', string='Closed By', readonly=True)
    closure_notes = fields.Text(string='Closure Notes')
    
    # Quality Check Link (if quality module exists)
    # quality_check_id = fields.Many2one('quality.check', string='Related Quality Check')  # Requires quality module
    
    # Color for kanban view
    color = fields.Integer(string='Color Index', compute='_compute_color', store=True)
    
    @api.depends('state', 'severity')
    def _compute_color(self):
        """Set color based on state and severity for kanban view"""
        for record in self:
            if record.state == 'closed':
                record.color = 10  # Green
            elif record.state == 'cancelled':
                record.color = 7   # Gray
            elif record.severity == 'critical':
                record.color = 1   # Red
            elif record.severity == 'high':
                record.color = 3   # Orange
            elif record.severity == 'medium':
                record.color = 4   # Blue
            else:
                record.color = 0   # White
    
    @api.depends('capa_ids')
    def _compute_capa_count(self):
        for record in self:
            record.capa_count = len(record.capa_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.nonconformance') or _('New')
        return super().create(vals_list)
    
    def action_start_investigation(self):
        """Move to investigation state"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Can only start investigation from Draft state.'))
        
        self.state = 'investigation'
        self.message_post(body=_('Investigation started by %s') % self.env.user.name)
        self._track_changes('write', context_info='Investigation started')
        return True
    
    def action_mark_contained(self):
        """Mark as contained"""
        self.ensure_one()
        if self.state != 'investigation':
            raise ValidationError(_('Can only mark as contained from Investigation state.'))
        
        if not self.containment_action:
            raise ValidationError(_('Please document the containment action taken.'))
        
        self.state = 'contained'
        self.message_post(body=_('Nonconformance contained by %s') % self.env.user.name)
        self._track_changes('write', context_info='Marked as contained')
        return True
    
    def action_close(self):
        """Close nonconformance"""
        self.ensure_one()
        if self.state not in ['investigation', 'contained']:
            raise ValidationError(_('Can only close from Investigation or Contained state.'))
        
        # Check if CAPA is required for high/critical severity
        if self.severity in ['high', 'critical'] and not self.capa_ids:
            raise ValidationError(_('High/Critical severity nonconformances require a CAPA before closure.'))
        
        self.write({
            'state': 'closed',
            'closed_date': fields.Date.today(),
            'closed_by_id': self.env.user.id,
        })
        
        self.message_post(body=_('Nonconformance closed by %s') % self.env.user.name)
        self._track_changes('write', context_info='Closed')
        return True
    
    def action_create_capa(self):
        """Create CAPA from this nonconformance"""
        self.ensure_one()
        
        capa = self.env['medtech.capa'].create({
            'nonconformance_ids': [(4, self.id)],
            'description': f"CAPA for NC: {self.name} - {self.description[:100]}",
            'source': 'nonconformance',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'CAPA',
            'res_model': 'medtech.capa',
            'res_id': capa.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_capas(self):
        """View related CAPAs"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'CAPAs',
            'res_model': 'medtech.capa',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.capa_ids.ids)],
            'context': {'default_nonconformance_ids': [(4, self.id)]},
        }
