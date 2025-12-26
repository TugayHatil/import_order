{
    'name': 'Import Orders',
    'version': '16.0.1.0.0',
    'summary': 'Standalone module for managing import orders with custom models',
    'category': 'Purchase',
    'author': 'Antigravity / User',
    'depends': ['base', 'stock', 'product_manufacturer', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/import_order_line_wizard_views.xml',
        'views/import_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
