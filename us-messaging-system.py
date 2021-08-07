# Note: This bot was never released because of issues with Mailgun API and was scrapped in May 2020 since vaccine availability was no longer an issue


import requests
from time import sleep
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import namedtuple
import pgeocode
import math
from datetime import datetime

# file with the google drive api authentication info
SECRETS_FILE = ""

# scope for google drive api
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# list of appointments available from previous loop
already_available = []

# column index for specific info in excel
lat_column = 6
long_column = 7
state_column = 8
row_num_column = 9

# tuple of brands that will not be tweeted out
whitelist = ()

# format of info for each location that gave vaccine shots
location_format = namedtuple(
    'Info', [
        'name', 'brand', 'city', 'address', 'URL', 'coordinates', 'state', 'id'])

# categories in excel necessary for code
list_of_used_categories = [
    'Timestamp',
    'Email Address',
    'Distance',
    'Zip Code',
    'Consent']


# function to convert zipcode to coordinate
def zip_to_coordinate(zipcode):
    nomi = pgeocode.Nominatim('US')
    coordinate = nomi.query_postal_code(zipcode)
    info = namedtuple('zip_code', ['latitude', 'longitude', 'state_code'])
    lat_long = info(
        coordinate.latitude,
        coordinate.longitude,
        coordinate.state_code)
    return lat_long

# function to calculate distance between 2 coordinates
def distance(origin, destination):

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    # returning distance from user to location in miles
    return d * 0.621371

# function for basic writing to excel
def write_to_excel(message, row, column):
    sheet.update_cell(row, column, message)

# function to format brand name to how it is properly formatted
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
        brand = 'Hy-Vee'
        return brand
    elif brand == 'thrifty_white':
        brand = 'Thrifty White'
        return brand
    elif brand == 'heb':
        brand = 'H-E-B'
        return brand
    elif brand == 'thrifty_white':
        brand = 'Thrifty White'
        return brand
    elif brand == 'price_chopper':
        brand = 'Price Chopper'
        return brand
    else:
        brand = brand.title()

        return brand

# function to compile message to send in twitter dm
def compile_message(name, brand, address, city, state, url, coordinates):
    now = datetime.now()
    timestamp = now.strftime("%m/%d %H:%M")
    brand = format_brand(brand)

    try:
        return "As of " + timestamp + ": New appointment(s) available at [" + format_brand(brand) + " - " + city.title(
        ) + "]\n\n" + name + "\n\n" + address.title() + "\n" + city.title() + ", " + state + "\n" + str(coordinates) + "\n" + url + "\n"
    except TypeError:
        if name is None and brand is None:
            return False
        elif address is None and city is None and coordinates is None:
            return False
        elif brand is None and name is not None and address is not None and city is not None and state is not None and url is not None and coordinates is not None:
            return "\nAs of " + timestamp + ": New appointment(s) available at [" + format_brand(brand) + " - " + city.title(
            ) + "]\n\n" + address.title() + "\n" + city.title() + ", " + state + "\n" + str(coordinates) + "\n" + url + "\n"
        elif address is None and city is None and url is not None and coordinates is not None:
            return "\nAs of " + timestamp + ": New appointment(s) available at [" + format_brand(
                brand) + "]\n\n" + name + "\n\nAddress and city not known" + "\n" + str(coordinates) + "\n" + url + "\n"
        elif coordinates is None and url is None:
            return "\nAs of " + timestamp + ": New appointment(s) available at [" + format_brand(brand) + " - " + city.title(
            ) + "]\n\n" + name + "\n\n" + address.title() + "\n" + city.title() + ", " + state + "\n"
        elif coordinates is None and url is not None:
            return "\nAs of " + timestamp + ": New appointment(s) available at [" + format_brand(brand) + " - " + city.title(
            ) + "]\n\n" + name + "\n\n" + address.title() + "\n" + city.title() + ", " + state + "\n" + url + "\n"
        elif coordinates is not None and url is None:
            return "\nAs of " + timestamp + ": New appointment(s) available at [" + format_brand(brand) + " - " + city.title(
            ) + "]\n\n" + name + "\n\n" + address.title() + "\n" + city.title() + ", " + state + "\n" + str(coordinates) + "\n"

        else:
            return False

# function to send a email
def send_email(recipient, text, brand):
    # log email in .txt file
    f = open("records.txt", "a+")
    f.write("\n" + recipient + "\n" + text)
    f.close()

    # make post request to mailgun to send email
    return requests.post(
        "https://api.mailgun.net/v3/_____/messages",
        auth=("api", mailgun_api_key),
        data={"from": "US Vaccine Bot <_____>",
              "to": [recipient, "_____"],
              "subject": "Appointment(s) available at " + format_brand(brand),
              "text": text})


# function to send email without brand
def send_email_no_brand(recipient, text):
    # log email in .txt file
    f = open("records.txt", "a+")
    f.write("\n" + recipient + "\n" + text)
    f.close()

    # make post request to mailgun to send email
    return requests.post(
        "https://api.mailgun.net/v3/_____/messages",
        auth=("api", mailgun_api_key),
        data={"from": "US Vaccine Bot <_____>",
                      "to": [recipient, "_____"],
                      "subject": "COVID Vaccine appointment(s) available",
              "text": text})

