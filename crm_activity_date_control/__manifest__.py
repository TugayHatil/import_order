{
    'name': 'CRM Activity Date Control',
    'version': '16.0.1.2.0',
    'category': 'Sales/CRM',
    'summary': 'Dynamic activity deadline control based on CRM stages and activity types.',
    'description': """
CRM Dinamik Aktivite Tarih Kontrolü
==================================
Bu modül, aktivite türleri (mail.activity_type) bazında, 
CRM aşamalarına göre özel planlama günü sınırları ve uyarı mesajları tanımlamanıza olanak tanır.
""",
    'author': 'Tugay Hatil',
    'website': 'https://github.com/TugayHatil',
    'depends': ['crm', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_activity_type_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
