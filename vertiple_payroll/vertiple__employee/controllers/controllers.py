# -*- coding: utf-8 -*-
from odoo import http

# class VertipleEmployee(http.Controller):
#     @http.route('/vertiple__employee/vertiple__employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vertiple__employee/vertiple__employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vertiple__employee.listing', {
#             'root': '/vertiple__employee/vertiple__employee',
#             'objects': http.request.env['vertiple__employee.vertiple__employee'].search([]),
#         })

#     @http.route('/vertiple__employee/vertiple__employee/objects/<model("vertiple__employee.vertiple__employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vertiple__employee.object', {
#             'object': obj
#         })