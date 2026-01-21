from odoo import models, fields

class SupportType(models.Model):
    _name = 'support.type'
    _description = 'Support Type'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
