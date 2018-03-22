from odoo import fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[("xlsx", "xlsx")])

class YearlySalaryDetail(models.TransientModel):
    _inherit = 'yearly.salary.detail'

    def _get_default_category(self):
        return self.env['hr.salary.rule.category'].search([('code', '=', 'NET')], limit=1)

    category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True,
                                  default=_get_default_category)
