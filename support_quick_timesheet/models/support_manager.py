from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SupportManager(models.AbstractModel):
    _name = 'support.manager'
    _description = 'Support Manager Helper'

    @api.model
    def get_support_data(self):
        """ Fetch data for the frontend popup """
        partners = self.env['res.partner'].search_read(
            [('is_support_customer', '=', True)],
            ['id', 'display_name']
        )
        types = self.env['support.type'].search_read(
            [('active', '=', True)],
            ['id', 'name']
        )
        slots = self.env['support.slot'].search_read(
            [],
            ['id', 'name', 'duration']
        )
        return {
            'partners': partners,
            'types': types,
            'slots': slots,
        }

    @api.model
    def create_timesheet(self, partner_id, type_id, contact_person, slot_id):
        """ Create a timesheet entry based on popup selection """
        if not partner_id or not type_id or not contact_person or not slot_id:
            raise UserError(_("Missing required information."))

        _logger.info("Creating timesheet for partner_id: %s, type_id: %s, slot_id: %s", partner_id, type_id, slot_id)
        
        partner = self.env['res.partner'].browse(int(partner_id))
        support_type = self.env['support.type'].browse(int(type_id))
        slot = self.env['support.slot'].browse(int(slot_id))
        
        # Find support task for this partner
        task = self.env['project.task'].search([
            ('partner_id', '=', partner.id),
            ('is_support_task', '=', True)
        ], limit=1)
        
        _logger.info("Found task: %s", task.id if task else "None")

        if not task:
            raise UserError(_("No support task found for customer: %s") % partner.name)

        employee = self.env.user.employee_id
        if not employee:
            raise UserError(_("Current user does not have a related employee. Cannot create timesheet."))

        # Create timesheet
        vals = {
            'name': f"{contact_person} - {support_type.name}",
            'project_id': task.project_id.id,
            'task_id': task.id,
            'employee_id': employee.id,
            'unit_amount': slot.duration / 60.0,
            'date': fields.Date.today(),
        }
        _logger.info("Creating analytic line with vals: %s", vals)
        timesheet = self.env['account.analytic.line'].create(vals)

        return {
            'status': 'success',
            'timesheet_id': timesheet.id
        }

from odoo import http
from odoo.http import request

class SupportController(http.Controller):
    @http.route('/support/quick_form', type='http', auth='user')
    def support_quick_form(self, **kwargs):
        """ Render a minimal standalone support form """
        return request.render('support_quick_timesheet.standalone_form_template')
