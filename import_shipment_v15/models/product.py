from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    manufacturer_pref = fields.Char(string='Manufacturer Pref', help='Manufacturer part number or code for the product.')
