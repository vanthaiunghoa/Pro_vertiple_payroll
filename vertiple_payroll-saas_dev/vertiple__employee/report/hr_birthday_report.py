#-*- coding:utf-8 -*-

from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class bdayreport(models.AbstractModel):
    """
    This abstract model helps in defining the report for Birthday Details of Employees
    """
    _name = 'report.vertiple__employee.report_birthday'

    def _get_payslip_lines(self, register_ids, date_from, date_to):
        result = {}
        days =[]
        obj = self.env['hr.employee'].search([])
        from_date = datetime.strptime(date_from , '%d-%m-%Y')
        to_date = datetime.strptime(date_to , '%Y-%m-%d')

        diff = to_date - from_date 
        
        for i in range(diff.days + 1):
            new = from_date + timedelta(days=i)
            day = datetime.strftime(new,'%m-%d')
            days.append(day)

        i=0
        for rec in obj:
            birthdate =datetime.strptime(rec.birthday,'%Y-%m-%d')
            birthday = datetime.strftime(birthdate,'%m-%d')
            if birthday in days:
                result[i] = [rec.employee_id,rec.name,datetime.strptime(rec.birthday,"%Y-%m-%d").strftime("%d-%m-%Y"),]
                i+=1
        return result

    @api.model
    def render_html(self, docids, data=None):
        """
        default method for rendering the qweb html content in Odoo
        """
        register_ids = self.env.context.get('active_ids', [])
        contrib_registers = self.env['hr.employee'].browse(register_ids)
        new = data['form'].get('date_from')
        date_from = datetime.strptime(new,"%Y-%m-%d").strftime("%d-%m-%Y")
        date_to = data['form'].get('date_to')
        lines_data = self._get_payslip_lines(register_ids, date_from, date_to)
        docargs = {
            'doc_ids': register_ids,
            'doc_model': 'hr.employee',
            'docs': contrib_registers,
            'data': data,
            'lines_data': lines_data,
        }
        return self.env['report'].render('vertiple__employee.report_birthday', docargs)
