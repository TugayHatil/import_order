from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacturer_pref = fields.Char(string='Manufacturer Pref', help='Manufacturer preference code for product matching.')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('is_po_import') and name:
            # Priority 1: default_code (Internal Reference)
            domain = [('default_code', '=', name)] + (args or [])
            products = self.search(domain, limit=limit)
            if not products:
                # Priority 2: manufacturer_pref
                domain = [('manufacturer_pref', '=', name)] + (args or [])
                products = self.search(domain, limit=limit)
            
            if products:
                return products.ids
        
        return super(ProductProduct, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
