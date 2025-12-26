from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    import_order_line_id = fields.Many2one(
        'x_import_order_line',
        string='Import Order Line',
        ondelete='set null',
        index=True,
        help="Technical link to the original import order line."
    )
