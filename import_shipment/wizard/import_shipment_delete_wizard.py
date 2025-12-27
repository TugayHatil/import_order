from odoo import models, fields, api, _

class ImportShipmentDeleteWizard(models.TransientModel):
    _name = 'import.shipment.delete.wizard'
    _description = 'Import Shipment Deletion Confirmation'

    shipment_ids = fields.Many2many('import.shipment', string='Shipments to Delete')
    message = fields.Text(string='Mesaj', default='Kayıtları silmek istediğinize emin misiniz?')

    def action_confirm(self):
        if not self.shipment_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        self.shipment_ids.with_context(confirm_delete=True).unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
