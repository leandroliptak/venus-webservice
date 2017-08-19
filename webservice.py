#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, os, web, subprocess, json

urls = (
    '/astrolog', 'astrolog',
    '/astrolog/now', 'now'
)

app = web.application(urls, globals())

unicode_for_signs = { 1: "♈", 2: "♉", 3: "♊", 4: "♋", 5: "♌", 6: "♍", 7: "♎", 8: "♏",
    9: "♐", 10: "♑", 11: "♒", 12: "♓" }

class now:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        

        data = get_and_parse_astrolog()
        char_sun = unicode_for_signs[data["planets"][4]["sign"]]
        char_moon = unicode_for_signs[data["planets"][1]["sign"]]
        char_ac = unicode_for_signs[data["houses"][1]["sign"]]

        return "j  " + char_sun + "  s  " + char_moon + "  k  " + char_ac

class astrolog:
    def GET(self):
        data = get_and_parse_astrolog()
        return json.dumps(data, indent=4, separators=(',', ': '))

astrolog_dir = "astrolog"

def get_and_parse_astrolog():
    astrolog_output = get_astrolog_output()
    data = parse_astrolog(astrolog_output)
    return data

def get_astrolog_output():
    filename = str(time.time())
    process = subprocess.Popen(["./astrolog", "-n", "-o0", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=astrolog_dir)
    process.communicate()

    filename = os.path.join(astrolog_dir, filename)
    file = open(filename)
    lines = file.read().splitlines()
    file.close()
    os.remove(filename)

    return lines

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