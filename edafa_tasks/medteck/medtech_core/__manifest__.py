# -*- coding: utf-8 -*-
{
    'name': 'MedTech Core',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/MedTech',
    'summary': 'Core compliance framework - Audit trails, approvals, security groups',
    'description': """
MedTech Core Module
===================
Foundation module for FDA 21 CFR Part 820, EU MDR, and ISO 13485 compliance.

Features:
---------
* Audit trail mixin for compliance-grade change tracking
* Multi-stage approval workflow mixin
* Security groups (Operator, QA, Regulatory, Auditor, etc.)
* Company-level compliance configuration
    """,
    'author': 'MedTech ERP Team',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        # Security
        'security/medtech_security.xml',
        'security/ir.model.access.csv',
        # Data
        # Views
        'views/medtech_audit_views.xml',
        # 'views/medtech_config_views.xml',
        # Menus
        'views/medtech_menus.xml',
        # Demo Data
        'demo/demo_data.xml',
    ],
    'demo': [],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
}
