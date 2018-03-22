# -*- coding: utf-8 -*-
from odoo import http

# class EmailRemainder(http.Controller):
#     @http.route('/email_remainder/email_remainder/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/email_remainder/email_remainder/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('email_remainder.listing', {
#             'root': '/email_remainder/email_remainder',
#             'objects': http.request.env['email_remainder.email_remainder'].search([]),
#         })

#     @http.route('/email_remainder/email_remainder/objects/<model("email_remainder.email_remainder"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('email_remainder.object', {
#             'object': obj
#         })