from odoo import models, fields, api, _

class ImportShipmentDeleteWizard(models.TransientModel):
    _name = 'import.shipment.delete.wizard'
    _description = 'Import Shipment Deletion Confirmation'

    message = fields.Text(string='Mesaj', default='Kayıtları silmek istediğinize emin misiniz?')

    def action_confirm(self):
        shipment_ids = self.env.context.get('shipment_ids_to_delete')
        if not shipment_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        records = self.env['import.shipment'].browse(shipment_ids)
        records.with_context(confirm_delete=True).unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
