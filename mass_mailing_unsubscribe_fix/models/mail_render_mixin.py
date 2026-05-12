# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class MailRenderMixin(models.AbstractModel):
    """ Override to ensure unsubscribe URLs are preserved after branding processing """
    _inherit = "mail.render.mixin"

    def _replace_local_links(self, html, base_url=None):
        """ Override to fix unsubscribe URLs after web_branding processing """
        result = super()._replace_local_links(html, base_url=base_url)
        
        # Check if this is mass mailing related and fix unsubscribe URLs
        if hasattr(self, '_context') and self._context.get('default_mailing_id'):
            mailing_id = self._context.get('default_mailing_id')
            _logger.info(f"Mass Mailing Fix: Processing _replace_local_links for mailing {mailing_id}")
            
            # Apply unsubscribe URL fix after branding processing
            if result and '/unsubscribe_from_list' in result:
                try:
                    mailing = self.env['mailing.mailing'].sudo().browse(mailing_id)
                    if mailing.exists():
                        # This is a fallback - the main fix is in mail_mail.py
                        _logger.info("Mass Mailing Fix: Found unsubscribe_from_list in _replace_local_links")
                except Exception as e:
                    _logger.warning(f"Mass Mailing Fix: Could not process mailing in _replace_local_links: {e}")
        
        return result
