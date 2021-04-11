# -*- coding: utf-8 -*-
{
    'name': "Solid Reports",

    'summary': """""",

    'description': """
    """,

    'author': "Alargm Ahmed",


    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sale_management','account','sale_management','purchase','stock','account_accountant'],

    'data': [
        'reports/cheque_printing.xml',
        'reports/tax_invoice_report.xml',
        'reports/delivery_note_report.xml',
        'reports/proforma_invoice_report.xml',
        'reports/quotation_report.xml',
        'reports/order_conformation_report.xml',
        'reports/credit_note_report.xml',
        'reports/purchase_order_report.xml',
        'reports/good_receive_note_report.xml',
        'reports/good_return_note_report.xml',
        'reports/receipt_voucher_report.xml',
        # 'reports/header_and_footer.xml',


   ],
    'application':True,
    'sequence' : 0,

}
