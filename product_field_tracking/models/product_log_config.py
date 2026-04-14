# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductLogConfig(models.Model):
    _name = 'product.log.config'
    _description = 'Product Log Configuration'
    _rec_name = 'field_id'

    field_id = fields.Many2one(
        'ir.model.fields', 
        string='Field', 
        required=True, 
        ondelete='cascade',
        domain=[('model', 'in', ['product.template', 'product.product'])]
    )
    model_id = fields.Many2one(
        'ir.model', 
        string='Model', 
        related='field_id.model_id', 
        store=True, 
        readonly=True
    )
    field_name = fields.Char(related='field_id.name', string='Field Technical Name', readonly=True)
    field_description = fields.Char(related='field_id.field_description', string='Field Description', readonly=True)

    _sql_constraints = [
        ('field_unique', 'unique(field_id)', 'This field is already being tracked!')
    ]
