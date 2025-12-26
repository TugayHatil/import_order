from odoo import models, fields, api, _

class ImportOrder(models.Model):
    _name = 'x_import_order'
    _description = 'Import Order'
    _order = 'name desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Supplier', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    x_date_expected = fields.Date(string='Expected Date', default=fields.Date.context_today)
    x_picking_type_id = fields.Many2one('stock.picking.type', string='Receiving Operation', domain=[('code', '=', 'incoming')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')
    line_ids = fields.One2many('x_import_order_line', 'import_order_id', string='Order Lines')
    x_line_ids_readonly = fields.One2many('x_import_order_line', 'import_order_id', string='Order Lines (Readonly)')
    amount_total = fields.Monetary(string='Total Amount', store=True, readonly=True, compute='_compute_total')

    @api.depends('line_ids.price_subtotal')
    def _compute_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('price_subtotal'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('x_import_order') or _('New')
        return super(ImportOrder, self).create(vals)

    def action_confirm(self):
        for order in self:
            order.write({'state': 'done'})

    def action_cancel(self):
        for order in self:
            order.write({'state': 'cancel'})

    def action_draft(self):
        for order in self:
            order.write({'state': 'draft'})

class ImportOrderLine(models.Model):
    _name = 'x_import_order_line'
    _description = 'Import Order Line'

    import_order_id = fields.Many2one('x_import_order', string='Import Order', ondelete='cascade')
    state = fields.Selection(related='import_order_id.state', string='Order Status', readonly=True, store=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    x_teknik_referans = fields.Char(string='Teknik Referans', compute='_compute_teknik_referans', store=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    x_qty_incoming = fields.Float(string='Incoming', default=0.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True, store=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price', default=0.0)
    currency_id = fields.Many2one(related='import_order_id.currency_id', store=True, readonly=True)
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.depends('import_order_id.name', 'product_id.manufacturer_pref')
    def _compute_teknik_referans(self):
        for line in self:
            order_name = line.import_order_id.name or ''
            pref = line.product_id.manufacturer_pref or ''
            if order_name and pref:
                line.x_teknik_referans = f"{order_name}-{pref}"
            else:
                line.x_teknik_referans = order_name or pref
