from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    manufacturer_pref = fields.Char(string='Manufacturer Pref', help="Code used for Import Shipment matchmaking (FIFO).")
    x_manufacturer_code = fields.Char(related='manufacturer_pref', string='X Manufacturer Code', readonly=False, store=True)
