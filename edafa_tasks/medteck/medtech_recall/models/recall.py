# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MedTechRecall(models.Model):
    """Recall Event Management"""
    _name = 'medtech.recall'
    _description = 'Recall Event'
    _inherit = ['medtech.approval.mixin', 'medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    _audit_tracked_fields = ['classification', 'severity', 'state', 'affected_determination']

    name = fields.Char(string='Recall Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True)
    
    # Classification
    classification = fields.Selection([
        ('class_i', 'Class I - Most Serious'),
        ('class_ii', 'Class II - Moderate'),
        ('class_iii', 'Class III - Least Serious'),
    ], string='FDA Classification', required=True, tracking=True,
       help='Class I: Dangerous/defective products that could cause serious health problems or death\n'
            'Class II: Products that might cause temporary health problem or slight threat of serious nature\n'
            'Class III: Products unlikely to cause adverse health reaction but violate FDA labeling/manufacturing regulations')
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Severity', required=True, default='high', tracking=True)
    
    recall_type = fields.Selection([
        ('safety', 'Safety Recall'),
        ('quality', 'Quality Issue'),
        ('regulatory', 'Regulatory Compliance'),
        ('precautionary', 'Precautionary'),
    ], string='Recall Type', required=True, default='safety', tracking=True)
    
    # Trigger Source
    trigger_source = fields.Selection([
        ('internal_testing', 'Internal Testing'),
        ('customer_complaint', 'Customer Complaint'),
        ('field_service', 'Field Service Report'),
        ('supplier_issue', 'Supplier Issue'),
        ('regulatory_authority', 'Regulatory Authority Request'),
        ('capa', 'CAPA Investigation'),
        ('other', 'Other'),
    ], string='Trigger Source', required=True, tracking=True)
    
    # trigger_capa_id = fields.Many2one('medtech.capa', string='Trigger CAPA')
    # trigger_nonconformance_id = fields.Many2one('medtech.nonconformance', string='Trigger Nonconformance')
    
    # Description
    description = fields.Text(string='Recall Reason', required=True, tracking=True)
    health_hazard_evaluation = fields.Text(string='Health Hazard Evaluation',
                                           help='Assessment of health risks posed to users')
    
    # Dates
    initiation_date = fields.Date(string='Recall Initiation Date', default=fields.Date.today, required=True, tracking=True)
    target_completion_date = fields.Date(string='Target Completion Date', tracking=True)
    actual_completion_date = fields.Date(string='Actual Completion Date', readonly=True)
    
    # Affected Population Determination
    affected_determination = fields.Selection([
        ('by_lot', 'By Finished Lot/Serial'),
        ('by_serial', 'By Specific Serials'),
        ('by_component', 'By Component Lot (Genealogy)'),
        ('by_date_range', 'By Manufacturing Date Range'),
        ('by_product', 'By Product/Model'),
    ], string='Affected Determination Method', required=True, tracking=True)
    
    # Affected Items (depending on determination method)
    affected_lot_ids = fields.Many2many('stock.lot', 'recall_lot_rel', string='Affected Lots/Serials')
    affected_serial_ids = fields.Many2many('stock.lot', 'recall_serial_rel', string='Specific Serials')
    affected_component_lot_id = fields.Many2one('stock.lot', string='Defective Component Lot',
                                                help='Component lot that triggers recall via genealogy')
    affected_product_ids = fields.Many2many('product.product', string='Affected Products')
    
    date_range_start = fields.Date(string='Manufacturing Start Date')
    date_range_end = fields.Date(string='Manufacturing End Date')
    
    # Calculated Affected Population
    total_manufactured = fields.Integer(string='Total Manufactured', compute='_compute_affected_population')
    total_in_stock = fields.Integer(string='In Stock', compute='_compute_affected_population')
    total_distributed = fields.Integer(string='Distributed to Customers', compute='_compute_affected_population')
    total_returned = fields.Integer(string='Returned', compute='_compute_affected_population')
    
    # Actions
    recall_action = fields.Selection([
        ('retrieve', 'Retrieve/Return to Manufacturer'),
        ('field_correction', 'Field Correction/Modification'),
        ('customer_notification', 'Customer Notification Only'),
        ('destroy', 'Destroy in Field'),
    ], string='Recall Action', required=True, default='retrieve', tracking=True)
    
    correction_instructions = fields.Text(string='Correction Instructions',
                                         help='Instructions for field correction or customer action')
    
    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active Recall'),
        ('monitoring', 'Monitoring'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True, index=True)
    
    # Quarantines
    quarantine_ids = fields.One2many('medtech.quarantine', 'recall_id', string='Quarantines')
    quarantine_count = fields.Integer(string='Quarantines', compute='_compute_quarantine_count')
    
    # Customer Notifications
    customer_notification_ids = fields.One2many('medtech.recall.notification', 'recall_id', string='Customer Notifications')
    notification_count = fields.Integer(string='Notifications Sent', compute='_compute_notification_count')
    impacted_customer_count = fields.Integer(string='Impacted Customers', compute='_compute_impacted_customer_count', store=False)

    # Simulation + CAPA linkage
    simulation_done = fields.Boolean(string='Simulation Completed', default=False, readonly=True, tracking=True)
    simulation_at = fields.Datetime(string='Simulation Completed At', readonly=True)
    simulation_notes = fields.Text(string='Simulation Notes')
    nonconformance_id = fields.Many2one('medtech.nonconformance', string='Related Nonconformance', readonly=True)
    capa_id = fields.Many2one('medtech.capa', string='Related CAPA', readonly=True)

    # Regulatory Pack
    regulatory_pack_generated = fields.Boolean(string='Regulatory Pack Generated', default=False, readonly=True, tracking=True)
    regulatory_pack_generated_at = fields.Datetime(string='Regulatory Pack Generated At', readonly=True)
    
    # Regulatory Reporting
    fda_reported = fields.Boolean(string='Reported to FDA', tracking=True)
    fda_report_date = fields.Date(string='FDA Report Date')
    fda_report_number = fields.Char(string='FDA Report Number')
    
    eu_competent_authority_reported = fields.Boolean(string='Reported to EU Competent Authority', tracking=True)
    eu_report_date = fields.Date(string='EU Report Date')
    eu_fsca_number = fields.Char(string='EU FSCA Number', help='Field Safety Corrective Action number')
    
    # Effectiveness
    effectiveness_check_date = fields.Date(string='Effectiveness Check Date')
    effectiveness_result = fields.Text(string='Effectiveness Check Result')
    
    # Responsible
    responsible_id = fields.Many2one('res.users', string='Recall Coordinator', tracking=True,
                                     default=lambda self: self.env.user)
    
    @api.depends('quarantine_ids')
    def _compute_quarantine_count(self):
        for record in self:
            record.quarantine_count = len(record.quarantine_ids)
    
    @api.depends('customer_notification_ids')
    def _compute_notification_count(self):
        for record in self:
            record.notification_count = len(record.customer_notification_ids)

    @api.depends('customer_notification_ids.customer_id')
    def _compute_impacted_customer_count(self):
        for record in self:
            record.impacted_customer_count = len(record.customer_notification_ids.mapped('customer_id'))
    
    @api.depends('affected_determination', 'affected_lot_ids', 'affected_component_lot_id', 
                 'affected_product_ids', 'date_range_start', 'date_range_end')
    def _compute_affected_population(self):
        """Calculate affected population based on determination method"""
        for record in self:
            affected_serials = self.env['stock.lot']
            
            if record.affected_determination == 'by_lot':
                affected_serials = record.affected_lot_ids
            
            elif record.affected_determination == 'by_serial':
                affected_serials = record.affected_serial_ids
            
            elif record.affected_determination == 'by_component':
                # Use traceability to find all finished devices with this component
                if record.affected_component_lot_id:
                    trace_result = self.env['medtech.traceability.query'].get_component_impact(
                        record.affected_component_lot_id.id
                    )
                    affected_dhr_ids = [d['dhr_id'] for d in trace_result.get('affected_devices', [])]
                    dhrs = self.env['medtech.dhr'].browse(affected_dhr_ids)
                    affected_serials = dhrs.mapped('serial_lot_id')
            
            elif record.affected_determination == 'by_date_range':
                # Find DHRs manufactured in date range
                if record.date_range_start and record.date_range_end:
                    dhrs = self.env['medtech.dhr'].search([
                        ('manufacture_date', '>=', record.date_range_start),
                        ('manufacture_date', '<=', record.date_range_end),
                    ])
                    affected_serials = dhrs.mapped('serial_lot_id')
            
            elif record.affected_determination == 'by_product':
                # Find all lots of affected products
                affected_serials = self.env['stock.lot'].search([
                    ('product_id', 'in', record.affected_product_ids.ids)
                ])
            
            # Calculate counts
            record.total_manufactured = len(affected_serials)
            
            # Count quarantined/in stock
            quarantined_quants = self.env['stock.quant'].search([
                ('lot_id', 'in', affected_serials.ids),
                ('quantity', '>', 0),
            ])
            record.total_in_stock = len(quarantined_quants.mapped('lot_id'))
            
            # Distributed = manufactured - in stock
            record.total_distributed = record.total_manufactured - record.total_in_stock
            
            # Count returned (from quarantines marked as returned)
            returned_quarantines = record.quarantine_ids.filtered(lambda q: q.status == 'returned')
            record.total_returned = len(returned_quarantines)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medtech.recall') or _('New')
        return super().create(vals_list)
    
    def action_activate_recall(self):
        """Activate recall and create quarantines"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise ValidationError(_('Can only activate recalls from Draft state.'))
        
        if not self.description:
            raise ValidationError(_('Recall reason is required.'))
        
        # Calculate affected population first
        self._compute_affected_population()
        
        # Create quarantines for in-stock items
        self._create_quarantines()
        
        # Generate customer notifications for distributed items
        self._generate_customer_notifications()
        
        # Update state
        self.state = 'active'
        
        self.message_post(body=_('Recall activated by %s. %d units affected, %d quarantined, %d distributed.') % 
                         (self.env.user.name, self.total_manufactured, self.total_in_stock, self.total_distributed))
        self._track_changes('write', context_info='Recall activated')
        
        return True

    def action_run_recall_simulation(self):
        """Run end-to-end recall simulation for the selected affected population."""
        self.ensure_one()

        affected_serials = self._get_affected_serials()
        if not affected_serials:
            raise ValidationError(_('No affected lots/serials found. Please define affected population before simulation.'))

        self._compute_affected_population()
        self._create_quarantines()
        self._generate_customer_notifications()
        self._ensure_recall_capa()

        vals = {
            'simulation_done': True,
            'simulation_at': fields.Datetime.now(),
            'state': 'active' if self.state == 'draft' else self.state,
            'simulation_notes': _('Recall simulation executed for %d affected lot(s)/serial(s).') % len(affected_serials),
        }
        self.write(vals)

        self.message_post(body=_(
            'Recall simulation completed by %s. Quarantines: %d, Notifications: %d, CAPA: %s'
        ) % (
            self.env.user.name,
            len(self.quarantine_ids),
            len(self.customer_notification_ids),
            self.capa_id.name or _('Not Created')
        ))
        self._track_changes('write', context_info='Recall simulation completed')
        return True

    def action_generate_regulatory_pack(self):
        """Mark and open FDA/EU regulatory report pack."""
        self.ensure_one()
        self.write({
            'regulatory_pack_generated': True,
            'regulatory_pack_generated_at': fields.Datetime.now(),
        })
        report_action = self.env.ref('medtech_recall.action_report_recall_pack', raise_if_not_found=False)
        if not report_action:
            raise UserError(_('Recall report action is not configured.'))
        return report_action.report_action(self)
    
    def _create_quarantines(self):
        """Create quarantine records for affected in-stock items"""
        self.ensure_one()
        
        # Get affected serials based on determination method
        affected_serials = self._get_affected_serials()
        
        # Find stock quants for these serials
        quants = self.env['stock.quant'].search([
            ('lot_id', 'in', affected_serials.ids),
            ('quantity', '>', 0),
            ('location_id.usage', '=', 'internal'),  # Only internal locations
        ])
        
        for quant in quants:
            existing = self.env['medtech.quarantine'].search([
                ('recall_id', '=', self.id),
                ('lot_id', '=', quant.lot_id.id),
                ('location_id', '=', quant.location_id.id),
                ('status', '=', 'quarantined'),
            ], limit=1)
            if existing:
                continue

            # Create quarantine record
            self.env['medtech.quarantine'].create({
                'recall_id': self.id,
                'lot_id': quant.lot_id.id,
                'product_id': quant.product_id.id,
                'location_id': quant.location_id.id,
                'quantity': quant.quantity,
                'quarantine_date': fields.Datetime.now(),
                'reason': f"Recall {self.name}: {self.description[:100]}",
                'status': 'quarantined',
            })
            
            # Mark quant as quarantined
            quant.write({
                'is_quarantined': True,
                'quarantine_reason': f"Recall: {self.name}",
                'quarantine_date': fields.Datetime.now(),
            })
        
        return True
    
    def _generate_customer_notifications(self):
        """Generate customer notification records for distributed items"""
        self.ensure_one()
        
        affected_serials = self._get_affected_serials()
        
        # Find deliveries of these serials
        pickings = self.env['stock.picking'].search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', '=', 'done'),
            ('move_line_ids.lot_id', 'in', affected_serials.ids),
        ])
        
        # Group by customer
        customers = {}
        for picking in pickings:
            customer = picking.partner_id
            if customer not in customers:
                customers[customer] = []
            
            # Get serials from this picking
            serials = picking.move_line_ids.filtered(
                lambda ml: ml.lot_id in affected_serials
            ).mapped('lot_id')
            customers[customer].extend(serials)
        
        # Create notification records
        for customer, serials in customers.items():
            existing = self.env['medtech.recall.notification'].search([
                ('recall_id', '=', self.id),
                ('customer_id', '=', customer.id),
            ], limit=1)
            if existing:
                combined = set(existing.affected_serial_ids.ids + [s.id for s in set(serials)])
                existing.write({'affected_serial_ids': [(6, 0, list(combined))]})
                continue

            self.env['medtech.recall.notification'].create({
                'recall_id': self.id,
                'customer_id': customer.id,
                'affected_serial_ids': [(6, 0, [s.id for s in set(serials)])],
                'notification_method': 'email',
                'status': 'pending',
            })
        
        return True
    
    def _get_affected_serials(self):
        """Get all affected serial/lot numbers based on determination method"""
        self.ensure_one()
        
        if self.affected_determination == 'by_lot':
            return self.affected_lot_ids
        elif self.affected_determination == 'by_serial':
            return self.affected_serial_ids
        elif self.affected_determination == 'by_component':
            if self.affected_component_lot_id:
                trace_result = self.env['medtech.traceability.query'].get_component_impact(
                    self.affected_component_lot_id.id
                )
                dhr_ids = [d['dhr_id'] for d in trace_result.get('affected_devices', [])]
                dhrs = self.env['medtech.dhr'].browse(dhr_ids)
                return dhrs.mapped('serial_lot_id')
        elif self.affected_determination == 'by_date_range':
            if self.date_range_start and self.date_range_end:
                dhrs = self.env['medtech.dhr'].search([
                    ('manufacture_date', '>=', self.date_range_start),
                    ('manufacture_date', '<=', self.date_range_end),
                ])
                return dhrs.mapped('serial_lot_id')
        elif self.affected_determination == 'by_product':
            return self.env['stock.lot'].search([
                ('product_id', 'in', self.affected_product_ids.ids)
            ])
        
        return self.env['stock.lot']

    def _ensure_recall_capa(self):
        """Open/link NC + CAPA from recall simulation."""
        self.ensure_one()

        nc = self.nonconformance_id
        if not nc:
            nc = self.env['medtech.nonconformance'].create({
                'source': 'complaint',
                'severity': self.severity,
                'description': _('Recall %(recall)s: %(reason)s') % {
                    'recall': self.name,
                    'reason': self.description,
                },
                'affected_lot_ids': [(6, 0, self._get_affected_serials().ids)],
                'affected_product_ids': [(6, 0, self.affected_product_ids.ids)],
                'state': 'investigation',
            })
            self.nonconformance_id = nc.id

        capa = self.capa_id
        if not capa:
            capa = self.env['medtech.capa'].create({
                'source': 'recall',
                'description': _('CAPA opened from Recall %(recall)s') % {'recall': self.name},
                'nonconformance_ids': [(4, nc.id)],
                'affected_serial_lot_ids': [(6, 0, self._get_affected_serials().ids)],
                'affected_product_ids': [(6, 0, self.affected_product_ids.ids)],
                'action_plan': _('Investigate recall root cause and implement corrective/preventive actions.'),
                'target_completion_date': fields.Date.today(),
                'responsible_id': self.responsible_id.id or self.env.user.id,
            })
            self.capa_id = capa.id

        return capa
    
    def action_close_recall(self):
        """Close recall after all actions completed"""
        self.ensure_one()
        
        if self.state != 'active':
            raise ValidationError(_('Can only close active recalls.'))
        
        # Check if all quarantines are resolved
        pending_quarantines = self.quarantine_ids.filtered(lambda q: q.status == 'quarantined')
        if pending_quarantines:
            raise ValidationError(_('Cannot close recall with %d pending quarantines.') % len(pending_quarantines))
        
        self.write({
            'state': 'closed',
            'actual_completion_date': fields.Date.today(),
        })
        
        self.message_post(body=_('Recall closed by %s') % self.env.user.name)
        self._track_changes('write', context_info='Recall closed')
        
        return True
    
    def action_view_quarantines(self):
        """View quarantines for this recall"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quarantines',
            'res_model': 'medtech.quarantine',
            'view_mode': 'tree,form',
            'domain': [('recall_id', '=', self.id)],
        }
    
    def action_view_notifications(self):
        """View customer notifications"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Notifications',
            'res_model': 'medtech.recall.notification',
            'view_mode': 'tree,form',
            'domain': [('recall_id', '=', self.id)],
        }
    
    @api.model
    def get_total_affected_customers(self):
        """Get total number of affected customers across all recalls"""
        notifications = self.env['medtech.recall.notification'].search([])
        return len(notifications.mapped('customer_id'))
