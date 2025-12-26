import base64
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ImportShipmentExcelWizard(models.TransientModel):
    _name = 'import.shipment.excel.wizard'
    _description = 'Import Shipment Excel Wizard'

    import_file = fields.Binary(string='Excel File', required=True)
    file_name = fields.Char(string='File Name')
    line_ids = fields.One2many('import.shipment.excel.line', 'wizard_id', string='Preview Lines')
    
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('validated', 'Doğrulandı'),
        ('done', 'Tamamlandı')
    ], string='Status', default='draft')

    def action_preview(self):
        self.ensure_one()
        if not self.import_file:
            raise UserError(_("Lütfen bir Excel dosyası yükleyin."))

        try:
            file_data = base64.b64decode(self.import_file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
        except Exception as e:
            raise UserError(_("Excel dosyası okunamadı. Hata: %s") % str(e))

        preview_vals = []
        for row_index in range(sheet.nrows):
            if row_index == 0: continue # Skip header
            ref_val, qty_val, message, status = self._parse_excel_row(sheet, row_index)
            preview_vals.append((0, 0, {
                'reference': ref_val,
                'quantity': qty_val,
                'state': status,
                'message': message
            }))
        
        self.write({
            'line_ids': [(5, 0, 0)] + preview_vals,
            'state': 'draft'
        })
        
        return self._reopen_wizard()

    def _parse_excel_row(self, sheet, row_index):
        try:
            # Assumes Column 0 is Reference, Column 1 is Quantity
            ref = str(sheet.cell_value(row_index, 0)).strip()
            qty = float(sheet.cell_value(row_index, 1) or 0.0)
            return ref, qty, '', 'pending'
        except Exception as e:
            return '', 0.0, str(e), 'failed'

    def action_validate(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id') # Ideally we filter by something? 
        # Actually user requirement says "import_shipment kayitlarina referans alani eklemelisin"
        # And "Import order addonu icerisinde yaptigimiz yapinin aynisi".
        # Import order matched wizard lines to Odoo lines.
        # Here we should match wizard lines to 'import.shipment' records.
        # Which 'import.shipment' records? All active ones? Or ones related to a specific PO?
        # User implies we run this generally or contextually. 
        # Usually checking ALL import.shipment lines that match the reference is risky if duplicates exist.
        # But reference is PO Name + Pref, so it should be unique enough per Shipment Line if PO + Product is unique.
        
        for line in self.line_ids:
            # Search for import.shipment with matching reference
            # Filter by state? Probably only draft/imported ones.
            target_lines = self.env['import.shipment'].search([
                ('reference', '=', line.reference),
                ('state', 'not in', ['done', 'cancel']) 
            ])
            
            if target_lines:
                line.write({
                    'match_ids': [(6, 0, target_lines.ids)],
                    'state': 'success',
                    'message': _('Eşleşme bulundu: %s kayıt') % len(target_lines)
                })
            else:
                line.write({
                    'state': 'failed', 
                    'message': _('Referans bulunamadı.')
                })

        self.write({'state': 'validated'})
        return self._reopen_wizard()

    def action_confirm(self):
        self.ensure_one()
        
        valid_lines = self.line_ids.filtered(lambda l: l.state == 'success')
        if not valid_lines:
            raise UserError(_("Aktarılacak geçerli satır yok."))

        for line in valid_lines:
            for shipment_line in line.match_ids:
                # Update imported_qty
                # If multiple matches, do we distribute? Or set same?
                # Usually 1-to-1 is expected. If 1-to-many, maybe splitting?
                # For now, simplest logic: Set imported_qty on all matched lines. 
                # Be careful if multiple lines share reference. 
                # If they share reference (Same PO, Same Product), they are duplicates?
                # "PO00030-PA". If multiple lines have same product in same PO, reference is same.
                # Logic: We might need to handle this.
                # Assuming unique product per PO for now based on reference construction.
                
                shipment_line.imported_qty = line.quantity
                if shipment_line.state == 'draft':
                    shipment_line.state = 'imported'

        self.write({'state': 'done'})
        return {'type': 'ir.actions.act_window_close'} # Or reload

    def action_reset(self):
        self.write({'state': 'draft', 'line_ids': [(5, 0, 0)]})
        return self._reopen_wizard()

    def _reopen_wizard(self):
        return {
            'name': _('Excel ile Aktar'),
            'type': 'ir.actions.act_window',
            'res_model': 'import.shipment.excel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

class ImportShipmentExcelLine(models.TransientModel):
    _name = 'import.shipment.excel.line'
    _description = 'Import Shipment Excel Wizard Line'

    wizard_id = fields.Many2one('import.shipment.excel.wizard', string='Wizard', ondelete='cascade')
    reference = fields.Char(string='Referans')
    quantity = fields.Float(string='Miktar')
    match_ids = fields.Many2many('import.shipment', string='Matched Lines')
    
    state = fields.Selection([
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız')
    ], string='Durum', default='pending')
    message = fields.Char(string='Mesaj')
