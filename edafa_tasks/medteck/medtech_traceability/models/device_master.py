# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    """Extend product to add device master fields"""
    _inherit = 'product.template'

    is_medical_device = fields.Boolean(string='Is Medical Device')
    device_family = fields.Char(string='Device Family')
    risk_class = fields.Selection([
        ('class_i', 'Class I'),
        ('class_iia', 'Class IIa'),
        ('class_iib', 'Class IIb'),
        ('class_iii', 'Class III'),
    ], string='Risk Classification')
    
    intended_use = fields.Text(string='Intended Use')
    regulatory_region_ids = fields.Many2many('medtech.regulatory.region', string='Regulatory Regions')
    udi_di = fields.Char(string='UDI-DI (Device Identifier)', help='Unique Device Identifier - Device Identifier')
    
    # Link to UDI records
    udi_ids = fields.One2many('medtech.udi', 'device_master_id', string='UDI Records')
    udi_count = fields.Integer(string='UDI Count', compute='_compute_udi_count')
    
    @api.depends('udi_ids')
    def _compute_udi_count(self):
        for record in self:
            record.udi_count = len(record.udi_ids)
    
    def action_view_udis(self):
        """Smart button to view UDI records"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'UDI Records',
            'res_model': 'medtech.udi',
            'view_mode': 'tree,form',
            'domain': [('device_master_id', '=', self.id)],
            'context': {'default_device_master_id': self.id, 'default_udi_di': self.udi_di},
        }


class MedTechRegulatoryRegion(models.Model):
    """Regulatory regions for device classification"""
    _name = 'medtech.regulatory.region'
    _description = 'Regulatory Region'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
