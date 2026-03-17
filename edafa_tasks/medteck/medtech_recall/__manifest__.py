# -*- coding: utf-8 -*-
{
    'name': 'MedTech Recall Management',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/MedTech',
    'summary': 'Recall events, Quarantine management, Customer notifications, Regulatory reporting',
    'description': """
MedTech Recall Management Module
=================================
Complete recall lifecycle management from identification to closure.

Features:
---------
* Recall event classification (Class I/II/III)
* Affected population determination (by lot/serial/component/date)
* Automatic quarantine creation and enforcement
* Stock blocking for quarantined items
* Customer notification list generation
* Integration with CAPA and traceability
* Regulatory report pack generation
    """,
    'author': 'MedTech ERP Team',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['medtech_core', 'medtech_traceability', 'medtech_quality_capa', 'stock', 'mail'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/sequences.xml',
        # Views
        'views/recall_views.xml',
        # 'views/quarantine_views.xml',
        # Menus
        'views/recall_menus.xml',
        'views/dashboard_actions.xml',
        # Reports
        'reports/recall_report_pack.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'medtech_recall/static/src/js/recall_dashboard.js',
            'medtech_recall/static/src/xml/recall_dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