# function to alert of multiple locations at once
def send_multiple_emails(recipient, text):
    # log email in .txt file
    f = open("records.txt", "a+")
    f.write("\n" + recipient + "\n" + text)
    f.close()

    # make post request to mailgun to send email
    return requests.post(
        "https://api.mailgun.net/v3/_____/messages",
        auth=("api", mailgun_api_key),
        data={"from": "US Vaccine Bot <_____>",
                      "to": [recipient, "_____"],
                      "subject": "Appointments available for COVID-19 Vaccine",
              "text": text})


# google drive api setup
creds = ServiceAccountCredentials.from_json_keyfile_name(SECRETS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open("_____").sheet1
sheet2 = client.open("_____").sheet1
# get all info from excel

while True:

    sleep(5)
    states_used = []

    available = []

    # counter for identifiying row of excel spreadsheet with responses, starts
    # at row 1 and add immediately because if counter+=1 is at the end, error
    # in zip code to coordinate would skip and would turn into infinite loop
    user_counter = 1

    responses = sheet.get_all_records()

    # delete all rows with blank answers in needed categories
    deletion_counter = 1
    for response in responses:
        deletion_counter += 1
        for key in response:

            try:
                if response[key].isspace() and key in list_of_used_categories:
                    sheet.delete_rows(deletion_counter)
            except AttributeError:
                continue

    for response in responses:

        user_counter += 1
        # code to add latitude, longitude, and state to excel
        if response['Latitude'] == '' or response['Longitude'] == '' or response['State'] == '':
            # grab named tuple with lat, long, and initials
            lls = zip_to_coordinate(str(response['Zip Code']))
            if lls.state_code == 'nan' or lls.latitude == 'nan' or lls.latitude == 'nan':
                # write latitude
                write_to_excel('ERROR', user_counter, lat_column)
                # write longitude
                write_to_excel('ERROR', user_counter, long_column)
                # write state code
                write_to_excel('ERROR', user_counter, state_column)
                continue
            else:

                # write latitude
                write_to_excel(lls.latitude, user_counter, lat_column)
                # write longitude
                write_to_excel(lls.longitude, user_counter, long_column)
                # write state code
                write_to_excel(lls.state_code, user_counter, state_column)

                if lls.state_code not in states_used:
                    states_used.append(lls.state_code)
        else:
            if response['State'] not in states_used:
                states_used.append(response['State'])

    # check availability of vaccines in states that are using the bot
    for state in states_used:
        current_locations = requests.get(
            'https://www.vaccinespotter.org/api/v0/states/' +
            state +
            '.json').json()['features']
        for location in current_locations:
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
                            state,
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
                            state,
                            id))

        sleep(5)

    # create list of email messages to send
    for response in responses:
        send_backlog = []
        if response['Latitude'] == 'ERROR' or response['Latitude'] == 'ERROR' or response['State'] == 'ERROR':
            continue
        else:

            r_lat_long = (response['Longitude'], response['Latitude'])

        for location in available:

            if location.state == response['State'] and location.id not in already_available and distance(
                    r_lat_long, location.coordinates) < response['Distance']:
                if compile_message(
                        location.name,
                        location.brand,
                        location.address,
                        location.city,
                        location.state,
                        location.URL,
                        location.coordinates) is not False:
                    try:
                        latitude = location.coordinates[1]
                        longitude = location.coordinates[0]
                        formatted_coordinates = (latitude, longitude)
                    except TypeError:
                        pass
                    message = compile_message(
                        location.name,
                        location.brand,
                        location.address,
                        location.city,
                        location.state,
                        location.URL,
                        formatted_coordinates)
                    send_backlog.append(message)

            else:
                continue
        if len(send_backlog) == 0:
            continue
        elif len(send_backlog) == 1:
            if location.brand is not None:
                try:

                    send_email(
                        response['Email Address'],
                        send_backlog[0],
                        location.brand)
                except BaseException:
                    continue
            elif location.brand is None:
                try:

                    send_email_no_brand(
                        response['Email Address'], send_backlog[0])
                except BaseException:
                    continue
        elif len(send_backlog) > 1:
            full_message = ''
            for message in send_backlog:
                full_message += ('\n' + message)
            try:

                send_multiple_emails(response['Email Address'], full_message)
            except BaseException:
                continue

    already_available = []
    for location in available:
        already_available.append(location.id)

    # code to cancel subscription for those who filled out form to cancel
    cancel_responses = sheet2.get_all_records()
    cancel_counter = 1
    for response in cancel_responses:
        cancel_counter += 1

        for count, r in enumerate(responses):
            if response['Email Address'] == r['Email Address']:
                sheet.delete_row(count)

    # delete all rows with errors
    error_counter = 1
    for response in responses:
        error_counter += 1
        for key in response:
            if response[key] == 'ERROR':
                sheet.delete_row(error_counter)
