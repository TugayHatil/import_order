from odoo import models, fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    x_is_import_type = fields.Boolean(string='Is Import Type?', default=False)
