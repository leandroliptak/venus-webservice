#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from datetime import timedelta

import os
import sys

out_dir = "img/"

astrolog = Astrolog()
day_shift = 5

profile = {}

def run(person, start_date, end_date):
	print "Perfil:", person
	print "Desde:", start_date
	print "Hasta:", end_date
	print "--"

	d = start_date
	while d < end_date:
		run_date(person, d)
		d = d + timedelta(days=day_shift)

def run_date(person, date):
	print "Date", date
	out = astrolog.run("-i", person, "-T", str(date.month), str(date.day), str(date.year),
		"-RT0", "6", "7", "8", "9", "10",
		"-RA", "Tri", "Sex",
		"-c", "1", # Casas Koch
		"-RC", "22", "31", # Incluyo cúspides de casas
		"-Ao", "Opp", "3", "-Ao", "Con", "3", "-Ao", "Squ", "3")
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

		#print date.strftime('%d/%m/%Y'), transit + "(T)", aspect, natal, power

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

def analysis(natal, transit, aspect):
		tp = profile[(natal, transit)][aspect]
		periods = isolate_periods(tp)

		for period in periods:
			if len(period) < 4: return # No se puede interpolar con menos de 4 elementos

			start_year = period[0][0].year
			print "Analysis", natal, transit, aspect, start_year

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

colors_for_planets = { "Sun": "goldenrod", "Moon": "khaki", "Mercury": "magenta", "Venus": "green", "Mars": "red",
	"Jupiter": "crimson", "Saturn": "dark blue", "Uranus": "sky blue", "Neptune": "teal", "Pluto": "maroon"}

s_for_p = { "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Sun": "⊙", "Mars": "♂",
	"Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇" }

s_for_a = { "Opp": "☍", "Sex": "⚹", "Tri": "△", "Squ": "□", "Con": "☌" }

def group_analysis(natal, transit, aspect):
	tp = profile[(natal, transit)][aspect]

	str_name = s_for_p[transit] + " t " + s_for_a[aspect] + " " + s_for_p[natal]

	begin = tp[0][0]
	end = tp[-1][0]

	duration = (end - begin).days
	d_years = duration / 365
	d_months = (duration % 365) / 30

	x = np.array([ calendar.timegm(v[0].timetuple()) for v in tp ], dtype="float64")
	y = np.array([ v[2] for v in tp ], dtype="float64")
	max_dates = argrelmax(y)

	f = interp1d(x, y, kind='cubic')

	plt.plot(x, f(x), 'xkcd:' + colors_for_planets[natal], label=str_name)

	y_off = [15, 40]
	x_off = [0, 20]
	for v in [0] + list(max_dates[0]):
		label = str_name + "\n" + tp[v][0].strftime('%d/%m/%Y') + "\n" + tp[v][1]
		label.encode("utf-8")
		plt.annotate(label, xy=(x[v], y[v]), xytext=(x_off[0], y_off[0]), textcoords = 'offset points',
			arrowprops=dict(arrowstyle="->"), fontsize=8)
		y_off = y_off[::-1]
		x_off = x_off[::-1]

	plt.xticks([])
	plt.yticks([])

#	plt.suptitle(str_name, fontsize=16)
#	plt.title(str_duration, y=1.19)
#	plt.subplots_adjust(left=0.1, right=0.9, top=0.75, bottom=0.1)

	## Se guarda la imagen
#	plt.savefig("img/%s_%s_%s.png" % (natal, transit, aspect))
#	plt.clf()

def create_pdf():
	print "Creando el PDF"
	pdf = FPDF()
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

	pdf.output("profile.pdf", "F")	

#########################################################################################################
#########################################################################################################

if len(sys.argv) < 4:
	print "Parámetros: <persona> <fecha_desde> <fecha_hasta>"
	quit()

start_date = parser.parse(sys.argv[2])
end_date = parser.parse(sys.argv[3])

run(sys.argv[1], start_date, end_date)

natal_order = ["Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
	"Ascendant", "Midheaven", "Descendant", "Nadir",
	"2nd", "3rd", "5th", "6th", "8th", "9th", "11th", "12th"]
transit_order = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

for natal in natal_order:
	for transit in transit_order:
		if (natal, transit) in profile:
			aspects = profile[(natal, transit)]
			for aspect in aspects:
				analysis(natal, transit, aspect)
				#group_analysis(natal, transit, aspect)
#plt.legend()
#plt.show()
create_pdf()
