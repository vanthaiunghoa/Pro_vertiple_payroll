# -*- coding:utf-8 -*-
from odoo import api, fields, models


class MonthlyTaxReport(models.AbstractModel):
    _name = 'report.report_xlsx.monthly_tax_report'

    def get_days(self, form, emp):
        """
        @returns: this method gives us the amounts from the salary rules by querying the database
        """
        salary_rules = self.env['hr.salary.rule'].browse(form['category_id'])

        amount = []
        for i in salary_rules:
            self.env.cr.execute("""
                            select sum(total)
                            from hr_payslip_line as pl
                            left join hr_payslip as p on pl.slip_id = p.id
                            where p.state = 'done' and p.employee_id = %s and pl.salary_rule_id = %s 
                            and p.date_from >= %s 
                            and p.date_from <= %s;""", (emp, i.id, form['start_date'], form['end_date'],)
                                )
            sal = self.env.cr.fetchall()
            if sal[0][0] is None:
                amount.append(0.0)
            else:
                amount.append(sal[0][0])
        total_amount = sum(amount)
        emp_id = self.env['hr.employee'].browse(emp)
        amount.insert(0, emp_id.name)
        amount.insert(0, emp_id.emp_id)
        amount.append(total_amount)
        return amount

    def get_total(self, form):
        """
        @returns: returns the total amount from all the salary rules by querying from the database
        """
        total = []
        salary_rules = self.env['hr.salary.rule'].browse(form['category_id'])
        for rule in salary_rules:
            sub_total = []
            for emp in form['employee_ids']:
                self.env.cr.execute("""
                        SELECT sum(total) FROM hr_payslip_line as pl
                        LEFT JOIN hr_payslip as p on pl.slip_id = p.id
                        WHERE p.state = 'done' and pl.salary_rule_id = %s and p.employee_id = %s
                        and p.date_from >= %s and p.date_from <= %s;
                        """, (rule.id, emp, form['start_date'], form['end_date']))
                temp_total = self.env.cr.fetchall()
                if temp_total[0][0] is None:
                    sub_total.append(0.0)
                else:
                    sub_total.append(temp_total[0][0])
            a = sum(sub_total)
            total.append(a)
        final_total = sum(total)
        total.append(final_total)
        total.insert(0, 'Total')
        total.insert(0, ' ')
        return total

    def get_list(self, form):
        """
        @returns: returns the list of column names that has to printed on the report
        """
        sal_obj = self.env['hr.salary.rule'].browse(form['category_id'])
        list_sal = []
        for i in sal_obj:
            list_sal.append(i.name)
        result = ['Employee Id'] + ['Employee'] + list_sal + ['Total']
        return result

    def get_employee(self, form):
        return self.env['hr.employee'].browse(form.get('employee', []))

    @api.model
    def render_html(self, docids, data=None):
        """
        default method of Odoo for rendering the qweb HTML content
        """
        register_ids = self.env.context.get('active_ids', [])
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': register_ids,
            'doc_model': 'model',
            'docs': docs,
            'data': data,
            'get_employee': self.get_employee,
            'get_days': self.get_days,
            'get_list': self.get_list,
            'get_total': self.get_total
        }
        return self.env['report'].render('report_xlsx.monthly_tax_report', docargs)
