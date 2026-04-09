from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_private_tab_visible = fields.Boolean(
        compute='_compute_is_private_tab_visible',
        string='Is Private Tab Visible'
    )

    def _compute_is_private_tab_visible(self):
        """
        Login olan kullanıcının bağlı olduğu çalışanın şirketi ile 
        görüntülenen çalışanın şirketi aynı mı kontrol eder.
        """
        # self.env.user.employee_id, kullanıcının bağlı olduğu çalışanı döner.
        # Birden fazla olması durumunda ilkini alıyoruz.
        current_user_employee = self.env.user.employee_id[:1]
        
        for rec in self:
            # Eğer login olan kullanıcıya bağlı bir çalışan kaydı yoksa 
            # veya şirketler uyuşmuyorsa sekmeyi gizlemek için False döneriz.
            if not current_user_employee or rec.company_id != current_user_employee.company_id:
                rec.is_private_tab_visible = False
            else:
                rec.is_private_tab_visible = True
