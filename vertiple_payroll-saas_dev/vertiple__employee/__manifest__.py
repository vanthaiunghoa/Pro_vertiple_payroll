# -*- coding: utf-8 -*-
{
    'name': "Enthsquare | HRMS",

    'summary': """
        Vertiple | Human Resource Management System""",

    'description': """
        Human Resource Management System (Human Resources Process flow with no Enthsquare Payroll)
    """,

    'author': "Enthsquare Technologies",
    'website': "https://www.enthsquare.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'images' : ['static/description/src/img/sign.png'],
    'depends': ['base', 'document', 'hr', 'hr_attendance', 'hr_contract', 'hr_holidays', 'employee_service','enthsquare_payroll', 'vr_attendance_payroll'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_reports.xml',
        'views/templates.xml',
        'views/mail_templates.xml',
        'views/views.xml',
        'views/contract.xml',
        'wizard/hr_birthday_wizard.xml',
        'wizard/hr_anniversary_wizard.xml',
        'views/hr_birthday_views.xml',
        'views/hr_anniversary_views.xml',
        'views/server_actions.xml',
        'views/automated_actions.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
