# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class AccountJournal(osv.osv):
    _inherit = "account.journal"
    _columns = {
        'is_eface':  fields.boolean('Factura Electronica', required=False, help="Marque si este diario utilizara emision de facturas electronica"),
    }
