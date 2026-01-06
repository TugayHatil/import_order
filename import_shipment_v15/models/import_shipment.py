from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ImportShipment(models.Model):
    _name = 'import.shipment'
    _description = 'Import Shipment Line'
    _order = 'id desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True)
    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('partially_imported', 'Partially Imported'),
        ('imported', 'Imported'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='waiting', compute='_compute_state', store=True, tracking=True)

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', required=True, ondelete='cascade')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', related='purchase_line_id.order_id', store=True)
    product_id = fields.Many2one('product.product', string='Product', related='purchase_line_id.product_id', store=True)
    
    # Custom fields
    manufacturer_code = fields.Char(string='Manufacturer Code', related='product_id.product_tmpl_id.x_manufacturer_code', store=True)

    ordered_qty = fields.Float(string='Ordered Qty', related='purchase_line_id.product_qty', store=True)
    imported_qty = fields.Float(string='Imported Qty', help="Cumulative quantity imported via Excel", copy=False, default=0.0)
    incoming_qty = fields.Float(string='Incoming Qty', help="Quantity being imported in current session", copy=False, default=0.0)
    received_qty = fields.Float(string='Received Qty', compute='_compute_received_qty', store=True)
    open_qty = fields.Float(string='Open Qty', compute='_compute_open_qty', store=True)
    
    expected_date = fields.Date(string='Expected Date')
    
    picking_ids = fields.Many2many('stock.picking', string='Pickings', copy=False)

    @api.depends('purchase_line_id', 'purchase_line_id.order_id.name', 'product_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.purchase_order_id.name or ''} - {rec.product_id.name or ''}"

    @api.depends('ordered_qty', 'imported_qty')
    def _compute_open_qty(self):
        for rec in self:
            rec.open_qty = max(0.0, rec.ordered_qty - rec.imported_qty)

    @api.depends('purchase_line_id.move_ids.state', 'purchase_line_id.move_ids.quantity_done')
    def _compute_received_qty(self):
        for rec in self:
            # received_qty is the sum of done quantities in moves linked to this shipment line
            moves = self.env['stock.move'].search([
                ('import_shipment_id', '=', rec.id),
                ('state', '=', 'done')
            ])
            rec.received_qty = sum(moves.mapped('quantity_done'))

    @api.depends('received_qty', 'ordered_qty', 'imported_qty')
    def _compute_state(self):
        for rec in self:
            if rec.state == 'cancel':
                continue
            if rec.received_qty >= rec.ordered_qty and rec.ordered_qty > 0:
                rec.state = 'done'
            elif rec.imported_qty >= rec.ordered_qty and rec.ordered_qty > 0:
                rec.state = 'imported'
            elif rec.imported_qty > 0:
                rec.state = 'partially_imported'
            else:
                rec.state = 'waiting'
