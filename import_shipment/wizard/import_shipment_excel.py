import base64
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ImportShipmentExcel(models.TransientModel):
    _name = 'import.shipment.excel'
    _description = 'Import Shipment Excel Wizard'

    file = fields.Binary(string='Excel File', required=True)
    filename = fields.Char(string='Filename')
    
    def action_import(self):
        self.ensure_one()
        if not self.file:
            raise UserError(_("Please upload an Excel file."))
            
        try:
            file_data = base64.b64decode(self.file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
        except Exception as e:
            raise UserError(_("Could not read excel file. Error: %s") % str(e))
            
        # Excel Columns: Supplier Ref, PO Number, Product Code, Quantity
        # Assuming 0-based index: 0=Ref, 1=PO, 2=Product, 3=Qty
        
        # We need to match with existing import.shipment records.
        # Matching Logic:
        # P0 + Product -> Unique identification in import.shipment (if not split lines)
        # Actually PO line is unique. 
        # If excel has PO Number and Product Code, we can find the import shipment line.
        
        not_found_rows = []
        
        for row_index in range(1, sheet.nrows): # Skip header
            try:
                supplier_ref = str(sheet.cell_value(row_index, 0)).strip()
                po_number = str(sheet.cell_value(row_index, 1)).strip()
                product_code = str(sheet.cell_value(row_index, 2)).strip()
                quantity = float(sheet.cell_value(row_index, 3) or 0.0)
                
                # Search criteria
                domain = [
                    ('purchase_order_id.name', '=', po_number),
                    ('product_id.default_code', '=', product_code),
                    ('state', 'in', ['draft', 'imported']) 
                    # We allow updating if partially_received? Maybe not for safety.
                    # Plan said state -> imported.
                ]
                
                shipment = self.env['import.shipment'].search(domain, limit=1)
                
                if shipment:
                    shipment.write({
                        'imported_qty': quantity,
                        'shipment_ref': supplier_ref,
                        'state': 'imported'
                    })
                else:
                    not_found_rows.append(f"Row {row_index+1}: PO {po_number}, Product {product_code}")
                    
            except Exception as e:
                not_found_rows.append(f"Row {row_index+1}: Error {str(e)}")
                
        if not_found_rows:
            # For now, just show a warning or return a text action, 
            # but standard Odoo practice often validates first.
            # We'll just raise a warning with list of failures.
            raise UserError(_("Import completed with errors/missing matches:\n%s") % '\n'.join(not_found_rows))
            
        return {'type': 'ir.actions.act_window_close'}
