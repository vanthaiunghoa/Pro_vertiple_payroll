# -*- coding: utf-8 -*-
{
    'name': "Vertiple | Attendance-Payroll",

    'summary': """
        Integration of Attendances with Payroll""",

    'description': """
        Integration of Attendances with Payroll
    """,

    'author': "Vertiple",
    'website': "http://www.vertiple.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'enthsquare_payroll', 'hr_attendance', 'hr_public_holidays', 'email_remainder', 'vertiple__employee'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/holidays_compensatory.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
