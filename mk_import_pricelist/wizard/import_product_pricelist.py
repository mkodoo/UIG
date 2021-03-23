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


class ProductPricelist(models.TransientModel):
    _name = "import.product.pricelist"
    _description = "Import Product Pricelist"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('name', 'Name'),('code', 'Code'),('barcode', 'Barcode')],string='Select Product By',default='name')        

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

    
    def make_product_pricelist(self, values):

        prod_pricelist_obj = self.env['product.pricelist']
        product_templ_obj = self.env['product.template']

        DATETIME_FORMAT = "%Y-%m-%d"

        product = values['product']
        pricelist = values['pricelist'].lower()
        price = values['price'].lower()
        min_qty = values['min_qty'] or 1
        current_time=datetime.now().strftime('%Y-%m-%d')
        st_dt = datetime.strptime(values.get('start_dt') or current_time, DATETIME_FORMAT)
        ed_dt = datetime.strptime(values.get('end_dt') or current_time, DATETIME_FORMAT)
        find_product = False

        if pricelist and price:

            if self.import_prod_option == 'barcode':
            
                find_product = product_templ_obj.search([('barcode','=',product)])
                            
            elif self.import_prod_option == 'code':
                
                find_product = product_templ_obj.search([('default_code','=',product)])
            
            else:
                find_product = product_templ_obj.search([('name','=ilike',product.lower())])


            if find_product:
                pricelist_id = prod_pricelist_obj.search([('name','=ilike',pricelist)])

                if not pricelist:
                    
                    raise ValidationError(_('Please fill the pricelist column.') % pricelist)
                    return

                else:

                    get_pricelist = False

                    pricelist_exist = prod_pricelist_obj.search([('name','=ilike',pricelist)])

                    if pricelist_exist:
                        get_pricelist = pricelist_exist 
                    else:
                        product_pricelist = {
                            'name':values['pricelist'],
                        }

                        get_pricelist = prod_pricelist_obj.create(product_pricelist)

                    item_list ={
                        'pricelist_id': get_pricelist.id,
                        'fixed_price': price,
                        'min_quantity': min_qty,
                        'date_start': st_dt,
                        'date_end': ed_dt,
                        'applied_on':'1_product',
                        'product_tmpl_id' : find_product.id 
                    }
                    main_list = values.keys()
                    for i in main_list:
                        model_id = self.env['ir.model'].search([('model','=','product.pricelist.item')])           
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

                    self.env['product.pricelist.item'].create(item_list)

        else:
            raise ValidationError(_("Pricelist or price are required."))


    
    def import_product_pricelist(self):
            
            if self.import_option == 'csv':
                
                if(self.file):
                    try:
                        keys = ['product', 'pricelist','price','min_qty','start_dt','end_dt']
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
                                res = self.make_product_pricelist(values)
                else:
                    raise ValidationError(_('Please Seelect a file.'))
            else:
                
                if(self.file):
                    try:
                        fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                        fp.write(binascii.a2b_base64(self.file))
                        fp.seek(0)
                        values = {}
                        workbook = xlrd.open_workbook(fp.name)
                        sheet = workbook.sheet_by_index(0)
                    except Exception:
                        raise ValidationError(_("Invalid file!"))

                    for row_no in range(sheet.nrows):
                        val = {}
                        if row_no <= 0:
                            line_fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                        else:
                            line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))

                            start_date_string = False
                            end_dt_string = False

                            if line[4] and line[5]:
                                
                                start_dt = int(float(line[4]))
                                end_dt = int(float(line[5]))

                                start_dt_datetime = datetime(*xlrd.xldate_as_tuple(start_dt, workbook.datemode))
                                end_dt_datetime = datetime(*xlrd.xldate_as_tuple(end_dt, workbook.datemode))

                                start_date_string = start_dt_datetime.date().strftime('%Y-%m-%d')
                                end_dt_string = end_dt_datetime.date().strftime('%Y-%m-%d')
                            
                            min_qty = 1

                            if line[3]:
                                min_qty = int(float(line[3]))
                            

                            values.update({
                                'product':line[0],
                                'pricelist' : line[1],
                                'price' : line[2],
                                'min_qty' : min_qty,
                                'start_dt' : start_date_string,
                                'end_dt' : end_dt_string,
                            })
                            count = 0
                            for l_fields in line_fields:
                                if(count > 5):
                                    values.update({l_fields : line[count]})                        
                                count+=1                             

                            res = self.make_product_pricelist(values)

                else:

                    raise ValidationError(_('Please Select a file.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
