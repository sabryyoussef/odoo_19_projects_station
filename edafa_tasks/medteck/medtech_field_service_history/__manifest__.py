# -*- coding: utf-8 -*-
{
    'name': 'MedTech Field Service History',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/MedTech',
    'summary': 'Service visits, Maintenance plans, Firmware updates, Field corrections, Part replacements',
    'description': """
MedTech Field Service History Module
=====================================
Track all field service activities and link to DHR.

Features:
---------
* Service visit records with technician signatures
* Maintenance plan scheduling
* Firmware update tracking (old/new versions)
* Parts replacement with serial traceability
* Photo/evidence attachment
* Offline-friendly design for field use
* Integration with DHR compilation
* Recall action tracking
    """,
    'author': 'MedTech ERP Team',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['medtech_core', 'medtech_traceability', 'stock', 'mail'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/sequences.xml',
        # Views
        'views/service_visit_views.xml',
        # Menus
        'views/field_service_menus.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
