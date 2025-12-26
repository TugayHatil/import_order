import base64
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ImportOrderLineWizard(models.TransientModel):
    _name = 'order.line.excel.import.wizard'
    _description = 'Excel Import Wizard'

    import_file = fields.Binary(string='Excel File', required=True)
    file_name = fields.Char(string='File Name')
    line_ids = fields.One2many('order.line.excel.import.line', 'wizard_id', string='All Preview Lines')
    
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('validated', 'Doğrulandı'),
        ('done', 'Tamamlandı')
    ], string='Durum', default='draft')

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    partner_id = fields.Many2one(
        'res.partner', 
        string='Tedarikçi', 
        domain=[('supplier_rank', '>', 0)]
    )
    
    import_order_id = fields.Many2one(
        'x_import_order',
        string='Import Order',
        default=lambda self: self.env.context.get('active_id')
    )


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
            if row_index == 0: continue
            ref_val, qty_val, price_val, status, message = self._parse_excel_row(sheet, row_index)
            preview_vals.append((0, 0, {
                'reference': ref_val,
                'quantity': qty_val,
                'excel_price_unit': price_val,
                'state': 'pending' if status == 'pending' else 'failed',
                'message': message
            }))
        
        self.write({
            'line_ids': [(5, 0, 0)] + preview_vals,
            'state': 'draft'
        })
        
        return self._reopen_wizard()

    def _parse_excel_row(self, sheet, row_index):
        try:
            ref = str(sheet.cell_value(row_index, 0)).strip()
            qty = float(sheet.cell_value(row_index, 1) or 0.0)
            price = float(sheet.cell_value(row_index, 2) or 0.0)
            return ref, qty, price, 'pending', ''
        except Exception as e:
            return '', 0.0, 0.0, 'failed', str(e)

    def action_validate(self):
        self.ensure_one()
        for line in self.line_ids:
            target_lines = self.env['x_import_order_line'].search([('x_teknik_referans', '=', line.reference)])
            if target_lines:
                odoo_price = target_lines[0].price_unit
                line.write({
                    'match_ids': [(6, 0, target_lines.ids)],
                    'import_price_unit': odoo_price,
                    'state': 'success' if abs(odoo_price - line.excel_price_unit) < 0.01 else 'warning',
                    'message': _('Eşleşme bulundu.') if abs(odoo_price - line.excel_price_unit) < 0.01 else _('Fiyat farkı var.')
                })
            else:
                line.write({'state': 'failed', 'message': _('Referans bulunamadı.')})

        self.write({'state': 'validated'})
        return self._reopen_wizard()

    def action_confirm(self):
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_("Lütfen devam etmeden önce bir Tedarikçi seçin."))
        
        # 1. Filter valid lines
        valid_lines = self.line_ids.filtered(lambda l: l.state in ['success', 'warning'])
        if not valid_lines:
            return {'type': 'ir.actions.act_window_close'}

        # 2. Create Purchase Order
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'date_order': fields.Date.today(),
            'company_id': self.env.company.id,
            'origin': self.import_order_id.name or _('Excel Import: %s') % self.file_name,
        })
        
        PurchaseOrderLine = self.env['purchase.order.line']

        for line in valid_lines:
            # 3. Update existing match if exists
            if line.match_ids:
                line.match_ids.write({'x_qty_incoming': line.quantity})
                
                # Get the technical reference ID from match_ids (taking the first one)
                import_line_id = line.match_ids[0].id
            else:
                import_line_id = False

            # 4. Create PO Line
            # We assume the product info comes from match_ids or needs to be found. 
            # In the wizard logic, we matched lines. 
            # If no match_ids but valid (e.g. forced), we might fail if we don't have product_id.
            # But the logic says 'warning' lines have a match but price diff. 'success' have match.
            # 'failed' have no match. So valid_lines ALWAYS have match_ids.
            
            if line.match_ids:
                matched_line = line.match_ids[0]
                PurchaseOrderLine.create({
                    'order_id': purchase_order.id,
                    'product_id': matched_line.product_id.id,
                    'name': matched_line.product_id.name, # Required field
                    'product_qty': line.quantity,
                    'price_unit': line.excel_price_unit, # Use Excel price
                    'date_planned': fields.Date.today(),
                    'product_uom': matched_line.product_id.uom_po_id.id,
                    'import_order_line_id': matched_line.id,
                })

        self.write({'state': 'done'})
        return {
            'name': _('Satınalma Siparişi'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_reset(self):
        self.write({'state': 'draft', 'line_ids': [(5, 0, 0)]})
        return self._reopen_wizard()

    def _reopen_wizard(self):
        return {
            'name': _('Excel ile Aktar'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.line.excel.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

class ImportOrderLineWizardLine(models.TransientModel):
    _name = 'order.line.excel.import.line'
    _description = 'Excel Import Wizard Preview Line'

    wizard_id = fields.Many2one('order.line.excel.import.wizard', string='Wizard', ondelete='cascade')
    reference = fields.Char(string='Referans')
    quantity = fields.Float(string='Miktar')
    import_price_unit = fields.Float(string='Import Birim Fiyat')
    excel_price_unit = fields.Float(string='Excel Birim Fiyat')
    match_ids = fields.Many2many('x_import_order_line', string='Matched Lines')
    currency_id = fields.Many2one(related='wizard_id.currency_id')
    state = fields.Selection([
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('warning', 'Kontrol'),
        ('failed', 'Başarısız')
    ], string='Durum', default='pending')
    message = fields.Char(string='Mesaj')
