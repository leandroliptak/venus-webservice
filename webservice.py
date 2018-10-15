#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os, web, subprocess, json
from web import form
from transit_teacher import TransitTeacher
from astrolog_wrapper import Astrolog

urls = (
    '/astrolog', 'astrolog',
    '/astrolog/now', 'now',
    '/astrolog/transits', 'transits',
    '/astrolog/transits_mailing', 'transits_mailing',
    '/astrolog/interface', 'interface'
)

app = web.application(urls, globals())

render = web.template.render('templates/')

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

class transits_mailing:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        
        
        TransitTeacher.initialize()
        astrolog = Astrolog()
        transits = astrolog.transits_now()
        teacher = TransitTeacher()

        return teacher.explain_for_mailing(transits)

interfaceForm = form.Form(
    form.Textbox("Nombre"),
    form.Textbox(u"Día"),
    form.Textbox("Mes"),
    form.Textbox(u"Año"),
    form.Textbox("Hora"),
    form.Textbox("Uso horario"),
    form.Textbox("Longitud"),
    form.Textbox("Latitud"),
    form.Textbox("Lugar"),
    )

class interface:
    def GET(self):
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        

        f = interfaceForm()
        return render.interface(f)
    def POST(self):
        data = web.input()

        astrolog = Astrolog()        
        out, err = astrolog.run("-qb", data["Mes"], data["Día"], data["Año"], data["Hora"], "ST",
            data["Uso horario"], data["Longitud"], data["Latitud"], "-zi", data["Nombre"],
            data["Lugar"])

        return out

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