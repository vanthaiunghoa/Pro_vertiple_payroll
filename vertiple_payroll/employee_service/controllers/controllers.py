# -*- coding: utf-8 -*-
from odoo import http

# class EmployeeService(http.Controller):
#     @http.route('/employee_service/employee_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_service/employee_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_service.listing', {
#             'root': '/employee_service/employee_service',
#             'objects': http.request.env['employee_service.employee_service'].search([]),
#         })

#     @http.route('/employee_service/employee_service/objects/<model("employee_service.employee_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_service.object', {
#             'object': obj
#         })