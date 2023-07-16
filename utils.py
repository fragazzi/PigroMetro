import requests


def geocode_place(place):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={place}"
    response = requests.get(url)
    data = response.json()
    if data:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat, lon
    else:
        return None, None


def calculate_distance(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    response = requests.get(url)
    data = response.json()
    if data.get('code') == 'Ok':
        route = data['routes'][0]
        distance = route['distance'] / 1000
        return distance
    else:
        return None


def transform_date(date_tokens):
    if 0 < int(date_tokens[0]) < 10:
        date_tokens[0] = "0" + date_tokens[0]

    month_dict_ita = {
        'gennaio': '01',
        'febbraio': '02',
        'marzo': '03',
        'aprile': '04',
        'maggio': '05',
        'giugno': '06',
        'luglio': '07',
        'agosto': '08',
        'settembre': '09',
        'ottobre': '10',
        'novembre': '11',
        'dicembre': '12'
    }

    return f"{date_tokens[0]}/{month_dict_ita[date_tokens[1]]}/{date_tokens[2]}"