# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

import logging
import time
import tempfile
import binascii
import xlrd
import io
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning ,ValidationError
from odoo import models, fields, exceptions, api, _
import re
_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class VendorPricelist(models.TransientModel):
    _name = "import.vendor.pricelist"
    _description = "Import Vendor Pricelist"
    
    
    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product By',default='name')        
    import_prod_variant_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product Variant BY',default='name')

    def check_splcharacter(self ,test):
        # Make own character set and pass 
        # this as argument in compile method
     
        string_check= re.compile('@')
     
        # Pass the string in search 
        # method of regex object.
        if(string_check.search(str(test)) == None):
            return False
        else: 
            return True
    
    def make_pricelist(self, values):

        supplier_search = self.env['product.supplierinfo']

        if not values.get('vendor'):
            raise ValidationError(_("Vendor name is required."))
            return

        product_templ_obj = self.env['product.template']
        product_variant_obj = self.env['product.product']
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        partner_id = self.find_partner(values.get('vendor'))
        currency_id = self.find_currency(values.get('currency'))
        product_template_search = False
        product_variant_search = False

        if values.get('date_start') and values.get('date_end'):
            set_start_date = self.find_start_date(values.get('date_start'))
            set_end_date = self.find_end_date(values.get('date_end'))

        # Product Template
        if self.import_prod_option == 'barcode':
            product_template_search = product_templ_obj.search([('barcode',  '=',values['product_template'])],limit=1)

        elif self.import_prod_option == 'code':
            product_template_search = product_templ_obj.search([('default_code', '=',values['product_template'])],limit=1)
                        
        else:
            product_template_search = product_templ_obj.search([('name', '=',values['product_template'])],limit=1)
            

        # Product Variant
        if self.import_prod_variant_option == 'barcode':
            product_variant_search = product_variant_obj.search([('barcode',  '=',values['product_variant'])],limit=1)
            
        elif self.import_prod_variant_option == 'code':
            product_variant_search = product_variant_obj.search([('default_code', '=',values['product_variant'])],limit=1)
            
        else:       
            product_variant_search = product_variant_obj.search([('name', '=',values['product_variant'])],limit=1)

        if len(product_variant_search) == 0:
            if not product_variant_search:
                raise ValidationError(_("%s This product variant is not available in system, please enter valid product."%(values['product_variant']) ))
        if len(product_template_search) ==0:
            if not product_template_search:
                raise ValidationError(_("%s This product template is not available in system, please enter valid product."%(values['product_template']) ))        

        if product_variant_search and product_template_search:
            for variant in product_variant_search:
                if variant.product_tmpl_id.id != product_template_search.id:
                    raise ValidationError(_("The %s is not a variant of %s."%(variant.name,product_template_search.name) ))

        vals = {}
        if currency_id:
            vals = {
                'name' : partner_id.id,
                'product_tmpl_id' : product_template_search.id,
                'product_id' : product_variant_search[0].id or False,
                'min_qty' : values.get('min_qty') or 1,
                'price' : values.get('price') or 0,
                'currency_id' : currency_id.id,
                'date_start' : values.get('date_start') or False,
                'date_end' : values.get('date_end') or False,
                'delay' : values.get('delay') or 0,
            }
        else:
            vals = {
                'name' : partner_id.id,
                'product_tmpl_id' : product_template_search.id,
                'product_id' : product_variant_search[0].id,
                'min_qty' : values.get('min_qty') or 1,
                'price' : values.get('price') or 0,
                'date_start' : values.get('date_start') or False,
                'date_end' : values.get('date_end') or False,
                'delay' : values.get('delay') or 0,
            }
        main_list = values.keys()
        for i in main_list:
            model_id = self.env['ir.model'].search([('model','=','product.supplierinfo')])           
            if type(i) == bytes:
                normal_details = i.decode('utf-8')
            else:
                normal_details = i
            if normal_details.startswith('x_'):
                any_special = self.check_splcharacter(normal_details)
                if any_special:
                    split_fields_name = normal_details.split("@")
                    technical_fields_name = split_fields_name[0]
                    many2x_fields = self.env['ir.model.fields'].search([('name','=',technical_fields_name),('state','=','manual'),('model_id','=',model_id.id)])
                    if many2x_fields.id:
                        if many2x_fields.ttype in ['many2one','many2many']: 
                            if many2x_fields.ttype =="many2one":
                                if values.get(i):
                                    fetch_m2o = self.env[many2x_fields.relation].search([('name','=',values.get(i))])
                                    if fetch_m2o.id:
                                        vals.update({
                                            technical_fields_name: fetch_m2o.id
                                            })
                                    else:
                                        raise ValidationError(_('"%s" This custom field value "%s" not available in system') % (i , values.get(i)))
                            if many2x_fields.ttype =="many2many":
                                m2m_value_lst = []
                                if values.get(i):
                                    if ';' in values.get(i):
                                        m2m_names = values.get(i).split(';')
                                        for name in m2m_names:
                                            m2m_id = self.env[many2x_fields.relation].search([('name', '=', name)])
                                            if not m2m_id:
                                                raise ValidationError(_('"%s" This custom field value "%s" not available in system') % (i , name))
                                            m2m_value_lst.append(m2m_id.id)

                                    elif ',' in values.get(i):
                                        m2m_names = values.get(i).split(',')
                                        for name in m2m_names:
                                            m2m_id = self.env[many2x_fields.relation].search([('name', '=', name)])
                                            if not m2m_id:
                                                raise ValidationError(_('"%s" This custom field value "%s" not available in system') % (i , name))
                                            m2m_value_lst.append(m2m_id.id)

                                    else:
                                        m2m_names = values.get(i).split(',')
                                        m2m_id = self.env[many2x_fields.relation].search([('name', 'in', m2m_names)])
                                        if not m2m_id:
                                            raise ValidationError(_('"%s" This custom field value "%s" not available in system') % (i , m2m_names))
                                        m2m_value_lst.append(m2m_id.id)
                                vals.update({
                                    technical_fields_name : m2m_value_lst
                                    })        
                        else:
                            raise ValidationError(_('"%s" This custom field type is not many2one/many2many') % technical_fields_name)                                                                                                    
                    else:
                        raise ValidationError(_('"%s" This m2x custom field is not available in system') % technical_fields_name)
                else:
                    normal_fields = self.env['ir.model.fields'].search([('name','=',normal_details),('state','=','manual'),('model_id','=',model_id.id)])
                    if normal_fields.id:
                        if normal_fields.ttype ==  'boolean':
                            vals.update({
                                normal_details : values.get(i)
                                })
                        elif normal_fields.ttype == 'char':
                            vals.update({
                                normal_details : values.get(i)
                                })                              
                        elif normal_fields.ttype == 'float':
                            if values.get(i) == '':
                                float_value = 0.0
                            else:
                                float_value = float(values.get(i)) 
                            vals.update({
                                normal_details : float_value
                                })                              
                        elif normal_fields.ttype == 'integer':
                            if values.get(i) == '':
                                int_value = 0
                            else:
                                int_value = int(values.get(i)) 
                            vals.update({
                                normal_details : int_value
                                })                              
                        elif normal_fields.ttype == 'selection':
                            vals.update({
                                normal_details : values.get(i)
                                })                              
                        elif normal_fields.ttype == 'text':
                            vals.update({
                                normal_details : values.get(i)
                                })                              
                    else:
                        raise ValidationError(_('"%s" This custom field is not available in system') % normal_details)
        sale_id = supplier_search.create(vals)            

        return sale_id

    
    def find_start_date(self, start_date):
        DATETIME_FORMAT = "%Y-%m-%d"
        if date:
            try:
                i_date = datetime.strptime(start_date, DATETIME_FORMAT).date()
            except Exception:
                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
            return i_date
        else:
            raise ValidationError(_('Start Date field is blank in sheet Please add the date.'))

    
    def find_end_date(self, end_date):
        DATETIME_FORMAT = "%Y-%m-%d"
        if date:
            try:
                i_date = datetime.strptime(end_date, DATETIME_FORMAT).date()
            except Exception:
                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
            return i_date
        else:
            raise ValidationError(_('End Date field is blank in sheet Please add the date.'))

    
    def find_currency(self, name):
        currency_obj = self.env['res.currency']
        currency_search = currency_obj.search([('name', '=', name)])
        if currency_search:
            return currency_search

    
    def find_partner(self, name):
        partner_obj = self.env['res.partner']
        partner_search = partner_obj.search([('name', '=', name)])
        if partner_search:
            return partner_search
        else:
            partner_id = partner_obj.create({
                'name' : name
            })
            return partner_id

    
    def import_vendor_pricelist(self):

        if self.import_option == 'csv':
            if self.file:
                try:
                    keys = ['vendor', 'product_template', 'product_variant','min_qty', 'price', 'currency','date_start','date_end','delay']
                    csv_data = base64.b64decode(self.file)
                    data_file = io.StringIO(csv_data.decode("utf-8"))
                    data_file.seek(0)
                    file_reader = []
                    csv_reader = csv.reader(data_file, delimiter=',')
                    file_reader.extend(csv_reader)
                except Exception:
                    raise ValidationError(_("Invalid file!"))
                values = {}
                for i in range(len(file_reader)):
                    field = list(map(str, file_reader[i]))
                    count = 1
                    count_keys = len(keys)
                    if len(field) > count_keys:
                        for new_fields in field:
                            if count > count_keys :
                                keys.append(new_fields)                
                            count+=1                     
                    values = dict(zip(keys, field))
                    if values:
                        if i == 0:
                            continue
                        else:
                            values.update({'option':self.import_option})

                            res = self.make_pricelist(values)
            else:
                raise ValidationError(_('Please Seelect a file.'))
        else:
            if self.file:
                try:
                    fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.file))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)
                except:
                    raise ValidationError(_("Invalid file!"))
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        line_fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                        
                        start_date_string = False
                        end_dt_string = False
                        delay = line[8] or 1

                        if line[6] and line[7]:
                            if line[6] != '':
                                if line[6].split('/'):
                                    if len(line[6].split('/')) > 1:
                                        raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                                    if len(line[6]) > 8 or len(line[6]) < 5:
                                        raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                            if line[7] != '':
                                if line[7].split('/'):
                                    if len(line[7].split('/')) > 1:
                                        raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                                    if len(line[7]) > 8 or len(line[7]) < 5:
                                        raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))        
                            start_dt = int(float(line[6]))
                            end_dt = int(float(line[7]))
                        
                            start_dt_datetime = datetime(*xlrd.xldate_as_tuple(start_dt, workbook.datemode))
                            end_dt_datetime = datetime(*xlrd.xldate_as_tuple(end_dt, workbook.datemode))

                            start_date_string = start_dt_datetime.date().strftime('%Y-%m-%d')
                            end_dt_string = end_dt_datetime.date().strftime('%Y-%m-%d')

                        values.update({
                            'vendor':line[0],
                            'product_template' : line[1].split('.')[0],
                            'product_variant' : line[2].split('.')[0],
                            'min_qty' : line[3] or 1,
                            'price' : line[4],
                            'currency' : line[5],
                            'date_start' : start_date_string,
                            'date_end' : end_dt_string,
                            'delay' : int(float(delay)),
                        })
                        count = 0
                        for l_fields in line_fields:
                            if(count > 8):
                                values.update({l_fields : line[count]})                        
                            count+=1                         
                        res = self.make_pricelist(values)
            else:
                raise ValidationError(_('Please Seelect a file.'))

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
