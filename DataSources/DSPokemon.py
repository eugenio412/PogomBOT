import math

class DSPokemon:
	def __init__(self, encounter_id, spawnpoint_id, pokemon_id, latitude, longitude, disappear_time, ivs, move1, move2):
		self.encounter_id = encounter_id
		self.spawnpoint_id = spawnpoint_id
		self.pokemon_id = pokemon_id
		self.latitude = latitude
		self.longitude = longitude
		self.disappear_time = disappear_time # Should be datetime
		self.ivs = ivs
		self.move1 = move1
		self.move2 = move2

	def getEncounterID(self):
		return self.encounter_id

	def getSpawnpointID(self):
		return self.spawnpoint_id

	def getPokemonID(self):
		return self.pokemon_id

	def getLatitude(self):
		return self.latitude

	def getLongitude(self):
		return self.longitude

	def getDisappearTime(self):
		return self.disappear_time

	def getIVs(self):
		return self.ivs

	def getMove1(self):
		return self.move1

	def getMove2(self):
		return self.move2

	def filterbylocation(self,SW_loc,NE_loc,location_I,distance_I):
		rat = distance_I / 6378.1 # Assuming that we are on earth!

		# Do a simple conditional, no maths
		if float(self.latitude) >= SW_loc.deg_lat and float(self.latitude) <= NE_loc.deg_lat and float(self.longitude) >= SW_loc.deg_lon and float(self.longitude) <= NE_loc.deg_lon:
			# Now do the real maths...
			if math.acos(math.sin(location_I.rad_lat) * math.sin(math.radians(float(self.latitude))) + math.cos(location_I.rad_lat) * math.cos(math.radians(float(self.latitude))) * math.cos(math.radians(float(self.longitude)) - (location_I.rad_lon))) <= rat:
				itsIN = True
			else:
				itsIN = False
		else:
			itsIN = False

		return itsIN
