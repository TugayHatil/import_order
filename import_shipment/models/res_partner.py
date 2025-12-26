from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_import_vendor = fields.Boolean(string="Is Import Vendor", help="If checked, Purchase Orders for this vendor will not generate standard Pickings on confirmation. Instead, they will generate Import Shipment records.")
