# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class MedTechDHR(models.Model):
    """Device History Record - Complete compilation of device lifecycle"""
    _name = 'medtech.dhr'
    _description = 'Device History Record (DHR)'
    _inherit = ['medtech.audit.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'
    
    _audit_tracked_fields = ['serial_lot_id', 'device_master_id', 'production_order_id', 'state']

    display_name = fields.Char(string='DHR Name', compute='_compute_display_name', store=True)
    
    # Core Identity
    serial_lot_id = fields.Many2one('stock.lot', string='Serial/Lot Number', required=True, tracking=True)
    device_master_id = fields.Many2one('product.template', string='Device Master', 
                                       domain=[('is_medical_device', '=', True)], tracking=True)
    udi_id = fields.Many2one('medtech.udi', string='UDI Record', compute='_compute_udi_id')
    
    # Manufacturing
    production_order_id = fields.Many2one('mrp.production', string='Manufacturing Order', tracking=True)
    manufacture_date = fields.Datetime(string='Manufacturing Date', related='production_order_id.date_start', readonly=True)
    # work_order_ids = fields.One2many(related='production_order_id.workorder_ids', string='Work Orders', readonly=True)
    
    # Components & Genealogy
    consumed_component_ids = fields.One2many('medtech.dhr.component', 'dhr_id', string='Consumed Components')
    component_count = fields.Integer(string='Component Count', compute='_compute_component_count')
    
    # Quality
    # qc_result_ids = fields.Many2many('quality.check', string='QC Results', 
    #                                  help='Quality checks performed during manufacturing')
    # deviation_ids = fields.Many2many('medtech.nonconformance', string='Deviations/Nonconformances')
    
    # Engineering Changes
    # eco_ids = fields.Many2many('mrp.eco', string='Engineering Change Orders (ECOs)', 
    #                            help='ECOs that affected this device during manufacturing')
    
    # Distribution
    shipment_ids = fields.Many2many('stock.picking', string='Shipments')
    customer_id = fields.Many2one('res.partner', string='Final Customer', compute='_compute_customer')
    ship_date = fields.Datetime(string='Ship Date', compute='_compute_ship_date')
    
    # Field Service
    # service_visit_ids = fields.One2many('medtech.service.visit', 'device_serial_id', string='Service Visits')
    # service_count = fields.Integer(string='Service Visits', compute='_compute_service_count')
    
    # DHR Compilation
    state = fields.Selection([
        ('draft', 'Draft'),
        ('compiled', 'Compiled'),
        ('approved', 'Approved'),
    ], string='DHR State', default='draft', tracking=True)
    
    compiled_date = fields.Datetime(string='Compiled Date')
    compiled_by_id = fields.Many2one('res.users', string='Compiled By')
    html_snapshot = fields.Html(string='DHR Snapshot', help='HTML snapshot for PDF generation')
    
    # Audit & Recall Status
    # recall_ids = fields.Many2many('medtech.recall', string='Recalls Affecting This Device')
    # is_recalled = fields.Boolean(string='Currently Recalled', compute='_compute_recall_status')
    
    @api.depends('serial_lot_id', 'device_master_id')
    def _compute_display_name(self):
        for record in self:
            if record.serial_lot_id and record.device_master_id:
                record.display_name = f"DHR: {record.device_master_id.name} / {record.serial_lot_id.name}"
            elif record.serial_lot_id:
                record.display_name = f"DHR: {record.serial_lot_id.name}"
            else:
                record.display_name = 'New DHR'
    
    @api.depends('serial_lot_id')
    def _compute_udi_id(self):
        for record in self:
            if record.serial_lot_id:
                udi = self.env['medtech.udi'].search([('lot_id', '=', record.serial_lot_id.id)], limit=1)
                record.udi_id = udi.id if udi else False
            else:
                record.udi_id = False
    
    @api.depends('consumed_component_ids')
    def _compute_component_count(self):
        for record in self:
            record.component_count = len(record.consumed_component_ids)
    
    def _compute_customer(self):
        for record in self:
            # Get from last outgoing shipment
            if record.shipment_ids:
                outgoing = record.shipment_ids.filtered(lambda p: p.picking_type_code == 'outgoing')
                if outgoing:
                    record.customer_id = outgoing[-1].partner_id.id
                else:
                    record.customer_id = False
            else:
                record.customer_id = False
    
    def _compute_ship_date(self):
        for record in self:
            if record.shipment_ids:
                outgoing = record.shipment_ids.filtered(lambda p: p.picking_type_code == 'outgoing' and p.state == 'done')
                if outgoing:
                    record.ship_date = outgoing[-1].date_done
                else:
                    record.ship_date = False
            else:
                record.ship_date = False
    
    # @api.depends('service_visit_ids')
    # def _compute_service_count(self):
    #     for record in self:
    #         record.service_count = len(record.service_visit_ids)
    
    # @api.depends('recall_ids')
    # def _compute_recall_status(self):
    #     for record in self:
    #         active_recalls = record.recall_ids.filtered(lambda r: r.state == 'active')
    #         record.is_recalled = bool(active_recalls)
    
    def action_compile_dhr(self):
        """Compile complete DHR from all sources"""
        self.ensure_one()
        
        # Gather manufacturing data
        if self.production_order_id:
            # Get consumed components
            self._compile_components()
            
            # Get QC results (if quality module exists)
            if 'quality.check' in self.env:
                qc_checks = self.env['quality.check'].search([
                    ('production_id', '=', self.production_order_id.id)
                ])
                self.qc_result_ids = [(6, 0, qc_checks.ids)]
        
        # Get shipments
        pickings = self.env['stock.picking'].search([
            ('move_ids.lot_ids', 'in', self.serial_lot_id.id)
        ])
        self.shipment_ids = [(6, 0, pickings.ids)]
        
        # Compile HTML snapshot
        self._generate_html_snapshot()
        
        # Update state
        self.write({
            'state': 'compiled',
            'compiled_date': fields.Datetime.now(),
            'compiled_by_id': self.env.user.id,
        })
        
        self._track_changes('write', context_info='DHR compiled')
        
        return True
    
    def _compile_components(self):
        """Extract consumed components from manufacturing order"""
        self.ensure_one()
        if not self.production_order_id:
            return
        
        # Clear existing
        self.consumed_component_ids.unlink()
        
        # Get stock moves from production
        for move in self.production_order_id.move_raw_ids.filtered(lambda m: m.state == 'done'):
            for move_line in move.move_line_ids:
                self.env['medtech.dhr.component'].create({
                    'dhr_id': self.id,
                    'component_product_id': move.product_id.id,
                    'component_lot_id': move_line.lot_id.id,
                    'quantity': move_line.quantity,
                    'consumed_date': move.date,
                })
    
    def _generate_html_snapshot(self):
        """Generate HTML snapshot for PDF export"""
        self.ensure_one()
        
        html = f"""
        <div class="dhr-snapshot">
            <h1>Device History Record</h1>
            <h2>{self.device_master_id.name if self.device_master_id else 'N/A'}</h2>
            <h3>Serial/Lot: {self.serial_lot_id.name}</h3>
            <p><strong>Compiled:</strong> {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Compiled By:</strong> {self.env.user.name}</p>
            
            <h3>Manufacturing Information</h3>
            <p><strong>Manufacturing Order:</strong> {self.production_order_id.name if self.production_order_id else 'N/A'}</p>
            <p><strong>Manufacturing Date:</strong> {self.manufacture_date or 'N/A'}</p>
            
            <h3>Components ({len(self.consumed_component_ids)})</h3>
            <table>
                <tr><th>Component</th><th>Lot/Serial</th><th>Quantity</th></tr>
        """
        
        for comp in self.consumed_component_ids:
            html += f"""
                <tr>
                    <td>{comp.component_product_id.name}</td>
                    <td>{comp.component_lot_id.name if comp.component_lot_id else 'N/A'}</td>
                    <td>{comp.quantity}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h3>Quality Checks</h3>
        """
        
        if self.qc_result_ids:
            html += f"<p>{len(self.qc_result_ids)} quality checks performed</p>"
        else:
            html += "<p>No quality checks recorded</p>"
        
        html += f"""
            <h3>Shipment Information</h3>
            <p><strong>Customer:</strong> {self.customer_id.name if self.customer_id else 'Not shipped'}</p>
            <p><strong>Ship Date:</strong> {self.ship_date or 'N/A'}</p>
            
            <h3>Service History</h3>
            <p>{len(self.service_visit_ids)} service visit(s)</p>
        </div>
        """
        
        self.html_snapshot = html
    
    def compute_genealogy_tree(self):
        """Compute genealogy tree for traceability dashboard"""
        self.ensure_one()
        
        def build_tree(dhr_record):
            """Recursively build genealogy tree"""
            if not dhr_record:
                return None
            
            tree_node = {
                'id': dhr_record.id,
                'name': dhr_record.display_name,
                'serial_number': dhr_record.serial_lot_id.name if dhr_record.serial_lot_id else None,
                'lot_number': dhr_record.serial_lot_id.name if dhr_record.serial_lot_id else None,
                'product': dhr_record.device_master_id.name if dhr_record.device_master_id else None,
                'manufacturing_date': dhr_record.manufacture_date.strftime('%Y-%m-%d') if dhr_record.manufacture_date else None,
                'components': []
            }
            
            # Add consumed components
            for component in dhr_record.consumed_component_ids:
                comp_node = {
                    'name': component.component_product_id.name,
                    'serial_number': component.component_lot_id.name if component.component_lot_id else None,
                    'lot_number': component.component_lot_id.name if component.component_lot_id else None,
                    'quantity': component.quantity,
                    'components': []
                }
                
                # If component has its own DHR, recurse
                if component.component_dhr_id:
                    sub_tree = build_tree(component.component_dhr_id)
                    if sub_tree:
                        comp_node['components'] = sub_tree.get('components', [])
                
                tree_node['components'].append(comp_node)
            
            return tree_node
        
        return build_tree(self)
    
    def action_generate_pdf(self):
        """Generate PDF report"""
        self.ensure_one()
        if self.state != 'compiled':
            self.action_compile_dhr()
        
        return self.env.ref('medtech_traceability.action_report_dhr').report_action(self)


class MedTechDHRComponent(models.Model):
    """Components consumed in device manufacturing"""
    _name = 'medtech.dhr.component'
    _description = 'DHR Component'
    _order = 'consumed_date'
    
    dhr_id = fields.Many2one('medtech.dhr', string='DHR', required=True, ondelete='cascade')
    component_product_id = fields.Many2one('product.product', string='Component', required=True)
    component_lot_id = fields.Many2one('stock.lot', string='Component Lot/Serial')
    quantity = fields.Float(string='Quantity Consumed', default=1.0)
    consumed_date = fields.Datetime(string='Consumed Date')
    
    # Nested DHR for sub-assemblies
    component_dhr_id = fields.Many2one('medtech.dhr', string='Component DHR', 
                                       help='If component is also a tracked device')
