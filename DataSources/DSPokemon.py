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