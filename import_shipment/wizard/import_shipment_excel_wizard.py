import logging
import base64
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

    picking_ids = fields.Many2many('stock.picking', string='Created Pickings')

    # Column mapping (0-based): 
    # 0=Ref(PO-Pref), 1=Quantity, 2=Price, 3=Date
    
    def _parse_excel_row(self, sheet, row_index):
        import xlrd
        try:
            ref = str(sheet.cell_value(row_index, 0)).strip()
            qty = float(sheet.cell_value(row_index, 1) or 0.0)
            price = float(sheet.cell_value(row_index, 2) or 0.0)
            
            # Date handling
            date_val = sheet.cell_value(row_index, 3)
            date_obj = False
            if date_val:
                if sheet.cell_type(row_index, 3) == xlrd.XL_CELL_DATE:
                    date_tuple = xlrd.xldate_as_tuple(date_val, sheet.book.datemode)
                    date_obj = fields.Datetime.to_datetime("%04d-%02d-%02d %02d:%02d:%02d" % date_tuple)
                else:
                    # Try to parse string if not date type?
                    date_obj = fields.Datetime.to_datetime(str(date_val))
            
            return ref, qty, price, date_obj, '', 'pending'
        except Exception as e:
            return '', 0.0, 0.0, False, str(e), 'failed'

    def action_preview(self):
        import xlrd
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
        for row_index in range(1, sheet.nrows): # Skip header
            ref_val, qty_val, price_val, date_val, message, status = self._parse_excel_row(sheet, row_index)
            preview_vals.append((0, 0, {
                'reference': ref_val,
                'quantity': qty_val,
                'excel_price': price_val,
                'date': date_val,
                'state': status,
                'message': message
            }))
        
        self.write({
            'line_ids': [(5, 0, 0)] + preview_vals,
            'state': 'draft'
        })
        
        return self._reopen_wizard()

    def action_validate(self):
        self.ensure_one()
        for line in self.line_ids:
            target_lines = self.env['import.shipment'].search([
                ('name', '=', line.reference),
                ('state', '!=', 'done') 
            ])
            
            if target_lines:
                odoo_price = target_lines[0].price_unit
                msgs = []
                state = 'success'
                
                if abs(odoo_price - line.excel_price) > 0.01:
                    state = 'warning'
                    msgs.append(_('Fiyat farkı (Sipariş: %s, Excel: %s)') % (odoo_price, line.excel_price))

                if not msgs:
                    msgs.append(_('Eşleşme bulundu.'))

                line.write({
                    'match_ids': [(6, 0, target_lines.ids)],
                    'odoo_price': odoo_price,
                    'state': state,
                    'message': ' | '.join(msgs)
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
        valid_lines = self.line_ids.filtered(lambda l: l.state in ['success', 'warning'])
        if not valid_lines:
            raise UserError(_("Aktarılacak geçerli satır yok."))

        pickings = self.env['stock.picking']

        # Process by Date? Users might want separate pickings for separate dates.
        dates = list(set(valid_lines.mapped('date')))
        
        for d in dates:
            date_lines = valid_lines.filtered(lambda l: l.date == d)
            # Find all shipment lines and their quantities for this date batch
            shipments_map = {}
            shipments_to_process = self.env['import.shipment']
            
            for line in date_lines:
                for shipment_line in line.match_ids:
                    # Update cumulative quantity
                    shipment_line.imported_qty += line.quantity
                    shipments_to_process |= shipment_line
                    shipments_map[shipment_line.id] = line.quantity

            if shipments_to_process:
                # Create Picking for this batch
                batch_pickings = shipments_to_process.with_context(items_qty_map=shipments_map).create_incoming_picking(excel_date=d)
                if batch_pickings:
                    pickings |= batch_pickings

        self.write({'state': 'done'})
        
        if pickings:
            return {
                'name': _('Incoming Pickings'),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', pickings.ids)],
            }
            
        return {'type': 'ir.actions.act_window_close'}

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
    excel_price = fields.Float(string='Excel Fiyat')
    odoo_price = fields.Float(string='Sipariş Fiyat')
    date = fields.Datetime(string='Tarih')
    match_ids = fields.Many2many('import.shipment', string='Matched Lines')
    
    state = fields.Selection([
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('warning', 'Kontrol'),
        ('failed', 'Başarısız')
    ], string='Durum', default='pending')
    message = fields.Char(string='Mesaj')
