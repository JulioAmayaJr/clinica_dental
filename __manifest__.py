{
    'name': 'Clínica Dental',
    'version': '19.0.1.0.0',
    'summary': 'Gestión integral para clínicas dentales',
    'description': '''
        Sistema completo de gestión para clínicas dentales:
        pacientes, citas, tratamientos, odontograma,
        documentos médicos e imágenes con flujo de revisión.
    ''',
    'author': 'Clínica Dental Dev',
    'category': 'Healthcare',
    'depends': [
        'base',
        'mail',
        'calendar',
        'contacts',
        'sale_management',
        'account',
        'web',
        'website_crm',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/paciente_views.xml',
        'views/cita_views.xml',
        'views/tratamiento_views.xml',
        'views/odontograma_views.xml',
        'views/documento_medico_views.xml',
        'views/presupuesto_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
