# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, tools

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    """ Override to fix unsubscribe URL replacement issue """
    _inherit = ['mail.mail']

    def _send_prepare_values(self, partner=None):
        """ Override to fix the unsubscribe URL replacement logic """
        res = super(MailMail, self)._send_prepare_values(partner)
        
        if self.mailing_id and res.get('email_to'):
            base_url = self.mailing_id.get_base_url()
            emails = tools.email_split(res.get('email_to')[0])
            email_to = emails and emails[0] or False

            unsubscribe_url = self.mailing_id._get_unsubscribe_url(email_to, self.res_id)
            unsubscribe_oneclick_url = self.mailing_id._get_unsubscribe_oneclick_url(email_to, self.res_id)
            view_url = self.mailing_id._get_view_url(email_to, self.res_id)

            _logger.info(f"Mass Mailing Fix: Processing unsubscribe URL for mailing {self.mailing_id.id}")
            _logger.info(f"Mass Mailing Fix: Generated unsubscribe URL: {unsubscribe_url}")

            # Fix: replace both absolute and relative unsubscribe URLs
            if not tools.is_html_empty(res.get('body')):
                original_body = res['body']
                
                # First try absolute URL replacement (original behavior)
                if f'{base_url}/unsubscribe_from_list' in res['body']:
                    res['body'] = res['body'].replace(
                        f'{base_url}/unsubscribe_from_list',
                        unsubscribe_url,
                    )
                    _logger.info(f"Mass Mailing Fix: Replaced absolute URL {base_url}/unsubscribe_from_list")
                
                # Then try relative URL replacement (fix for templates using relative URLs)
                if '/unsubscribe_from_list' in res['body']:
                    res['body'] = res['body'].replace(
                        '/unsubscribe_from_list',
                        unsubscribe_url,
                    )
                    _logger.info(f"Mass Mailing Fix: Replaced relative URL /unsubscribe_from_list")
                
                # Additional fix: try without leading slash
                if 'unsubscribe_from_list' in res['body']:
                    res['body'] = res['body'].replace(
                        'unsubscribe_from_list',
                        unsubscribe_url,
                    )
                    _logger.info(f"Mass Mailing Fix: Replaced unsubscribe_from_list without slash")
                
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
                elif 'view' in res.get('body'):
                    res['body'] = res['body'].replace(
                        'view',
                        view_url,
                    )

                # Log if body changed
                if original_body != res['body']:
                    _logger.info("Mass Mailing Fix: Email body was modified")
                else:
                    _logger.warning("Mass Mailing Fix: No URL replacement made - check if unsubscribe_from_list exists in email body")

            # add headers
            res.setdefault("headers", {}).update({
                'List-Unsubscribe': f'<{unsubscribe_oneclick_url}>',
                'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
                'Precedence': 'list',
                'X-Auto-Response-Suppress': 'OOF',  # avoid out-of-office replies from MS Exchange
            })
        return res
