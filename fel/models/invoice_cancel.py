# -*- encoding: UTF-8 -*-

from openerp.osv import fields, osv
from openerp import api
from datetime import datetime, timedelta
from lxml import etree as ET
import datetime as dt
import dateutil.parser
from dateutil.tz import gettz
from openerp.tools.translate import _
from dateutil import parser
from .numero_a_texto import Numero_a_Texto
import json
from openerp.exceptions import except_orm, Warning, RedirectWarning
import logging
import base64
import requests
from json import loads
from random import randint
import re


@api.multi
def set_data_for_invoice_cancel(self):
    xmlns = "http://www.sat.gob.gt/dte/fel/0.1.0"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation = "http://www.sat.gob.gt/dte/fel/0.1.0"
    version = "0.1"
    ns = "{xsi}"
    DTE = "dte"
    cno = "http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0"

    root = ET.Element("{" + xmlns + "}GTAnulacionDocumento", Version="0.1",
                      attrib={"{" + xsi + "}schemaLocation": schemaLocation})
    doc = ET.SubElement(root, "{" + xmlns + "}SAT")
    dte = ET.SubElement(doc, "{" + xmlns + "}AnulacionDTE", ID="DatosCertificados")
    date_invoice = self.dte_fecha or datetime.now()
    #formato1 = "%Y-%m-%d"
    date_invoice = datetime.strptime(date_invoice, '%Y-%m-%d %H:%M:%S')
    # print(type(date_invoice))
    # print(date_invoice)
    racion_de_6h = timedelta(hours=6)
    date_invoice = date_invoice - racion_de_6h
    print(date_invoice)
    #formato2 = "%d-%m-%Y"
    #date_due = date_due.strftime(formato2)
    formato1 = "%Y-%m-%dT%H:%M:%S.%f"
    date_invoice = date_invoice.strftime(formato1)[:-3]
    if self.partner_id.vat:
        vat = self.partner_id.vat
        vat = re.sub('\ |\?|\.|\!|\/|\;|\:|\-', '', vat)
        vat = vat.upper()
    else:
        vat = "CF"
    fecha_emision = dt.datetime.now(gettz("America/Guatemala")
                                    ).__format__('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    dge = ET.SubElement(dte, "{" + xmlns + "}DatosGenerales", FechaEmisionDocumentoAnular=date_invoice, FechaHoraAnulacion=fecha_emision,
                        ID="DatosAnulacion", IDReceptor=vat, MotivoAnulacion="Anulación", NITEmisor=self.company_id.vat, NumeroDocumentoAAnular=str(self.uuid))

    cont = ET.tostring(root, encoding="UTF-8", method='xml')
    buscar = "ns0"
    rmpl = "dte"
    cont = cont.decode('utf_8')
    cont = cont.replace(buscar, rmpl)
    cont = cont.encode('utf_8')
    dat = base64.b64encode(cont)
    return dat


@api.multi
def send_data_api_cancel(self, xml_data):
    api = self.env['api.data.configuration'].search([])[0]
    if not api:
        return False
    XML = xml_data
    url = api.url_firma
    ran = str(randint(1, 99999))
    data_send = {'llave': api.key_firma,
                 'archivo': XML,
                 'codigo': ran,
                 'alias': api.user,
                 'es_anulacion': 'S'}

    response = requests.request("POST", url, data=data_send)
    #print ("response12", response.text)
    rp = response.json()

    dt = rp["archivo"]
    payload = {
        'nit_emisor': self.company_id.vat,
        'correo_copia': self.company_id.email,
        'xml_dte': dt,
    }

    ident = str(randint(1111111, 9999999))
    headers = {
        'usuario': api.user,
        'llave': api.key_certificado,
        'content-type': "application/json",
        'identificador': ident,
    }

    url = api.url_anulacion
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    # print(response.text)
    rp = response.json()
    uuid = rp["uuid"]
    serie = rp["serie"]
    numero_dte = rp["numero"]
    dte_fecha = rp["fecha"]
    cantidad_errores = rp["cantidad_errores"]
    descripcion_errores = rp["descripcion_errores"]
    #resulta_codigo = tree_res.find('ERROR').attrib['Codigo']
    #resulta_descripcion = tree_res.find('ERROR').text
    if cantidad_errores > 0:
        raise Warning(_("You cannot validate an invoice\n Error No:%s\n %s." %
                        (cantidad_errores, descripcion_errores)))
        #message = _("You cannot validate an invoice\n Error No:%s\n %s.") % (cantidad_errores,descripcion_errores)
        # self.message_post(body=message)
        #raise UserError(_("En este momento no se puede enviar la factura al servicio web.\n Favor de contactar al administrador."))
    return uuid, serie, numero_dte, dte_fecha
