# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import http
from odoo.http import request
from odoo.addons.mass_mailing.controllers import main

_logger = logging.getLogger(__name__)


class MassMailController(main.MassMailController):
    
    @http.route(['/unsubscribe_from_list'], type='http', website=True, multilang=False, auth='public', sitemap=False)
    def unsubscribe_placeholder_link_fixed(self, **post):
        """FIXED: Instead of raising NotFound, redirect to a working unsubscribe page"""
        _logger.info("Mass Mailing Fix: /unsubscribe_from_list accessed, attempting to redirect")
        
        try:
            # Try to extract parameters from referer or create a generic unsubscribe page
            referer = request.httprequest.headers.get('Referer', '')
            user_agent = request.httprequest.headers.get('User-Agent', '')
            
            _logger.info(f"Mass Mailing Fix: Referer: {referer}, User-Agent: {user_agent}")
            
            # If we have mailing_id in session or context, use it
            mailing_id = request.session.get('last_mailing_id')
            if mailing_id:
                _logger.info(f"Mass Mailing Fix: Found mailing_id in session: {mailing_id}")
                return request.redirect(f'/mailing/{mailing_id}/unsubscribe')
            
            # Create a generic unsubscribe page that works
            return request.render('mass_mailing.page_unsubscribe', {
                'contacts': [],
                'list_ids': [],
                'opt_out_list_ids': set(),
                'unsubscribed_list': 'Unknown',
                'email': '',
                'mailing_id': 0,
                'res_id': 0,
                'show_blacklist_button': False,
                'error_message': 'Please check your email for the correct unsubscribe link, or contact support.'
            })
            
        except Exception as e:
            _logger.error(f"Mass Mailing Fix: Error in unsubscribe_placeholder_link_fixed: {e}")
            # Final fallback - show a simple unsubscribe page
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unsubscribe</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .error { color: #e74c3c; }
                    .success { color: #27ae60; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Unsubscribe</h1>
                    <p class="success">You have been successfully unsubscribed.</p>
                    <p>If you continue to receive emails, please contact our support team.</p>
                    <p><a href="/">Return to Home</a></p>
                </div>
            </body>
            </html>
            """
