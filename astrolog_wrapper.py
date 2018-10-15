import time, os, web, subprocess, string, re
from transit import Transit

class Astrolog:
	astrolog_dir = "astrolog"

	planet_numbers = { "Moon": 1, "Merc": 2, "Venu": 3, "Sun": 4, "Mars": 5, "Jupi": 6, "Satu": 7,
		"Uran": 8, "Nept": 9, "Plut": 10 }

	sign_numbers = { "Ari": 1, "Tau": 2, "Gem": 3, "Can": 4, "Leo": 5, "Vir": 6, "Lib": 7,
	    "Sco": 8, "Sag": 9, "Cap": 10, "Aqu": 11, "Pis": 12 }

	house_numbers = { "Asce": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6, "Desc": 7,
	    "8th": 8, "9th": 9, "Midh": 10, "11th": 11, "12th": 12 }

	def transits_now(self):
		out, err = self.run("-d", "-n")
		lines = string.join(out, "").splitlines()
		transits = []
		for line in lines:
			line = re.sub("([0-9]{1,2}-) ([1-9]-[0-9]{4})", r"\1\2", line) # FIX DATES
			splitted = filter(None, line.split(" "))
			planet = splitted[3][:4]
			planet_number = self.planet_numbers[planet]

			sign = re.sub("[()\[\]]", "", splitted[4])
			sign_number = self.sign_numbers[sign]

			t = Transit(planet_number, sign_number)

			type = splitted[5]
			transit_type = None
			if type in ["Con", "Sex", "Squ", "Tri", "Opp"]:
				t.set_type("aspect")
				aspect = type
				second_planet = splitted[7][:4]
				second_planet_number = self.planet_numbers[second_planet]
				second_sign = re.sub("[()\[\]]", "", splitted[6])
				second_sign_number = self.sign_numbers[second_sign]
				t.set_aspect(aspect, second_planet_number, second_sign_number)
			elif type == "-->":
				t.set_type("enter")
				enter_sign = splitted[6][:3]
				enter_sign_number = self.sign_numbers[enter_sign]
				t.set_enter_sign(enter_sign_number)
			elif re.search("./.", type):
				t.set_type(splitted[5])

			transits.append(t)
		return transits

	def planets_now(self):
		return self.run_to_file("-n")

	def run(self, *parameters):
		process = subprocess.Popen(["./astrolog"] + list(parameters),
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			cwd=self.astrolog_dir)
		out, err = process.communicate()
		return out, err

	def run_to_file(self, *parameters):
		filename = str(time.time())
		self.run("-o0", filename, *parameters)

		filename = os.path.join(self.astrolog_dir, filename)
		file = open(filename)
		lines = file.read().splitlines()
		file.close()
		os.remove(filename)

		return lines

	def parse(self, input):
	    planets = {}
	    houses = {}

	    for line in input[2:]:
	        splitted = filter(None, line.split(" "))
	        planet_or_house = splitted[1]

	        data = {}
	        if planet_or_house in self.planet_numbers:
	            number = self.planet_numbers[planet_or_house]
	            data["sign"] = self.sign_numbers[splitted[3]]
	            data["degree"] = int(splitted[2])
	            data["minute"] = int(splitted[4].split(".")[0])
	            planets[number] = data
	        elif planet_or_house in self.house_numbers:
	            number = self.house_numbers[planet_or_house]
	            data["sign"] = self.sign_numbers[splitted[3]]
	            data["degree"] = int(splitted[2])
	            data["minute"] = int(splitted[4].split(".")[0])
	            houses[number] = data

	    return { "planets": planets, "houses": houses}