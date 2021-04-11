# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Master Key.
#
##############################################################################

{
    'name': 'MK Sale Receipt',
    'version': '14.0.1.0',
    'sequence': 2,
    'category': 'base',
    'description':
         """
        MK Treasury.
         """,
    'summary': 'MK Sale Receipt',
    'author': 'Master Key',
    'depends': ['sale'],
    'data': [
        'views/sale_report_template.xml',
        'views/sale_order_menu_template.xml',
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
