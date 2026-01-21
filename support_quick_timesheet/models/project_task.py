from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_support_task = fields.Boolean(string='Is Support Task', default=False)
