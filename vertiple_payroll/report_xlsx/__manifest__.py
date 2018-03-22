{
    'name': "Base report xlsx",

    'summary': """
        Base module to create xlsx report""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Reporting',
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'external_dependencies': {'python': ['xlsxwriter']},
    'depends': [
        'base', 'hr_payroll', 'l10n_in_hr_payroll'
    ],
    'data': [
        'views/views.xml',
        'views/report_hryearlysalary.xml',
        'wizards/monthlytax_wizard_view.xml',
        'views/monthlytax_template.xml'
    ],
    'installable': True,
}
