import json
import pandas as pd


with open('diamante.json') as json_file:
    data = json.load(json_file)


result = []
for item in data["features"]:
    try:
        temp_price = int(item.get('properties').get('name'))
    except ValueError:
        temp_price = 0

    if item.get('geometry').get('type') == "Polygon" and item.get('properties').get('name') and temp_price:
        my_dict = {}
        my_dict['polygon'] = []
        my_dict['price'] = temp_price
        my_dict['city_id'] = 118
        my_dict['vehicle_type_id'] = 3
        my_dict['round_trip_percent'] = 20
        my_dict['company_id'] = 14
        my_dict['negotiation_id'] = 8
        if len(item.get('geometry').get('coordinates')):
            my_dict['polygon'] = item.get('geometry').get('coordinates')[0]

        result.append(my_dict)

df = pd.DataFrame(result)
df.to_excel('diamante.xlsx')
