from odoo import models, fields, api

class CrmActivityStageConfig(models.Model):
    _name = 'crm.activity.stage.config'
    _description = 'CRM Activity Stage Configuration'

    activity_type_id = fields.Many2one(
        'mail.activity.type', 
        string='Activity Type', 
        ondelete='cascade', 
        required=True
    )
    stage_id = fields.Many2one(
        'crm.stage', 
        string='CRM Stage', 
        required=True
    )
    days_limit = fields.Integer(
        string='Days Limit', 
        default=3, 
        required=True
    )
    warning_message = fields.Char(
        string='Warning Message', 
        required=True, 
        translate=True
    )

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    crm_stage_config_ids = fields.One2many(
        'crm.activity.stage.config', 
        'activity_type_id', 
        string='CRM Stage Configurations'
    )
