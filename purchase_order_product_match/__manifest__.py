{
    'name': 'Purchase Order Product Match Extension',
    'version': '15.0.1.0.0',
    'summary': 'Match products by manufacturer_pref during PO import.',
    'description': """
        This module enhances the product matching logic during Purchase Order Excel imports.
        If a product cannot be found by its Internal Reference (default_code), 
        the system will automatically try to match it using the Manufacturer Pref (manufacturer_pref) field.
        This behavior is restricted only to Purchase Order and Purchase Order Line imports.
    """,
    'category': 'Inventory/Purchase',
    'author': 'Antigravity',
    'depends': ['purchase', 'product'],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
