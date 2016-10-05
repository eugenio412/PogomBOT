import json
import urllib.request

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
#
#   - individual_attack: None
#   - individual_defense: None
#   - individual_stamina: None
#   - move_1: None
#   - move_2: None

try:
    conditionsSetURL = 'http://127.0.0.1:2100/'

    poke_iv_disabled = {"type": "pokemon",
                        "message": {"disappear_time": 1474660231, "encounter_id": "MTA0NTI4NzU4MzE0ODQzMDIwNjE",
                                    "pokemon_id": 11, "spawnpoint_id": "47c3c2a0e33", "longitude": 50.1,
                                    "latitude": 52.1}}
    poke_iv_not_available = {"type": "pokemon",
                             "message": {"disappear_time": 1474660231, "encounter_id": "MTA0NTI4NzU4MzE0ODQzMDIwNjE",
                                         "pokemon_id": 11, "spawnpoint_id": "47c3c2a0e33", "longitude": 50.1,
                                         "latitude": 52.1, "individual_attack": 3, "individual_defense": 9,
                                         "individual_stamina": 12, "move_1": 237, "move_2": 105}}
    poke_iv_available = {"type": "pokemon",
                         "message": {"disappear_time": 1474660231, "encounter_id": "MTA0NTI4NzU4MzE0ODQzMDIwNjE",
                                     "pokemon_id": 11, "spawnpoint_id": "47c3c2a0e33", "longitude": 50.1,
                                     "latitude": 52.1, "individual_attack": None, "individual_defense": None,
                                     "individual_stamina": None, "move_1": None, "move_2": None}}

    newConditions = poke_iv_disabled
    params = json.dumps(newConditions).encode('utf8')
    req = urllib.request.Request(conditionsSetURL, data=params, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf8'))
except Exception as e:
    print(e)
