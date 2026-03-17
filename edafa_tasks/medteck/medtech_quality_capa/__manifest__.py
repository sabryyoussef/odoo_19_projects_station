# -*- coding: utf-8 -*-
{
    'name': 'MedTech Quality & CAPA',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing/MedTech',
    'summary': 'Nonconformance, Deviations, CAPA workflow, Effectiveness checks',
    'description': """
MedTech Quality & CAPA Module
==============================
Corrective and Preventive Action management with workflow controls.

Features:
---------
* Nonconformance records (manufacturing, incoming, complaint, service)
* CAPA workflow with stage gates and approvals
* Root cause analysis tracking
* Effectiveness check enforcement
* Integration with recalls and audit trails
* QA and Regulatory approval routing
    """,
    'author': 'MedTech ERP Team',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['medtech_core', 'stock', 'mrp', 'mail'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data
        'data/sequences.xml',
        'data/pharma_locations.xml',
        # Views
        'views/nonconformance_views.xml',
        'views/capa_views.xml',
        'views/incoming_qc_views.xml',
        'views/weighing_dispensing_views.xml',
        'views/inprocess_qc_views.xml',
        'views/compounding_batch_views.xml',
        'views/sterilization_batch_views.xml',
        'views/filling_batch_views.xml',
        'views/packaging_batch_views.xml',
        'views/final_release_batch_views.xml',
        'views/full_workflow_wizard_views.xml',
        'views/workflow_dashboard_actions.xml',
        # Menus
        'views/quality_capa_menus.xml',
        # Dashboards
        'views/capa_dashboard_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'medtech_quality_capa/static/src/js/capa_dashboard.js',
            'medtech_quality_capa/static/src/xml/capa_dashboard.xml',
            'medtech_quality_capa/static/src/js/workflow_dashboard.js',
            'medtech_quality_capa/static/src/xml/workflow_dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
