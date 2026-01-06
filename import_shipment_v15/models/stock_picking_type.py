from odoo import models, fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    x_is_import_type = fields.Boolean(
        string='Is Import Type?', 
        default=False,
        help="If checked, Purchase Orders using this operation type will not create pickings automatically. "
             "Instead, lines will be collected into the Import Shipment list."
    )
