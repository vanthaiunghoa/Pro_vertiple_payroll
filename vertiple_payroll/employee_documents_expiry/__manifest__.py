# -*- coding: utf-8 -*-
{
    'name': 'Employee Documents',
    'version': '10.0.2.1',
    'summary': """Manages Employee Documents With Expiry Notifications.""",
    'description': """Manages Employee Related Documents with Expiry Notifications.""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Enthsquare Technologies',
    'company': 'Enthsquare Technologies',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_check_list_view.xml',
        'views/employee_document_view.xml',
    ],
    'demo': ['data/data.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
