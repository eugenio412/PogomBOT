from .DSPokemon import DSPokemon

import os
from datetime import datetime
import logging

import json
import threading
import itertools
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

def startServer(port):
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    server.serve_forever()

#WebHook CallBack
#Request body contains:
# - type: String ("pokemon")
# - message: Object
#   - disappear_time: Long
#   - encounter_id: String (B64?, e.g. MTA0NTI4NzU4MzE0ODQzMDIwNjE=)
#   - pokemon_id: Integer (e.g. 11)
#   - spawnpoint_id: String (e.g. 47c3c2a0e33)
#   - longitude: 40.442506
#   - latitude: -79.957962
class WebhookHandler(BaseHTTPRequestHandler):
    instance = None
    def do_POST(self):
        data_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(data_length)
        payload = post_data.decode('utf-8')
        js = json.loads(payload)
        if js["type"] == "pokemon":
            data = js["message"]
            disappear_time = datetime.utcfromtimestamp(data['disappear_time'])
            encounter_id = str(data["encounter_id"])
            pok_id = str(data["pokemon_id"])
            spaw_point = str(data["spawnpoint_id"])
            longitude = str(data["longitude"])
            latitude = str(data["latitude"])

            # already done in pogobot.py
            #print(dissapear_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M:%S"))
            poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, None, None, None)
            self.instance.addPoke(poke)
        elif js["type"] == "pokestop":
            data = js["message"]
            pass
        elif js["type"] == "gym":
            data = js["message"]
            pass
        elif js["type"] == "gym-details":
            data = js["message"]
            pass
        else:
            pass
        self.send_response(200)
    # disable webserver logging
    def log_message(self, format, *args):
        return

class DSPokemonGoMapWebhook():
    method = None
    def __init__(self, connectString, method):
        port = int(connectString)
        logger.info('Starting webhook on port %s.' % (port))
        self.pokeDict = dict()
        self.lock = threading.Lock()
        WebhookHandler.instance = self
        th = threading.Thread(target=startServer, args=[int(port)])
        th.start()
        self.method = method

    def addPoke(self, poke):
        pok_id = poke.getPokemonID()
        self.method(poke)
        pass

    def getPokemonByIds(self, ids):
        return []
        