# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Mailing Unsubscribe Fix',
    'summary': 'Fixes unsubscribe URL replacement issue in mass mailing',
    'description': """
This module fixes the unsubscribe URL replacement issue where the placeholder
'/unsubscribe_from_list' in email templates was not being properly replaced
with the actual unsubscribe URL, causing 404 errors when users clicked unsubscribe.

Version 2.0 includes comprehensive regex patterns to handle all possible URL formats
and overrides web_branding module interference to ensure unsubscribe links work
correctly in all scenarios.
    """,
    'version': '2.0.0',
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
