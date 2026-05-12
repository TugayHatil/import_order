from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    import_shipment_id = fields.Many2one('import.shipment', string='Import Shipment', index=True)
    x_purchase_order_names = fields.Char(string='Purchase Orders', help="Comma separated list of purchase orders related to this move.")

    def write(self, vals):
        moves_to_revert = self.env['stock.move']
        if 'state' in vals and vals['state'] == 'cancel':
            for move in self:
                if move.state != 'cancel' and move.import_shipment_id:
                    moves_to_revert |= move

        res = super(StockMove, self).write(vals)

        if vals.get('state') == 'done':
            for move in self:
                if move.import_shipment_id:
                    move.import_shipment_id._compute_received_qty()

        for move in moves_to_revert:
            # Revert the quantity on the import shipment line
            # using product_uom_qty (demand) because that's what was added
            new_qty = max(0, move.import_shipment_id.imported_qty - move.product_uom_qty)
            move.import_shipment_id.sudo().write({'imported_qty': new_qty})

        return res

    def unlink(self):
        for move in self:
            if move.state != 'cancel' and move.import_shipment_id:
                new_qty = max(0, move.import_shipment_id.imported_qty - move.product_uom_qty)
                move.import_shipment_id.sudo().write({'imported_qty': new_qty})
        
        return super(StockMove, self).unlink()
