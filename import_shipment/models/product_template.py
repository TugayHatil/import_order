from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacturer_pref = fields.Char(string='Manufacturer Pref', help="Code used for Import Shipment matchmaking (FIFO).")
