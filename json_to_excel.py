import json
import pandas as pd


with open('map.json') as json_file:
    data = json.load(json_file)


result = []
for item in data["features"]:
    if item.get('geometry').get('type') == "Polygon" and item.get('properties').get('Name'):
        my_dict = {}
        my_dict['polygon'] = []
        my_dict['price'] = item.get('properties').get('Name')
        my_dict['city_id'] = 118
        my_dict['vehicle_type_id'] = 3
        my_dict['round_trip_percent'] = 20
        my_dict['comapany_id'] = 9
        if len(item.get('geometry').get('coordinates')):
            my_dict['polygon'] = item.get('geometry').get('coordinates')[0]

        result.append(my_dict)

df = pd.DataFrame(result)
df.to_excel('map.xlsx')
