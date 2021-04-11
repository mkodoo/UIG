# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Master Key.
#
##############################################################################

from odoo import models, fields, api, _


class treasury_treasury(models.Model):
    _name = 'treasury.treasury'
    _description = "Treasury Treasury Name"
    
    project_id = fields.Many2one('project.project',string="File No")
    partner_id = fields.Many2one('res.partner',string="Client")
    task_id = fields.Many2one('project.task',string="Matter No")
    amount = fields.Float(string="Total Amount")
    balance_due = fields.Float(string="Balance Due")
    line_ids = fields.One2many('treasury.treasury.line','treasury_id',string="Line")

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.partner_id = self.project_id.partner_id or False


class treasury_treasury_line(models.Model):
    _name = 'treasury.treasury.line'
    _description = "Treasury Line Name"

    treasury_id = fields.Many2one('treasury.treasury',string="Treasury")
    payment_milestone_id = fields.Many2one('treasury.treasury.milestone',string="Payment Milestone")
    amount = fields.Float(string="Amount")
    completed = fields.Boolean(string="Completed")
    due_amount = fields.Float(string="Due Amount")
    received = fields.Boolean(string="Received")
    received_amount = fields.Float(string="Received Amount")
    balance_due = fields.Float(string="Balance Due")
    voucher_number = fields.Float(string="Receipt No")
    receipt_voucher = fields.Many2one('ir.attachment',string="Receipt Attachment")
    remarks = fields.Text(string="Remarks")
    

    
                     
    
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
