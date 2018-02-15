# -*- coding: utf-8 -*-
{
    'name': 'Employee Checklist',
    'version': '10.0.1.0.0',
    'summary': """Manages Employee's Entry & Exit Process""",
    'description': """This module is used to remembering the employee's entry and exit progress.""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Enthsquare Technologies',
    'company': 'Enthsquare Technologies',
    'website': "https://www.enthsquare.com",
    'depends': ['base', 'employee_documents_expiry'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_form_inherit_view.xml',
        'views/checklist_view.xml',
        'views/settings_view.xml',
    ],
    'demo': [],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
