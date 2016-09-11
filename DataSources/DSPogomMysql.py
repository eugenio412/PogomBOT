from .DSPokemon import DSPokemon

import os
from datetime import datetime
import logging

import pymysql

logger = logging.getLogger(__name__)

class DSPogomMysql():
	def __init__(self, connectString):
		# open the database
		sql_pattern = 'mysql://(.*?):(.*?)@(.*?):(\d*)/(\S+)'
		(user, passw, host, port, db) = re.compile(sql_pattern).findall(connectString)[0]
		logger.info('Connecting to remote database')
		self.con = pymysql.connect(user=user,password=passw,host=host,port=int(port),database=db)

	def getPokemonByIds(self, ids):
		pokelist = []

		sqlquery = "SELECT encounter_id, spawnpoint_id, pokemon_id, latitude, longitude, disappear_time FROM pokemon WHERE pokemon_id in ("
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

					poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, None)
					pokelist.append(poke)
		except Exception as e:
			logger.error('[%s] %s' % (chat_id, repr(e)))
			pass
		return pokelist