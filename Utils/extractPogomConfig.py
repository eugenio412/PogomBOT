import sys
import logging
import os
import json

if len(sys.argv) < 2:
    print("Usage: \n\tpython3 %s <FullPathToPogom>" % (sys.argv[0]))
    sys.exit()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

accs = 0
acc_type = []
acc_user = []
acc_pass = []

locs = 0
loc_loc = []
loc_rad = []

gmaps = None

jsonPath = os.path.join(sys.argv[1], "config.json")
try:
    with open(jsonPath, "r", encoding='utf-8') as f:
        config = json.loads(f.read())
        for w in config["ACCOUNTS"]:
            acc_type.append("ptc")
            acc_user.append(w["username"])
            acc_pass.append(w["password"])
            accs += 1
        for w in config["SCAN_LOCATIONS"]:
            loc_loc.append(w["location"])
            loc_rad.append(w["radius"])
            locs += 1
        gmaps = config["GOOGLEMAPS_KEY"]

        print("Accs: %d, Locs: %d" % (accs, locs))

        print('--- for pokemongo-map config.ini:')
        pogom_str = ""
        for w in acc_type:
            pogom_str = "%s, %s" % (pogom_str, w)
        pogom_str = pogom_str[2:]
        print("auth-service: [%s]" % pogom_str)
        pogom_str = ""
        for w in acc_user:
            pogom_str = "%s, %s" % (pogom_str, w)
        pogom_str = pogom_str[2:]
        print("username: [%s]" % pogom_str)
        pogom_str = ""
        for w in acc_pass:
            pogom_str = "%s, %s" % (pogom_str, w)
        pogom_str = pogom_str[2:]
        print("password: [%s]" % pogom_str)

        print('--- only for your information:')
        pogom_str = ""
        for w in loc_loc:
            pogom_str = "%s / %s" % (pogom_str, w)
        pogom_str = pogom_str[2:]
        print("locations: [%s]" % pogom_str)
        pogom_str = ""
        for w in loc_rad:
            pogom_str = "%s / %s" % (pogom_str, w)
        pogom_str = pogom_str[2:]
        print("radius: [%s]" % pogom_str)
except Exception as e:
    logger.error('%s' % (repr(e)))
