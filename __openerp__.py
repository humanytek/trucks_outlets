{
    'name': 'Trucks Outlets',
    'version': '1.0',
    'author': 'Humanytek',
    'website': 'http://humanytek.com',
    'depends': ['sale', 'sale_contract_type'],
    'data': [
        'security/ir.model.access.csv',
        'security/trucks_outlets_access_rules.xml',
        'views/trucks_outlets.xml',
        'views/sale_order.xml',
    ]
}
