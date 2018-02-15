
{
    'name': 'Vertiple | Branding',
    'version': '10.0.1.0',
    'author': 'Enthsquare Technologies',
    'category': 'Productivity',
    'website': 'http://www.enthsquare.com',
    'sequence': 2,
    'summary': 'Bebranding Vertiple. Powered by SOG, No bindings, Title & favicon change.',
    'description': """

Vertiple | Branding
============
1.Adds Powered by System On Grid label in footer
2.Adds Vertiple in Window Title
3.Removes Documentation, Support, Online account
    """,
    
    'depends': ['web','base','mail'],
    'data': [
        'views/app_odoo_customize_view.xml',
        'views/app_theme_config_settings_view.xml',
        'views/ir_ui_menu.xml',
        # data
        'data/ir_config_parameter.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
        'static/src/xml/customize_user_menu.xml',
    ],
}

