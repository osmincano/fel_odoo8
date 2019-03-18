
# -*- encoding: UTF-8 -*-

from openerp.osv import fields, osv
from openerp import api
#import xml.etree.cElementTree as ET
#from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from lxml import etree as ET
import datetime as dt
import dateutil.parser
from dateutil.tz import gettz
from openerp.tools.translate import _
from dateutil import parser
from .numero_a_texto import Numero_a_Texto
from .credit_note import set_data_for_invoice_credit, send_data_api_credit
from .invoice_cancel import set_data_for_invoice_cancel, send_data_api_cancel
import json
from openerp.exceptions import except_orm, Warning, RedirectWarning
import logging
import base64
import requests
from json import loads
from random import randint
import re


class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        # Cambiada para procesar los datos devueltos por WS
        if self.journal_id.is_eface == False:
            return super(AccountInvoice, self).invoice_validate()
        res = super(AccountInvoice, self).invoice_validate()
        if self.type == "out_invoice":
            print "self:", self
            xml_data = self.set_data_for_invoice()
            self.letras = str(Numero_a_Texto(self.amount_total))
            uuid, serie, numero_dte, dte_fecha = self.send_data_api(xml_data)
            message = _("Facturacion Electronica: Serie %s  Numero %s") % (serie, numero_dte)
            self.message_post(body=message)
            self.uuid = uuid
            self.serie = serie
            self.numero_dte = numero_dte
            myTime = dateutil.parser.parse(dte_fecha)
            racion_de_6h = timedelta(hours=6)
            myTime = myTime + racion_de_6h
            formato2 = "%Y-%m-%d %H:%M:%S"
            myTime = myTime.strftime(formato2)
            self.dte_fecha = myTime

        if self.type == "out_refund" and self.refund_invoice_id:
            xml_data = set_data_for_invoice_credit(self)
            #print ("xml credit note:",xml_data)
            self.letras = str(Numero_a_Texto(self.amount_total))
            uuid, serie, numero_dte, dte_fecha = send_data_api_credit(self, xml_data)
            message = _("Nota de Credito: Serie %s  Numero %s") % (serie, numero_dte)
            self.message_post(body=message)
            self.uuid = uuid
            self.serie = serie
            self.numero_dte = numero_dte
            myTime = dateutil.parser.parse(dte_fecha)
            racion_de_6h = timedelta(hours=6)
            myTime = myTime + racion_de_6h
            formato2 = "%Y-%m-%d %H:%M:%S"
            myTime = myTime.strftime(formato2)
            self.dte_fecha = myTime

        return res

    @api.multi
    def action_cancel(self):
        # Cambiada para procesar los datos devueltos por WS
        if self.journal_id.is_eface == False:
            return super(AccountInvoice, self).action_cancel()
        res = super(AccountInvoice, self).action_cancel()
        if self.type == "out_invoice":
            xml_data = set_data_for_invoice_cancel(self)
            uuid, serie, numero_dte, dte_fecha = send_data_api_cancel(self, xml_data)
            message = _("Factura Cancelada: Serie %s  Numero %s") % (serie, numero_dte)
            self.message_post(body=message)
            self.uuid = uuid
            self.serie = serie
            self.numero_dte = numero_dte
            myTime = dateutil.parser.parse(dte_fecha)
            racion_de_6h = timedelta(hours=6)
            myTime = myTime + racion_de_6h
            formato2 = "%Y-%m-%d %H:%M:%S"
            myTime = myTime.strftime(formato2)
            self.dte_fecha = myTime

        if self.type == "out_refund" and self.uuid:
            xml_data = set_data_for_invoice_cancel(self)
            uuid, serie, numero_dte, dte_fecha = send_data_api_cancel(self, xml_data)
            message = _("Nota de Credito Cancelada: Serie %s  Numero %s") % (serie, numero_dte)
            self.message_post(body=message)
            self.uuid = uuid
            self.serie = serie
            self.numero_dte = numero_dte
            myTime = dateutil.parser.parse(dte_fecha)
            racion_de_6h = timedelta(hours=6)
            myTime = myTime + racion_de_6h
            formato2 = "%Y-%m-%d %H:%M:%S"
            myTime = myTime.strftime(formato2)
            self.dte_fecha = myTime

        return res

    @api.multi
    def set_data_for_invoice(self):

        xmlns = "http://www.sat.gob.gt/dte/fel/0.1.0"
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        schemaLocation = "http://www.sat.gob.gt/dte/fel/0.1.0"
        version = "0.4"
        ns = "{xsi}"
        DTE = "dte"
        root = ET.Element("{" + xmlns + "}GTDocumento", Version="0.4",
                          attrib={"{" + xsi + "}schemaLocation": schemaLocation})
        doc = ET.SubElement(root, "{" + xmlns + "}SAT", ClaseDocumento="dte")
        dte = ET.SubElement(doc, "{" + xmlns + "}DTE", ID="DatosCertificados")
        dem = ET.SubElement(dte, "{" + xmlns + "}DatosEmision", ID="DatosEmision")
        fecha_emision = dt.datetime.now(gettz("America/Guatemala")
                                        ).__format__('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        dge = ET.SubElement(dem, "{" + xmlns + "}DatosGenerales",
                            CodigoMoneda="GTQ",  FechaHoraEmision=fecha_emision, Tipo="FACT")
        emi = ET.SubElement(dem, "{" + xmlns + "}Emisor", AfiliacionIVA="GEN", CodigoEstablecimiento="1", CorreoEmisor=self.company_id.email,
                            NITEmisor=self.company_id.vat, NombreComercial=self.company_id.name, NombreEmisor=self.company_id.name)
        dire = ET.SubElement(emi, "{" + xmlns + "}DireccionEmisor")
        ET.SubElement(dire, "{" + xmlns + "}Direccion").text = "4 Avenida 19-26 zona 10"
        ET.SubElement(dire, "{" + xmlns + "}CodigoPostal").text = "01009"
        ET.SubElement(dire, "{" + xmlns + "}Municipio").text = "Guatemala"
        ET.SubElement(dire, "{" + xmlns + "}Departamento").text = "Guatemala"
        ET.SubElement(dire, "{" + xmlns + "}Pais").text = "GT"

        if self.partner_id.vat:
            vat = self.partner_id.vat
            vat = re.sub('\ |\?|\.|\!|\/|\;|\:|\-', '', vat)
            vat = vat.upper()
        else:
            vat = "CF"

        # if self.partner_id.vat:
        rece = ET.SubElement(dem, "{" + xmlns + "}Receptor", CorreoReceptor=self.partner_id.email or "",
                             IDReceptor=vat, NombreReceptor=self.partner_id.name)
        direc = ET.SubElement(rece, "{" + xmlns + "}DireccionReceptor")
        ET.SubElement(direc, "{" + xmlns + "}Direccion").text = self.partner_id.street or "Ciudad"
        ET.SubElement(direc, "{" + xmlns + "}CodigoPostal").text = "01009"
        ET.SubElement(direc, "{" + xmlns + "}Municipio").text = "Guatemala"
        ET.SubElement(direc, "{" + xmlns + "}Departamento").text = "Guatemala"
        ET.SubElement(direc, "{" + xmlns + "}Pais").text = "GT"

        # Frases
        invoice_line = self.invoice_line
        fra = ET.SubElement(dem, "{" + xmlns + "}Frases")
        ET.SubElement(fra, "{" + xmlns + "}Frase", TipoFrase="1", CodigoEscenario="1")
        lista = []
        for line_id in invoice_line:
            if int(line_id.product_id.CodeEscenario) > 0:
                if int(line_id.product_id.CodeEscenario) in lista:
                    pass
                else:
                    ET.SubElement(fra, "{" + xmlns + "}Frase", TipoFrase="4",
                                  CodigoEscenario=line_id.product_id.CodeEscenario)
                    lista.append(int(line_id.product_id.CodeEscenario))
        # items
        items = ET.SubElement(dem, "{" + xmlns + "}Items")
        tax_in_ex = 1
        cnt = 0
        # LineasFactura
        for line in invoice_line:
            cnt += 1
            p_type = 0
            BoS = "B"
            if line.product_id.type == 'service':
                p_type = 1
                BoS = "S"
            for tax in line.invoice_line_tax_id:
                if tax.price_include:
                    tax_in_ex = 0

            # Item
            item = ET.SubElement(items, "{" + xmlns + "}Item",
                                 BienOServicio=BoS, NumeroLinea=str(cnt))
            if line.invoice_line_tax_id:
                tax = "IVA"
            else:
                raise Warning(_("Las lineas de Factura deben de llevar impuesto."))
            for imp in line.invoice_line_tax_id:
                if imp.price_include == True:
                    price_unit = line.price_unit
                    price_unit = round(price_unit, 4)
                else:
                    price_unit = ((line.price_unit*(imp.amount/100.00)) + line.price_unit)
                    price_unit = round(price_unit, 4)

            if line.product_id.CodeGravable == '2':
                CodeTax = "EXENTO"
            else:
                CodeTax = 'IVA'

            ET.SubElement(item, "{" + xmlns + "}Cantidad").text = str(line.quantity)
            ET.SubElement(item, "{" + xmlns + "}UnidadMedida").text = "UND"
            ET.SubElement(
                item, "{" + xmlns + "}Descripcion").text = (line.name + " /" + CodeTax) or " "
            ET.SubElement(item, "{" + xmlns + "}PrecioUnitario").text = str(round(price_unit, 4))
            ET.SubElement(
                item, "{" + xmlns + "}Precio").text = str(round(line.quantity * price_unit, 4))
            ET.SubElement(item, "{" + xmlns + "}Descuento").text = str(
                round((line.discount * (line.quantity * price_unit))/100, 4))

            impuestos = ET.SubElement(item, "{" + xmlns + "}Impuestos")
            impuesto = ET.SubElement(impuestos, "{" + xmlns + "}Impuesto")
            price = price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_id.compute_all(
                price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            print "taxes:", taxes
            price_tax = taxes['total_included'] - taxes['total']
            ET.SubElement(impuesto, "{" + xmlns + "}NombreCorto").text = tax
            ET.SubElement(
                impuesto, "{" + xmlns + "}CodigoUnidadGravable").text = line.product_id.CodeGravable
            ET.SubElement(
                impuesto, "{" + xmlns + "}MontoGravable").text = str(round(line.price_subtotal, 4))
            ET.SubElement(impuesto, "{" + xmlns + "}MontoImpuesto").text = str(round(price_tax, 4))
            ET.SubElement(
                item, "{" + xmlns + "}Total").text = str(round(taxes['total_included'], 4))
        # Totales
        totales = ET.SubElement(dem, "{" + xmlns + "}Totales")
        timpuestos = ET.SubElement(totales, "{" + xmlns + "}TotalImpuestos")
        tim = ET.SubElement(timpuestos, "{" + xmlns + "}TotalImpuesto",
                            NombreCorto="IVA", TotalMontoImpuesto=str(round(self.amount_tax, 4)))
        ET.SubElement(totales, "{" + xmlns + "}GranTotal").text = str(round(self.amount_total, 4))

        # Adenda
        ade = ET.SubElement(doc, "{" + xmlns + "}Adenda")
        #ET.SubElement(ade, "NITEXTRANJERO").text = "111111"
        ET.SubElement(ade, "CAJERO").text = "1"
        ET.SubElement(ade, "VENDEDOR").text = "1"
        ET.SubElement(ade, "Subtotal").text = str(round(self.amount_untaxed, 4))
        ET.SubElement(ade, "Fuente").text = self.user_id.name
        date_due = self.date_due
        date_due = datetime.strptime(date_due, '%Y-%m-%d')
        formato2 = "%d-%m-%Y"
        date_due = date_due.strftime(formato2)
        ET.SubElement(ade, "FechaVencimiento").text = date_due
        print "ENCO:", ET
        print type(root)
        cont = ET.tostring(root, encoding="UTF-8", method='xml')
        print "CBDE"
        buscar = "ns0"
        rmpl = "dte"
        cont = cont.decode('utf_8')
        cont = cont.replace(buscar, rmpl)
        cont = cont.encode('utf_8')
        dat = base64.b64encode(cont)
        return dat

    @api.multi
    def send_data_api(self, xml_data=None):
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
                     'es_anulacion': 'N'}

        response = requests.request("POST", url, data=data_send)
        rp = response.json()

        dt = rp["archivo"]
        url = api.url_certificado
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
            # message = _("You cannot validate an invoice\n Error No:%s\n %s.") % (
            #    cantidad_errores, descripcion_errores)
            # self.message_post(body=message)
            # raise UserError(
            #    _("En este momento no se puede enviar la factura al servicio web.\n Favor de contactar al administrador."))
        return uuid, serie, numero_dte, dte_fecha
