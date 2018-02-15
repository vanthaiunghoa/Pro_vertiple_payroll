from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ReportHrSalaryByMonth(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, model_object):

        for o in model_object:
            sheet = workbook.add_worksheet('Yearly Salary By Head')

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
                                                   'bold': True})

            # Setting Colum Widths
            sheet.set_column('A:A', 15)
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

            # Sheet Title
            sheet.merge_range('A1:N1', "Yearly Salary Details", title_format)
            sheet.merge_range('A2:N2', "", title_format1)

            # From print_report of hr.salary.employee.month model
            o.ensure_one()
            data = {'ids': self.env.context.get('active_ids', [])}
            res = o.read()
            res = res and res[0] or {}
            data.update({'form': res})

            # Report Headers
            sheet.write('A3', 'From', headcell_format)
            sheet.write('B3', o.start_date)
            sheet.write('C3', 'To', headcell_format)
            sheet.write('D3', o.end_date)
            sheet.write('F3', 'Category', headcell_format)
            sheet.write('G3', data['form']['category_id'][1])

            # Table Headers
            sheet.write('A5', 'Name', headcell_format)

            wiz_obj = self.env['report.l10n_in_hr_payroll.report_hrsalarybymonth']
            form, months, total_months = wiz_obj.get_periods(data['form'])
            col = 1
            for month in wiz_obj.get_periods(data['form'])[0]:
                sheet.write(4, col, month, headcell_format)
                col += 1

            sheet.write('N5', 'Total', headcell_format)

            # Table Body
            main_row = 5
            row = 5
            for e in wiz_obj.get_employee(data['form'], months, total_months):
                sheet.write(main_row, 0, e[0])
                main_row += 1
                col = 1
                for month_sal in e[1:]:
                    sheet.write(row, col, str(month_sal))
                    col += 1
                    if col == 14:
                        row += 1
                        col = 1
            sheet.write(main_row, 0, 'Total', bold)

            # Table Footer
            col = 1
            for t in wiz_obj.get_months_tol():
                for tdata in t:
                    sheet.write(main_row, col, str(tdata))
                    col += 1
            # Total Amount
            mnths_total = wiz_obj.get_months_tol()
            total = wiz_obj.get_total(mnths_total)
            sheet.write(row, 13, total, bold)
            

ReportHrSalaryByMonth('report.l10n_in_hr_payroll.report_hrsalarybymonth', 'hr.salary.employee.month')
