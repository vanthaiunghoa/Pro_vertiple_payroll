# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, tools, _
from num2words import num2words
from datetime import datetime, timedelta
import babel, calendar
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class enthsquare_payroll(models.Model):
    _inherit='hr.payslip'

    lwp = fields.Integer(compute='get_lwp')
    leaves = fields.Integer(compute='get_leaves')
    days_per_month = fields.Char(compute='get_number_of_days')
    days_in_given_month = fields.Integer(compute='get_number_of_days')
    employee_name = fields.Char(string='Employee',compute='_get_employee_name')
    name = fields.Char(string='Payslip Name', readonly=True, states={'draft': [('readonly', False)]})
    bank = fields.Char('Bank', compute='get_bank',readonly=True)
    acc_number = fields.Char('Account number', compute='get_acc_number',readonly=True)

    def get_total_deductions(self):
        """
        @return: gives the total amount of all the deductions
        """
        total = 0
        for i in self.line_ids:
            if i.category_id.code == 'DED':
                total += i.total
        return total
    
    @api.one
    def get_bank(self):
       self.bank = self.sudo().employee_id.bank_account_id.bank_id.name

    @api.one
    def get_acc_number(self):
       self.acc_number = self.sudo().employee_id.bank_account_id.acc_number

    @api.multi
    def _get_employee_name(self):
       self.employee_name = self.employee_id.name

    @api.depends('date_from','date_to')
    def get_number_of_days(self):
        self.days_per_month = int((datetime.strptime(self.date_to, "%Y-%m-%d") - datetime.strptime(self.date_from, "%Y-%m-%d")).days)+1
        temp = datetime.strptime(self.date_from, "%Y-%m-%d")
        self.days_in_given_month = calendar.monthrange(temp.year, temp.month)[1]
        
    @api.one
    def get_lwp(self):
        self.lwp = '0'
        for i in self.worked_days_line_ids:            
            if i.code == "Unpaid":
                self.lwp = i.number_of_days

    @api.one
    def get_leaves(self):
        self.leaves = '0'
        for i in self.worked_days_line_ids:            
            if i.code.find('Legal Leaves') == 0:
                self.leaves = i.number_of_days

    @api.multi
    def numtowords(self, amt):
        r = num2words(float(amt), lang='en_IN')
        return r.title()

    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        #defaults
        res = {
            'value': {
                'line_ids': [],
                #delete old input lines
                'input_line_ids': map(lambda x: (2, x,), self.input_line_ids.ids),
                #delete old worked days lines
                'worked_days_line_ids': map(lambda x: (2, x,), self.worked_days_line_ids.ids),
                #'details_by_salary_head':[], TODO put me back
                'name': '',
                'contract_id': False,
                'struct_id': False,
            }
        }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee = self.env['hr.employee'].browse(employee_id)
        locale = self.env.context.get('lang', 'en_US')
        res['value'].update({
            'name': _('Pay Slip for %s') % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
            'company_id': employee.company_id.id,
        })

        if not self.env.context.get('contract'):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employee, date_from, date_to)

        if not contract_ids:
            return res
        contract = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update({
            'contract_id': contract.id
        })
        struct = contract.struct_id
        if not struct:
            return res
        res['value'].update({
            'struct_id': struct.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to)
        input_line_ids = self.get_inputs(contract_ids, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang', 'en_US')
        self.name = _('Pay Slip for %s') % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines

        input_line_ids = self.get_inputs(contract_ids, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines
        return

class EmployeeDetails(models.Model):
    _inherit = 'hr.employee'
 
    emp_id = fields.Char(string='Employee ID')
    first_name = fields.Char("First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char("Last Name")
    pf_acc_number = fields.Char('PF Account Number')
    pan_number = fields.Char('PAN Number')
    check_field = fields.Char('check field')
 
    @api.onchange('last_name','first_name')
    def concantenation_of_names(self):
        """Funtionality of Concantenation of First Name & Last Name"""
        for rec in self:
            if (rec.last_name and rec.first_name and rec.middle_name) and rec.name == False:
                rec.name= str(self.first_name) + " " + str(self.middle_name) + " " + str(self.last_name)


class HrPayslipAdvice(models.Model):
    _inherit = 'hr.payroll.advice'
    
    @api.multi
    def compute_advice(self):
        """
       Advice - Create Advice lines in Payment Advice and
       compute Advice lines.
       """
        for advice in self:
            old_lines = self.env['hr.payroll.advice.line'].search([('advice_id', '=', advice.id)])
            if old_lines:
                old_lines.unlink()
            payslips = self.env['hr.payslip'].search([('date_from', '<=', advice.date), ('date_to', '>=', advice.date), ('state', '=', 'done')])
            for slip in payslips:
                if not slip.sudo().employee_id.bank_account_id and not slip.sudo().employee_id.bank_account_id.acc_number:
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name,))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.sudo().employee_id.bank_account_id.acc_number,
                        'ifsc_code': slip.sudo().employee_id.bank_account_id.bank_bic or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
                slip.advice_id = advice.id


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    # for multi-company record rule (Payslip Batches and Payment Advice)
    company_id = fields.Many2one('res.company', string='Company',copy=False, default=lambda self: self.env['res.company']._company_default_get())
    
    @api.multi
    def create_advice(self):
        for run in self:
            if run.available_advice:
                raise UserError(_("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") % (run.name,))
            company = self.env.user.company_id
            advice = self.env['hr.payroll.advice'].create({
                        'batch_id': run.id,
                        'company_id': company.id,
                        'name': run.name,
                        'date': run.date_end,
                        'bank_id': company.id or False
                    })
            for slip in run.slip_ids:
                # TODO is it necessary to interleave the calls ?
                slip.action_payslip_done()
                if not slip.sudo().employee_id.bank_account_id or not slip.sudo().employee_id.bank_account_id.acc_number:
                    raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name))
                payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if payslip_line:
                    self.env['hr.payroll.advice.line'].create({
                        'advice_id': advice.id,
                        'name': slip.sudo().employee_id.bank_account_id.acc_number,
                        'ifsc_code': slip.sudo().employee_id.bank_account_id.bank_id.bic or '',
                        'employee_id': slip.employee_id.id,
                        'bysal': payslip_line.total
                    })
        self.write({'available_advice': True})


class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic = fields.Float(string='Basic (%)', digits=dp.get_precision('Payroll'),
        help='This calculates the Basic. \nBasic computed as percentage(%)')
