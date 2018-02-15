from odoo import models, fields, api


class contract(models.Model):
    _inherit = 'hr.contract'
    
    @api.multi
    def send_system_appointment_mail(self):
        """Find the e-mail template and sends that template"""
        template = self.env.ref('vertiple__employee.appointment_letter_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
