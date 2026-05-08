from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def load(self, fields, data):
        """ 
        Overriding load to set a context flag that triggers custom product matching 
        in product.product's _name_search.
        """
        return super(PurchaseOrder, self.with_context(is_po_import=True)).load(fields, data)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def load(self, fields, data):
        """ 
        Overriding load to set a context flag that triggers custom product matching 
        in product.product's _name_search.
        """
        return super(PurchaseOrderLine, self.with_context(is_po_import=True)).load(fields, data)
