# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

{
    'name': 'Import Pricelist',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'MRP',
    'description':
        """
        This Module add below functionality into odoo

        1.Import sale, Vendor and product pricelist from Excel File\n
        
    """,
    'summary': 'Import pricelist',
    'author': 'Master Key',
    'depends': ['sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_sale_pricelist.xml',
        'wizard/import_vendor_pricelist.xml',
        'wizard/import_product_pricelist.xml',
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
