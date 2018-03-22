# -*- coding: utf-8 -*-
from odoo import models, fields, api

import datetime
from odoo.exceptions import ValidationError

class EmployeeServices(models.Model):
    """
    Employee Services will enable employee to post a service request(Address Proof etc) to HR Manager
    """
    _name="employee_service.employee_service"

    name = fields.Char(string='Service Request ID',readonly=True,)
    emp_id = fields.Many2one("hr.employee",readonly=True,string="Employee Name")
    service = fields.Many2one('employee_service.employee_request_type',string="Request type",required=True)
    created_date = fields.Date('Created On',readonly=True)
    close_date = fields.Date('Closed On',readonly=True)
    status =fields.Selection([
        ('open', 'Open'),
        ('close', 'Closed')
    ], string='Status', track_visibility='always', default= 'open',copy=False,)
    description = fields.Text(string ='Description')
    documents =fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Documents')
    user_id = fields.Many2one('res.users', string='User', related='emp_id.user_id', related_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    email = fields.Char('Email')
    emp_name = fields.Char('Name')

    def action_close(self):
        """
        this method allows one to change from one state to another
        """
        if not self.status =='close':
            self.write({'status':'close'})
            self.write({'close_date':datetime.date.today()})

    @api.model
    def create(self, vals):
        if not self.status =='close':
            vals['created_date'] = datetime.date.today()
            vals['name'] = self.env['ir.sequence'].next_by_code('service.code')
            resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)]) 
            employee = self.env['hr.employee'].search([('resource_id','=',resource.id)])
            vals['emp_id'] = employee.id
            vals['emp_name'] = employee.name
            vals['email'] = employee.work_email
            return super(EmployeeServices, self).create(vals)
        else:
            raise ValidationError("Your are already in  %s" % self.status)

    @api.multi
    def unlink(self):
        if self.status == 'close':
            raise ValidationError("You cannot delete a service which is in closed state")
        return super(EmployeeServices, self).unlink()


class EmployeeServiceType(models.Model):
    _name="employee_service.employee_request_type"

    name=fields.Char("Request Type")
