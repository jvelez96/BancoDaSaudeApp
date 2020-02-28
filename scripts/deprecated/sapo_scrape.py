import requests
from bs4 import BeautifulSoup
import geopy.distance # accurate distance based on default ellipsoid WGS-84

MAIN_URL="https://farmacias.sapo.pt"
API_URL="/api/pharmacy/county/{}00?filtro=all"


response = requests.get(MAIN_URL+API_URL.format())

if(response.status_code != 200):
    raise Exception

query = response.json()

if(len(query)==0):
    # empty list, returned nothing...
    raise Exception

# each element as keys -> 'item', 'log', 'lat'
# item is html content, others string
'''
'<li class="[ no-margin all-100 ] " data-pharmacy-lon="-25.568268" data-pharmacy-lat="37.745097" > <div class="[ tiny-vertical-padding small-vertical-padding medium-half-vertical-padding large-half-vertical-padding xlarge-half-vertical-padding ] pharmacy"> <div class="[ column-group tiny-half-gutters small-half-gutters medium-half-horizontal-gutters large-half-horizontal-gutters xlarge-half-horizontal-gutters ] communist"> <div class="[ tiny-100 small-100 medium-70 large-70 xlarge-70 ]">  <div class="details"> <h5 class="[ no-margin-bottom ]"> <a href="/farmacia/farmacia-santa-cruz-5">Farmácia Santa Cruz</a> </h5> <div>  <span>Rua Dr. Filomeno da Câmara 7 - Lagoa - S. Miguel</span> </div>   <div class="[ fs-xsmall fw-900 uppercase ] variable-info"> <span class="[  ] distance-km hide-all" data-pharmacy-dist>Distância: </span>  <span class="[  ] closed">Fechada</span>  </div> </div> </div> <div class="[ tiny-100 small-100 medium-30 large-30 xlarge-30 ]"> <a class="[ ink-button ] full-width" href="https://maps.google.com/maps?f=d&daddr=37.745097,-25.568268&ll=37.745097,-25.568268&z=15" target="_blank"> <i class="fa fa-map fa-external-link"></i> <span class="[ _hide-all ]">Ver no mapa</span>  </a>  </div> </div> </div> </li>'
'''

# Localizar ve q as cordenadas pertencem a santarem, busca todas as farmacias de santarem, e calcula a distancia
# Manhatan distance e capaz de ser a solucao mais facil 
# geopy.distance.distance(t,tuple).km


soup = BeautifulSoup(, "html.parser")

a_tag=soup2.find("a") # find next a tag

ph_info_url = a_tag['href']
ph_name = a_tag.contents[0] # list wit 1 name, TEST
ph_lat,ph_long=


