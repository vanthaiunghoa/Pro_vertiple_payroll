# -*- coding:utf-8 -*-
from odoo import api, fields, models
from datetime import datetime


class MonthlyTaxes(models.TransientModel):
    _name = 'report_xlsx.monthly_tax'
    _description = 'Ad-hoc Details Report'

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    start_date = fields.Date(string='Start Date', required=True, default=datetime.now().strftime('%Y-%m-01'))
    end_date = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_rel', 'employee_id', string='Employees', required=True)
    category_id = fields.Many2many('hr.salary.rule', 'hr_salary_rule_rel', string='Salary Component', required=True)

    @api.multi
    def print_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        active_ids = self.env.context.get('active_ids', [])
        datas = {
            'ids': active_ids,
            'model': 'hr.employee',
            'form': self.read()[0]
        }
        print "datas:", datas
        return self.env['report'].get_action(self, 'report_xlsx.monthly_tax_report', data=datas)
