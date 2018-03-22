# -*- coding: utf-8 -*-
{
    'name': "Vertiple | Payroll",
    'summary': """
        Payroll Outsourcing Made Easy!""",
    'description': """
        Vertiple processes monthly salary,  Employee self-service, Statutory Compliance, Reports made hassel-free
    """,
    'author': "Enthsquare Technologies",
    'website': "http://www.enthsquare.com",
    'sequence': 1,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','l10n_in_hr_payroll', 'app_odoo_customize' , 'document', 'havelock_backend_theme', 'report_xlsx', 'hr', 'hr_attendance'],
    
    # always loaded
    'data': [
        'data/dept_data.xml',
        'data/hr_payroll_rules.xml',
        'data/l10n_in_hr_payroll_rules.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/payslip_report.xml',
        'views/payslip_report_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
