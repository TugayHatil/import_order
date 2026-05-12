# -*- coding: utf-8 -*-
from . import models
from . import controllers
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Mailing Unsubscribe Fix',
    'summary': 'Fixes unsubscribe URL replacement issue in mass mailing',
    'description': """
This module fixes the unsubscribe URL replacement issue where the placeholder
'/unsubscribe_from_list' in email templates was not being properly replaced
with the actual unsubscribe URL, causing 404 errors when users clicked unsubscribe.

Version 4.0 includes all missing unsubscribe templates and a direct route override
for /unsubscribe_from_list, ensuring complete compatibility with both Community and 
Premium/Enterprise versions.
    """,
    'version': '4.0.0',
    'category': 'Marketing/Email Marketing',
    'author': 'Tugay Hatil',
    'website': 'https://github.com/TugayHatil',
    'depends': ['mass_mailing'],
    'data': [
        'security/ir.model.access.csv',
        'views/unsubscribe_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
