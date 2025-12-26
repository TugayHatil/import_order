from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _create_picking(self):
        # Filter orders: Skip picking creation if picking type has use_import_shipment
        normal_orders = self.filtered(lambda o: not o.picking_type_id.use_import_shipment)
        
        # Call super only for normal orders
        if normal_orders:
            return super(PurchaseOrder, normal_orders)._create_picking()
        return True

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        # Create import shipment records if picking type has use_import_shipment
        for order in self:
            if order.picking_type_id.use_import_shipment:
                for line in order.order_line:
                    if line.product_id.type == 'service':
                        continue
                    self.env['import.shipment'].create({
                        'partner_id': order.partner_id.id,
                        'purchase_line_id': line.id,
                        'ordered_qty': line.product_qty,
                        'date_planned': line.date_planned,
                    })
        return res
