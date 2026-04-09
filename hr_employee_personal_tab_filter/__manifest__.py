{
    'name': 'HR Employee Personal Tab Filter',
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': 'Hides Personal Information tab if employee company does not match user company.',
    'description': """
Çalışan Kartı Sekme Gizleme
===========================
Bu modül, bir çalışanın kartındaki 'Kişisel Bilgiler' (personal_information) sekmesini, 
yalnızca login olan kullanıcının bağlı olduğu çalışan kaydı ile görüntülenen çalışanın 
şirketi aynı ise gösterir. Farklı şirket durumunda bu sekmeyi gizler.
""",
    'author': 'Tugay Hatil',
    'website': 'https://github.com/TugayHatil',
    'depends': ['hr'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
