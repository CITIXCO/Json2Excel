import pandas as pd
df_json = pd.read_json('map.geojson')
df_json.to_excel('map.xlsx')
