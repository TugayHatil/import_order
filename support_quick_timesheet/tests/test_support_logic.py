from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestSupportLogic(TransactionCase):

    def setUp(self):
        super(TestSupportLogic, self).setUp()
        self.Partner = self.env['res.partner']
        self.Project = self.env['project.project']
        self.Task = self.env['project.task']
        self.SupportType = self.env['support.type']
        self.SupportSlot = self.env['support.slot']
        self.SupportManager = self.env['support.manager']

        # Create support data
        self.customer = self.Partner.create({
            'name': 'Support Customer Test',
            'is_support_customer': True,
        })
        self.support_type = self.SupportType.create({'name': 'Test Type'})
        self.slot = self.SupportSlot.create({
            'name': '15 dk',
            'duration': 15.0
        })

        self.project = self.Project.create({'name': 'Support Project'})
        self.support_task = self.Task.create({
            'name': 'Support Task Test',
            'project_id': self.project.id,
            'partner_id': self.customer.id,
            'is_support_task': True,
        })

    def test_01_create_timesheet_success(self):
        """ Test successful timesheet creation via support manager """
        # Ensure user has employee
        employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'user_id': self.env.user.id
        })

        result = self.SupportManager.create_timesheet(
            self.customer.id,
            self.support_type.id,
            'John Doe',
            self.slot.id
        )

        self.assertEqual(result['status'], 'success')
        timesheet = self.env['account.analytic.line'].browse(result['timesheet_id'])
        self.assertEqual(timesheet.unit_amount, 0.25) # 15/60
        self.assertEqual(timesheet.name, 'John Doe - Test Type')
        self.assertEqual(timesheet.task_id.id, self.support_task.id)

    def test_02_create_timesheet_no_task(self):
        """ Test error when no support task exists for customer """
        self.support_task.unlink()
        
        with self.assertRaises(UserError):
            self.SupportManager.create_timesheet(
                self.customer.id,
                self.support_type.id,
                'John Doe',
                self.slot.id
            )
