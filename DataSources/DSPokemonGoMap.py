from .DSPokemon import DSPokemon

import os
from datetime import datetime
import logging

import sqlite3 as lite

logger = logging.getLogger(__name__)


class DSPokemonGoMap:
    def __init__(self, connect_string):
        # open the database
        db_path = os.path.join(connect_string, 'pogom.db')
        logger.info('Connecting to local database')
        self.con = lite.connect(db_path, check_same_thread=False)

    def get_pokemon_by_ids(self, ids):
        pokelist = []

        sqlquery = ("SELECT encounter_id, spawnpoint_id, pokemon_id, latitude, longitude, disappear_time "
                    "FROM pokemon WHERE")
        sqlquery += ' disappear_time > "' + str(datetime.utcnow()) + '"'
        sqlquery += ' AND pokemon_id in ('
        for pokemon in ids:
            sqlquery += str(pokemon) + ','
        sqlquery = sqlquery[:-1]
        sqlquery += ')'
        sqlquery += ' ORDER BY pokemon_id ASC'

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

                poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, None, None,
                                 None)
                pokelist.append(poke)

        return pokelist
