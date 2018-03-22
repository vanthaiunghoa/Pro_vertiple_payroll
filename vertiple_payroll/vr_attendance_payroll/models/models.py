# [ADD] upto leaves except non-working-days
import time
from datetime import datetime, timedelta
import babel
import calendar
import math

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    """
    Contract Model Inherit
    """
    _inherit = 'hr.contract'

    holiday_calendar = fields.Many2one('hr.holidays.public', string='Holiday Calendar')

    def _compute_worked_days(self, holiday_calendar_id, date_from, date_to):
        """
        @returns: the length(number of days) of the list which has the days that are worked
                  by taking the days between the specified date range.

        """
        empty_list = []

        df = datetime.strptime(str(date_from).split(" ")[0], '%Y-%m-%d').date()
        dt = datetime.strptime(str(date_to).split(" ")[0], '%Y-%m-%d').date()

        for rec in holiday_calendar_id.line_ids:
            rec_date = datetime.strptime((rec.date).split(" ")[0], '%Y-%m-%d').date()
            if df <= rec_date and rec_date <= dt:
                empty_list.append(rec_date)

        return len(empty_list)


class HrAttendance(models.Model):
    """
    Hr Attendance Model Inherit
    """
    _inherit = 'hr.attendance'

    date_check_in = fields.Date(string="date of checkin")
    test_field = fields.Char(compute='_check_in_date')

    def _check_in_date(self):
        checkin = datetime.strptime(self.check_in, '%Y-%m-%d %H:%M:%S')
        self.write({'date_check_in': checkin.date()})

    def _compute_worked_days(self, employee_id, date_from, date_to):
        """
        @returns: Checks the condition from the payroll engine feature specified at the company
                  level, validates and sends the flow to the super method to process payroll the
                  the default way(Odoo standard feature).

                  Else returns the number of calculated days categorized with respect to new payroll
                  engine
        """
        em = self.env['hr.employee'].browse(employee_id)
        rc = self.env['res.company'].search([('id', '=', em.company_id.id)])
        if not rc.feature:
            l = []
            df = datetime.strptime(str(date_from).split(" ")[0], '%Y-%m-%d').date()
            dt = datetime.strptime(str(date_to).split(" ")[0], '%Y-%m-%d').date()

            work = self.env['hr.contract'].search([('employee_id', '=', employee_id)])

            # Day of the week are represented by the numbers starting from sunday
            a = [0, 1, 2, 3, 4, 5, 6]
            b = []

            for i in work:
                for j in i.working_hours.attendance_ids:
                    b.append(int(j.dayofweek))

            # Checks whether the given day falls out of the the 'b'(where there are no attendances) 
            nwd_from_shift = [elem for elem in a if elem not in b]

            # list to hold public holidays
            pub_hol = []

            # list to hold leaves from attendances
            leaves_attn = []

            pub_hol_temp = self.env['hr.holidays.public.line'].search([])
            hol_temp = self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to),
            ])

            for rec in hol_temp:
                k = datetime.strptime(rec.date_from, '%Y-%m-%d %H:%M:%S')
                leaves_attn.append(datetime.strftime(k, '%Y-%m-%d'))

            for rec in pub_hol_temp:
                pub_hol.append(rec.date)

            extended_list = pub_hol + leaves_attn

            for record in self:
                check_date = datetime.strptime(str(record.check_in.split(" ")[0]), '%Y-%m-%d').date()
                if record.employee_id.id == employee_id:
                    if df <= check_date <= dt:
                        k = datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')
                        new = datetime.strftime(k, '%Y-%m-%d')
                        if new not in extended_list and k.weekday() not in nwd_from_shift:
                            l.append(new)
            m = set(l)
            n = list(m)
            res = len(n) - self.compute_unpaid_attendances(date_from, employee_id)
            return res
        else:
            super(HrAttendance, self)._compute_worked_days(employee_id, date_from, date_to)

    def compute_unpaid_attendances(self, date_from, employee_id):
        """
        @returns: the number of days from that falls under unpaid category
        """
        holiday = self.env['hr.holidays.public.line'].search([])
        holiday_list = []
        current_date = datetime.strptime(date_from, "%Y-%m-%d")
        no_of_leaves_from_attendance = 0

        for rec in holiday:
            new_date = datetime.strptime(rec.date, "%Y-%m-%d")
            if new_date.month == current_date.month:
                holiday_list.append(rec.date)

        obj = self.env['hr.attendance'].search([('employee_id', '=', employee_id)])

        d = {}
        for record in obj:
            s = datetime.strptime(str(record.check_in).split(" ")[0], '%Y-%m-%d').date()
            if not s in holiday_list:
                if s in d:
                    d[s] += record.worked_hours
                else:
                    d[s] = record.worked_hours

        for key, value in d.items():
            if value < obj[0].employee_id.calendar_id.min_work_hours:
                no_of_leaves_from_attendance += 0.5
        return no_of_leaves_from_attendance

    def _compute_total_worked_hours(self, employee_id, date_from, date_to):
        """
        queries the total number of hours from the attendances
        """
        x = [0]
        for record in self:
            if record.employee_id.id == employee_id:
                df = str(date_from)
                dt = str(date_to)

                self.env.cr.execute(
                    "SELECT sum(worked_hours) FROM hr_attendance WHERE check_out::text LIKE '%s%%' and employee_id = %d" % (
                    df, employee_id))
                new = self.env.cr.fetchall()
                if df == dt:
                    self.env.cr.execute(
                        "SELECT sum(worked_hours) FROM hr_attendance WHERE check_out::text LIKE '%s%%' and employee_id = %d" % (
                        df, employee_id))
                else:
                    dt = str(datetime.strptime(dt, "%Y-%m-%d") + timedelta(days=1))
                    self.env.cr.execute(
                        "SELECT sum(worked_hours) FROM hr_attendance WHERE check_out BETWEEN '%s' AND '%s' AND employee_id = %d" % (
                        df, dt, employee_id))
                res = self.env.cr.fetchall()
                x = res[0]
        return x[0]


