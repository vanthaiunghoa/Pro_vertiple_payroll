# -*- coding: utf-8 -*-
from odoo import models, fields, api
from calendar import monthrange
import datetime



class EmailRemainder(models.Model):
    _inherit = 'res.company'

    email_remainder = fields.Boolean(string='Enable/Disable Email Reminder')
    pay_day = fields.Char(string='Salary Pay Day', help='The day of the month where the salary is usually paid on')
    recipient_email = fields.Char(string='Email Id', help='Recipient email Id to send the email reminder')
    first_remainder = fields.Char(string=' day(s)', help='The number of day(s) before the Salary Pay Day. Eg: 5 day(s)')
    second_remainder = fields.Char(string=' day(s)', help='The number of day(s) before the Salary Pay Day. Eg: 5 day(s)')
    third_remainder = fields.Char(string=' day(s)', help='The number of day(s) before the Salary Pay Day. Eg: 5 day(s)')
    feature = fields.Boolean(string='Enable/Disable Saas Feature', default=True)


    def remainder(self):
        """
        method that handles the automatic email reminders for client requesting the data.
        """
        if self.feature == True:
            today = datetime.date.today()
            if today.month - 1 == 0:
                month = 12
            else:
                month = today.month
            temp = monthrange(today.year, month)[1]
            companies = self.env['res.company'].search([])
            for comp in companies:
                if comp.email_remainder:
                    rem1 = int(comp.pay_day) - int(comp.first_remainder)
                    if rem1 < 0:
                        if temp + rem1 == today.day:
                            template = self.env.ref('email_remainder.first_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    elif rem1 == 0:
                        if today.day == 1:
                            template = self.env.ref('email_remainder.first_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    elif rem1 > 0:
                        if rem1 == today.day:
                            template = self.env.ref('email_remainder.first_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    rem2 = int(comp.pay_day) - int(comp.second_remainder)
                    if rem2 < 0:
                        if temp + rem2 == today.day:
                            template = self.env.ref('email_remainder.second_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    elif rem2 == 0:
                        if today.day == 1:
                            template = self.env.ref('email_remainder.second_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    elif rem2 > 0:
                        if rem2 == today.day:
                            template = self.env.ref('email_remainder.second_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    rem3 = int(comp.pay_day) - int(comp.third_remainder)
                    if rem3 < 0:
                        if temp + rem3 == today.day:
                            template = self.env.ref('email_remainder.third_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    elif rem3 == 0:
                        if today.day == 1:
                            template = self.env.ref('email_remainder.third_email_remainder_template')
                            template.with_context().send_mail(comp.id)
                    elif rem3 > 0:
                        if rem3 == today.day:
                            template = self.env.ref('email_remainder.third_email_remainder_template')
                            template.with_context().send_mail(comp.id)
