import sys
import os
import json
import logging
import fnmatch

logger = logging.getLogger(__name__)


class Locales:
    def __init__(self):
        self.__pokemon_name = dict()
        self.__move_name = dict()
        self.__locale = dict()
        self.default_lang = 'en'
        self.__default_avail = False

        # Read lang files
        path_to_local = "Locales/"
        for file in os.listdir(path_to_local):
            if fnmatch.fnmatch(file, 'pokemon.*.json'):
                self.__read_pokemon_names(file.split('.')[1])
            if fnmatch.fnmatch(file, 'moves.*.json'):
                self.__read_move_names(file.split('.')[1])
            if fnmatch.fnmatch(file,'lang.*.json'):
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

    def __read_pokemon_names(self, loc):
        logger.info('Reading pokemon names. <%s>' % loc)
        config_path = "Locales/pokemon." + loc + ".json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.__pokemon_name[loc] = json.loads(f.read())
        except Exception as e:
            logger.error('%s' % (repr(e)))
            # Pass to ignore if some files missing.
            pass

    def __read_move_names(self, loc):
        logger.info('Reading move names. <%s>' % loc)
        config_path = "Locales/moves." + loc + ".json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.__move_name[loc] = json.loads(f.read())
        except Exception as e:
            logger.error('%s' % (repr(e)))
            # Pass to ignore if some files missing.
            pass

    def __read_locale(self,loc):
        logger.info('Reading locale. <%s>' % loc)
        config_path = "Locales/lang." + loc + ".json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.__locale[loc] = json.loads(f.read())
        except Exception as e:
            logger.error('%s' % (repr(e)))
            # Pass to ignore if some files missing.
            pass

    def __getLan(self,loc,id):
        lan = list(self.__locale.keys())
        if not loc in lan:
            loc = self.default_lang
        if id == 0:
            return  self.__locale[loc]
        elif id == 1:
            return self.__pokemon_name[loc]
        elif id == 2:
            return self.__move_name[loc]

    def get_move(self,loc,id):
        lang = self.__getLan(loc,2)
        return lang[str(id)]

    def get_pokemon_name(self,loc,id):
        lang = self.__getLan(loc,1)
        return lang[str(id)]

    def get_string(self,loc,id):
        lang = self.__getLan(loc,0)
        return lang[str(id)]