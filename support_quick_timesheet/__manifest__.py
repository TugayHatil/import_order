{
    'name': 'Odoo Support Quick Timesheet',
    'version': '16.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Quick timesheet entry for support via popup',
    'author': 'Antigravity',
    'website': 'https://github.com/tugay',
    'depends': ['project', 'hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'views/support_type_views.xml',
        'views/support_slot_views.xml',
        'views/res_partner_views.xml',
        'views/project_task_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'support_quick_timesheet/static/src/scss/support_popup.scss',
            'support_quick_timesheet/static/src/xml/support_popup.xml',
            'support_quick_timesheet/static/src/js/support_popup.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
