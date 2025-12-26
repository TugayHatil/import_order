{
    'name': 'Import Shipment Management',
    'version': '16.0.1.0.0',
    'summary': 'Manage import shipments, consolidation, and partial receipts.',
    'description': """
        This module allows managing import shipments by:
        - Preventing automatic picking creation for import vendors.
        - Collecting PO lines into import shipment lines.
        - Updating quantities via Excel.
        - Creating consolidated incoming pickings.
        - Integrating with MRP for properly calculating planned supply.
    """,
    'category': 'Inventory/Purchase',
    'author': 'Antigravity',
    'depends': ['purchase', 'stock', 'mrp', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/import_shipment_views.xml',
        'views/res_partner_views.xml',
        'wizard/import_shipment_excel_views.xml', # To be implemented
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
