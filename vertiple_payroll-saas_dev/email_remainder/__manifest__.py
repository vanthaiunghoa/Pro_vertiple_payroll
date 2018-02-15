# -*- coding: utf-8 -*-
{
    'name': "Vertiple | Auto Email Reminder",

    'summary': """
        Lets you configure the auto email remainder in the company requesting client for the data to process the payroll""",

    'description': """
        
    """,

    'author': "Enthsquare Technologies India Pvt. Ltd",
    'website': "http://www.enthsquare.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
