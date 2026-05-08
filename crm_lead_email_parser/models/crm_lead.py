import re
from odoo import models, api, tools

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}
        
        body = msg_dict.get('body', '')
        if body:
            # Convert HTML body to plain text to easily parse the text
            plaintext_body = tools.html2plaintext(body)
            
            # Extract fields based on the specific format
            name_pattern = re.search(r'1\.\s*Ad:\s*(.*?)(?=2\.\s*E-posta:|$)', plaintext_body, re.DOTALL | re.IGNORECASE)
            phone_pattern = re.search(r'3\.\s*Telefon:\s*(.*?)(?=4\.\s*Size nasıl yardımcı olabiliriz\?:|$)', plaintext_body, re.DOTALL | re.IGNORECASE)
            desc_pattern = re.search(r'4\.\s*Size nasıl yardımcı olabiliriz\?:\s*(.*)', plaintext_body, re.DOTALL | re.IGNORECASE)
            
            if name_pattern:
                contact_name = name_pattern.group(1).strip()
                if contact_name:
                    custom_values['contact_name'] = contact_name
            
            if phone_pattern:
                mobile = phone_pattern.group(1).strip()
                if mobile:
                    custom_values['mobile'] = mobile
            
            if desc_pattern:
                description = desc_pattern.group(1).strip()
                if description:
                    custom_values['description'] = description

        return super(CrmLead, self).message_new(msg_dict, custom_values)
