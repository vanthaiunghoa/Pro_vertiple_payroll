from odoo import models, fields, api, exceptions, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError

import datetime, random, re


class BaseActionRule(models.Model):
    """
    fix: We are overriding the base action rule in order to fix the _check action rule issue
    """
    _inherit = 'base.action.rule'


    @api.model
    def _check(self, automatic=False, use_new_cursor=False):
        """ This Function is called by scheduler. """

        if '__action_done' not in self._context:
            self = self.with_context(__action_done={})

        # retrieve all the action rules to run based on a timed condition
        eval_context = self._get_eval_context()
        for action in self.with_context(active_test=True).search([('kind', '=', 'on_time')]):
            last_run = fields.Datetime.from_string(action.last_run) or datetime.datetime.utcfromtimestamp(0)

            # retrieve all the records that satisfy the action's condition
            domain = []
            context = dict(self._context)
            if action.filter_domain:
                domain = safe_eval(action.filter_domain, eval_context)
            elif action.filter_id:
                domain = safe_eval(action.filter_id.domain, eval_context)
                context.update(safe_eval(action.filter_id.context))
                if 'lang' not in context:
                    # Filters might be language-sensitive, attempt to reuse creator lang
                    # as we are usually running this as super-user in background
                    filter_meta = action.filter_id.get_metadata()[0]
                    user_id = (filter_meta['write_uid'] or filter_meta['create_uid'])[0]
                    context['lang'] = self.env['res.users'].browse(user_id).lang
            records = self.env[action.model].with_context(context).search(domain)

            # determine when action should occur for the records
            if action.trg_date_id.name == 'date_action_last' and 'create_date' in records._fields:
                get_record_dt = lambda record: record[action.trg_date_id.name] or record.create_date
            else:
                get_record_dt = lambda record: record[action.trg_date_id.name]

            # process action on the records that should be executed
            now = datetime.datetime.now()
            for record in records:
                record_dt = get_record_dt(record)
                if not record_dt:
                    continue
                action_dt = self._check_delay(action, record, record_dt)
                if action_dt <= now: 
                    try:
                        action._process(record)
                    except Exception:
                        _logger.error(traceback.format_exc())

            action.write({'last_run': fields.Datetime.now()})

            if automatic:
                # auto-commit for batch processing
                self._cr.commit()


class VertipleEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_id = fields.Char(string='Employee ID')
    family = fields.One2many("vertiple__employee.family_rel",'rel_id')
    blood_group = fields.Many2one('vertiple__employee.blood_group', string='Blood Group')
    contact_number = fields.Char('Contact Number')
    emergency_contact = fields.Char('Emergency Contact')
    birthday_as_per_cert = fields.Date('Date of Birth (as per certificate)')
    esic_num = fields.Char('ESIC Number')
    manager_status = fields.Char('Manager Status', readonly=True)
    manager_feedback = fields.Selection([
        ('good', 'GOOD'),
        ('avg','AVERAGE'),
        ('poor','POOR'),
        ], string='Feedback', default=False)
    hr_status = fields.Char('HR Status', readonly=True)
    hr_feedback = fields.Selection([
         ('good', 'GOOD'),
        ('avg','AVERAGE'),
        ('poor','POOR'),
        ], string='Feedback', default=False)
    probation_date_end = fields.Date('Probation Date End')
    state = fields.Selection([
        ('probation', 'PROBATION'),
        ('manager_review','MANAGER REVIEW'),
        ('hr_review','HR REVIEW'),
        ('confirmed', 'CONFIRMED'),
        ('notice', 'NOTICE / RESIGN'),
        ('exit','EXIT'),
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='probation',)
    check_field = fields.Boolean(string="Check", compute='get_user')
    working_address = fields.Char('Working Address', compute='get_working',readonly=True)
    new_check_state = fields.Boolean(string="state check", compute='check_state',default=True)
    check_page = fields.Boolean(string="Personal Page Check", compute='check_page_def',default=True)

    @api.one
    def check_page_def(self):
        """
        we are writing this for giving appropriate permissions for the personal information tab
        in the employee directory.
        on top of this we are also specifying the attrs in xml view for the same field.
        """
        if not self.env.user.has_group('base.group_system') and not self.env.user.has_group('hr.group_hr_manager') and not self.env.user.has_group('hr.group_hr_user'):
            if self.user_id.id == self._uid:
                self.check_page = True
            else:
                self.check_page = False
        else:
            self.check_page = True

    @api.one
    def check_state(self):
        """
        check state field is used for giving the appropriate permissions to an employee to view
        the employee state status bar in the employee directory. With the Employee can only we 
        his/her status bar and in what state of employement is in.
        """
        if not self.env.user.has_group('base.group_system') and not self.env.user.has_group('hr.group_hr_manager'):
            if self.user_id.id == self._uid:
                self.new_check_state = True
            else:
                self.new_check_state = False
        else:
            self.new_check_state = True

    @api.constrains('identification_id','pf_acc_number','esic_num')
    def validate_id_pf_esic(self):
        """
        validations for fields identification_id, PF account number & ESI number
        """
        if self.identification_id:
            if len(self.identification_id) > 16:
                raise ValidationError("Aadhar Number should not exceed 16 digits")
            if self.identification_id.isdigit() == False:
                raise ValidationError("Aadhar Number should not contain AlphaNumeric string")
        if self.pf_acc_number:
            if len(self.pf_acc_number) > 26:
                raise ValidationError("PF Number should not exceed 26 digits")
        if self.esic_num:
            if len(self.esic_num) > 10:
                raise ValidationError("ESIC Number should not exceed 10 digits")
    
    @api.constrains('pan_number')
    def validate_pan_number(self):
        """
        pan number field validation
        """
        if self.pan_number:
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', self.pan_number):
                raise ValidationError('PAN number is not valid ')

    @api.constrains('family')
    def validate_emergency(self):
        """
        this method allows user to tell that out of many family contacts there can only be one 
        emergency contact. If it is more that one then user will be prompted with an error.
        """
        l=[]
        for i in self.family:
            if not i.rel_emergency in l:
                l.append(i.rel_emergency)
            else:
                raise ValidationError("Check Emergency contact for only one person")

    @api.one
    def get_working(self):
		self.working_address = str(self.address_id.name)+",\n"+str(self.address_id.street)+","+str(self.address_id.city)+",\n"+str(self.address_id.zip)+","+str(self.address_id.state_id.name)+",\n"+str(self.address_id.country_id.name)

    @api.one
    def get_user(self):
        """
        get user method get the current user and allows the current user to click the resign
        button of his own and not anyone else
        """
        if self.user_id.id == self._uid:
            self.check_field = True
        else:
            self.check_field = False

    @api.multi
    def status_approve_manager(self):
        """Manager's Employee Approval Status"""
        self.write({'manager_status':'Approved'})
        return self.write({'state': 'hr_review'})

    @api.multi
    def status_refuse_manager(self):
        """Manager's Employee Refusal Status"""
        self.write({'manager_status':'Refused'})
        return self.write({'state': 'hr_review'})

    @api.multi
    def status_approve_hr(self):
        """HR's Employee Approval Status"""
        self.write({'hr_status': 'Approved'})
        return self.write({'state': 'confirmed'})

    @api.multi
    def status_refuse_hr(self):
        """HR's Employee Refusal Status"""
        self.write({'hr_status': 'Refused'})
        return self.write({'state': 'notice'})

    @api.multi
    def manager_approve(self):
        """Set's the manager's status to Approve & sends email notificaiton"""
        self.status_approve_manager()
        template = self.env.ref('vertiple__employee.manager_review_to_hr')
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def manager_refuse(self):
        """Set's the manager's status to Refuse & sends email notificaiton"""
        self.status_refuse_manager()
        template = self.env.ref('vertiple__employee.manager_review_to_hr')
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def hr_approve(self):
        """Set's the hr's status to Approve & sends email notificaiton"""
        if not self.state=='notice' and not self.state == 'exit' and not self.state == 'manager_review':
            self.status_approve_hr()
            template = self.env.ref('vertiple__employee.hr_review_to_emp')
            self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def hr_refuse(self):
        """Set's the hr's status to Refuse & sends email notificaiton"""
        if not self.state == 'notice' and not self.state == 'exit' and not self.state == 'manager_review':
            self.status_refuse_hr()
            template = self.env.ref('vertiple__employee.hr_review_to_emp')
            self.env['mail.template'].browse(template.id).send_mail(self.id)
        else:
            raise ValidationError("You are already in  %s" % self.state)

    # Workflow Setting Methods
    # These methods allows one to travel from one Employee state to another  

    @api.multi
    def set_to_probation(self):
        self.write({'state': 'probation'})

    @api.multi
    def set_to_manager_review(self):
        self.write({'state': 'manager_review'})

    @api.multi
    def action_hr_review(self):
        self.write({'state': 'hr_review'})

    @api.multi
    def set_to_confirm(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def set_to_notice(self):
        self.write({'state': 'notice'})

    @api.multi
    def set_to_exit(self):
        self.write({'state': 'exit'})

    @api.multi
    def emp_resign(self):
        """Send's email and changes state to notice"""
        if not self.state == 'notice':
            self.sudo().set_to_notice()
            template = self.env.ref('vertiple__employee.request_resign_template')
            self.env['mail.template'].browse(template.id).send_mail(self.id)
        else:
            raise ValidationError("Your are already in  %s" % self.state)

    @api.onchange('last_name', 'middle_name', 'first_name')
    def concatenation_of_names(self):
        for rec in self:
            if (rec.last_name and rec.first_name and rec.middle_name) and rec.name == False:
                rec.name = str(self.first_name) + " " + str(self.middle_name) + " " + str(self.last_name)

    @api.multi
    def send_system_setup_mail(self):
        """Find the e-mail template and sends that template"""
        template = self.env.ref('vertiple__employee.system_setup_mail_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)


class BloodGroup(models.Model):
    _name = 'vertiple__employee.blood_group'
    
    name = fields.Char(string="Blood Group", required=True)


class FamilyRel(models.Model):
    """
    model fields for holding the family emergency contacts
    """
    _name = 'vertiple__employee.family_rel'
    
    name = fields.Char(string="Name", required=True,)
    rel_type = fields.Selection([
       ('1', 'Father'),
       ('2','Mother'),
       ('3','Wife'),
       ('4','Brother'),
       ('5','Cousin'),
       ], string='Relation', default=False)
    rel_contact_num=fields.Char("Contact Number")
    rel_emergency = fields.Boolean("Emergency contact")
    rel_id = fields.Many2one('hr.employee') 
