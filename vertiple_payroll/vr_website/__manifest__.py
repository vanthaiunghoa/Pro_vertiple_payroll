# -*- coding: utf-8 -*- 
{
    'name': "Vertiple | Website",

    'summary': """
        Customised Website module on top of Official Website""",

    'description': """
        Logo & Favion for Vertiple
    """,

    'author': "Enthsquare Technologies",
    'website': "http://www.enthsquare.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website'],

    'images': [
            'static/src/img/vertiple.png',
            'static/src/img/vertiple.ico',],

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