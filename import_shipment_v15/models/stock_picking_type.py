from odoo import models, fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    use_import_shipment = fields.Boolean(
        string="Use Import Shipment",
        help="If checked, Purchase Orders using this picking type will follow the Import Shipment flow instead of standard picking creation."
    )
