from odoo import models, fields, api
from odoo.osv import expression

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacturer_pref = fields.Char(string='Manufacturer Pref', index=True, help='Manufacturer preference code for product matching.')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('is_po_import') and name:
            # Optimization: Use _search to get only IDs from DB without instantiating records
            # Priority 1: default_code (Internal Reference)
            domain = [('default_code', '=', name)]
            products = self._search(expression.AND([domain, args or []]), limit=limit, access_rights_uid=name_get_uid)
            
            if not products:
                # Priority 2: manufacturer_pref
                domain = [('manufacturer_pref', '=', name)]
                products = self._search(expression.AND([domain, args or []]), limit=limit, access_rights_uid=name_get_uid)
            
            if products:
                return products
        
        return super(ProductProduct, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
