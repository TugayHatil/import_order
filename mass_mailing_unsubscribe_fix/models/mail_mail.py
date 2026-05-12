# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, tools


class MailMail(models.Model):
    """Override to fix unsubscribe URL replacement issue"""
    _inherit = ['mail.mail']

    def _send_prepare_values(self, partner=None):
        """Override to fix the unsubscribe URL replacement logic"""
        res = super(MailMail, self)._send_prepare_values(partner)
        
        if self.mailing_id and res.get('email_to'):
            base_url = self.mailing_id.get_base_url()
            emails = tools.email_split(res.get('email_to')[0])
            email_to = emails and emails[0] or False

            unsubscribe_url = self.mailing_id._get_unsubscribe_url(email_to, self.res_id)
            unsubscribe_oneclick_url = self.mailing_id._get_unsubscribe_oneclick_url(email_to, self.res_id)
            view_url = self.mailing_id._get_view_url(email_to, self.res_id)

            # Fix: replace both absolute and relative unsubscribe URLs
            if not tools.is_html_empty(res.get('body')):
                # First try absolute URL replacement (original behavior)
                if f'{base_url}/unsubscribe_from_list' in res['body']:
                    res['body'] = res['body'].replace(
                        f'{base_url}/unsubscribe_from_list',
                        unsubscribe_url,
                    )
                # Then try relative URL replacement (fix for templates using relative URLs)
                elif '/unsubscribe_from_list' in res['body']:
                    res['body'] = res['body'].replace(
                        '/unsubscribe_from_list',
                        unsubscribe_url,
                    )
                
                # Same fix for view URLs
                if f'{base_url}/view' in res.get('body'):
                    res['body'] = res['body'].replace(
                        f'{base_url}/view',
                        view_url,
                    )
                elif '/view' in res.get('body'):
                    res['body'] = res['body'].replace(
                        '/view',
                        view_url,
                    )

            # add headers
            res.setdefault("headers", {}).update({
                'List-Unsubscribe': f'<{unsubscribe_oneclick_url}>',
                'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
                'Precedence': 'list',
                'X-Auto-Response-Suppress': 'OOF',  # avoid out-of-office replies from MS Exchange
            })
        return res
