import itertools
import json
import logging
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

from .DSPokemon import DSPokemon

logger = logging.getLogger(__name__)


def start_server(port):
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    server.serve_forever()


# WebHook CallBack
# Request body contains:
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
            encounter_id = data["encounter_id"]
            pok_id = data["pokemon_id"]
            spaw_point = data["spawnpoint_id"]
            longitude = data["longitude"]
            latitude = data["latitude"]

            # already done in pogobot.py
            # print(dissapear_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M:%S"))
            poke = DSPokemon(encounter_id, spaw_point, pok_id, latitude, longitude, disappear_time, None, None, None)
            self.instance.add_poke(poke)
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


def remove_old_pokemon(item):
    delta = item.get_disappear_time() - datetime.utcnow()
    return delta.seconds > 0


class DSPokemonGoMapWebhook:
    def __init__(self, connect_string):
        port = int(connect_string)
        logger.info('Starting webhook on port %s.' % port)
        self.pokeDict = dict()
        self.lock = threading.Lock()
        WebhookHandler.instance = self
        th = threading.Thread(target=start_server, args=[int(port)])
        th.start()

    def add_poke(self, poke):
        pok_id = poke.get_pokemon_id()
        curr_time = datetime.utcnow()

        self.lock.acquire()
        if pok_id not in self.pokeDict:
            self.pokeDict[pok_id] = []
        else:
            self.pokeDict[pok_id][:] = itertools.filterfalse(remove_old_pokemon, self.pokeDict[pok_id])
        self.pokeDict[pok_id].append(poke)
        self.lock.release()
        pass

    def get_pokemon_by_ids(self, ids):
        poke_list = []
        self.lock.acquire()
        curr_time = datetime.utcnow()
        for pid in ids:
            if pid in self.pokeDict:
                for poke in self.pokeDict[pid]:
                    delta = poke.get_disappear_time() - curr_time
                    if delta.seconds > 0:
                        poke_list.append(poke)
        self.lock.release()
        return poke_list
