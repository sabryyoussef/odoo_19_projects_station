# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Document Prints',
    'version': '19.0.1.0.0',
    'summary': 'Printable HR employee documents with an extensible report scaffold.',
    'description': """
Phase 1 delivers Work Commencement Notice as a QWeb PDF report.
The module is structured to support additional HR document templates later.
    """,
    'category': 'Human Resources',
    'author': 'Edafa',
    'license': 'LGPL-3',
    'depends': ['hr'],
    'data': [
        'reports/hr_employee_documents_report.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'test': [
        'tests/test_hr_employee_document_prints.py',
    ],
}