class HrPayslip(models.Model):
    """
    Payslip mode Inherit
    """
    _inherit = 'hr.payslip'

    days_in_month = fields.Integer(compute='_get_number_of_days')
    total_worked_days = fields.Float(compute='_get_total_worked_days')

    @api.onchange('date_from', 'date_to')
    def _get_number_of_days(self):
        self.days_in_month = int(
            (datetime.strptime(self.date_to, "%Y-%m-%d") - datetime.strptime(self.date_from, "%Y-%m-%d")).days) + 1
        temp = datetime.strptime(self.date_from, "%Y-%m-%d")
        self.days_in_month = calendar.monthrange(temp.year, temp.month)[1]

    @api.depends('worked_days_line_ids')
    def _get_total_worked_days(self):
        temp = 0.0
        for day in self.worked_days_line_ids:
            temp += day.number_of_days

        self.total_worked_days = temp
        return temp

    @api.model
    def get_worked_day_lines(self, employee, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        reg_work_hours = employee.calendar_id.reg_work_hours

        def was_on_leave_interval(employee_id, date_from, date_to):
            date_from = fields.Datetime.to_string(date_from)
            date_to = fields.Datetime.to_string(date_to)
            return self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', date_from),
                ('date_to', '>=', date_to)
            ], limit=1)

        res = []
        # fill only if the contract as a working schedule linked
        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        for contract in self.env['hr.contract'].browse(contract_ids).filtered(lambda contract: contract.working_hours):
            uom_hour = contract.employee_id.resource_id.calendar_id.uom_id or self.env.ref('product.product_uom_hour',
                                                                                           raise_if_not_found=False)
            interval_data = []
            holidays = self.env['hr.holidays']
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}
            day_from = fields.Datetime.from_string(date_from)
            day_to = fields.Datetime.from_string(date_to)
            nb_of_days = (day_to - day_from).days + 1

            # Gather all intervals and holidays
            for day in range(0, nb_of_days):
                working_intervals_on_day = contract.working_hours.get_working_intervals_of_day(
                    start_dt=day_from + timedelta(days=day))
                for interval in working_intervals_on_day:
                    interval_data.append(
                        (interval, was_on_leave_interval(contract.employee_id.id, interval[0], interval[1])))

            # Extract information from previous data. A working interval is considered:
            # - as a leave if a hr.holiday completely covers the period
            # - as a working period instead
            for interval, holiday in interval_data:
                holidays |= holiday
                hours = (interval[1] - interval[0]).total_seconds() / 3600.0
                if holiday:
                    # if he was on leave, fill the leaves dict
                    if holiday.holiday_status_id.name in leaves:
                        leaves[holiday.holiday_status_id.name]['number_of_hours'] += hours
                    else:
                        leaves[holiday.holiday_status_id.name] = {
                            'name': holiday.holiday_status_id.name,
                            'sequence': 5,
                            'code': holiday.holiday_status_id.name,
                            'number_of_days': 0.0,
                            'number_of_hours': hours,
                            'contract_id': contract.id,
                        }
                else:
                    # add the input vals to tmp (increment if existing)
                    attendances['number_of_hours'] += hours


            # Clean-up the results  
            leaves = [value for key, value in leaves.items()]
            for data in [attendances] + leaves:
                data['number_of_days'] = uom_hour._compute_quantity(data['number_of_hours'], uom_day, employee.id) \
                    if uom_day and uom_hour \
                    else data['number_of_hours'] / reg_work_hours
                res.append(data)
        return res
        

    @api.model
    def get_worked_day_lines_mod(self, employee, contract_ids, date_from, date_to):
        reg_work_hours = employee.calendar_id.reg_work_hours

        em = self.env['hr.employee'].browse(employee.id)
        rc = self.env['res.company'].search([('id', '=', em.company_id.id)])
        if not rc.feature:
            def create_empty_worked_lines(employee_id, contract_id, date_from, date_to):
                attendance = {
                    'name': 'Attendances',
                    'sequence': 1,
                    'code': 'ATTN',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract_id,
                }

                valid_days = [
                    ('check.date_from', '>=', date_from),
                    ('check.date_to', '<=', date_to),
                ]

                public_holiday = {
                    'name': 'Public Holidays',
                    'sequence': 11,
                    'code': 'PHL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract_id,
                }

                non_working_day = {
                    'name': 'Non-Working Days',
                    'sequence': 11,
                    'code': 'NWD',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract_id,
                }

                return attendance, valid_days, public_holiday, non_working_day


            attendances = []
            public_holidays = []
            leaves = []
            non_working_days = []

            approved_leaves = self.get_worked_day_lines(employee, contract_ids, date_from, date_to)
            temp = approved_leaves[1:]

            for contract in self.env['hr.contract'].browse(contract_ids):
                attendance, valid_days, public_holiday, non_working_day = create_empty_worked_lines(contract.employee_id.id,
                                                                                                    contract.id, date_from,
                                                                                                    date_to)

                # needed so that the shown hours matches any calculations you use them for
                obj = self.env['hr.attendance'].search([])
                attendance['number_of_days'] = obj._compute_worked_days(contract.employee_id.id, date_from, date_to)
                attendance['number_of_hours'] = obj._compute_total_worked_hours(contract.employee_id.id, date_from, date_to)
                attendances.append(attendance)

                holiday_obj = self.env['hr.contract'].search([])
                public_holiday['number_of_days'] = holiday_obj._compute_worked_days(contract.holiday_calendar, date_from,
                                                                                    date_to)
                public_holiday['number_of_hours'] = public_holiday['number_of_days'] * reg_work_hours
                public_holidays.append(public_holiday)

            for i in temp:
               leaves.append(i)

            temp1 = 0.0
            for i in approved_leaves:
                temp1 += i.get('number_of_days')

            day_from = fields.Datetime.from_string(date_from)
            day_to = fields.Datetime.from_string(date_to)
            nb_of_days = (day_to - day_from).days + 1

            non_working_day['number_of_days'] = nb_of_days - temp1

            non_working_day['number_of_hours'] = non_working_day['number_of_days'] * reg_work_hours
            non_working_days.append(non_working_day)


            return attendances + leaves + public_holidays + non_working_days
        else:
            return self.get_worked_day_lines(employee, contract_ids, date_from, date_to)

    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        # defaults
        res = {
            'value': {
                'line_ids': [],
                # delete old input lines
                'input_line_ids': map(lambda x: (2, x,), self.input_line_ids.ids),
                # delete old worked days lines
                'worked_days_line_ids': map(lambda x: (2, x,), self.worked_days_line_ids.ids),
                # 'details_by_salary_head':[], TODO put me back
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
            'name': _('Pay Slip of %s for %s') % (
            employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
            'company_id': employee.company_id.id,
        })

        if not self.env.context.get('contract'):
            # fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                # set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                # if we don't give the contract, then the input to fill should be for all current contracts of the employee
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
        # computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines_mod(employee, contract_ids, date_from, date_to)
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

        em = self.env['hr.employee'].browse(employee.id)
        rc = self.env['res.company'].search([('id', '=', em.company_id.id)])

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang', 'en_US')
        self.name = _('Pay Slip of %s for %s') % (
        employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        # computation of the salary input
        if not rc.feature:
            worked_days_line_ids = self.get_worked_day_lines_mod(employee, contract_ids, date_from, date_to)
        else:
            worked_days_line_ids = self.get_worked_day_lines(employee, contract_ids, date_from, date_to)
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


class ConfigWorkTimings(models.Model):
    """
    Models holds the fields that are to be displayed in the calendar which are required for calculating
    the full day, half days & the regular working hours per day
    """
    _inherit = 'resource.calendar'

    reg_work_hours = fields.Float('Regular Working Hours')
    min_work_hours = fields.Float('Minimum Working Hours')


class ConfigWorkHours(models.Model):
    _inherit = 'resource.calendar.attendance'

    @api.onchange('hour_from')
    def _onchange_hour_from(self):
        """auto calculates the hours for hour_to later reg_work_hours"""
        temp = self.hour_from + self.calendar_id.reg_work_hours

        # logic for not exceeding 24Hr format and revolving around the same
        if self.hour_from != 0:
            if temp > 24:
                self.hour_to = temp - 24
            else:
                self.hour_to = temp

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            resource = employee.resource_id.sudo()
            if resource and resource.calendar_id:
                hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id, compute_leaves=True)
                uom_hour = resource.calendar_id.uom_id
                uom_day = self.env.ref('product.product_uom_day')
                if uom_hour and uom_day:
                    return uom_hour._compute_quantity(hours, uom_day, employee_id)

    check_box = fields.Boolean(string="Check", compute='action_for_button')

    state = fields.Selection([
       ('draft', 'To Submit'),
       ('cancel', 'Cancelled'),
       ('confirm', 'To Approve'),
       ('refuse', 'Refused'),
       ('validate1', 'Second Approval'),
       ('validate', 'Approved'),
       ('cancel_leave', 'Leave Cancelled'),
       ('reject', 'Leave Cancellation Rejected'),
       ('approve', 'Leave Cancellation Approved'),

       ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
           help="The status is set to 'To Submit', when a holiday request is created." +
           "\nThe status is 'To Approve', when holiday request is confirmed by user." +
           "\nThe status is 'Refused', when holiday request is refused by manager." +
           "\nThe status is 'Approved', when holiday request is approved by manager.")

    @api.one
    def action_for_button(self):
        if self.user_id.id == self._uid:
            self.check_box = True
        else:
            self.check_box = False

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user') and not self.env.user.has_group('vertiple__employee.reporting_manager') :
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

    @api.multi
    def action_validate(self):
        HOURS_PER_DAY = self.employee_id.calendar_id.reg_work_hours

        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user') and not self.env.user.has_group('vertiple__employee.reporting_manager'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [(6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                #Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True

    def _check_state_access_right(self, vals):
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.env['res.users'].has_group('hr_holidays.group_hr_holidays_user') and not self.env['res.users'].has_group('vertiple__employee.reporting_manager') and not self.env['res.users'].has_group('vertiple__employee.only_employee'):
            return False
        return True

    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user') and not self.env.user.has_group('vertiple__employee.reporting_manager'):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1','approve']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        return True

    @api.multi
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request
            or if he is an Hr Manager.
        """
        user = self.env.user
        group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_manager')
        group_hrms_emp = self.env.ref('vertiple__employee.reporting_manager')
        for holiday in self:
            if group_hr_manager in user.groups_id or holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True
            elif group_hrms_emp in user.groups_id or holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True

    @api.one
    def action_leave_cancellation(self):
        self.write({'state':'cancel_leave'})

    @api.one
    def action_leave_cancel_approval(self):
        self.write({'state':'approve'})

    @api.one
    def action_leave_cancel_refusal(self):
        self.write({'state':'validate'})


class ProductUoM(models.Model):
    _inherit = 'product.uom'

    @api.multi
    def _compute_quantity(self, qty, to_unit, employee_id, round=True, rounding_method='UP'):
        e_id = self.env['hr.employee'].browse(employee_id)
        reg_work_hours = e_id.calendar_id.reg_work_hours

        em = self.env['hr.employee'].browse(employee_id)
        rc = self.env['res.company'].search([('id', '=', em.company_id.id)])
        if not rc.feature:
            if not self:
                return qty
            self.ensure_one()
            if self.category_id.id != to_unit.category_id.id:
                if self._context.get('raise-exception', True):
                    raise UserError(_(
                        'Conversion from Product UoM %s to Default UoM %s is not possible as they both belong to different Category!.') % (
                                    self.name, to_unit.name))
                else:
                    return qty

            try:
                amount = qty / reg_work_hours
            except:
                raise ValidationError("Please assign a valid working shift to Employee in Employee Directory")
            if to_unit:
                amount = amount * to_unit.factor
                if round:
                    amount = tools.float_round(amount, precision_rounding=to_unit.rounding, rounding_method=rounding_method)
            return amount
        else:
            return super(ProductUoM, self)._compute_quantity(qty, to_unit, round=True, rounding_method='UP')


class CompensatoryHolidays(models.Model):
    _name = "compensatory_holiday"

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def get_leave_type(self):
        obj = self.env['hr.holidays.status'].search([])
        for i in obj:
            if i.name == "Compensatory Days":
                k = i
        return k

    name = fields.Char('Description')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('cancel_leave', 'Leave Cancelled'),
        ('reject', 'Leave Cancellation Rejected'),
        ('approve', 'Leave Cancellation Approved'),

        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
            help="The status is set to 'To Submit', when a holiday request is created." +
            "\nThe status is 'To Approve', when holiday request is confirmed by user." +
            "\nThe status is 'Refused', when holiday request is refused by manager." +
            "\nThe status is 'Approved', when holiday request is approved by manager.")
    date_from = fields.Datetime('Start Date',index=True)
    date_to = fields.Datetime('End Date', copy=False)
    holiday_status_id = fields.Many2one("hr.holidays.status", string="Leave Type", required=True,default=get_leave_type)
    employee_id = fields.Many2one('hr.employee', string='Employee',readonly = True, default= _default_employee)
    holiday_type = fields.Selection([
            ('employee', 'By Employee'),
            ('category', 'By Employee Tag')], string='Allocation Mode', required=True, default='employee',help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category')
    number_of_days_temp = fields.Float('Allocation')
    notes = fields.Text('Reasons')
    holiday_id = fields.Many2one('hr.holidays', string='Holidays')

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for holiday in self:
            domain =[
                    ('date_from', '<=', holiday.date_to),
                    ('date_to', '>=', holiday.date_from),
                    ('employee_id', '=', holiday.employee_id.id),
                    ('id', '!=', holiday.id),
                    ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            resource = employee.resource_id.sudo()
            if resource and resource.calendar_id:
                hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id, compute_leaves=True)
                uom_hour = resource.calendar_id.uom_id
                uom_day = self.env.ref('product.product_uom_day')
                if uom_hour and uom_day:
                    return uom_hour._compute_quantity(hours, uom_day, employee_id)

        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        HOURS_PER_DAY = self.employee_id.calendar_id.reg_work_hours

        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_from','date_to','employee_id')
    @api.constrains('date_from','date_to','employee_id')
    def validate_compensatory(self):
        obj = self.env['hr.holidays.public'].search([])
        public_holidays=[]
        obj2 = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id)])
        attendance = []
        wd_dict={}
        for i in obj2:
            checkin_date = datetime.strptime(i.check_in,"%Y-%m-%d %H:%M:%S")
            date_checkin = datetime.strftime(checkin_date,"%Y-%m-%d")
            wd_dict[date_checkin]=i.worked_hours
            attendance.append(date_checkin)

        contract_obj = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)])
        for i in contract_obj:
            for j in i.holiday_calendar.line_ids:
                public_holidays.append(j.date)
        if self.date_from:
            date = str(self.date_from)
            to = str(self.date_to)
            date_from = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
            from_date = datetime.strftime(date_from,"%Y-%m-%d")
            date_to = datetime.strptime(to,"%Y-%m-%d %H:%M:%S")
            to_date = datetime.strftime(date_to,"%Y-%m-%d")
            from_hr = datetime.strftime(date_from,"%H-%M-%S")
            to_hr = datetime.strftime(date_to,"%H-%M-%S")
            if from_date not in public_holidays:
                raise ValidationError("Please check the datep!!!")
            if to_date not in public_holidays:
                raise ValidationError("Please check the datep!!!")
            if from_date not in attendance:
                raise ValidationError("Please check the date!!!")
            if to_date not in attendance:
                raise ValidationError("Please check the date!!!")
            if from_hr >= to_hr:
                raise ValidationError("The start date must be anterior to the end date!!!")

    # Insert records to Allocation Request using create method and insert query
    @api.multi
    def insert_query(self, holiday_status_id, employee_id, user_id, holiday_type, number_of_days_temp, name,date_from,date_to):
        self.env.cr.execute("INSERT INTO hr_holidays(holiday_status_id,employee_id,user_id,holiday_type,number_of_days_temp,state,type,name,number_of_days,date_from,date_to) VALUES(%d,%d,%d,'%s',%d,'confirm','add','%s',%d,'%s','%s')" %(holiday_status_id, employee_id, user_id, holiday_type, number_of_days_temp, name, number_of_days_temp,date_from,date_to))

    @api.model
    def create(self, vals):
        holiday_status_id = vals['holiday_status_id']
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id
        user_id = self.env.uid
        holiday_type = vals['holiday_type']
        number_of_days_temp = vals['number_of_days_temp']
        name = vals['name']
        date_from = vals['date_from']
        date_to = vals['date_to']
        self.insert_query(holiday_status_id, employee_id, user_id, holiday_type, number_of_days_temp, name,date_from,date_to)
        return super(CompensatoryHolidays, self).create(vals)

    # Delete records of Allocation Requests using unlink method and delete query 
    @api.one
    def delete_query(self,name):
        self.env.cr.execute("DELETE FROM hr_holidays where date_from='%s'" %(name));

    @api.one
    def unlink(self):
        name_id = str(self.date_from)
        self.delete_query(name_id)
        super(CompensatoryHolidays, self).unlink()

    # Update Records Allocation Requests using write method and update query
    @api.one
    def update_query(self, holiday_status_id,  holiday_type, number_of_days_temp, name, date_from,date_to,user_id):
        self.env.cr.execute("UPDATE hr_holidays set name = '%s', holiday_status_id = %d, holiday_type = '%s', number_of_days_temp = %d, date_from = '%s', date_to = '%s' WHERE date_from='%s' and user_id=%d" %(name, holiday_status_id, holiday_type, number_of_days_temp, date_from, date_to, date_from, user_id))

    @api.multi
    def write(self,values):
        try:
            values['name'] = values['name']
        except:
            values['name'] = self.name
        try:
            values['holiday_status_id'] = values['holiday_status_id']
        except:
            values['holiday_status_id'] = self.holiday_status_id.id
        try:
            values['employee_id'] = values['employee_id']
        except:
            values['employee_id'] = self.employee_id.id
        try:
            values['number_of_days_temp'] = values['number_of_days_temp']
        except:
            values['number_of_days_temp'] = self.number_of_days_temp
        try:
            values['date_from'] = values['date_from']
        except:
            values['date_from'] = self.date_from
        try:
            values['date_to'] =values['date_to']
        except:
            values['date_to'] = self.date_to
        try:
            values['holiday_type'] =values['holiday_type']
        except:
            values['holiday_type'] = self.holiday_type
        user_id = self.env.uid


        self.update_query(values['holiday_status_id'], values['holiday_type'], values['number_of_days_temp'], values['name'],values['date_from'],values['date_to'],user_id)
        result = super(CompensatoryHolidays, self).write(values)
        return result

    # State change to Approved which is being fetched from inherited hr holidays class
    @api.one
    def action_comp_approve(self,datefrom):
        if datefrom == self.date_from:
            self.write({'state': 'validate'})


    # State change to To Approve which is being fetched from inherited hr holidays class
    @api.one
    def action_comp_confirm(self,date_from):
        if date_from ==self.date_from:
            self.write({'state':'confirm'})


class Employee(models.Model):
    """
    Adds the Extra states for the Leaves in Employee Model
    """
    _inherit = "hr.employee"

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Leave Status",
       selection=[
           ('draft', 'New'),
           ('confirm', 'Waiting Approval'),
           ('refuse', 'Refused'),
           ('validate1', 'Waiting Second Approval'),
           ('validate', 'Approved'),
           ('cancel', 'Cancelled'),
           ('cancel_leave', 'Leave Cancelled'),
           ('reject', 'Leave Cancellation Rejected'),
           ('approve', 'Leave Cancellation Approved'),
       ])
