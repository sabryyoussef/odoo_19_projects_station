# -*- coding: utf-8 -*-
{
    'name': 'MedTech Vendor Compliance',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/MedTech',
    'summary': 'Vendor certifications, Expiry tracking, Purchase order gatekeeping',
    'description': """
MedTech Vendor Compliance Module
=================================
Ensure suppliers maintain required quality certifications.

Features:
---------
* Vendor certification tracking (ISO 9001, ISO 13485, Quality Agreements)
* Expiry date monitoring and alerts
* Purchase order confirmation blocking when certifications missing/expired
* Exception approval workflow with audit trail
* Vendor compliance scorecard
    """,
    'author': 'MedTech ERP Team',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['medtech_core', 'purchase', 'mail'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/vendor_certification_views.xml',
        # Menus
        'views/vendor_menus.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
