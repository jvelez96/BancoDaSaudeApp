# Scrape Farmacias Portuguesas

import requests
from bs4 import BeautifulSoup
import geopy.distance # accurate distance based on default ellipsoid WGS-84
import pickle

MAIN_URL="https://farmacias.sapo.pt"
API_URL="/api/pharmacy/county/{}00?filtro=all"


CONCELHO_URL = "https://www.farmaciasportuguesas.pt/catalogo/anfws/pesquisafarm/getHtmlOptionConcelhos?distrito={}"
FREGUESIA_URL="https://www.farmaciasportuguesas.pt/catalogo/anfws/pesquisafarm/getHtmlOptionFreguesias?distrito={}&concelho={}"

distritos = {}
concelhos = {}
freguesias = {}

# relacoes entre regioes Lisboa->Oeiras->Porto Salvo
distritos_relation = {}
concelhos_relation = {}


query_distrito='''<select sb="26849906" id="pharmacy-district" name="pharmacy-district" class="selectbox" style="display: none;">\n\t\t\t\t\t\t\t\t\t<option value="closetome">Perto de Mim</option>\n\t\t\t\t\t\t\t\t\t<option value="">Todos os Distritos</option>\n\t\t\t\t\t\t\t\t\t<option value="1">Aveiro</option><option value="2">Beja</option><option value="3">Braga</option><option value="4">Bragança</option><option value="5">Castelo Branco</option><option value="6">Coimbra</option><option value="7">Évora</option><option value="8">Faro</option><option value="9">Guarda</option><option value="44">Ilha da Graciosa</option><option value="31">Ilha da Madeira</option><option value="43">Ilha da Terceira</option><option value="48">Ilha das Flores</option><option value="32">Ilha de Porto Santo</option><option value="41">Ilha de Santa Maria</option><option value="45">Ilha de São Jorge</option><option value="42">Ilha de São Miguel</option><option value="49">Ilha do Corvo</option><option value="47">Ilha do Faial</option><option value="46">Ilha do Pico</option><option value="10">Leiria</option><option value="11">Lisboa</option><option value="12">Portalegre</option><option value="13">Porto</option><option value="14">Santarém</option><option value="15">Setúbal</option><option value="16">Viana do Castelo</option><option value="17">Vila Real</option><option value="18">Viseu</option>\t\t\t\t\t\t\t\t</select>'''

distrito_soup = BeautifulSoup(query_distrito,"html.parser")
options = distrito_soup.findAll('option')



for op in options:
    value = op['value']
    try:
        distrito_nr = int(value)
    except ValueError as e:
        # not valid nr option
        print(e)
        continue
    distritos[op.contents[0]] = distrito_nr

print(distritos)

#got distritos
#gotta get concelhos

for distrito_name in distritos.keys():
    response = requests.get(CONCELHO_URL.format(distritos[distrito_name]))

    if(response.status_code != 200):
        raise Exception

    query = response.content

    soup = BeautifulSoup(query,"html.parser")
    options = soup.findAll('option')

    distritos_relation[distrito_name] = []

    for op in options:
        value = op['value']
        try:
            nr = int(value)
        except ValueError as e:
            # not valid nr option
            print(e)
            continue
        concelhos[op.contents[0]] = nr
        distritos_relation[distrito_name].append(op.contents[0])


print(distritos_relation)
print(concelhos)

#gotta get freguesia
for distrito_name in distritos_relation.keys():
    for concelho_name in distritos_relation[distrito_name]:
        response = requests.get(FREGUESIA_URL.format(distritos[distrito_name],concelhos[concelho_name]))

        if(response.status_code != 200):
            raise Exception

        query = response.content

        soup = BeautifulSoup(query,"html.parser")
        options = soup.findAll('option')

        concelhos_relation[concelho_name] = []

        for op in options:
            value = op['value']
            try:
                nr = int(value)
            except ValueError as e:
                # not valid nr option
                print(e)
                continue
            freguesias[op.contents[0]] = nr
            concelhos_relation[concelho_name].append(op.contents[0])


print(concelhos_relation)
print(freguesias)

with open("scrape_locales.pkl","wb") as f:
    pickle.dump([distritos,concelhos,freguesias,distritos_relation,concelhos_relation],f,pickle.HIGHEST_PROTOCOL)
print("Saved")

