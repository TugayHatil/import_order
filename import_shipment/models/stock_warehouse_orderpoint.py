from odoo import models

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def _compute_qty(self):
        # Standard method normally calls _compute_qty_to_order
        # But we need to check where 'qty_on_hand' or 'qty_forecast' is used or 'incoming_qty'.
        # Actually, in Odoo 16, _compute_qty_to_order uses virtual_available (forecasted).
        # We want to treat 'open_qty' of import shipments as 'Incoming' effectively? 
        # Or as 'Planned' supply that isn't yet in 'Incoming Stock Moves'.
        # If we skip picking creation, 'incoming_qty' on product will NOT include these PO quantities.
        # So we need to add them back for MRP/Orderpoint calculations.
        
        super(StockWarehouseOrderpoint, self)._compute_qty()
        
        # We need to adjust 'qty_forecast' or the result of computation?
        # The field 'qty_to_order' is what we want to influence.
        # qty_to_order = product_max_qty - qty_forecast + qty_to_order_computed...
        
        # It's safer to hook into product.product._compute_quantities if we want global visibility,
        # but the request specifically said "stock.warehouse.orderpoint" and "_compute_qty_to_order". (9.2)
        
        # Let's inspect where we interfere.
        # If we add to 'qty_forecast' (virtual_available), it will reduce 'qty_to_order'.
        
        # However, _compute_qty on orderpoint calculates:
        # line.qty_on_hand = product.qty_available
        # line.qty_forecast = product.virtual_available
        
        pass

    def _get_product_context(self):
        """
        Used in _compute_qty to get context for product.product read_group or fields_get.
        We can't easily inject logic here to change product.virtual_available directly without overriding product logic.
        """
        return super()._get_product_context()

    # Re-reading the requirement 9.2:
    # stock.warehouse.orderpoint -> _compute_qty_to_order
    # MRP open_qty alanını dikkate alır.
    
    # In Odoo 16, _compute_qty_to_order is working on the recordset.
    
    def _compute_qty_to_order(self):
        super(StockWarehouseOrderpoint, self)._compute_qty_to_order()
        for orderpoint in self:
            # We want to REDUCE the qty_to_order by the amount we have coming in via Import Shipments
            # because Odoo sees them as missing (since no stock.move exists yet).
            
            # Find open import shipments for this product and location (or company/warehouse)
            # Orderpoints are per location. Import Shipments are per PO (partner location -> destination).
            # We assume destination is the warehouse stock location.
            
            domain = [
                ('product_id', '=', orderpoint.product_id.id),
                ('state', 'in', ['draft', 'imported', 'partially_received']),
                # We need to match location.
                # Import shipments (via PO) usually go to Picking Type -> Default Dest Location.
                # verifying if it matches orderpoint.location_id is complex but necessary for multi-warehouse.
                # For simplicity, assuming company match or single warehouse.
                ('purchase_line_id.order_id.picking_type_id.default_location_dest_id', '=', orderpoint.location_id.id)
            ]
            
            shipments = self.env['import.shipment'].search(domain)
            incoming_shipment_qty = sum(shipments.mapped('open_qty'))
            
            # If we have 100 needed, but 40 are coming in shipment (and not in moves), 
            # Odoo thinks we need 100. We should say we need 60.
            # So we subtract incoming_shipment_qty from qty_to_order.
            
            if incoming_shipment_qty > 0:
                orderpoint.qty_to_order = max(0.0, orderpoint.qty_to_order - incoming_shipment_qty)

