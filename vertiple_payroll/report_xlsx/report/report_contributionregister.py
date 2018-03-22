from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ReportContributionRegister(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, model_object):
        for obj in model_object:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])

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
            # Report Title
            sheet.merge_range('A1:F1', "Payslip Lines By Contribution Register", title_format)
            sheet.merge_range('A2:F2', "", title_format1)

            # Setting Colum Widths
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 15)
            sheet.set_column('C:C', 15)
            sheet.set_column('D:D', 15)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 15)

            # Report Headers
            sheet.write(2, 0, 'Register Name', headcell_format)
            sheet.write(3, 0, obj.name)

            # Retriving Dates from Wizard
            wizard_obj = self.env['payslip.lines.contribution.register'].search([])
            for rec in wizard_obj:
                date_from = rec.date_from
                date_to = rec.date_to

            sheet.write(2, 2, 'Date From', headcell_format)
            sheet.write(3, 2, date_from)

            sheet.write(2, 4, 'Date To', headcell_format)
            sheet.write(3, 4, date_to)

            sheet.write('A7', 'Payslip Name', headcell_format)
            sheet.write('B7', 'Code', headcell_format)
            sheet.write('C7', 'Name', headcell_format)
            sheet.write('D7', 'Quantity', headcell_format)
            sheet.write('E7', 'Amount', headcell_format)
            sheet.write('F7', 'Total', headcell_format)

            # Getting the data from the 'report.hr_payroll.report_contributionregister'
            register_ids = self.env.context.get('active_ids', [])
            lines_data = self.env['report.hr_payroll.report_contributionregister']._get_payslip_lines(register_ids,
                                                                                                      date_from,
                                                                                                      date_to)

            # Populating the retrieved data over the cells of the sheet
            col = 0
            row = 7
            for line in lines_data.get(obj.id, []):
                col = 0
                sheet.write(row, col, line.employee_id.name)
                col += 1
                sheet.write(row, col, line.code)
                col += 1
                sheet.write(row, col, line.name)
                col += 1
                sheet.write(row, col, line.quantity)
                col += 1
                sheet.write(row, col, line.amount)
                col += 1
                sheet.write(row, col, line.total)
                row += 1

            contrib_registers = self.env['hr.contribution.register'].browse(register_ids)
            lines_total = {}

            for register in contrib_registers:
                lines = lines_data.get(register.id)
                lines_total[register.id] = lines and sum(lines.mapped('total')) or 0.0

            sheet.write(row + 2, 4, "Total", headcell_format)
            sheet.write(row + 2, 5, lines_total.get(obj.id), bold)


ReportContributionRegister('report.hr_payroll.report_contributionregister', 'hr.contribution.register')