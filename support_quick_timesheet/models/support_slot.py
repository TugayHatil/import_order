from odoo import models, fields

class SupportSlot(models.Model):
    _name = 'support.slot'
    _description = 'Support Time Slot'
    _order = 'sequence, id'

    name = fields.Char(string='Label', required=True, help="Display label on the button (e.g., 15 dk)")
    duration = fields.Float(string='Duration (Minutes)', required=True, help="Duration in minutes")
    sequence = fields.Integer(string='Sequence', default=10)

    @property
    def duration_hours(self):
        return self.duration / 60.0
