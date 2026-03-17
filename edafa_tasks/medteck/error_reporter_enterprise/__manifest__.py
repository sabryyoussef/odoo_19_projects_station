{
    'name': 'Error Reporter Enterprise',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Professional error reporting and tracking system for Odoo',
    'description': """
Error Reporter Module for Odoo 19
==================================
Allows testers to easily report errors during Odoo 19 upgrade testing.

Features:
---------
* Quick report button in systray
* Simple form for error details
* Screenshot/attachment upload
* Auto-capture user, date, current menu
* Status tracking (New/In Progress/Fixed)
* Export to documentation
* Watch the full video demo: https://youtu.be/wXnRhGiVZF4

Perfect for QA testing and bug tracking!
    """,
    'author': 'Sabry Youssef',
    'website': 'https://edu-sabry.odoo.com/error-reporter-enterprise',
    'license': 'LGPL-3',
    'price': 500.00,
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/wXnRhGiVZF4',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/error_report_views.xml',
        'views/error_report_menu.xml',
        'data/khaled_oct27_errors.xml',
        'data/ian_oct27_errors.xml',
        'data/ian_oct28_errors.xml',
        'data/khaled_oct28_errors.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'error_reporter_enterprise/static/src/js/systray_error_button.js',
            'error_reporter_enterprise/static/src/xml/systray_error_button.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

