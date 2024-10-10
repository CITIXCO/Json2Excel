import json
import pandas as pd
import kml2geojson

companies = {
    'medellin': 16,
    'barranquilla': 20,
    'bucaramanga': 14,
    'ibague': 21,
    'girardot': 23,
    'cali': 25,
    'pereira': 27,
    'bogota': 28,
}

cities = {
    'medellin': 547,
    'barranquilla': 88,
    'bucaramanga': 120,
    'ibague': 428,
    'girardot': 372,
    'cali': 150,
    'pereira': 657,
    'bogota': 107,
}

permission_map = {
    'edit_invoice': 20,
    'edit_destinatary_click_lite': 21,
    'edit_order_value': 22,
}


def citix_kml_dict_to_data_frame(
    *,
    data,
    city_id,
    company_id,
    negotiation_id,
    enterprise,
    vehicle_type_id=3,
    round_trip_percent=20
):
    result = []
    for item in data["features"]:
        try:
            base_name = item.get('properties').get('Name')
            if not base_name:
                base_name = item.get('properties').get('name')
            if not base_name:
                base_name = item.get('properties').get('NAME')
            if not base_name:
                base_name = '0'
            price = int(base_name)
        except ValueError:
            price = 0

        real_name = item.get('properties').get('Description')
        if not real_name:
            real_name = item.get('properties').get('description')
        if not real_name:
            real_name = item.get('properties').get('DESCRIPTION')
        if not real_name:
            real_name = enterprise

        if item.get('geometry').get('type') == "Polygon":
            my_dict = {}
            my_dict['name'] = f"{real_name}"
            my_dict['polygon'] = []
            my_dict['price'] = price
            my_dict['city_id'] = city_id
            my_dict['vehicle_type_id'] = vehicle_type_id
            my_dict['round_trip_percent'] = round_trip_percent
            my_dict['company_id'] = company_id
            my_dict['negotiation_id'] = negotiation_id
            if len(item.get('geometry').get('coordinates')):
                my_dict['polygon'] = item.get('geometry').get('coordinates')[0]

            result.append(my_dict)

    return pd.DataFrame(result)


def kml_to_geojson(*, kml_path):
    return kml2geojson.main.convert(kml_path)


def convert_to_area_tariff_sql_query(*, data_frame):
    insert_query = """
INSERT INTO services.area_tariffs
(
    name,
    polygon,
    price,
    city_id,
    vehicle_type_id,
    round_trip_percent,
    company_id,
    negotiation_id
)
    """

    values = []
    for index, row in data_frame.iterrows():
        values.append(
            f"('{row['name']}','{json.dumps(row['polygon'])}',{row['price']},{row['city_id']},{
                row['vehicle_type_id']},{row['round_trip_percent']},{row['company_id']},{row['negotiation_id']})"
        )

    return f"{insert_query} VALUES {', '.join(values)};"


def convert_to_area_tariffs_users_sql_query(
    *,
    user_id,
    negotiation_id,
    company
):
    backend = "FRANCHISES"
    return f"""
INSERT INTO services.area_tariffs_users
    (user_id, backend, negotiation_id, company_id)
VALUES
    ({user_id}, '{backend}', {negotiation_id}, {company});
"""

def convert_to_permissions_sql_query(*, users, permissions):
    insert_query = """
INSERT INTO franchises.model_has_permissions
    (permission_id, model_type, model_id)
"""
    model_type = "App\\\\User"
    values = []
    for user in users:
        for permission in permissions:
            values.append(
                f"({permission_map[permission]}, '{model_type}', {user})"
            )

    return f"{insert_query} VALUES {', '.join(values)};"


def main():
    # config

    enterprise = "Don Jacobo Bototá"
    kml_path = "kmls\DJ BOGOTA DOM.kml"
    negotiation_id = 59
    franchise_user_id = 480
    city = "bogota"
    permissions = [
        "edit_destinatary_click_lite",
        # "edit_order_value",
        "edit_invoice",
    ]

    # process

    kml = kml_to_geojson(kml_path=kml_path)

    if len(kml) == 0:
        print("[error] No data found")
        return

    kml = kml[0]

    df = citix_kml_dict_to_data_frame(
        data=kml,
        city_id=cities[city],
        company_id=companies[city],
        negotiation_id=negotiation_id,
        enterprise=enterprise,
    )

    area_tariff = convert_to_area_tariff_sql_query(data_frame=df)

    print(area_tariff)

    area_tariff_user = convert_to_area_tariffs_users_sql_query(
        user_id=franchise_user_id,
        negotiation_id=negotiation_id,
        company=companies[city]
    )

    print(area_tariff_user)

    permissions = convert_to_permissions_sql_query(
        users=[franchise_user_id],
        permissions=permissions
    )

    print(permissions)


if __name__ == "__main__":
    main()
