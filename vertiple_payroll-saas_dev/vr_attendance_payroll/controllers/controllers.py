# -*- coding: utf-8 -*-
from odoo import http

# class VrAttendancePayroll(http.Controller):
#     @http.route('/vr_attendance_payroll/vr_attendance_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vr_attendance_payroll/vr_attendance_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vr_attendance_payroll.listing', {
#             'root': '/vr_attendance_payroll/vr_attendance_payroll',
#             'objects': http.request.env['vr_attendance_payroll.vr_attendance_payroll'].search([]),
#         })

#     @http.route('/vr_attendance_payroll/vr_attendance_payroll/objects/<model("vr_attendance_payroll.vr_attendance_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vr_attendance_payroll.object', {
#             'object': obj
#         })