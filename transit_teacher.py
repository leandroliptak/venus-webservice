# -*- coding: utf-8 -*-

import json
import StringIO

class TransitTeacher:
	db = {}

	planet_font_letter = { 1: "B", 2: "C", 3: "D", 4: "A", 5: "E", 6: "F", 7: "G", 8: "H",
		9: "I", 10: "J" }

	unicode_for_planets = { 1: "☽", 2: "☿", 3: "♀", 4: "⊙", 5: "♂", 6: "♃", 7: "♄", 8: "♅",
		9: "♆", 10: "♇" }

	unicode_for_signs = { 1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h",
	    9: "i", 10: "j", 11: "k", 12: "l" }

	unicode_for_aspects = { "opp": "n", "sex": "q", "tri": "p", "squ": "o", "con": "m" }

	@classmethod
	def initialize(cls):
		cls.db = json.loads(open("transits/teacher.json").read())

	@classmethod
	def unicode_for(cls, sign_number):
		return cls.unicode_for_signs[sign_number].decode("utf-8")

	@classmethod
	def unicode_for_aspect(cls, aspect_code):
		return cls.unicode_for_aspects[aspect_code].decode("utf-8")

	@classmethod
	def unicode_for_planet(cls, sign_number):
		return cls.unicode_for_planets[sign_number].decode("utf-8")

	@classmethod
	def font_letter_for(cls, planet_number):
		return cls.planet_font_letter[planet_number]

	def explain_for_mailing(self, transits):
		out = StringIO.StringIO()

		for transit in transits:
			if transit.type == "aspect":
				first = self.planet(transit.planet)
				second = self.planet(transit.second_planet)
				aspect = self.aspect(transit.aspect)

				out.write("<span style='font-size: 24px;'>")
				out.write(self.unicode_for_planet(transit.planet) + " " +
					self.unicode_for_aspect(transit.aspect.lower()) + " " +
					self.unicode_for_planet(transit.second_planet) + " ")

				out.write(first["name"].capitalize() + " en " +
					aspect["name"] + " a " + second["name"])
				out.write("</span><br>")

				out.write("<p>" + first["desc"].capitalize() + " " + aspect["desc"]
					+ " " + second["desc"] + ".</p><br><br>")
			elif transit.type == "enter":
				first = self.planet(transit.planet)
				sign = self.sign(transit.enter_sign)
				out.write("<span style='font-size: 24px;'>")
				out.write(self.unicode_for_planet(transit.planet) + " " +
					self.unicode_for(transit.enter_sign) + " ")				
				out.write(first["name"].capitalize() + " entra en el signo de " + sign["name"])
				out.write("</span><br><br>")

		return out.getvalue()

	def explain_all(self, transits):
		out = StringIO.StringIO()
		out.writelines("<table class='transit'>")

		for transit in transits:
			self.explain(transit, out)

		out.writelines("</table>")
		return out.getvalue()

	def explain(self, transit, out):
		if transit.type == "aspect":
			self.explain_aspect(transit, out)
		elif transit.type == "enter":
			self.explain_enter(transit, out)

	def explain_enter(self, transit, out):
		first = self.planet(transit.planet)
		sign = self.sign(transit.enter_sign)

		self.def_title(first["name"].capitalize() + " entra en el signo de " + sign["name"], out)

		out.write("<tr>")
		self.def_symbols(self.font_letter_for(transit.planet) + "<br>" +
			self.unicode_for(transit.enter_sign), out)
		out.write("</tr>")

	def explain_aspect(self, transit, out):
		first = self.planet(transit.planet)
		second = self.planet(transit.second_planet)
		aspect = self.aspect(transit.aspect)

		self.def_title(first["name"].capitalize() + " en " + aspect["name"] + " a " + second["name"], out)

		out.write("<tr>")
		self.def_symbols(self.font_letter_for(transit.planet) + "<br>" +
			self.unicode_for_aspect(transit.aspect.lower()) + "<br>" +
			self.font_letter_for(transit.second_planet),out)

		self.def_desc(first["desc"].capitalize() + " " + aspect["desc"] + " " + second["desc"] + ".", out)
		out.write("</tr>")

	def def_desc(self, text, out):
		out.write("<td>")
		out.write(text)
		out.write("</td>")

	def def_symbols(self, text, out):
		out.write("<td class='transit-symbols'>")
		out.write(text)
		out.write("</td>")

	def def_title(self, text, out):
		out.write("<tr><td class='transit-title' colspan='2'>")
		out.write(text)
		out.write("</td></tr>")

	def aspect(self, aspect_code):
		return self.db["aspects"][aspect_code.lower()]

	def planet(self, planet_number):
		return self.db["planets"][str(planet_number)]

	def sign(self, sign_number):
		return self.db["signs"][str(sign_number)]
