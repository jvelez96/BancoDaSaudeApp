'''
Scrape Farmacias Portuguesas 
Alot mais complicado than sapo....
'''

import requests
from bs4 import BeautifulSoup
import geopy.distance # accurate distance based on default ellipsoid WGS-84
import pickle

PH_URL = "https://www.farmaciasportuguesas.pt/catalogo/anfws/Pesquisafarm/googlemaps?pharmacy-district={0}&pharmacy-service=off&pharmacy-concelho={1}&pharmacy-freguesia={2}&pharmacy-county={0}"

farmacias=[]


with open("scrape_locales.pkl","rb") as f:
    distritos,concelhos,freguesias,distritos_relation,concelhos_relation = pickle.load(f)

for distrito_name in distritos_relation.keys():
    for concelho_name in distritos_relation[distrito_name]:
        for freguesia_name in concelhos_relation[concelho_name]:

            response = requests.get(PH_URL.format(distritos[distrito_name],concelhos[concelho_name],freguesias[freguesia_name]))

            if(response.status_code != 200):
                raise Exception

            query = response.json()

            if(len(query)==0):
                # empty list, returned nothing...
                raise Exception

            farms = query['farms']

            for farm in farms:
                farmacias.append({'distrito':distrito_name,'concelho':concelho_name,'freguesia':freguesia_name,'ph':(farm['Name'],farm['Address'],farm['PostalCode'],farm['Locale'],farm['Phone'],farm['GeoCoordinates']['Latitude'],farm['GeoCoordinates']['Longitude'],farm['Code'])})

print(farmacias)

with open("scrape_ph.pkl","wb") as f:
    pickle.dump(farmacias,f,pickle.HIGHEST_PROTOCOL)
print("Saved")

'''
{'Name': 'Farmácia Ferreira do Vale',
 'Label': 'De Serviço',
 'Icon': '/catalogo/media/imagens_mapa/icon-location-4.png?v=2',
 'Open': 'YES',
 'ShiftMode': 'YES',
 'Permanent': '',
 'Extended': '',
 'Schedule': '',
 'Address': 'Largo 5 de Outubro ',
 'PFPSubscriber': '1',
 'HasEcommerce': '1',
 'PostalCode': '3050-082',
 'Phone': '239911220',
 'Locale': 'Barcouço',
 'Code': '07366',
 'GeoCoordinates': {'Latitude': 40.304295, 'Longitude': -8.472505},
 'Distance': '184.97',
 'DistanceLabel': '184.97 km'}
'''
