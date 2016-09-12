from .DSPokemon import DSPokemon

import os
from datetime import datetime
import logging

import sqlite3 as lite

logger = logging.getLogger(__name__)

class DSPokemonGoMapIV():
	def __init__(self, connectString):
		# open the database
		db_path = os.path.join(connectString, 'pogom.db')
		logger.info('Connecting to local database')
		self.con = lite.connect(db_path, check_same_thread=False)

	def getPokemonByIds(self, ids):
		pokelist = []

		sqlquery = ("SELECT encounter_id, spawnpoint_id, pokemon_id, latitude, longitude, disappear_time, "
			"individual_attack, individual_defense, individual_stamina, move_1, move_2 "
			"FROM pokemon WHERE pokemon_id in (")
		for pokemon in ids:
			sqlquery += str(pokemon) + ','
		sqlquery = sqlquery[:-1]
		sqlquery += ')'
		sqlquery += ' AND disappear_time > "' + str(datetime.utcnow()) + '"'
		sqlquery += ' ORDER BY pokemon_id ASC'

		try:
			with self.con:
				cur = self.con.cursor()

				cur.execute(sqlquery)
				rows = cur.fetchall()
				for row in rows:
					encounter_id = str(row[0])
					spaw_point = str(row[1])
					pok_id = str(row[2])
					latitude = str(row[3])
					longitude = str(row[4])

					disappear = str(row[5])
					disappear_time = datetime.strptime(disappear[0:19], "%Y-%m-%d %H:%M:%S")

					individual_attack = row[6]
					individual_defense = row[7]
					individual_stamina = row[8]
					
					if row[9] is not None:
						move1 = str(row[9])
						move2 = str(row[10])
					else:
						move1 = None
						move2 = None

					iv = None
					if individual_attack is not None:
						iv = str((int(individual_attack) +  int(individual_defense) + int(individual_stamina)) / 45 * 100)
						iv = iv[0:4]

					poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, iv, move1, move2)
					pokelist.append(poke)
		except Exception as e:
			logger.error('[%s] %s' % (chat_id, repr(e)))
			pass
		return pokelist
