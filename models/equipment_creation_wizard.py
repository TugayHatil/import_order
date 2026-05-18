# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EquipmentCreationWizard(models.TransientModel):
    _name = 'equipment.creation.wizard'
    _description = 'Equipment Creation Wizard'

    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True
    )
    product_name = fields.Char(
        string='Product Name',
        readonly=True
    )
    category_id = fields.Many2one(
        'maintenance.equipment.category',
        string='Category',
        required=True
    )
    equipment_name = fields.Char(
        string='Equipment Name',
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'product_name' in fields_list and res.get('product_id'):
            product = self.env['product.template'].browse(res['product_id'])
            res['product_name'] = product.name
            res['equipment_name'] = product.name
        return res

    def action_create_equipment(self):
        """Create equipment and link to product"""
        self.ensure_one()
        
        # Create equipment
        equipment = self.env['maintenance.equipment'].create({
            'name': self.equipment_name,
            'category_id': self.category_id.id,
            'active': True,
        })
        
        # Link equipment to product
        self.product_id.equipment_id = equipment.id
        
        # Close wizard
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Cancel equipment creation"""
        return {'type': 'ir.actions.act_window_close'}
