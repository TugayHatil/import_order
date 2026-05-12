from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    x_manufacturer_code = fields.Char(related='product_tmpl_id.manufacturer_pref', string='X Manufacturer Code', readonly=False, store=True)
