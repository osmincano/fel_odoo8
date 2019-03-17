# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class AccountInvoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        "uuid": fields.char("Numero Autorizacion", readonly=True, states={'draft': [('readonly', False)]}),
        "serie": fields.char("Serie", readonly=True, states={'draft': [('readonly', False)]}),
        "numero_dte": fields.char("Numero DTE", readonly=True, states={'draft': [('readonly', False)]}),
        "dte_fecha": fields.datetime("Fecha Autorizacion", readonly=True, states={'draft': [('readonly', False)]}),
        "cae": fields.text("CAE", readonly=True, states={'draft': [('readonly', False)]}),
        "letras": fields.text("Total Letras", readonly=True, states={'draft': [('readonly', False)]}),
    }
