import xml.etree.cElementTree as ET
from xml.dom import minidom
from zeep import Client
from lxml import etree

from medicamentos.models import Product,Med,Warehouse
import logging

logger = logging.Logger(__name__)


# client = Client('https://webservices3.ocp.pt/banco_saude/inventory?wsdl')


def soap_auth_header():
    auth= etree.Element("Authentication",xmlns="http://service.bs.ocp.com/")
    username=etree.SubElement(auth, "Username",xmlns="")
    password=etree.SubElement(auth, "Password",xmlns="")

    username.text="000000"
    password.text="UeE9BD1"
    return auth


AUTH_HEADER=soap_auth_header()


def get_inventory_level_OCP(med_id="",warehouse_id=""):
    # return works like json object
    '''Example return
    {
    'TransactionState': {
        'code': 100,
        'message': 'Success',
        'state': 'OK'
    },
    'inventoryLevel': [
        {
            'Medicine_ID': '0000000',
            'Medicine_Description': 'Teste Medicine',
            'Quantity': 10,
            'Unit': None,
            'Warehouse_ID': '2',
            'Stock_Date': datetime.datetime(2019, 4, 6, 0, 0, tzinfo=<FixedOffset '+01:00'>)
        },
        {
            'Medicine_ID': '0000000',
            'Medicine_Description': 'Teste Medicine',
            'Quantity': 15,
            'Unit': None,
            'Warehouse_ID': '5',
            'Stock_Date': datetime.datetime(2019, 4, 6, 0, 0, tzinfo=<FixedOffset '+01:00'>)
        }
    ]
}
'''
    return client.service.getInventoryLevel({"Medicine_ID":med_id,"Warehouse_ID":warehouse_id},_soapheaders=[AUTH_HEADER])


def update_inventory_db():

    response = get_inventory_level_OCP()


    all_products = response.inventoryLevel

    for product in all_products:
        med = warehouse = product = None
        try:
            med = Med.objects.get(med_id=product.Medicine_ID)

            warehouse = Warehouse.objects.get(warehouse_id=int(product.Warehouse_ID))

            # product = Product.objects.get(med=med,warehouse=warehouse)

        except Med.DoesNotExist or Med.MultipleObjectsReturned:
            pass
        except Warehouse.DoesNotExist or Warehouse.MultipleObjectsReturned:
            pass
        except Product.DoesNotExist:
            # product = Product(med=med,warehouse=warehouse,exp_date=,)
            pass
        except Product.MultipleObjectsReturned as e:
            logger.critical("update_inventory_db: Multiple products with same warehouse and med; warehouse: {}, med: {}".format(warehouse,med))
        except Exception as e:
            pass






def pretty_xml(elem):
    """return a pretty printed XML string for the Element"""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

"""Still incomplete and wrong"""

def order_operation_write():
    """create the file structure"""
    root = ET.Element ("soapenv:Envelope")
    root.set("xmlns:soapenv", "http://schemas.xmlsoap.org/soap/envelope/")
    root.set("xmlns:govx", "http://GovX.Service.Inventory")
    header = ET.SubElement(root,"soapenv:Header")
    body = ET.SubElement(header,"soapenv:Body")
    orderOperation = ET.SubElement(body,"mx3:orderOperation")
    pharmacy = ET.SubElement(orderOperation, "mx3:Pharmacy_ID").text = "22231"
    tree = ET.ElementTree(root)
    tree.write("filename.xml")




# def ws_get_stock(xml):
#     try:
#         p = untangle.parse(xml)
#         nr_stock = int(p.soapenv_Envelope.soapenv_Body.mx3_getInventoryLevel.mx3_medicamento.cdata)
#         return nr_stock
#     except Exception as e:
#         logger.error("Error in parsing web service ws_get_stock:{}".format(e))

