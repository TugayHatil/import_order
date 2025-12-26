from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _create_picking(self):
        # Filter orders: Skip picking creation for import vendors
        normal_orders = self.filtered(lambda o: not o.partner_id.is_import_vendor)
        
        # Call super only for normal orders
        if normal_orders:
            return super(PurchaseOrder, normal_orders)._create_picking()
        return True

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        # Create import shipment records for import vendors
        for order in self:
            if order.partner_id.is_import_vendor:
                for line in order.order_line:
                    self.env['import.shipment'].create({
                        'partner_id': order.partner_id.id,
                        'purchase_line_id': line.id,
                        'ordered_qty': line.product_qty,
                    })
        return res
