# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Mailing Unsubscribe Fix',
    'summary': 'Fixes unsubscribe URL replacement issue in mass mailing',
    'description': """
This module fixes the unsubscribe URL replacement issue where the placeholder
'/unsubscribe_from_list' in email templates was not being properly replaced
with the actual unsubscribe URL, causing 404 errors when users clicked unsubscribe.
    """,
    'version': '1.0.0',
    'category': 'Marketing/Email Marketing',
    'author': 'Tugay Hatil',
    'website': 'https://github.com/TugayHatil',
    'depends': ['mass_mailing'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
