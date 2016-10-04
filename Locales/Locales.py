import fnmatch
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)


class Locales:

    @staticmethod
    def __customisation_dict():
        # The default dictionary
        d = dict(
            move="$MOVE_NAME",
            pok_name="$POKE_NAME",
        )
        return d

    def __init__(self):
        self.__pokemon_name = dict()
        self.__move_name = dict()
        self.__locale = dict()
        self.default_lang = 'en'
        self.__default_avail = False
        self.__customisation_file = 'messages.json'

        # Read lang files
        path_to_local = self.__get_default_dir()

        for file in os.listdir(path_to_local):
            if fnmatch.fnmatch(file, 'pokemon.*.json'):
                self.__read_pokemon_names(file.split('.')[1])
            if fnmatch.fnmatch(file, 'moves.*.json'):
                self.__read_move_names(file.split('.')[1])
            if fnmatch.fnmatch(file, 'lang.*.json'):
                self.__read_locale(file.split('.')[1])
                if file.split('.')[1] == self.default_lang:
                    self.__default_avail = True

        if not self.__default_avail:
            lan = list(self.__locale.keys())
            if len(lan) == 1:
                self.default_lang = lan[0]
                self.__default_avail = True
            else:
                lan = lan.sort()
                self.default_lang = lan[0]
                self.__default_avail = True

        self.__load_customisation()

    def __read_pokemon_names(self, loc):
        logger.info('Reading pokemon names. <%s>' % loc)
        config_path = os.path.join(self.__get_default_dir(), "pokemon." + loc + ".json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.__pokemon_name[loc] = json.loads(f.read())
        except Exception as e:
            logger.error('%s' % (repr(e)))
            # Pass to ignore if some files missing.
            pass

    def __read_move_names(self, loc):
        logger.info('Reading move names. <%s>' % loc)
        config_path = os.path.join(self.__get_default_dir(), "moves." + loc + ".json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.__move_name[loc] = json.loads(f.read())
        except Exception as e:
            logger.error('%s' % (repr(e)))
            # Pass to ignore if some files missing.
            pass

    def __read_locale(self, loc):
        logger.info('Reading locale. <%s>' % loc)
        config_path = os.path.join(self.__get_default_dir(), "lang." + loc + ".json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.__locale[loc] = json.loads(f.read())
        except Exception as e:
            logger.error('%s' % (repr(e)))
            # Pass to ignore if some files missing.
            pass

    def __get_lan(self, loc, id_in):
        lan = list(self.__locale.keys())
        if loc not in lan:
            loc = self.default_lang
        if id_in == 0:
            return self.__locale[loc]
        elif id_in == 1:
            return self.__pokemon_name[loc]
        elif id_in == 2:
            return self.__move_name[loc]

    def get_move(self, loc, id_in):
        lang = self.__get_lan(loc, 2)
        return self.__appy_move_customisation(lang, id_in)

    def get_pokemon_name(self, loc, id_in):
        lang = self.__get_lan(loc, 1)
        return self.__appy_name_customisation(lang, id_in)

    def get_string(self, loc, id_in):
        lang = self.__get_lan(loc, 0)
        try:
            r = lang[str(id_in)]
        except:
            lang = self.__get_lan(self.default_lang, 0)
            r = lang[str(id_in)]
        return r

    @property
    def locales(self):
        # return list(self.__locale.keys()) # THIS IS TO BE USED WHEN TRANSLATION IS COMPLETE
        return list(self.__pokemon_name.keys())

    def __get_default_dir(self):
        directory = os.path.join(
            os.path.dirname(sys.argv[0]), "Locales")
        return directory

    def __load_customisation(self):
        fullpath = os.path.join(self.__get_default_dir(), self.__customisation_file)

        logger.info('Customisation loading.')
        self.customisation = []
        if os.path.isfile(fullpath):
            try:
                with open(fullpath, 'r', encoding='utf-8') as f:
                    self.customisation = json.load(f)
                logger.info('Customisation loaded successful.')
            except Exception as e:
                logger.error(e)
        else:
            logger.warn('No Customisation file present.')
            self.customisation = self.__customisation_dict()

    def __save_customisation(self):
        fullpath = os.path.join(self.__get_default_dir(), self.__customisation_file)

        logger.info('Customisation saving.')
        try:
            with open(fullpath, 'w', encoding='utf-8') as file:
                json.dump(self.customisation, file, indent=4, sort_keys=True, separators=(',', ':'))
            logger.info('Customisation saved  successful.')
        except Exception as e:
            logger.warn('Error while saving customisation. (%s)' % e)

    def __appy_name_customisation(self, read_in, id_in):
        try:
            r = read_in[str(id_in)]
        except:
            read_in = self.__get_lan(self.default_lang, 1)
            r = read_in[str(id_in)]

        base_string = self.customisation['pok_name']
        base_string = base_string.replace('$POKE_NAME', r)
        base_string = base_string.replace('$POKE_NUMBER', str(id_in))

        return base_string

    def __appy_move_customisation(self, read_in, id_in):
        try:
            r = read_in[str(id_in)]
        except:
            read_in = self.__get_lan(self.default_lang, 1)
            r = read_in[str(id_in)]

        base_string = self.customisation['move']
        base_string = base_string.replace('$MOVE_NAME', r)
        base_string = base_string.replace('$MOVE_NUMBER', str(id_in))

        return base_string
