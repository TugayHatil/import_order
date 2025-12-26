from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ImportShipment(models.Model):
    _name = 'import.shipment'
    _description = 'Import Shipment Line'
    _order = 'id desc'

    name = fields.Char(string='Shipment Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('imported', 'Imported'),
        ('partially_received', 'Partially Received'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', required=True, ondelete='cascade')
    purchase_order_id = fields.Many2one('purchase.order', related='purchase_line_id.order_id', string='Purchase Order', store=True, readonly=True)
    
    product_id = fields.Many2one('product.product', string='Product', related='purchase_line_id.product_id', store=True, readonly=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', related='purchase_line_id.product_uom', store=True, readonly=True)
    price_unit = fields.Float(related='purchase_line_id.price_unit', string='Unit Price', store=True, readonly=True)
    
    ordered_qty = fields.Float(string='Ordered Qty', related='purchase_line_id.product_qty', store=True, readonly=True)
    imported_qty = fields.Float(string='Imported Qty', help="Quantity verified via Excel import or manual entry", copy=False)
    received_qty = fields.Float(string='Received Qty', compute='_compute_received_qty', store=True, copy=False)
    open_qty = fields.Float(string='Open Qty', compute='_compute_open_qty', store=False, help="Ordered - Imported")
    
    shipment_ref = fields.Char(string='Supplier/Excel Ref')
    picking_id = fields.Many2one('stock.picking', string='Incoming Picking', copy=False)
    
    active = fields.Boolean(default=True)
    
    reference = fields.Char(string='Reference', compute='_compute_reference', store=True)

    @api.depends('purchase_order_id.name', 'product_id.manufacturer_pref')
    def _compute_reference(self):
        for record in self:
            ref_parts = []
            if record.purchase_order_id.name:
                ref_parts.append(record.purchase_order_id.name)
            if record.product_id.manufacturer_pref:
                ref_parts.append(record.product_id.manufacturer_pref)
            
            if len(ref_parts) == 2:
                record.reference = "-".join(ref_parts)
            else:
                record.reference = record.shipment_ref or ''

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('import.shipment') or _('New')
        return super(ImportShipment, self).create(vals)

    @api.depends('purchase_line_id.move_ids.state', 'purchase_line_id.move_ids.quantity_done')
    def _compute_received_qty(self):
        # Logic: 
        # Typically, standard PO lines track received qty via move_ids associated with the PO line.
        # Here, we will perform moves that are ALSO associated with this purchase_line_id.
        # However, we might want to track specifically moves created FROM this import shipment.
        # The design says: 8.3 Stock Move Created -> purchase_line_id, import_shipment_id
        # We need a field on stock.move to link to import.shipment? 
        # Or we filters moves by this import shipment.
        # Let's see if we can add a field to stock.move in stock.move model definition or use a domain.
        # Ideally, we should add 'import_shipment_id' to stock.move.
        for record in self:
            moves = self.env['stock.move'].search([
                ('import_shipment_id', '=', record.id),
                ('state', '=', 'done')
            ])
            record.received_qty = sum(moves.mapped('quantity_done'))

    @api.depends('ordered_qty', 'imported_qty')
    def _compute_open_qty(self):
        for record in self:
            record.open_qty = max(0, record.ordered_qty - record.imported_qty)

    def create_incoming_picking(self):
        """
        Creates a single incoming picking for selected import shipment lines.
        Only valid if imported_qty > received_qty and state in ['imported', 'partially_received']
        """
        # Group by partner and warehouse (from PO)
        # Assuming all selected lines belong to same partner for simplicity, or we group them.
        
        # Filter actionable lines
        lines_to_process = self.filtered(lambda l: l.state in ['imported', 'partially_received'] and l.imported_qty > l.received_qty)
        
        if not lines_to_process:
            raise UserError(_("No valid lines to process. Check states (must be Imported/Partially Received) and quantities."))

        # Group by partner
        partners = lines_to_process.mapped('partner_id')
        
        pickings = self.env['stock.picking']
        
        for partner in partners:
            partner_lines = lines_to_process.filtered(lambda l: l.partner_id == partner)
            
            # Determine warehouse/picking type from the first PO (assuming logic consistency)
            # Or use a default incoming picking type for the company.
            # We'll take the picking_type_id from the first PO.
            first_po = partner_lines[0].purchase_order_id
            picking_type = first_po.picking_type_id
            if not picking_type:
                raise UserError(_("Picking type not found on Purchase Order %s") % first_po.name)

            picking_vals = {
                'partner_id': partner.id,
                'picking_type_id': picking_type.id,
                'location_id': partner.property_stock_supplier.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                'origin': ', '.join(set(partner_lines.mapped('name'))),
                'move_type': 'direct',
            }
            
            picking = self.env['stock.picking'].create(picking_vals)
            
            moves_to_create = []
            for line in partner_lines:
                qty_to_process = line.imported_qty - line.received_qty
                if qty_to_process <= 0:
                    continue
                
                move_vals = {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': qty_to_process,
                    'product_uom': line.product_uom.id,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'purchase_line_id': line.purchase_line_id.id,
                    'import_shipment_id': line.id,
                    'origin': line.name,
                }
                moves_to_create.append(move_vals)
            
            if moves_to_create:
                self.env['stock.move'].create(moves_to_create)
                picking.action_confirm()
                # Link picking to shipments
                partner_lines.write({'picking_id': picking.id})
                pickings |= picking

        return {
            'name': _('Incoming Picking'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', pickings.ids)],
        }
