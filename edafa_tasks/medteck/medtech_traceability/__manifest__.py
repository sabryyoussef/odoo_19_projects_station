# -*- coding: utf-8 -*-
{
    'name': 'MedTech Traceability',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/MedTech',
    'summary': 'UDI, Serial/Lot genealogy, DHR builder, Forward/Backward traceability',
    'description': """
MedTech Traceability Module
============================
Complete device traceability from components to finished goods to field.

Features:
---------
* UDI (Unique Device Identification) registry
* Device Master with regulatory classification
* Device History Record (DHR) compilation and PDF export
* Forward/backward traceability query engine
* Component genealogy tracking
* Integration with MRP, Inventory, and Field Service
    """,
    'author': 'MedTech ERP Team',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['medtech_core', 'stock', 'mrp', 'product', 'mail', 'purchase_stock'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        # Views
        'views/device_master_views.xml',
        'views/medtech_udi_views.xml',
        'views/medtech_dhr_views.xml',
        'views/traceability_batch_tools_views.xml',
        'views/traceability_menus.xml',
        'views/dashboard_actions.xml',
        # Reports
        'reports/dhr_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'medtech_traceability/static/src/js/traceability_dashboard.js',
            'medtech_traceability/static/src/xml/traceability_dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
