# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    product_ids = fields.One2many(
        'product.template',
        'equipment_id',
        string='Products'
    )
    product_count = fields.Integer(
        string='Product Count',
        compute='_compute_product_count',
        store=True
    )
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count',
        store=True
    )

    @api.depends('product_ids')
    def _compute_product_count(self):
        for equipment in self:
            equipment.product_count = len(equipment.product_ids)

    @api.depends('product_ids')
    def _compute_invoice_count(self):
        for equipment in self:
            # Count invoices that contain products linked to this equipment
            invoice_lines = self.env['account.move.line'].search([
                ('product_id', 'in', equipment.product_ids.mapped('product_variant_ids').ids),
                ('move_id.move_type', '=', 'out_invoice'),
                ('move_id.state', 'in', ['posted', 'in_payment'])
            ])
            invoices = invoice_lines.mapped('move_id')
            equipment.invoice_count = len(invoices)

    def action_view_products(self):
        """Open related products"""
        self.ensure_one()
        return {
            'name': 'Related Products',
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

    def action_view_invoices(self):
        """Open related invoices"""
        self.ensure_one()
        # Get invoice lines containing products linked to this equipment
        product_variant_ids = self.product_ids.mapped('product_variant_ids').ids
        invoice_lines = self.env['account.move.line'].search([
            ('product_id', 'in', product_variant_ids),
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.state', 'in', ['posted', 'in_payment'])
        ])
        invoices = invoice_lines.mapped('move_id')
        
        return {
            'name': 'Related Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
            'context': {'default_move_type': 'out_invoice'},
        }
