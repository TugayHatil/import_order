from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.constrains('date_deadline', 'res_id', 'res_model')
    def _check_crm_activity_deadline(self):
        """
        CRM Stage 3 (Nihai Teklif) ise aktivite tarihini 3 gün ile sınırlandırır.
        """
        for activity in self:
            if activity.res_model == 'crm.lead' and activity.res_id:
                # Bağlı olan CRM Fırsatını bul
                lead = self.env['crm.lead'].browse(activity.res_id)
                
                # İş Kuralı: Stage ID 3 ise (Nihai Teklif)
                if lead.exists() and lead.stage_id.id == 3:
                    if activity.date_deadline:
                        today = fields.Date.today()
                        max_allowed_date = today + timedelta(days=3)
                        
                        if activity.date_deadline > max_allowed_date:
                            raise ValidationError(_("Maksimum 3 gün sonrası için planlama yapabilirsiniz."))
