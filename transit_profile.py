#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://localhost:8080/astrolog/astrobio?date=23/5/1990&time=4:40&place=Buenos%20Aires,%20Argentina&mail=leandroliptak@gmail.com&from=1/1/2018&to=1/1/2019

from itertools import groupby
from operator import itemgetter

import numpy as np
from scipy.signal import argrelmax
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

from fpdf import FPDF

import calendar

import string
from astrolog_wrapper import Astrolog

from dateutil import parser
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import time as Time

import os
import sys
import shutil

import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

sender_address = 'leandroliptak.com@gmail.com'
sender_pass = 'creoenlamagia'

base_dir = "img/"

astrolog = Astrolog()
day_shift = 5

natal_order = ["Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
	"Ascendant", "Midheaven", "Descendant", "Nadir",
	"2nd", "3rd", "5th", "6th", "8th", "9th", "11th", "12th"]
transit_order = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

def from_webservice (data):
	try:
		date = data["date"]
		time = data["time"]
		place = data["place"]
		mail = data["mail"]
	except:
		return astrolog.person_arg_error_json("key")

	try:
		start_date = parser.parse(data["from"])
	except:
		return astrolog.person_arg_error_json("from")
	try:
		end_date = parser.parse(data["to"])
	except:
		return astrolog.person_arg_error_json("to")
	try:
		date_time = datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M")
	except:
		return astrolog.person_arg_error_json("date")
	try:
		location = astrolog.location(place)
	except:
		return astrolog.person_arg_error_json("place")


	if start_date > end_date:
		return astrolog.person_arg_error_json("range")


	difference_in_years = relativedelta(end_date, start_date).years
	if difference_in_years < 1 or difference_in_years > 10:
		return astrolog.person_arg_error_json("range")

	hour_shift = astrolog.hour_shift(date_time, location)

	_lat = astrolog.mm_ss(location.latlng[0])
	_long = -astrolog.mm_ss(location.latlng[1])

	profile = {}

	prefix = str(Time.time())
	out_dir = base_dir + prefix + "/"
	os.mkdir (out_dir)

	try:
		d = start_date
		while d < end_date:
			run_date_from_birthdata(profile, date_time, hour_shift, _long, _lat, d)
			d = d + timedelta(days=day_shift)

		for natal in natal_order:
			for transit in transit_order:
				if (natal, transit) in profile:
					aspects = profile[(natal, transit)]
					for aspect in aspects:
						analysis(out_dir, profile, natal, transit, aspect)

		create_pdf(out_dir, date_time, location, start_date, end_date)
		send_report(out_dir, mail)
	except:
		shutil.rmtree(out_dir)
		return astrolog.person_arg_error_json("other")

	shutil.rmtree(out_dir)

	data = { "status": "ok" }
	data["place"] = { "address" : location.address,
		"lat": location.latlng[0],
		"lng": location.latlng[1] }
	data["tz"] = hour_shift

	return json.dumps(data)

def send_report(out_dir, receiver_address):
	message = MIMEMultipart()
	message['From'] = sender_address
	message['To'] = receiver_address
	message['Subject'] = 'Informe de astrobiografía'

	path_to_pdf = out_dir + "profile.pdf"
	with open(path_to_pdf, "rb") as f:
	    attach = MIMEApplication(f.read(),_subtype="pdf")
	attach.add_header('Content-Disposition','attachment',filename="reporte.pdf")
	message.attach(attach)

	session = smtplib.SMTP('smtp.gmail.com', 587)
	session.starttls()
	session.login(sender_address, sender_pass)

	text = message.as_string()
	session.sendmail(sender_address, receiver_address, text)
	session.quit()

def run(person, start_date, end_date):
	profile = {}
	d = start_date
	while d < end_date:
		run_date(profile, person, d)
		d = d + timedelta(days=day_shift)
	return profile

def run_date_from_birthdata(profile, date_time, hour_shift, _long, _lat, date):
	out = astrolog.run("-qb", date_time.month, date_time.day, date_time.year,
		date_time.time(), "ST", -hour_shift, _long, _lat,
		"-T", str(date.month), str(date.day), str(date.year),
		"-RT0", "6", "7", "8", "9", "10",
		"-RA", "Tri", "Sex",
		"-c", "1", # Casas Koch
		"-RC", "22", "31", # Incluyo cúspides de casas
		"-Ao", "Opp", "3", "-Ao", "Con", "3", "-Ao", "Squ", "3")
	process_output(profile, out, date)

def run_date(profile, person, date):
	out = astrolog.run("-i", person, "-T", str(date.month), str(date.day), str(date.year),
		"-RT0", "6", "7", "8", "9", "10",
		"-RA", "Tri", "Sex",
		"-c", "1", # Casas Koch
		"-RC", "22", "31", # Incluyo cúspides de casas
		"-Ao", "Opp", "3", "-Ao", "Con", "3", "-Ao", "Squ", "3")
	process_output(profile, out, date)

