# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        # 1. Get tracked fields for this model
        log_configs = self.env['product.log.config'].sudo().search([
            ('model_id.model', '=', 'product.template')
        ])
        tracked_field_names = log_configs.mapped('field_id.name')
        
        # 2. Identify which of the changed fields are tracked
        fields_to_track = [f for f in vals.keys() if f in tracked_field_names]
        
        if not fields_to_track:
            return super().write(vals)

        # 3. Capture old values before update
        # Using read() because it's efficient for many records
        old_data = self.read(fields_to_track)
        old_values_map = {d['id']: d for d in old_data}

        # 4. Perform the write
        res = super(ProductTemplate, self).write(vals)

        # 5. Generate tracking logs
        # We perform this sudo() to ensure logging works regardless of user permissions on tracking models
        self.sudo()._log_dynamic_changes(fields_to_track, old_values_map)

        return res

    def _log_dynamic_changes(self, fields_to_track, old_values_map):
        TrackingValue = self.env['mail.tracking.value']
        # Fetch metadata for all tracked fields in one go for efficiency
        fields_metadata = self.fields_get(fields_to_track)
        
        for record in self:
            tracking_values = []
            for field_name in fields_to_track:
                old_raw = old_values_map.get(record.id, {}).get(field_name)
                new_raw = record[field_name]
                field = record._fields[field_name]
                
                # Normalize values for comparison and tracking
                if field.type == 'many2one':
                    # read() returns ID for many2one in Odoo 16
                    old_id = old_raw[0] if isinstance(old_raw, (list, tuple)) else old_raw
                    new_id = new_raw.id if new_raw else False
                    is_changed = old_id != new_id
                    
                    # Odoo's create_tracking_values expects recordsets for relational fields
                    o_val = record.env[field.comodel_name].browse(old_id) if old_id else record.env[field.comodel_name]
                    n_val = new_raw # This is already a recordset
                else:
                    is_changed = old_raw != new_raw
                    o_val, n_val = old_raw, new_raw

                if is_changed:
                    col_info = fields_metadata.get(field_name)
                    # Odoo v16 requires a metadata dict (col_info) with 'string' and 'type' keys
                    val = TrackingValue.create_tracking_values(
                        o_val, n_val, field_name, col_info, 100, record._name
                    )
                    if val:
                        tracking_values.append((0, 0, val))

            if tracking_values:
                # Post to chatter using the native tracking format
                record.message_post(
                    body='',
                    tracking_value_ids=tracking_values
                )
