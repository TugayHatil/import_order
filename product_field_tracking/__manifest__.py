{
    'name': 'Product Field Tracking',
    'version': '16.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Log changes to selected product fields in the chatter.',
    'description': """
Product Field Tracking
======================
This module allows users to dynamically select which product fields should be tracked in the chatter.
Configuration is available under Inventory > Configuration > Product Log.
""",
    'author': 'Tugay Hatil',
    'depends': ['product', 'stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_log_config_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
