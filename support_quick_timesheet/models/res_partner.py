from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_support_customer = fields.Boolean(string='Is Support Customer', default=False)
