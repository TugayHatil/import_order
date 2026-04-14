# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def write(self, vals):
        # 1. Get tracked fields for this model
        log_configs = self.env['product.log.config'].sudo().search([
            ('model_id.model', '=', 'product.product')
        ])
        tracked_field_names = log_configs.mapped('field_id.name')
        
        # 2. Identify which of the changed fields are tracked
        fields_to_track = [f for f in vals.keys() if f in tracked_field_names]
        
        if not fields_to_track:
            return super(ProductProduct, self).write(vals)

        # 3. Capture old values
        old_data = self.read(fields_to_track)
        old_values_map = {d['id']: d for d in old_data}

        # 4. Perform the write
        res = super(ProductProduct, self).write(vals)

        # 5. Generate tracking logs
        # Note: product.template logic is separate. If a template field is changed on a product.product record,
        # it might trigger product.template write too. We handle product.product specific fields here.
        self.sudo()._log_dynamic_changes(fields_to_track, old_values_map)

        return res

    def _log_dynamic_changes(self, fields_to_track, old_values_map):
        TrackingValue = self.env['mail.tracking.value']
        for record in self:
            tracking_values = []
            for field_name in fields_to_track:
                old_raw = old_values_map.get(record.id, {}).get(field_name)
                new_raw = record[field_name]

                if old_raw != new_raw:
                    field = record._fields[field_name]
                    val = TrackingValue.create_tracking_values(
                        old_raw, new_raw, field_name, field, record
                    )
                    if val:
                        tracking_values.append((0, 0, val))

            if tracking_values:
                record.message_post(
                    body='',
                    tracking_value_ids=tracking_values
                )
