from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_manufacturer_code = fields.Char(string='Üretici Kodu', help='Manufacturer part number or code for the product.')
