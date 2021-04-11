# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
	_inherit = 'account.move'

	amount_in_words = fields.Char(compute='get_amount_in_words')

	def get_amount_in_words(self):
		for record in self:
			
			record.amount_in_words = record.currency_id.amount_to_text(record.amount_total)


class AccountPayment(models.Model):
	_inherit = 'account.payment'

	amount_in_words = fields.Char(compute='get_amount_in_words')

	def get_amount_in_words(self):
		for record in self:
			record.amount_in_words = record.currency_id.amount_to_text(record.amount)
