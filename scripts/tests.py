import pickle
import xlrd
from xlrd import open_workbook
from utentes.models import Utente
from medicamentos.models import *



with open("./scripts/scrape_locales.pkl","rb") as f:
    distritos,concelhos,freguesias,distritos_relation,concelhos_relation = pickle.load(f)

d,d_max=0,0
c,c_max=0,0
f,f_max=0,0
ph,ph_max=0,0
m,m_max=0,0
a,a_max=0,0
r,m=0,0

for distrito_name in distritos_relation.keys():
    if len(distrito_name) > d_max: 
        d_max=len(distrito_name)
        d=distrito_name
    for concelho_name in distritos_relation[distrito_name]:
        if len(concelho_name) > c_max: 
            c_max=len(concelho_name)
            c=concelho_name
        for freguesia_name in concelhos_relation[concelho_name]:
            if len(freguesia_name) > f_max: 
                f_max=len(freguesia_name)
                f=str(freguesia_name)


with open("./scripts/scrape_ph.pkl","rb") as f:
    farmacias = pickle.load(f)

for l in farmacias:
    freguesia_name = l['freguesia']
    # freguesia_object = Freguesy.objects.get(nome=freguesia_name)

    # if not freguesia_object.nome:
    #     #se for vazio
    #     print("ERRO EM OBTER OBJECTO")

    farm = l['ph']
    if farm[4] == '':
        phonenr = None
    else:
        phonenr = farm[4]

    if len(farm[0]) > ph_max: 
        ph_max=len(farm[0])
        ph=farm[0]

    if len(farm[3]) > m: 
        m=len(farm[3])
        r=farm[3]

print("l",m,"localidade farm",r)

book=open_workbook('./scripts/scrape_meds.xlsx')
sheet=book.sheet_by_index(0)

for r in range(1, sheet.nrows):
    med_attributes=[sheet.cell(r, 0).value, sheet.cell(r, 1).value, sheet.cell(r, 4).value, sheet.cell(r, 3).value, sheet.cell(r, 5).value, 0, sheet.cell(r, 2).value, sheet.cell(r, 6).value]
    if len(med_attributes[2]) > m_max: 
        m_max=len(med_attributes[2])
        m=med_attributes[2]
    if len(med_attributes[3]) > a_max: 
        a_max=len(med_attributes[3])
        a=med_attributes[3]

print(f"l",d_max," name  ",d)
print(f"l",c_max," name  ",c)
print(f"l",f_max," name  ",f)
print(f"l",ph_max," name  ",ph)

print("MEDS")
print(f"l",m_max," name  ",m)
print(f"l",a_max," name  ",a)