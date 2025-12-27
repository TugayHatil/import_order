from odoo import models, fields, api, _

class ImportShipmentDeleteWizard(models.TransientModel):
    _name = 'import.shipment.delete.wizard'
    _description = 'Import Shipment Deletion Confirmation'

    message = fields.Text(string='Mesaj', default='Kayıtları silmek istediğinize emin misiniz?')

    def action_confirm(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return
        
        records = self.env['import.shipment'].browse(active_ids)
        return records.with_context(confirm_delete=True).unlink()
