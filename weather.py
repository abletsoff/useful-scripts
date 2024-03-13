import json
import sys
import requests
import argparse
from datetime import datetime

openweather = 'd2cbd0d95a959c4fbf2c7b7ac6b1bb00'    # https://openweathermap.org/api  (Current weather data plan)
geoip = 'at_FCSMvg6C0NhZriClQcxXnP80sa4e6'          # https://www.geoapify.com/pricing

openweather_url = 'http://api.openweathermap.org/data/2.5/weather?appid=' + openweather
geo_url = 'https://geo.ipify.org/api/v1?apiKey=' + geoip

def openweather_output(data):

    print(str(data['name'] + '-' + data['sys']['country']).center(40, '-') + '\n')

    state_data = data['weather'][0]
    print(' Time:\t\t', datetime.fromtimestamp(data['dt']).strftime('%A  %H:%M:%S'))
    print(' State:\t\t', state_data['main'], '(', state_data['description'], ')')

    main_data = data['main']
    print(' Temperature:\t', round(float(main_data['temp']) - 273, 2), '\u2103')
    print(' Feels like:\t', round(float(main_data['feels_like']) - 273, 2), '\u2103')
    print(' Pressure:\t', int(main_data['pressure']), 'hPa')
    print(' Humidity:\t', int(main_data['humidity']), '%')

    wind_data = data['wind']
    print(' Wind speed:\t', round(float(wind_data['speed']), 2), 'm/s')
    print(' Wind deg:\t ', int(wind_data['deg']), '\u00b0', sep='')

    sun_data = data['sys']
    print(' Sunrise:\t', datetime.fromtimestamp(sun_data['sunrise']).time())
    print(' Sunset:\t', datetime.fromtimestamp(sun_data['sunset']).time())

def response_api(url_master, arguments):

    try:
        url =  url_master
        for key, value in arguments.items():
            url += f'&{str(key)}={str(value)}'
        response = requests.get(url)
        return json.loads(response.text)

    except requests.exceptions.ConnectionError as exp:
        raise SystemExit('Connection failure')
    except json.JSONDecodeError as exp:
        raise exp

def get_location():
    try:
        json_geo = response_api(geo_url, {})
        return json_geo['location']['city'].split(" ", 1)[0]

    except SystemExit as exp:
        print("\a E: " + str(exp))      

def parser():
    parser = argparse.ArgumentParser(description='CLI weather forecast')
    parser.add_argument('-c', metavar='CITY', type=str, nargs='+', help='city for the weather forecast', \
            default=[get_location()])
    return parser.parse_args()

args = parser()

for arg in args.c:
    print()
    try:
        json_weather = response_api(openweather_url, arguments={'q': arg})
        openweather_output(json_weather)

    except SystemExit as exp:
         print("\aE: " + str(exp))

    except KeyError as exp:
        if exp.args[0] == 'name':
            print("\aE: Information about '%s' city is not available" %arg)
    except json.JSONDecodeError as exp:
        print("\aE: Information about '%s' city is not available" %arg)
print()
