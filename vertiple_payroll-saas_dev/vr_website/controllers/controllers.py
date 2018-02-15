# -*- coding: utf-8 -*-
from odoo import http

# class VrWebsite(http.Controller):
#     @http.route('/vr_website/vr_website/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vr_website/vr_website/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vr_website.listing', {
#             'root': '/vr_website/vr_website',
#             'objects': http.request.env['vr_website.vr_website'].search([]),
#         })

#     @http.route('/vr_website/vr_website/objects/<model("vr_website.vr_website"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vr_website.object', {
#             'object': obj
#         })