import base64
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ImportShipmentExcelWizard(models.TransientModel):
    _name = 'import.shipment.excel.wizard'
    _description = 'Import Shipment Excel Wizard'

    file = fields.Binary(string='Excel File', required=True)
    file_name = fields.Char(string='File Name')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)

    def action_import(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        
        try:
            workbook = xlrd.open_workbook(file_contents=base64.b64decode(self.file))
            sheet = workbook.sheet_by_index(0)
        except Exception as e:
            raise UserError(_("Invalid file format. Please upload a valid Excel file (.xls or .xlsx). Error: %s") % str(e))

        # Expected Columns: 0: Manufacturer Code / Product Ref, 1: Qty
        # We will try to match by x_manufacturer_code first, then default ref.
        
        for row_idx in range(1, sheet.nrows):
            code = str(sheet.cell_value(row_idx, 0)).strip()
            qty = sheet.cell_value(row_idx, 1)

            if not code or not qty:
                continue

            try:
                qty = float(qty)
            except ValueError:
                continue

            # Find matching import shipment lines for this partner and product
            # Product match: check x_manufacturer_code or default_code
            product = self.env['product.product'].search([
                '|', ('default_code', '=', code), 
                ('manufacturer_pref', '=', code)
            ], limit=1)

            if not product:
                _logger.warning("Product not found for code: %s", code)
                continue

            shipment_lines = self.env['import.shipment'].search([
                ('partner_id', '=', self.partner_id.id),
                ('product_id', '=', product.id),
                ('state', 'not in', ['done', 'cancel'])
            ])

            if shipment_lines:
                # Update the first matching line's incoming_qty (simplified logic)
                shipment_lines[0].write({'incoming_qty': qty})

        return {'type': 'ir.actions.act_window_close'}

    def action_confirm_import(self):
        """ Creates a picking for all lines with incoming_qty > 0 for this vendor """
        shipment_lines = self.env['import.shipment'].search([
            ('partner_id', '=', self.partner_id.id),
            ('incoming_qty', '>', 0),
            ('state', 'not in', ['done', 'cancel'])
        ])

        if not shipment_lines:
            raise UserError(_("No lines with incoming quantity found to confirm."))

        # Create Stock Picking
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.env.company.id)
        ], limit=1)

        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id or self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'origin': _("Import Shipment Consolidation"),
        }
        picking = self.env['stock.picking'].create(picking_vals)

        for line in shipment_lines:
            # Create Stock Move
            move_vals = {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.incoming_qty,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'purchase_line_id': line.purchase_line_id.id,
            }
            move = self.env['stock.move'].create(move_vals)
            line.write({
                'picking_ids': [(4, picking.id)],
                'incoming_qty': 0.0 # reset after processing
            })

        picking.action_confirm()
        
        return {
            'name': _('Incoming Picking'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'view_mode': 'form',
            'target': 'current',
        }
import logging
_logger = logging.getLogger(__name__)
