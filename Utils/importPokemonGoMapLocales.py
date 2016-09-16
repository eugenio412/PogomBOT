import sys
import logging
import os
import json
import fnmatch

if len(sys.argv) < 3:
    print ("Usage: \n\tpython3 %s <FULL_PATH_TO_PGO-MAP> <FULL_PATH_LOCALES_OUTPUT>" % (sys.argv[0]))
    sys.exit()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def convertTo(pokemon_en, lang):
	newlang_poke = dict()
	fileName = os.path.join(path_input, "static/locales/", lang + ".json")
	with open(fileName, 'r', encoding='utf-8') as poke_lang_file:
		poke_lang = json.loads(poke_lang_file.read())

	for poke_id in pokemon_en:
		try:
			en_name = pokemon_en[poke_id]['name']
			lang_name = poke_lang[en_name]
			newlang_poke[poke_id] = lang_name
		except Exception as e:
			logger.error("[%s] Missing: %s - %s" % (lang, poke_id, en_name))
			logger.error("[%s] %s" % (lang, repr(e)))

	fileName = os.path.join(path_output, "pokemon." + lang + ".json")
	with open(fileName, 'w', encoding='utf-8') as f:
		json.dump(newlang_poke, f, indent=4, sort_keys=True, separators=(',',':'))


def main():
	# Read lang files
	global path_input
	path_input = sys.argv[1]
	global path_output
	path_output = sys.argv[2]
	path_to_pokemon_en = os.path.join(path_input, "static/data/pokemon.json")
	path_to_locales = os.path.join(path_input, "static/locales/")

	pokemon_en = None
	with open(path_to_pokemon_en, 'r', encoding='utf-8') as f:
		pokemon_en = json.loads(f.read())

	for file in os.listdir(path_to_locales):
		if fnmatch.fnmatch(file, '*.json'):
			convertTo(pokemon_en, file.split('.')[0])

if __name__ == '__main__':
    main()