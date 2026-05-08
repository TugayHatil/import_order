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
            
            # Extract fields based on the specific format, being flexible with spaces
            name_pattern = re.search(r'1\.\s*Ad\s*:\s*(.*?)(?=2\.\s*E-posta\s*:|$)', plaintext_body, re.DOTALL | re.IGNORECASE)
            email_pattern = re.search(r'2\.\s*E-posta\s*:\s*(.*?)(?=3\.\s*Telefon\s*:|$)', plaintext_body, re.DOTALL | re.IGNORECASE)
            phone_pattern = re.search(r'3\.\s*Telefon\s*:\s*(.*?)(?=4\.\s*Size nasıl yardımcı olabiliriz\s*\?:|$)', plaintext_body, re.DOTALL | re.IGNORECASE)
            desc_pattern = re.search(r'4\.\s*Size nasıl yardımcı olabiliriz\s*\?:\s*(.*)', plaintext_body, re.DOTALL | re.IGNORECASE)
            
            def clean_value(val):
                # Remove leading/trailing asterisks and spaces
                val = val.strip(' *')
                # Remove Odoo html2plaintext link references like [1] mailto:...
                val = re.sub(r'\s*\[\d+\]\s*(?:mailto:|http:|https:|ftp:)[^\s]*', '', val)
                return val.strip(' *')

            if name_pattern:
                contact_name = clean_value(name_pattern.group(1))
                if contact_name:
                    custom_values['contact_name'] = contact_name
                    custom_values['partner_name'] = contact_name
                    
            if email_pattern:
                raw_email_text = email_pattern.group(1)
                # Sadece e-posta adresini ayıklamak için
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_email_text)
                if email_match:
                    extracted_email = email_match.group(0)
                    custom_values['email_from'] = extracted_email
                    msg_dict['from'] = extracted_email
                    msg_dict['email_from'] = extracted_email
                else:
                    # Bulunamazsa düzeltilmiş halini dene
                    email_from = clean_value(raw_email_text)
                    if email_from:
                        custom_values['email_from'] = email_from
                        msg_dict['from'] = email_from
                        msg_dict['email_from'] = email_from
            
            if phone_pattern:
                phone_num = clean_value(phone_pattern.group(1))
                if phone_num:
                    custom_values['mobile'] = phone_num
                    custom_values['phone'] = phone_num
            
            if desc_pattern:
                description = clean_value(desc_pattern.group(1))
                if description:
                    custom_values['description'] = description

        return super(CrmLead, self).message_new(msg_dict, custom_values)