def process_output(profile, out, date):
	lines = string.join(out, "").splitlines()

	for transit_influence in lines:
		if transit_influence == "Empty transit list.": continue
		
		w = transit_influence.split("- ")
		orb = w[1].split(" ")[1]
		power = float(w[-1].split(":")[-1].split(" R")[0])

		w = w[0].split("trans")[-1].split(" natal ")
		natal = w[-1].split(" ")[1]
		
		w = w[0].strip().split(" ")
		transit = w[0]
		aspect = w[-1]

		key = (natal, transit)

		if key not in profile:
			profile[key] = {}
		transit_profile = profile[key]

		if aspect not in transit_profile:
			transit_profile[aspect] = []

		date_power = transit_profile[aspect]
		date_power.append((date, orb, power))

def isolate_periods(profile):
	# Si entre un evento de transito y otro hay mas de un año de tiempo, es que son dos transitos distintos.
	# Así, separamos el profile dividiéndolo en los segmentos de tránsitos correspondientes.
	periods = []
	current = []
	last = profile[0]
	for transit in profile:
		if transit[0] - last[0] > timedelta(days=365):
			periods.append(current)
			current = []
		current.append(transit)
		last = transit

	periods.append(current)
	return periods

def analysis(out_dir, profile, natal, transit, aspect):
		tp = profile[(natal, transit)][aspect]
		periods = isolate_periods(tp)

		for period in periods:
			if len(period) < 4: return # No se puede interpolar con menos de 4 elementos

			start_year = period[0][0].year

			str_name = "%s %s (t) %s %s" % (start_year, transit, aspect, natal)

			begin = period[0][0]
			end = period[-1][0]

			duration = (end - begin).days
			d_years = duration / 365
			d_months = (duration % 365) / 30

			str_duration = u"Duración: %s días (aprox. %s años y %s meses)" % (duration, d_years, d_months)

			x = np.array([ calendar.timegm(v[0].timetuple()) for v in period ], dtype="float64")
			y = np.array([ v[2] for v in period ], dtype="float64")
			max_dates = argrelmax(y)

			f = interp1d(x, y, kind='cubic')

			plt.plot(x, y, 'o', x, f(x), '-')

			y_off = [15, 40]
			x_off = [0, 20]
			for v in [0] + list(max_dates[0]):
				label = period[v][0].strftime('%d/%m/%Y') + "\n" + period[v][1]
				plt.annotate(label, xy=(x[v], y[v]), xytext=(x_off[0], y_off[0]), textcoords = 'offset points',
					arrowprops=dict(arrowstyle="->"), fontsize=8)
				y_off = y_off[::-1]
				x_off = x_off[::-1]

			plt.xticks([])
			plt.yticks([])

			plt.suptitle(str_name, fontsize=16)
			plt.title(str_duration, y=1.19)
			plt.subplots_adjust(left=0.1, right=0.9, top=0.75, bottom=0.1)

			## Se guarda la imagen
			plt.savefig(out_dir + "%s_%s_%s_%s.png" % (start_year, natal, transit, aspect))
			plt.clf()

def create_pdf(out_dir, date_time, location, begin, end):

	class PDF(FPDF):
	    def header(self):
	        self.set_font('Arial', '', 10)
	        self.multi_cell(0,5, 'leandroliptak.com - Informe de Astrobiografia' +
	        	'\nDatos natales: ' + date_time.strftime('%d/%m/%Y %H:%M') + ' - Lugar: ' + location.address +
	        	'\nRango: ' + begin.strftime('%d/%m/%Y') + " hasta " + end.strftime('%d/%m/%Y'))

	pdf = PDF()
	transit_images = os.listdir(out_dir)
	transit_images.sort() # Ordenamos por año

	image_index = 2
	image_positions = [(15, 25), (15, 155)]

	for image in transit_images:
		if image_index > 1:
			pdf.add_page()
			#pdf.image("header.png", 15, 15, 100)
			image_index = 0

		x, y = image_positions[image_index]

		pdf.image(out_dir + image, x, y, 180)
		os.remove(out_dir + image)
		image_index = image_index + 1

	pdf.output(out_dir + "profile.pdf", "F")	

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "Parámetros: <persona> <fecha_desde> <fecha_hasta>"
		quit()

	start_date = parser.parse(sys.argv[2])
	end_date = parser.parse(sys.argv[3])

	profile = run(sys.argv[1], start_date, end_date)

	for natal in natal_order:
		for transit in transit_order:
			if (natal, transit) in profile:
				aspects = profile[(natal, transit)]
				for aspect in aspects:
					analysis(profile, natal, transit, aspect)
	create_pdf()