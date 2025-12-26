from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    manufacturer_pref = fields.Char(string='Manufacturer Pref')
