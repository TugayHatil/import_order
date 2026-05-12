# Mass Mailing Unsubscribe Fix

## Problem
In Odoo Premium, when users click the unsubscribe button in email marketing templates, they get a 404 error because the unsubscribe URL replacement logic fails to replace the placeholder `/unsubscribe_from_list` with the actual working unsubscribe URL.

## Root Cause
The URL replacement code in `mail_mail.py` only searches for `{base_url}/unsubscribe_from_list` (absolute URL) but templates use `/unsubscribe_from_list` (relative URL), so the replacement doesn't happen.

## Solution
This module overrides the `_send_prepare_values` method to handle both absolute and relative URLs:
- First tries absolute URL replacement (original behavior)
- Then tries relative URL replacement (the fix)
- Also applies the same fix to view URLs

## Installation
1. Copy this module to your Odoo addons directory
2. Update your addons list in Odoo
3. Install the "Mass Mailing Unsubscribe Fix" module
4. Restart Odoo server

## Compatibility
- Odoo 16.0 (Community and Enterprise/Premium)
- Depends on: mass_mailing

## Author
Tugay Hatil - https://github.com/TugayHatil

## License
LGPL-3
