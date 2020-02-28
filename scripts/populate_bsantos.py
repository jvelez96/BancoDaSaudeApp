import pickle
import xlrd
from xlrd import open_workbook
from utentes.models import Utente
from medicamentos.models import *

District.objects.all().delete()
Concelho.objects.all().delete()
Freguesy.objects.all().delete()
Pharmacy.objects.all().delete()
Med.objects.all().delete()
Order.objects.all().delete()
OrderDetails.objects.all().delete()


with open("./scripts/scrape_locales.pkl","rb") as f:
    distritos,concelhos,freguesias,distritos_relation,concelhos_relation = pickle.load(f)

with open("./scripts/scrape_ph.pkl","rb") as f:
    farmacias = pickle.load(f)

for distrito_name in distritos_relation.keys():
    d = District(nome=distrito_name)
    d.save()
    for concelho_name in distritos_relation[distrito_name]:
        c = Concelho(nome=concelho_name, district=d)
        c.save()
        for freguesia_name in concelhos_relation[concelho_name]:
            f = Freguesy(nome=freguesia_name, concelho=c, district=d)
            f.save()

for l in farmacias:
    freguesia_name = l['freguesia']
    freguesia_object = Freguesy.objects.get(nome=freguesia_name)

    if not freguesia_object.nome:
        #se for vazio
        print("ERRO EM OBTER OBJECTO")

    farm = l['ph']
    if farm[4] == '':
        phonenr = None
    else:
        phonenr = farm[4]
    p = Pharmacy(nome=farm[0],address=farm[1],postal_code=farm[2],localidade=farm[3],phone=phonenr,latitude=farm[5],longitude=farm[6], freguesia=freguesia_object)
    p.save()

book=open_workbook('./scripts/scrape_meds.xlsx')
sheet=book.sheet_by_index(0)

for r in range(1, sheet.nrows):
    if sheet.cell(r, 11).value == 'Comercializado':
        med_attributes=[sheet.cell(r, 0).value, sheet.cell(r, 1).value, sheet.cell(r, 4).value, sheet.cell(r, 3).value, sheet.cell(r, 5).value, 0, sheet.cell(r, 2).value,
         sheet.cell(r, 6).value if sheet.cell(r, 6).value!='' else 0,
         sheet.cell(r, 7).value if not isinstance(sheet.cell(r, 7).value, str) else 0,
         sheet.cell(r, 8).value if not isinstance(sheet.cell(r, 8).value, str) else 0,
         sheet.cell(r, 9).value if not isinstance(sheet.cell(r, 9).value, str) else 0,
         sheet.cell(r, 10).value if not isinstance(sheet.cell(r, 10).value, str) else 0]
        med = Med(med_id=med_attributes[0], active_principle=med_attributes[1], dosage=med_attributes[2], farmaceutical_form=med_attributes[3], packaging=med_attributes[4].split()[0], quantity_stock=med_attributes[5], name=med_attributes[6], cnpem=med_attributes[7], preco=med_attributes[8], preco_notificado=med_attributes[9], preco_utente=med_attributes[10], preco_pensionistas=med_attributes[11])
        med.save()
