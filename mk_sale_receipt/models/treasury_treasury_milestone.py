# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Master Key.
#
##############################################################################

from odoo import models, fields, api, _


class treasury_treasury_milestone(models.Model):
    _name = 'treasury.treasury.milestone'
    _description = "Treasury Milestone Name"
    
    name = fields.Char(string="Name")


                     
    
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
