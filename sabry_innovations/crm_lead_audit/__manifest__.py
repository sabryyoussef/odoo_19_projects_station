# -*- coding: utf-8 -*-
{
    'name': 'CRM Lead Audit Automation',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Automated audit system for CRM leads with activity tracking',
    'description': """
CRM Lead Audit Automation
=========================

This module extends the CRM functionality to provide automated auditing 
of leads that remain in the "New" stage without scheduled activities.

Key Features:
-------------
* Adds audit tracking fields to CRM leads
* Tracks audit status and audit dates
* Integrates with external Python automation scripts
* Provides visibility to Sales Managers

Technical Details:
------------------
* Adds x_is_audited boolean field
* Adds x_last_audit_date datetime field
* Extends crm.lead form view
* Implements security rules for Sales Manager access

Use Case:
---------
Designed to work with external Python scripts (using erppeek) that:
1. Query leads older than 48 hours without activities
2. Create audit activities for responsible salespersons
3. Mark leads as audited

Author: Senior Odoo Technical Architect
Date: March 4, 2026
    """,
    'author': 'Sabry Innovations',
    'website': 'https://www.sabryinnovations.com',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
