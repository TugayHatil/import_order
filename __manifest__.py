# -*- coding: utf-8 -*-
{
    'name': 'Equipment Management',
    'version': '16.0.1.0.0',
    'category': 'Maintenance',
    'summary': 'Link products with equipment and manage equipment-related invoices',
    'description': """
        Equipment Management Addon
        ==========================
        
        This addon adds the following features:
        
        * Add boolean field to product to mark it as equipment
        * Link products to maintenance equipment
        * Create equipment directly from product form
        * Smart buttons on equipment to view related products and invoices
        * Track invoices related to equipment through product links
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'product',
        'maintenance',
        'account',
    ],
    'data': [
        'views/product_template_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/equipment_creation_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
