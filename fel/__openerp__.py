# -*- encoding: UTF-8 -*-

{
    'name': 'Factura Electronica',
    'summary': """Web service integrado con Infile S.A""",
    'version': '8.0.1.0.',
    'description': """Factura Electronica para Guatemala""",
    'author': 'Osmin Cano --> osmincano@gmail.com',
    'website': 'https://pitaya.tech',
    'category': 'account',
    'depends': ['base', 'base_setup', 'account', 'document', 'account_cancel', 'product'],
    'data': [
        'views/api_view.xml',
        'views/account_journal_view.xml',
        'views/account_invoice_view.xml',
        'views/product_view.xml',
    ],
    'demo': [],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,


}
