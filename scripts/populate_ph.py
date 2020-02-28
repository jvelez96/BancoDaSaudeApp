import pickle

with open("scrape_ph.pkl","rb") as f:
    farmacias = pickle.load(f)

# print(len(farmacias))

for f in farmacias:
    distrito_name = f['distrito']
    concelho_name = f['concelho']
    freguesia_name = f['freguesia']
    
    # estrutura
    #(farm['Name'],farm['Address'],farm['PostalCode'],farm['Locale'],farm['Phone'],farm['GeoCoordinates']['Latitude'],farm['GeoCoordinates']['Longitude'],farm['Code'])
    farm = f['ph']