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

    line_filter = fields.Selection([
        ('all', 'Tümü'),
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('warning', 'Kontrol'),
        ('failed', 'Başarısız')
    ], string='Durum Filtresi', default='all')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ImportShipmentExcelWizard, self).fields_get(allfields, attributes)
        if 'line_filter' in res:
            wizard_id = self.env.context.get('wizard_id')
            if wizard_id:
                wizard = self.browse(wizard_id)
                res['line_filter']['selection'] = [
                    ('all', f"Tümü ({wizard.count_all})"),
                    ('pending', f"Beklemede ({wizard.count_pending})"),
                    ('success', f"Başarılı ({wizard.count_success})"),
                    ('warning', f"Kontrol ({wizard.count_warning})"),
                    ('failed', f"Başarısız ({wizard.count_failed})"),
                ]
        return res

    display_line_ids = fields.Many2many('import.shipment.excel.line', compute='_compute_display_line_ids', string='Görüntülenen Satırlar')

    # Count fields for the filter legend
    count_all = fields.Integer(compute='_compute_line_counts')
    count_pending = fields.Integer(compute='_compute_line_counts')
    count_success = fields.Integer(compute='_compute_line_counts')
    count_warning = fields.Integer(compute='_compute_line_counts')
    count_failed = fields.Integer(compute='_compute_line_counts')

    @api.depends('line_ids', 'line_ids.state')
    def _compute_line_counts(self):
        for wizard in self:
            wizard.count_all = len(wizard.line_ids)
            wizard.count_pending = len(wizard.line_ids.filtered(lambda l: l.state == 'pending'))
            wizard.count_success = len(wizard.line_ids.filtered(lambda l: l.state == 'success'))
            wizard.count_warning = len(wizard.line_ids.filtered(lambda l: l.state == 'warning'))
            wizard.count_failed = len(wizard.line_ids.filtered(lambda l: l.state == 'failed'))

    @api.depends('line_ids', 'line_filter', 'line_ids.state')
    def _compute_display_line_ids(self):
        for wizard in self:
            if not wizard.line_filter or wizard.line_filter == 'all':
                wizard.display_line_ids = wizard.line_ids
            else:
                wizard.display_line_ids = wizard.line_ids.filtered(lambda l: l.state == wizard.line_filter)

    # Column mapping (0-based): 
    # 0=Ref(PO-Pref), 1=Quantity, 2=Price, 3=Date
    
    def _parse_excel_row(self, sheet, row_index):
        import xlrd
        try:
            # Robust reading of reference (handle numbers vs strings)
            cell = sheet.cell(row_index, 0)
            if cell.ctype == xlrd.XL_CELL_NUMBER:
                ref = str(int(cell.value))
            else:
                ref = str(cell.value).strip() if cell.value else ''

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
        # Group result lines by Reference to handle total quantities
        grouped_lines = {}
        for line in self.line_ids:
            if line.reference not in grouped_lines:
                grouped_lines[line.reference] = self.env['import.shipment.excel.line']
            grouped_lines[line.reference] |= line

        for ref, lines in grouped_lines.items():
            total_excel_qty = sum(lines.mapped('quantity'))
            excel_price = lines[0].excel_price
            
            target_lines = self.env['import.shipment'].search([
                ('name', '=', ref),
                ('state', 'not in', ['done', 'imported', 'cancel']) 
            ], order='expected_date asc, id asc')
            
            if target_lines:
                total_ordered = sum(target_lines.mapped('ordered_qty'))
                odoo_price = target_lines[0].price_unit
                msgs = []
                state = 'success'
                
                if abs(odoo_price - excel_price) > 0.01:
                    state = 'warning'
                    msgs.append(_('Fiyat farkı (Sipariş: %s, Excel: %s)') % (odoo_price, excel_price))

                if total_excel_qty > total_ordered:
                    state = 'warning'
                    msgs.append(_('Fazla sevkiyat (Siparişi Aşıyor: %s > %s)') % (total_excel_qty, total_ordered))

                if not msgs:
                    msgs.append(_('Eşleşme bulundu (%s satıra dağıtılacak)') % len(target_lines))

                lines.write({
                    'match_ids': [(6, 0, target_lines.ids)],
                    'odoo_price': odoo_price,
                    'state': state,
                    'message': ' | '.join(msgs)
                })
            else:
                lines.write({
                    'state': 'failed', 
                    'message': _('Eşleşen sevkiyat satırı bulunamadı.')
                })

        self.write({'state': 'validated'})
        return self._reopen_wizard()

    def action_confirm(self):
        self.ensure_one()
        valid_lines = self.line_ids.filtered(lambda l: l.state in ['success', 'warning'])
        if not valid_lines:
            raise UserError(_("Aktarılacak geçerli satır yok."))

        pickings = self.env['stock.picking']
        shipments_map = {}
        
        # Batch by Date
        dates = list(set(valid_lines.mapped('date')))
        for d in dates:
            date_lines = valid_lines.filtered(lambda l: l.date == d)
            shipments_to_process = self.env['import.shipment']
            
            for line in date_lines:
                remaining_qty = line.quantity
                # Sort matching lines by expected date
                sorted_targets = line.match_ids.sorted(lambda l: (l.expected_date or fields.Date.today(), l.id))
                
                for idx, sl in enumerate(sorted_targets):
                    if remaining_qty <= 0:
                        break
                    
                    # FIFO logic
                    open_qty_for_this = max(0, sl.ordered_qty - sl.imported_qty)
                    
                    if idx == len(sorted_targets) - 1:
                        # Last line of the match set takes the surplus
                        qty_to_write = remaining_qty
                    else:
                        qty_to_write = min(open_qty_for_this, remaining_qty)
                    
                    if qty_to_write > 0:
                        sl.imported_qty += qty_to_write
                        shipments_to_process |= sl
                        shipments_map[sl.id] = shipments_map.get(sl.id, 0.0) + qty_to_write
                        remaining_qty -= qty_to_write

            if shipments_to_process:
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
        ctx = dict(self.env.context)
        ctx.update({'wizard_id': self.id})
        return {
            'name': _('Excel ile Aktar'),
            'type': 'ir.actions.act_window',
            'res_model': 'import.shipment.excel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
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
