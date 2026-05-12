# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
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

            # CRITICAL FIX: Apply URL replacement AFTER all other processing
            # This ensures our fix works even with web_branding and other modules
            if not tools.is_html_empty(res.get('body')):
                original_body = res['body']
                
                # Comprehensive URL replacement - handle all possible patterns
                body_to_process = res['body']
                
                # Pattern 1: Absolute URL with base_url
                pattern1 = re.compile(rf'{re.escape(base_url)}/unsubscribe_from_list([\'"?>])', re.IGNORECASE)
                body_to_process = pattern1.sub(rf'{unsubscribe_url}\1', body_to_process)
                
                # Pattern 2: Relative URL with leading slash
                pattern2 = re.compile(r'/unsubscribe_from_list([\'"?>])', re.IGNORECASE)
                body_to_process = pattern2.sub(rf'{unsubscribe_url}\1', body_to_process)
                
                # Pattern 3: Without leading slash
                pattern3 = re.compile(r'unsubscribe_from_list([\'"?>])', re.IGNORECASE)
                body_to_process = pattern3.sub(rf'{unsubscribe_url}\1', body_to_process)
                
                # Pattern 4: HTML href attribute patterns
                pattern4 = re.compile(r'href=["\']?/unsubscribe_from_list["\']?', re.IGNORECASE)
                body_to_process = pattern4.sub(f'href="{unsubscribe_url}"', body_to_process)
                
                # Pattern 5: General pattern for any context
                pattern5 = re.compile(r'unsubscribe_from_list', re.IGNORECASE)
                body_to_process = pattern5.sub(unsubscribe_url, body_to_process)
                
                # Same comprehensive patterns for view URLs
                pattern1_view = re.compile(rf'{re.escape(base_url)}/view([\'"?>])', re.IGNORECASE)
                body_to_process = pattern1_view.sub(rf'{view_url}\1', body_to_process)
                
                pattern2_view = re.compile(r'/view([\'"?>])', re.IGNORECASE)
                body_to_process = pattern2_view.sub(rf'{view_url}\1', body_to_process)
                
                pattern4_view = re.compile(r'href=["\']?/view["\']?', re.IGNORECASE)
                body_to_process = pattern4_view.sub(f'href="{view_url}"', body_to_process)
                
                res['body'] = body_to_process

                # Log if body changed
                if original_body != res['body']:
                    _logger.info("Mass Mailing Fix: Email body was modified successfully")
                    _logger.info(f"Mass Mailing Fix: Final unsubscribe URL in body: {unsubscribe_url}")
                else:
                    _logger.warning("Mass Mailing Fix: No URL replacement made - checking body content...")
                    _logger.info(f"Mass Mailing Fix: Body contains unsubscribe_from_list: {'unsubscribe_from_list' in res['body']}")

            # add headers
            res.setdefault("headers", {}).update({
                'List-Unsubscribe': f'<{unsubscribe_oneclick_url}>',
                'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
                'Precedence': 'list',
                'X-Auto-Response-Suppress': 'OOF',  # avoid out-of-office replies from MS Exchange
            })
        return res
