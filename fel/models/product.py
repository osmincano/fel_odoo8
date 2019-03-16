# -*- coding: utf-8 -*-

from openerp import api, tools, SUPERUSER_ID
from openerp.osv import osv, fields, expression


class ProductTemplate(osv.osv):
    _inherit = "product.template"

    _columns = {
        'CodeGravable': fields.selection([
            ('1', '1'),
            ('2', '2'),
        ], 'Codigo Unidad Gravable', store=True, readonly=False),
        'CodeEscenario': fields.selection([
            ('0', 'Afectos'),
            ('1', 'Exportaciones'),
            ('2', 'Servicios'),
            ('3', 'Ventas de Cooperativas'),
            ('4', 'Aportes y Donaciones a Asociaciones'),
            ('5', 'Pagos por el derecho de ser miembro y las cuotas periódicas'),
            ('6', 'Servicios Exentos'),
            ('7', 'Venta de Activos'),
            ('8', 'Servicios exentos centros educativos privados'),
            ('9', 'Medicamentos'),
            ('10', 'Vehículos'),
            ('11', 'Venta a Maquilas'),
            ('12', 'Ventas a zonas francas'),
        ], string='Codigo Escenario', store=True, readonly=False),
    }
    _defaults = {
        'CodeGravable': '1',
        'CodeEscenario': '0',
    }


class ProductProduct(osv.osv):
    _inherit = "product.product"

    def onchange_escenario(self, cr, uid, ids, CodeEscenario, context=None):
        r = {'value': {}}
        if int(CodeEscenario) > 0:
            CodeGravable = '2'
        else:
            CodeGravable = '1'
        r['value']['CodeGravable'] = CodeGravable
        return r
