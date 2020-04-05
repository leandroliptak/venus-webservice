#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby
from operator import itemgetter

import numpy as np
from scipy.signal import argrelmax
from scipy.interpolate import interp1d

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as mticker

from fpdf import FPDF

import calendar

import string
from astrolog_wrapper import Astrolog

from dateutil import parser
from datetime import timedelta
import time

import os
import sys

out_dir = "img/"

astrolog = Astrolog()
day_shift = 5

profile = {}

Writer = animation.writers['ffmpeg']
writer = Writer(fps=20, metadata=dict(artist='Leandro Liptak'), bitrate=1800)

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

		key = transit

		if key not in profile:
			profile[key] = []
		transit_profile = profile[key]

		if len(transit_profile) > 0:
			prev_date = transit_profile[-1][0]
			if prev_date == date:
				power = transit_profile[-1][1] + power
				transit_profile.pop()

		transit_profile.append((date, power))

def analysis(sdate, edate):
	fig, ax = plt.subplots(figsize=(10,6))

	dataset = {}
	planets = ["Saturn", "Uranus", "Neptune", "Pluto"]

	min = 0
	max = 0

	max_x = []

	for transit in planets:
		period = profile[transit]

		if len(period) < 4: return # No se puede interpolar con menos de 4 elementos

		begin = period[0][0]
		end = period[-1][0]

		x = np.array([ calendar.timegm(v[0].timetuple()) for v in period ], dtype="float64")
		y = np.array([ v[1] for v in period ], dtype="float64")
		
		f = interp1d(x, y, kind='cubic')
		dataset[transit] = {}
		dataset[transit]["x"] = x
		dataset[transit]["y"] = y
		dataset[transit]["f"] = f

		if np.min(y) < min: min = np.min(y)
		if np.max(y) > max: max = np.max(y)
		if len(x) > len(max_x): max_x = x

		#max_dates = argrelmax(y, order=10)
		#
		#y_off = [15, 40]
		#x_off = [0, 20]
		#for v in [0] + list(max_dates[0]):
		#	label = period[v][0].strftime('%d/%m/%Y')
		#	plt.annotate(label, xy=(x[v], y[v]), xytext=(x_off[0], y_off[0]), textcoords = 'offset points',
		#		arrowprops=dict(arrowstyle="->"), fontsize=8)
		#	y_off = y_off[::-1]
		#	x_off = x_off[::-1]

	plt.xlim(max_x[0], max_x[-1])
	plt.ylim(min, max)

	lines = []
	for planet in planets:
		ln, = plt.plot([], [], lw=2, label=planet)
		lines.append(ln)

	sdate_ = calendar.timegm(sdate.timetuple())
	def animate(i):
		d = sdate + timedelta(days=i * 30)
		d_ = calendar.timegm(d.timetuple())

		for n in range(0, len(planets)):
			planet = planets[n]
			ln = lines[n]
			x = dataset[planet]["x"]
			f = dataset[planet]["f"]
			x_ = np.linspace(x[0], d_, 2000)
			try:
				ln.set_data(x_, f(x_))
			except ValueError:
				pass

		return lines

	delta = edate - sdate
	months = delta.days / 30
	ani = animation.FuncAnimation(fig, animate, frames=months, interval=20, repeat=False, blit=True)
	
	def update_ticks(x, pos):
		t = time.gmtime(x)
		return time.strftime("%b %y", t)

	plt.locator_params(axis='x', nbins=20)
	
	ax.xaxis.set_major_formatter(mticker.FuncFormatter(update_ticks))
	ax.tick_params(axis ='x', rotation = 45)

	ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
	          ncol=2, fancybox=True, shadow=True)
	plt.show()
	
	#ani.save('video.mp4', writer=writer)
	#plt.savefig(out_dir + "%s_%s_%s_%s.png" % (start_year, natal, transit, aspect))


if len(sys.argv) < 4:
	print "Parámetros: <persona> <fecha_desde> <fecha_hasta>"
	quit()

start_date = parser.parse(sys.argv[2])
end_date = parser.parse(sys.argv[3])

run(sys.argv[1], start_date, end_date)
analysis(start_date, end_date)
