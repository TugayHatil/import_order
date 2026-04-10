from odoo import models, fields, api
from datetime import timedelta

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def write(self, vals):
        """
        Aşama değiştiğinde açık aktivitelerin tarihlerini yeni aşamaya göre kontrol et.
        """
        res = super(CrmLead, self).write(vals)
        if 'stage_id' in vals:
            for lead in self:
                lead._adjust_activities_by_stage_limit()
        return res

    def _adjust_activities_by_stage_limit(self):
        """
        Fırsatın açık aktivitelerini mevcut aşamanın gün kısıtına göre günceller.
        """
        self.ensure_one()
        today = fields.Date.today()
        
        # Sadece bu lead'e bağlı ve tamamlanmamış (açık) aktiviteleri al
        for activity in self.activity_ids:
            # Aktivite türü ve mevcut aşama için konfigürasyon var mı bak
            config = activity.activity_type_id.crm_stage_config_ids.filtered(
                lambda c: c.stage_id.id == self.stage_id.id
            )
            
            if config:
                config = config[0]
                # Maksimum izin verilen tarihi hesapla
                max_allowed_date = today + timedelta(days=config.days_limit)
                
                # Eğer planlanan tarih, izin verilen maksimum tarihten büyükse revize et
                if activity.date_deadline and activity.date_deadline > max_allowed_date:
                    activity.write({'date_deadline': max_allowed_date})
