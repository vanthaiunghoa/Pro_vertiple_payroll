from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ReportHrYearlySalary(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, model_object):

        # Cell & Sheet Formatting
        bold = workbook.add_format({'bold': True})
        title_format = workbook.add_format({'bold': 1,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'fg_color': '#FCFCD9'})

        title_format1 = workbook.add_format({'bold': 1,
                                             'border': 1,
                                             'align': 'center',
                                             'valign': 'vcenter'})

        headcell_format = workbook.add_format({'fg_color': 'silver',
                                               'bold': True
                                               })

        for o in model_object:
            # getting the data dict
            o.ensure_one()
            data = {'ids': self.env.context.get('active_ids', [])}
            res = o.read()
            res = res and res[0] or {}
            data.update({'form': res})

            employee = self.env['report.l10n_in_hr_payroll.report_hryearlysalary'].get_employee(data['form'])

            for id in employee:
                report_name = id.name
                sheet = workbook.add_worksheet(report_name[:31])

                # Setting Colum Widths
                sheet.set_column('A:A', 18)
                sheet.set_column('B:B', 12)
                sheet.set_column('C:C', 12)
                sheet.set_column('D:D', 12)
                sheet.set_column('E:E', 12)
                sheet.set_column('F:F', 12)
                sheet.set_column('G:G', 12)
                sheet.set_column('H:H', 12)
                sheet.set_column('I:I', 12)
                sheet.set_column('J:J', 12)
                sheet.set_column('K:K', 12)
                sheet.set_column('L:L', 12)
                sheet.set_column('M:M', 12)
                sheet.set_column('N:N', 12)

                # Report Title
                sheet.merge_range('A1:N1', id.company_id.name, title_format)
                sheet.merge_range('A2:N2', "", title_format1)

                # Report Headers
                sheet.write('A3', 'From', headcell_format)
                sheet.write('B3', o.date_from)
                sheet.write('C3', 'To', headcell_format)
                sheet.write('D3', o.date_to)

                sheet.write('A5', 'Employee ID', headcell_format)
                if id.emp_id:
                    sheet.write('B5', id.emp_id)
                sheet.write('D5', 'Department', headcell_format)
                if id.department_id:
                    sheet.write('E5', id.department_id.name)
                sheet.write('G5', 'Bank', headcell_format)
                if id.bank_account_id.bank_id:
                    sheet.write('H5', id.bank_account_id.bank_id.name)

                sheet.write('A6', 'Employee Name', headcell_format)
                sheet.write('B6', id.name)
                sheet.write('D6', 'Address', headcell_format)
                sheet.write('E6', id.address_home_id.name)

                sheet.write('A7', 'Designation', headcell_format)
                if id.job_id:
                    sheet.write('B7', id.job_id.name)
                sheet.write('D7', 'Phone no', headcell_format)
                if id.work_phone:
                    sheet.write('E7', id.work_phone)
                sheet.write('G7', 'Work Email', headcell_format)
                if id.work_email:
                    sheet.write('H7', id.work_email)

                # report.l10n_in_hr_payroll.report_hryearlysalary object
                obj = self.env['report.l10n_in_hr_payroll.report_hryearlysalary']

                # getting the headers [Names of the month]
                months = obj.get_periods(data['form'])
                for month in months:
                    obj.get_employee_detail(data['form'], id)
                    sheet.write('A10', 'Title', headcell_format)
                    col = 1
                    for month_sal in month[0:12]:
                        sheet.write(9, col, month_sal, headcell_format)
                        col += 1
                    sheet.write('N10', 'Total', headcell_format)

                # Records with Allowances
                sheet.write('A11', 'Allowances with Basic', bold)
                row = 11
                for allowance in obj.get_allow():
                    col = 0
                    for allow in allowance:
                        sheet.write(row, col, str(allow))
                        col += 1
                        if col == 14:
                            row = row + 1
                            col = 0
                sheet.write(row, 0, 'Deductions', bold)

                # Records with Deductions
                row += 1
                for deduct in obj.get_deduct():
                    col = 0
                    if deduct[0] not in ['Net']:
                        sheet.write(row, col, str(deduct[0]))
                        col += 1
                        if col == 14:
                            row = row + 1
                            col = 0
                    col = 0
                    for d in deduct:
                        sheet.write((row+1), col, str(d))
                        col += 1
                        if col == 14:
                            row = row + 1
                            col = 0

ReportHrYearlySalary('report.l10n_in_hr_payroll.report_hryearlysalary', 'yearly.salary.detail')
