# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Master Key.
#
##############################################################################

from odoo import models, fields, api, _

class product_product(models.Model):
    _inherit = 'product.product'
    
    def name_get(self):
        result = super(product_product,self).name_get()
        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)
        
        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')
        product_template_ids = self.sudo().mapped('product_tmpl_id').ids
        
        if partner_ids:
            supplier_info = self.env['customer.product.line'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
        return result
        
        
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        product_ids = super(product_product,self)._name_search(name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)
        if not product_ids and self._context.get('partner_id'):
            customer_ids = self.env['customer.product.line']._search([
                ('name', '=', self._context.get('partner_id')),
                '|',
                ('product_code', operator, name),
                ('product_name', operator, name)], access_rights_uid=name_get_uid)
            if customer_ids:
                product_ids = self._search([('product_tmpl_id.customer_lines', 'in', customer_ids)], limit=limit, access_rights_uid=name_get_uid)
        return product_ids
        

class product_template(models.Model):
    _inherit = 'product.template'
    
    customer_lines = fields.One2many('customer.product.line','product_tmpl_id', string='Customer')

class customer_product_line(models.Model):
    _name = 'customer.product.line'
    _description = "Customer Product"
    
    name = fields.Many2one('res.partner', string='Customer', required="1")
    product_id = fields.Many2one('product.product', string='Product Variant')
    product_name = fields.Char('Product Name')
    product_code = fields.Char('product Code')
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.user.company_id)
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
