#!/usr/bin/env python
import time, os, web, subprocess, json
from transit_teacher import TransitTeacher
from astrolog_wrapper import Astrolog

urls = (
    '/astrolog', 'astrolog',
    '/astrolog/now', 'now',
    '/astrolog/transits', 'transits'
)

app = web.application(urls, globals())

class now:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        

        data = get_and_parse_astrolog()
        char_sun = TransitTeacher.unicode_for(data["planets"][4]["sign"])
        char_moon = TransitTeacher.unicode_for(data["planets"][1]["sign"])
        char_ac = TransitTeacher.unicode_for(data["houses"][1]["sign"])

        return TransitTeacher.font_letter_for(4) + "  " + char_sun + "  " + \
            TransitTeacher.font_letter_for(1) + "  " + char_moon + "  k  " + char_ac

class transits:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        
        
        TransitTeacher.initialize()
        astrolog = Astrolog()
        transits = astrolog.transits_now()
        teacher = TransitTeacher()

        return teacher.explain_all(transits)

class astrolog:
    def GET(self):
        data = get_and_parse_astrolog()
        return json.dumps(data, indent=4, separators=(',', ': '))

astrolog_dir = "astrolog"

def get_and_parse_astrolog():
    astrolog = Astrolog()
    astrolog_output = astrolog.planets_now()
    data = parse_astrolog(astrolog_output)
    return data

planet_numbers = { "Moon": 1, "Merc": 2, "Venu": 3, "Sun": 4, "Mars": 5, "Jupi": 6, "Satu": 7,
    "Uran": 8, "Nept": 9, "Plut": 10 }

sign_numbers = { "Ari": 1, "Tau": 2, "Gem": 3, "Can": 4, "Leo": 5, "Vir": 6, "Lib": 7,
    "Sco": 8, "Sag": 9, "Cap": 10, "Aqu": 11, "Pis": 12 }

house_numbers = { "Asce": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6, "Desc": 7,
    "8th": 8, "9th": 9, "Midh": 10, "11th": 11, "12th": 12 }

def parse_astrolog(input):
    planets = {}
    houses = {}

    for line in input[2:]:
        splitted = filter(None, line.split(" "))
        planet_or_house = splitted[1]

        data = {}
        if planet_or_house in planet_numbers:
            number = planet_numbers[planet_or_house]
            data["sign"] = sign_numbers[splitted[3]]
            data["degree"] = splitted[2]
            planets[number] = data
        elif planet_or_house in house_numbers:
            number = house_numbers[planet_or_house]
            data["sign"] = sign_numbers[splitted[3]]
            data["degree"] = splitted[2]
            houses[number] = data

    return { "planets": planets, "houses": houses}

if __name__ == "__main__":
    app.run()