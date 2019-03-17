# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _


class APIModelConfiguration(osv.osv):
    _name = "api.data.configuration"
    _description = """API DATA Configuration"""
    _columns = {
        'company_id': fields.many2one('res.company', 'Empresa'),
        'user': fields.char("Usuario", required=True),
        'key_firma': fields.char("Llave Firma xml", required=True),
        'url_firma': fields.char("URL Firma xml", required=True),
        'key_certificado': fields.char("Llave Certificacion", required=True),
        'url_certificado': fields.char("URL Certificacion", required=True),
        'url_anulacion': fields.char("URL Anulacion", required=True),
        'code_est': fields.char("Codigo Establecimiento", required=True),
    }
    _order = 'id desc'
