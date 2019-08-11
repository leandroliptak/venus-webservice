#!/usr/bin/env python
import time, os, web, subprocess, json
from transit_teacher import TransitTeacher
from astrolog_wrapper import Astrolog

urls = (
    '/astrolog', 'astrolog',
    '/astrolog/now', 'now',
    '/astrolog/transits', 'transits',
    '/astrolog/transits_mailing', 'transits_mailing',
    '/astrolog/person', 'person'
)

app = web.application(urls, globals())

class person:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        

        data = web.input()

        astrolog = Astrolog()

        return astrolog.person(data["date"], data["time"], data["place"])

class now:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        

        data = get_and_parse_astrolog()
        char_sun = TransitTeacher.unicode_for(data["planets"][4]["sign"])
        char_moon = TransitTeacher.unicode_for(data["planets"][1]["sign"])
        char_ac = TransitTeacher.unicode_for(data["houses"][1]["sign"])

        return TransitTeacher.font_letter_for(4) + char_sun + "  " + \
            TransitTeacher.font_letter_for(1) + char_moon + "  P" + char_ac

class transits:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        
        
        TransitTeacher.initialize()
        astrolog = Astrolog()
        transits = astrolog.transits_now()
        teacher = TransitTeacher()

        return teacher.explain_all(transits)

class transits_mailing:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        
        
        TransitTeacher.initialize()
        astrolog = Astrolog()
        transits = astrolog.transits_now()
        teacher = TransitTeacher()

        return teacher.explain_for_mailing(transits)

class astrolog:
    def GET(self):
        data = get_and_parse_astrolog()
        return json.dumps(data, indent=4, separators=(',', ': '))

astrolog_dir = "astrolog"

def get_and_parse_astrolog():
    astrolog = Astrolog()
    astrolog_output = astrolog.planets_now()
    data = astrolog.parse(astrolog_output)
    return data

if __name__ == "__main__":
    app.run()