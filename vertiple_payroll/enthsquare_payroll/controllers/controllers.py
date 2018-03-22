# -*- coding: utf-8 -*-
from odoo import http

# class EnthsquarePayroll(http.Controller):
#     @http.route('/enthsquare_payroll/enthsquare_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/enthsquare_payroll/enthsquare_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('enthsquare_payroll.listing', {
#             'root': '/enthsquare_payroll/enthsquare_payroll',
#             'objects': http.request.env['enthsquare_payroll.enthsquare_payroll'].search([]),
#         })

#     @http.route('/enthsquare_payroll/enthsquare_payroll/objects/<model("enthsquare_payroll.enthsquare_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('enthsquare_payroll.object', {
#             'object': obj
#         })