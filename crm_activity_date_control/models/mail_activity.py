from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.constrains('date_deadline', 'res_id', 'res_model', 'activity_type_id')
    def _check_crm_activity_deadline(self):
        """
        CRM modülündeki aktiviteler için aşama bazlı dinamik tarih kontrolü.
        """
        for activity in self:
            if activity.res_model == 'crm.lead' and activity.res_id and activity.activity_type_id:
                # Bağlı olan CRM Fırsatını bul
                lead = self.env['crm.lead'].browse(activity.res_id)
                
                if lead.exists():
                    # Aktivite türü içerisindeki konfigürasyonlarda eşleşen aşamayı ara
                    config = activity.activity_type_id.crm_stage_config_ids.filtered(
                        lambda c: c.stage_id.id == lead.stage_id.id
                    )
                    
                    if config:
                        # Eğer bu aşama için bir kural tanımlanmışsa kontrolü yap
                        config = config[0]  # İlk eşleşen kuralı al
                        if activity.date_deadline:
                            today = fields.Date.today()
                            max_allowed_date = today + timedelta(days=config.days_limit)
                            
                            if activity.date_deadline > max_allowed_date:
                                # Kullanıcının girdiği özel uyarı mesajını göster
                                raise ValidationError(config.warning_message)
