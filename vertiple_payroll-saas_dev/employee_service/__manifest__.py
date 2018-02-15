# -*- coding: utf-8 -*-
{
    'name': "Vertiple | Employee Services",

    'summary': """
        Employee Services helps Employees to request for the Services.""",

    'description': """
        Employees Can request for the proofs: 1. Address Proof Request 2. Employement Proof Request etc.
    """,

    'author': "Enthsquare Technologies",
    'website': "http://www.enthsquare.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mail'],

    # always loaded
    'data': [
        'security/employee_service_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/mail_template.xml',
        'data/data.xml',
        'views/server_automated_actions.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
