{
    'name': 'Customer Product Name',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'product',
    'description':
        """
        This Module add below functionality into odoo

        1.Add Product Customer Name\n

    """,
    'summary': 'add customer in product',
    'author': 'Master Key',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
