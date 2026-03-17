# -*- coding: utf-8 -*-
{
    'name': 'Elevator Workflow',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'End-to-end Elevator Sales and Implementation workflow (views, data, minimal code)',
    'description': """
Elevator Sales and Implementation Workflow
===========================================
Configuration module for elevator sales: CRM stages, lead survey fields,
project/sale task linking, fleet on task, and final site measurements.

Uses only views, data, and minimal Python (field definitions). No business
logic; use Settings and Automated Actions for automation.
    """,
    'author': 'Edafa Tasks',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'sale_management',
        'project',
        'fleet',
        'stock',
        'mrp',
    ],
    'data': [
        'data/crm_stage_data.xml',
        'views/crm_lead_views.xml',
        'views/project_task_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
