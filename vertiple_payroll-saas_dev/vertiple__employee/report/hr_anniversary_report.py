#-*- coding:utf-8 -*-

from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class AnniversaryReport(models.AbstractModel):
    """
    This abstract model helps in defining the report for Anniversary Details of Employees
    """
    _name = 'report.vertiple__employee.report_anniversary'

    def _get_payslip_lines(self, register_ids, date_from, date_to):
        result = {}
        days =[]
        obj = self.env['hr.contract'].search([])
        from_date = datetime.strptime(date_from , '%Y-%m-%d')
        to_date = datetime.strptime(date_to , '%Y-%m-%d')

        diff = to_date - from_date 
        
        for i in range(diff.days + 1):
            new = from_date + timedelta(days=i)
            day = datetime.strftime(new,'%m-%d')
            days.append(day)

        i=0
        for rec in obj:
            startdate =datetime.strptime(rec.date_start,'%Y-%m-%d')
            start = datetime.strftime(startdate,'%Y-%m-%d')
            date_now = datetime.today()
            rd = relativedelta(date_now,startdate)
            difference= "{0.years} year(s) , {0.months} month(s) and {0.days} day(s)".format(rd)
            joinday = datetime.strftime(startdate,'%m-%d')

            if joinday in days:
                result[i] = [rec.employee_id.employee_id,rec.employee_id.name,datetime.strptime(rec.date_start,"%Y-%m-%d").strftime("%d-%m-%Y"),difference]
                i+=1
        return result

    @api.model
    def render_html(self, docids, data=None):
        """
        default method for rendering the qweb html content in Odoo
        """
        register_ids = self.env.context.get('active_ids', [])
        contrib_registers = self.env['hr.employee'].browse(register_ids)
        date_from = data['form'].get('date_from')
        date_to = data['form'].get('date_to')
        lines_data = self._get_payslip_lines(register_ids, date_from, date_to)
        
        docargs = {
            'doc_ids': register_ids,
            'doc_model': 'hr.employee',
            'docs': contrib_registers,
            'data': data,
            'lines_data': lines_data,
        }
        return self.env['report'].render('vertiple__employee.report_anniversary', docargs)
