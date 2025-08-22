class Transit:
	def __init__(self, planet, sign):
		self.planet = planet
		self.sign = sign

	def set_type(self, type):
		self.type = type

	def set_enter_sign(self, sign):
		self.enter_sign = sign

	def set_aspect(self, aspect, planet, sign):
		self.aspect = aspect
		self.second_planet = planet
		self.second_sign = sign

	def __str__(self):
		return "P " + str(self.planet) + " " + self.type

	def __repr__(self):
		return str(self)