import pickle


with open("scrape_locales.pkl","rb") as f:
    distritos,concelhos,freguesias,distritos_relation,concelhos_relation = pickle.load(f)

for distrito_name in distritos_relation.keys():
    for concelho_name in distritos_relation[distrito_name]:
        for freguesia_name in concelhos_relation[concelho_name]:
            