# -*- coding: utf-8 -*-
from odoo import models, api


class MedTechTraceabilityQuery(models.AbstractModel):
    """Traceability query engine for fast genealogy lookups"""
    _name = 'medtech.traceability.query'
    _description = 'Traceability Query Engine'

    @api.model
    def get_forward_trace(self, lot_id):
        """
        Forward traceability: Where did this lot/serial go?
        Returns all finished devices, shipments, customers that used this component
        """
        lot = self.env['stock.lot'].browse(lot_id)
        if not lot:
            return {}
        
        result = {
            'lot': lot.name,
            'product': lot.product_id.name,
            'finished_devices': [],
            'shipments': [],
            'customers': [],
        }
        
        # Find DHRs where this lot was consumed as a component
        component_usages = self.env['medtech.dhr.component'].search([
            ('component_lot_id', '=', lot_id)
        ])
        
        for usage in component_usages:
            dhr = usage.dhr_id
            result['finished_devices'].append({
                'dhr_id': dhr.id,
                'serial': dhr.serial_lot_id.name,
                'device': dhr.device_master_id.name if dhr.device_master_id else 'N/A',
                'customer': dhr.customer_id.name if dhr.customer_id else 'Not shipped',
            })
        
        # Find shipments with this lot
        stock_moves = self.env['stock.move.line'].search([
            ('lot_id', '=', lot_id),
            ('state', '=', 'done')
        ])
        
        for move_line in stock_moves:
            picking = move_line.move_id.picking_id
            if picking and picking.picking_type_code == 'outgoing':
                result['shipments'].append({
                    'picking_id': picking.id,
                    'name': picking.name,
                    'customer': picking.partner_id.name,
                    'date': picking.date_done.strftime('%Y-%m-%d') if picking.date_done else 'N/A',
                })
                
                if picking.partner_id and picking.partner_id.name not in result['customers']:
                    result['customers'].append(picking.partner_id.name)
        
        return result
    
    @api.model
    def get_backward_trace(self, lot_id):
        """
        Backward traceability: What went into this lot/serial?
        Returns all components, subassemblies, manufacturing details
        """
        lot = self.env['stock.lot'].browse(lot_id)
        if not lot:
            return {}
        
        result = {
            'lot': lot.name,
            'product': lot.product_id.name,
            'components': [],
            'manufacturing': {},
        }
        
        # Find DHR for this lot
        dhr = self.env['medtech.dhr'].search([('serial_lot_id', '=', lot_id)], limit=1)
        
        if dhr:
            # Get manufacturing info
            if dhr.production_order_id:
                result['manufacturing'] = {
                    'mo_name': dhr.production_order_id.name,
                    'date': dhr.manufacture_date.strftime('%Y-%m-%d %H:%M') if dhr.manufacture_date else 'N/A',
                    'responsible': dhr.production_order_id.user_id.name if dhr.production_order_id.user_id else 'N/A',
                }
            
            # Get all components
            for comp in dhr.consumed_component_ids:
                comp_data = {
                    'component': comp.component_product_id.name,
                    'lot': comp.component_lot_id.name if comp.component_lot_id else 'No lot',
                    'quantity': comp.quantity,
                    'date': comp.consumed_date.strftime('%Y-%m-%d') if comp.consumed_date else 'N/A',
                }
                
                # Recursive: if component has its own DHR, get its components too
                if comp.component_dhr_id:
                    comp_data['sub_components'] = self.get_backward_trace(comp.component_lot_id.id)
                
                result['components'].append(comp_data)
        
        return result
    
    @api.model
    def get_component_impact(self, component_lot_id):
        """
        Find all finished devices that used a specific component lot
        Critical for recalls: "This component batch is bad, which devices have it?"
        """
        component_lot = self.env['stock.lot'].browse(component_lot_id)
        if not component_lot:
            return {}
        
        result = {
            'component_lot': component_lot.name,
            'component_product': component_lot.product_id.name,
            'affected_devices': [],
            'affected_count': 0,
        }
        
        # Find all DHRs that consumed this component lot
        usages = self.env['medtech.dhr.component'].search([
            ('component_lot_id', '=', component_lot_id)
        ])
        
        for usage in usages:
            dhr = usage.dhr_id
            device_data = {
                'dhr_id': dhr.id,
                'device': dhr.device_master_id.name if dhr.device_master_id else 'N/A',
                'serial': dhr.serial_lot_id.name,
                'manufacture_date': dhr.manufacture_date.strftime('%Y-%m-%d') if dhr.manufacture_date else 'N/A',
                'customer': dhr.customer_id.name if dhr.customer_id else 'In stock',
                'location': 'Shipped to customer' if dhr.customer_id else 'In warehouse',
                'is_recalled': dhr.is_recalled,
            }
            result['affected_devices'].append(device_data)
        
        result['affected_count'] = len(result['affected_devices'])
        
        return result
    
    @api.model
    def get_shipment_trace(self, picking_id):
        """
        Get all serials/lots in a specific shipment
        """
        picking = self.env['stock.picking'].browse(picking_id)
        if not picking:
            return {}
        
        result = {
            'picking': picking.name,
            'customer': picking.partner_id.name if picking.partner_id else 'N/A',
            'date': picking.date_done.strftime('%Y-%m-%d') if picking.date_done else 'Not done',
            'devices': [],
        }
        
        # Get all lots from move lines
        for move_line in picking.move_line_ids:
            if move_line.lot_id:
                # Check if there's a DHR for this lot
                dhr = self.env['medtech.dhr'].search([('serial_lot_id', '=', move_line.lot_id.id)], limit=1)
                
                device_data = {
                    'product': move_line.product_id.name,
                    'lot_serial': move_line.lot_id.name,
                    'quantity': move_line.quantity,
                    'has_dhr': bool(dhr),
                    'dhr_id': dhr.id if dhr else False,
                }
                result['devices'].append(device_data)
        
        return result

    @api.model
    def get_batch_backward_trace(self, lot_id):
        lot = self.env['stock.lot'].browse(lot_id)
        if not lot:
            return {}

        result = {
            'lot': lot.name,
            'product': lot.product_id.name,
            'manufacturing_order': '-',
            'stage_records': [],
            'consumed_lots': [],
        }

        filling = self.env['medtech.filling.batch'].search([('finished_lot_id', '=', lot_id)], limit=1)
        if filling and filling.production_id:
            result['manufacturing_order'] = filling.production_id.name
            result['stage_records'].append(f'Filling:{filling.name}')

            packaging = self.env['medtech.packaging.batch'].search([('production_id', '=', filling.production_id.id)], limit=1)
            if packaging:
                result['stage_records'].append(f'Packaging:{packaging.name}')

            sterilization = self.env['medtech.sterilization.batch'].search([('production_id', '=', filling.production_id.id)], limit=1)
            if sterilization:
                result['stage_records'].append(f'Sterilization:{sterilization.name}')

            compounding = self.env['medtech.compounding.batch'].search([('production_id', '=', filling.production_id.id)], limit=1)
            if compounding:
                result['stage_records'].append(f'Compounding:{compounding.name}')

            weighing = self.env['medtech.weighing.batch'].search([('production_id', '=', filling.production_id.id)], limit=1)
            if weighing:
                result['stage_records'].append(f'Weighing:{weighing.name}')
                for line in weighing.line_ids:
                    if line.lot_id:
                        result['consumed_lots'].append(f'{line.product_id.display_name} / {line.lot_id.name}')

        return result

    @api.model
    def get_batch_forward_trace(self, lot_id):
        lot = self.env['stock.lot'].browse(lot_id)
        if not lot:
            return {}

        result = {
            'lot': lot.name,
            'product': lot.product_id.name,
            'produced_lots': [],
            'customers': [],
        }

        filling_lines = self.env['medtech.weighing.batch.line'].search([('lot_id', '=', lot_id)])
        mo_ids = filling_lines.mapped('batch_id.production_id').ids
        for mo in self.env['mrp.production'].browse(mo_ids):
            filling = self.env['medtech.filling.batch'].search([('production_id', '=', mo.id)], limit=1)
            if filling and filling.finished_lot_id:
                result['produced_lots'].append(filling.finished_lot_id.name)

        move_lines = self.env['stock.move.line'].search([
            ('lot_id', '=', lot_id),
            ('state', '=', 'done'),
        ])
        for line in move_lines:
            picking = line.move_id.picking_id
            if picking and picking.picking_type_code == 'outgoing' and picking.partner_id:
                customer_name = picking.partner_id.name
                if customer_name not in result['customers']:
                    result['customers'].append(customer_name)

        return result
