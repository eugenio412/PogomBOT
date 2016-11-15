import sys
import logging
import os
import json

if len(sys.argv) < 2:
    print ("Usage: \n\tpython3 %s <FullPathToPogom>" % (sys.argv[0]))
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

        print ("Accs: %d, Locs: %d" % (accs, locs))

        print ('--- for pokemongo-map config.ini:')
        str = ""
        for w in acc_type:
            str = "%s, %s" % (str, w)
        str = str[2:]
        print ("auth-service: [%s]" % (str))
        str = ""
        for w in acc_user:
            str = "%s, %s" % (str, w)
        str = str[2:]
        print ("username: [%s]" % (str))
        str = ""
        for w in acc_pass:
            str = "%s, %s" % (str, w)
        str = str[2:]
        print ("password: [%s]" % (str))

        print ('--- only for your information:')
        str = ""
        for w in loc_loc:
            str = "%s / %s" % (str, w)
        str = str[2:]
        print ("locations: [%s]" % (str))
        str = ""
        for w in loc_rad:
            str = "%s / %s" % (str, w)
        str = str[2:]
        print ("radius: [%s]" % (str))
except Exception as e:
    logger.error('%s' % (repr(e)))