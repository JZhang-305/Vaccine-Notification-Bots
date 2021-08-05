import requests
import time
import tweepy
from datetime import datetime
from collections import namedtuple

# input api key
api_key = ''
# input api secret key
api_secret_key = ''
# input access token
access_token = ''
# input access secret token
access_secret_token = ''

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_secret_token)
api = tweepy.API(auth)

# interval in seconds between each search
interval = 5

location_format = namedtuple(
    'Info', [
        'name', 'brand', 'city', 'address', 'URL', 'coordinates', 'state', 'id'])


def format_brand(brand):
    title_brands = [
        'walmart',
        'walgreens',
        'kroger',
        'albertsons',
        'pharmaca',
        'centura',
        'weis',
        'wegmans']
    if brand in title_brands:
        brand = brand.title()
        return brand
    elif brand == 'cvs':
        brand = brand.upper()
        return brand
    elif brand == 'sams_club':
        brand = "Sam's Club"
        return brand
    elif brand == 'rite_aid':
        brand = "Rite-Aid"
        return brand
    elif brand == 'comassvax':
        brand = 'COMassVax'
        return brand
    elif brand == 'southeastern_grocers':
        brand = "Southeastern Grocers"
        return brand
    elif brand == 'hyvee':
        brand == 'Hy-Vee'
        return brand
    elif brand == 'thrifty_white':
        brand == 'Thrifty White'
        return brand
    elif brand == 'heb':
        brand = 'H-E-B'
        return brand
    else:
        brand = brand.title()
        return brand


def compile_message(name, brand, address, city, state, url, coordinates):
    now = datetime.now()
    timestamp = now.strftime("%m/%d %H:%M")
    brand = format_brand(brand)

    try:
        return "As of " + timestamp + ": New appointment(s) available at [" + format_brand(
            brand) + " - " + city + "]\n\n" + name + "\n\n" + address + "\n" + city + ", " + state + "\n" + str(coordinates) + "\n" + url
    except TypeError:
        if name is None and brand is None:
            return False
        elif address is None and city is None and coordinates is None:
            return False
        elif brand is None and name is not None and address is not None and city is not None and state is not None and url is not None and coordinates is not None:
            return "As of " + timestamp + \
                ": New appointment(s) available at [" + brand + " - " + city + "]\n\n" + address + "\n" + city + ", " + state + "\n" + str(coordinates) + "\n" + url
        elif address is None and city is None and url is not None and coordinates is not None:
            return "As of " + timestamp + \
                ": New appointment(s) available at [" + brand + "]\n\n" + name + "\n\nAddress and city not known" + "\n" + str(coordinates) + "\n" + url
        elif coordinates is None and url is None:
            return "As of " + timestamp + \
                ": New appointment(s) available at [" + brand + " - " + city + "]\n\n" + name + "\n\n" + address + "\n" + city + ", " + state
        elif coordinates is None and url is not None:
            return "As of " + timestamp + \
                ": New appointment(s) available at [" + brand + " - " + city + "]\n\n" + name + "\n\n" + address + "\n" + city + ", " + state + "\n" + url
        elif coordinates is not None and url is None:
            return "As of " + timestamp + \
                ": New appointment(s) available at [" + brand + " - " + city + "]\n\n" + name + "\n\n" + address + "\n" + city + ", " + state + "\n" + str(coordinates)

        else:
            return False


already_available = []


while True:

    available = []
    try:
        ct = requests.get(
            'https://www.vaccinespotter.org/api/v0/states/ct.json').json()['features']
    except BaseException:
        continue
    for location in ct:
        if location['properties']['appointments_available_all_doses']:
            id = str(location['properties']['id']) + \
                str(location['properties']['provider_location_id'])
            try:
                available.append(
                    location_format(
                        location['properties']['name'],
                        location['properties']['provider'].upper(),
                        location['properties']['city'].title(),
                        location['properties']['address'],
                        location['properties']['url'],
                        location['geometry']['coordinates'],
                        'CT',
                        id))
            except AttributeError:
                available.append(
                    location_format(
                        location['properties']['name'],
                        location['properties']['provider'],
                        location['properties']['city'],
                        location['properties']['address'],
                        location['properties']['url'],
                        location['geometry']['coordinates'],
                        'CT',
                        id))

    time.sleep(interval)

    for location in available:
        if location.id not in already_available and location.brand != 'rite_aid':
            message = compile_message(
                location.name,
                location.brand,
                location.address,
                location.city,
                location.state,
                location.URL,
                location.coordinates)
            api.update_status(message)
            print(message)

    already_available = []
    for location in available:
        already_available.append(location.id)
