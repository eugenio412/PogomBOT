#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot thah look inside the database and see if the pokemon requested is appeared during the last scan
# This program is dedicated to the public domain under the CC0 license.
# First iteration made by eugenio412
# based on timerbot made inside python-telegram-bot example folder

# better on python3.4

"""please READ FIRST the README.md"""

import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3.")

from telegram.ext import Updater, CommandHandler, Job, MessageHandler, Filters
from telegram import Bot
import logging
from datetime import datetime, timezone
import os
import json
import threading
import DataSources
import Preferences
from geopy.geocoders import Nominatim
import Whitelist
import Locales

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
prefs = Preferences.UserPreferences()
jobs = dict()
geolocator = Nominatim()
lang = Locales.Locales()

# User dependant - dont add
sent = dict()
locks = dict()

# User dependant - Add to clear, addJob, loadUserConfig, saveUserConfig
# search_ids = dict()
# language = dict()
# location_ids = dict()
location_radius = 0.6

# pokemon rarity
pokemon_rarity = [[],
                  ["13", "16", "19", "41", "133"],
                  ["1", "7", "10", "17", "21", "23", "25", "29", "32", "35", "43", "46", "48", "58", "60", "69", "84",
                   "92", "96", "98", "120", "127", "129", "147"],
                  ["2", "4", "8", "11", "14", "15", "18", "20", "22", "27", "37", "39", "42", "47", "49", "50", "52",
                   "54", "56", "61", "63", "66", "70", "72", "74",
                   "77", "79", "81", "86", "90", "93", "95", "97", "100", "102", "104", "107", "108", "109", "111",
                   "114", "116", "118", "123", "124", "125", "126", "128", "138", "140", "143"],
                  ["3", "5", "6", "9", "12", "24", "30", "31", "33", "34", "36", "44", "53", "55", "57", "59", "64",
                   "67", "73", "75", "78", "80", "85", "88", "99",
                   "103", "105", "106", "110", "112", "113", "117", "119", "121", "122", "131", "134", "135", "137",
                   "142", "148", "149"],
                  ["26", "28", "38", "40", "45", "51", "62", "65", "68", "71", "76", "82", "83", "87", "89", "91", "94",
                   "101", "115", "130", "132", "136", "139", "141", "144", "145", "146", "150", "151"],
                  ]

rarity_value = ["very common", "common", "uncommon", "rare", "very rare", "ultrarare"]


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def cmd_help(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (help).' % (user_name, chat_id))
        return

    logger.info('[%s@%s] Sending help text.' % (user_name, chat_id))

    text = lang.get_string(prefs.get(chat_id).get('language'), 0)
    bot.sendMessage(chat_id, text)
    bot.sendMessage(chat_id, text='/lang [%s]' % ', '.join(lang.locales))


def cmd_start(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (start).' % (user_name, chat_id))
        return

    logger.info('[%s@%s] Starting.' % (user_name, chat_id))
    bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 1))
    cmd_help(bot, update)


def cmd_add(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (add).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    if len(args) <= 0:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 2))
        return
    add_job(bot, update, job_queue)
    logger.info('[%s@%s] Add pokemon.' % (user_name, chat_id))

    try:
        search = pref.get('search_ids')
        for x in args:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        pref.set('search_ids', search)
        cmd_list(bot, update)
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 3))


def cmd_add_by_rarity(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (addByRarity).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    if len(args) <= 0:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 4))
        return

    add_job(bot, update, job_queue)
    logger.info('[%s@%s] Add pokemon by rarity.' % (user_name, chat_id))

    try:
        rarity = int(args[0])

        search = pref.get('search_ids')
        for x in pokemon_rarity[rarity]:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        pref.set('search_ids', search)
        cmd_list(bot, update)
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 4))


def cmd_clear(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (clear).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    """Removes the job if the user changed their mind"""
    logger.info('[%s@%s] Clear list.' % (user_name, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return

    # Remove from jobs
    job = jobs[chat_id]
    job.schedule_removal()
    del jobs[chat_id]

    # Remove from sent
    del sent[chat_id]
    # Remove from locks
    del locks[chat_id]

    pref.reset_user()
    bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 11))


def cmd_remove(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (remove).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    logger.info('[%s@%s] Remove pokemon.' % (user_name, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return

    try:
        search = pref.get('search_ids')
        for x in args:
            if int(x) in search:
                search.remove(int(x))
        pref.set('search_ids', search)
        cmd_list(bot, update)
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 6))


def cmd_list(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (list).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    logger.info('[%s@%s] List.' % (user_name, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return

    try:
        lan = pref.get('language')
        tmp = lang.get_string(pref.get('language'), 7) + "\n"
        for x in pref.get('search_ids'):
            tmp += "%i %s\n" % (x, lang.get_pokemon_name(lan, x))
        bot.sendMessage(chat_id, text=tmp)
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))


def cmd_save(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (save).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    logger.info('[%s@%s] Save.' % (user_name, chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return
    pref.set_preferences()
    bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 8))


def cmd_load(bot, update, job_queue):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (load).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    logger.info('[%s@%s] Attempting to load.' % (user_name, chat_id))
    r = pref.load()
    if r is None:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 9))
        return

    if not r:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 12))
        return
    else:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 13))

    # We might be the first user and above failed....
    if len(pref.get('search_ids')) > 0:
        add_job(bot, update, job_queue)
        cmd_list(bot, update)
    else:
        if chat_id not in jobs:
            job = jobs[chat_id]
            job.schedule_removal()
            del jobs[chat_id]


def cmd_lang(bot, update, args):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (lang).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    try:
        lan = args[0]
        logger.info('[%s@%s] Setting lang.' % (user_name, chat_id))

        if lan in lang.locales:
            pref.set('language', args[0])
            bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 14) % lan)
        else:
            bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 15) % ', '.join(lang.locales))
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 16))


def cmd_location(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (location).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return

    user_location = update.message.location

    # We set the location from the users sent location.
    pref.set('location', [user_location.latitude, user_location.longitude, location_radius])

    logger.info('[%s@%s] Setting scan location to Lat %s, Lon %s, R %s' % (user_name, chat_id,
                                                                           pref['location'][0], pref['location'][1],
                                                                           pref['location'][2]))

    # Send confirmation nessage
    bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 17) %
                                  (pref['location'][0], pref['location'][1], 1000 * pref['location'][2]))


def cmd_location_str(bot, update, args):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (location_str).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return

    if len(args) <= 0:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 10))
        return

    try:
        user_location = geolocator.geocode(' '.join(args))
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 18))
        return

    # We set the location from the users sent location.
    pref.set('location', [user_location.latitude, user_location.longitude, location_radius])

    logger.info('[%s@%s] Setting scan location to Lat %s, Lon %s, R %s' % (user_name, chat_id,
                                                                           pref['location'][0],
                                                                           pref.preferences['location'][1],
                                                                           pref.preferences['location'][2]))

    # Send confirmation nessage
    bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 17) %
                                  (pref['location'][0], pref['location'][1], 1000 * pref['location'][2]))


def cmd_radius(bot, update, args):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (radius).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 5))
        return

    # Check if user has set a location
    user_location = pref.get('location')

    if user_location[0] is None:
        bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 10))
        return

    # Get the users location
    logger.info('[%s@%s] Retrieved Location as Lat %s, Lon %s, R %s (Km)' % (
        user_name, chat_id, user_location[0], user_location[1], user_location[2]))

    if len(args) < 1:
        bot.sendMessage(chat_id, text="Current scan location is: %f / %f with radius %.2f m"
                                      % (user_location[0], user_location[1], user_location[2]))
        return

    # Change the radius
    pref.set('location', [user_location[0], user_location[1], float(args[0]) / 1000])

    logger.info('[%s@%s] Set Location as Lat %s, Lon %s, R %s (Km)' % (user_name, chat_id, pref['location'][0],
                                                                       pref['location'][1], pref['location'][2]))

    # Send confirmation
    bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 17) % (pref['location'][0],
                                                                               pref['location'][1],
                                                                               1000 * pref['location'][2]))


def cmd_clear_location(bot, update):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelisted(user_name):
        logger.info('[%s@%s] User blocked (clearlocation).' % (user_name, chat_id))
        return

    pref = prefs.get(chat_id)
    pref.set('location', [None, None, None])
    bot.sendMessage(chat_id, text=lang.get_string(pref.get('language'), 19))
    logger.info('[%s@%s] Location has been unset' % (user_name, chat_id))


def cmd_add_to_whitelist(bot, update, args):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelist_enabled():
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 20))
        return
    if not whitelist.is_admin(user_name):
        logger.info('[%s@%s] User blocked (addToWhitelist).' % (user_name, chat_id))
        return

    if len(args) <= 0:
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 21))
        return

    try:
        for x in args:
            whitelist.add_user(x)
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 22))
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 21))


def cmd_rem_from_whitelist(bot, update, args):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    if not whitelist.is_whitelist_enabled():
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 20))
        return
    if not whitelist.is_admin(user_name):
        logger.info('[%s@%s] User blocked (remFromWhitelist).' % (user_name, chat_id))
        return

    if len(args) <= 0:
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 21))
        return

    try:
        for x in args:
            whitelist.rem_user(x)
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 23))
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))
        bot.sendMessage(chat_id, text=lang.get_string(prefs.get(chat_id).get('language'), 21))


# Functions
def error(bot, update, errors):
    logger.warn('Update "%s" caused error "%s"' % (update, errors))


def alarm(bot, job):
    chat_id = job.context[0]
    logger.info('[%s] Checking alarm.' % chat_id)
    check_and_send(bot, chat_id, prefs.get(chat_id).get('search_ids'))


def add_job(bot, update, job_queue):
    chat_id = update.message.chat_id
    user_name = update.message.from_user.username
    logger.info('[%s@%s] Adding job.' % (user_name, chat_id))

    try:
        if chat_id not in jobs:
            job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            job_queue.put(job)

            # User dependant
            if chat_id not in sent:
                sent[chat_id] = dict()
            if chat_id not in locks:
                locks[chat_id] = threading.Lock()
            text = lang.get_string(prefs.get(chat_id).get('language'), 24)
            bot.sendMessage(chat_id, text)
    except Exception as e:
        logger.error('[%s@%s] %s' % (user_name, chat_id, repr(e)))


def check_and_send(bot, chat_id, pokemons):
    pref = prefs.get(chat_id)
    lock = locks[chat_id]
    logger.info('[%s] Checking pokemon and sending notifications.' % chat_id)
    my_sent = []
    if len(pokemons) == 0:
        return

    try:
        allpokes = dataSource.get_pokemon_by_ids(pokemons)
        lan = pref['language']
        my_sent = sent[chat_id]
        location_data = pref['location']

        send_poke_without_IV = config.get('SEND_POKEMON_WITHOUT_IV', True)
        poke_min_IV_filter_list = config.get('POKEMON_MIN_IV_FILTER_LIST', dict())

        lock.acquire()

        for pokemon in allpokes:
            if location_data[0] is not None:
                if not pokemon.filterbylocation(location_data):
                    continue

            encounter_id = pokemon.get_encounter_id()
            pok_id = pokemon.get_pokemon_id()
            latitude = pokemon.get_latitude()
            longitude = pokemon.get_longitude()
            disappear_time = pokemon.get_disappear_time()
            iv = pokemon.get_ivs()
            move1 = pokemon.get_move1()
            move2 = pokemon.get_move2()

            delta = disappear_time - datetime.utcnow()
            delta_str = '%02d:%02d' % (int(delta.seconds / 60), int(delta.seconds % 60))
            disappear_time_str = disappear_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M:%S")

            title = lang.get_pokemon_name(lan, pok_id)
            address = lang.get_string(lan, 25) % (disappear_time_str, delta_str)

            if iv is not None:
                title += " IV:%s" % iv

            if move1 is not None and move2 is not None:
                # Use language if other move languages are available.
                move1_name = lang.get_move(lan, move1)
                move2_name = lang.get_move(lan, move2)
                address += lang.get_string(lan, 26) % (move1_name, move2_name)

            poke_min_IV = None
            if pok_id in poke_min_IV_filter_list:
                poke_min_IV = poke_min_IV_filter_list[pok_id]

            if encounter_id not in my_sent:
                my_sent[encounter_id] = disappear_time

                not_disappeared = delta.seconds > 0
                iv_none_and_send_without = (iv is None) and send_poke_without_IV
                iv_not_none_and_poke_min_i_v_none = (iv is not None) and (poke_min_IV is None)
                iv_higher_equal_filter = (iv is not None) and (poke_min_IV is not None) and (
                    float(iv) >= float(poke_min_IV))
                if not_disappeared and (
                                    not ivAvailable or iv_none_and_send_without or iv_not_none_and_poke_min_i_v_none or iv_higher_equal_filter):
                    if not config.get('SEND_MAP_ONLY', True):
                        real_loc = geolocator.reverse(", ".join([pokemon.get_latitude(), pokemon.get_longitude()]))
                        bot.sendMessage(chat_id, text='%s - %s\n%s' % (title, address, real_loc.address))
                    bot.sendVenue(chat_id, latitude, longitude, title, address)

    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
    lock.release()

    # Clean already disappeared pokemon
    # 2016-08-19 20:10:10.000000
    # 2016-08-19 20:10:10
    try:
        current_time = datetime.utcnow()
        lock.acquire()
        toDel = []
        for encounter_id in my_sent:
            time = my_sent[encounter_id]
            if time < current_time:
                toDel.append(encounter_id)
        for encounter_id in toDel:
            del my_sent[encounter_id]
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
    lock.release()


def read_config():
    config_path = os.path.join(
        os.path.dirname(sys.argv[0]), "config-bot.json")
    logger.info('Reading config: <%s>' % config_path)
    global config

    try:
        with open(config_path, "r", encoding='utf-8') as f:
            config = json.loads(f.read())
    except Exception as e:
        logger.error('%s' % (repr(e)))
        config = {}
    report_config()


def report_config():
    admins_list = config.get('LIST_OF_ADMINS', [])
    tmp = ''
    for admin in admins_list:
        tmp = '%s, %s' % (tmp, admin)
    tmp = tmp[2:]
    logger.info('LIST_OF_ADMINS: <%s>' % tmp)

    logger.info('TELEGRAM_TOKEN: <%s>' % (config.get('TELEGRAM_TOKEN', None)))
    logger.info('SCANNER_NAME: <%s>' % (config.get('SCANNER_NAME', None)))
    logger.info('DB_TYPE: <%s>' % (config.get('DB_TYPE', None)))
    logger.info('DB_CONNECT: <%s>' % (config.get('DB_CONNECT', None)))
    logger.info('DEFAULT_LANG: <%s>' % (config.get('DEFAULT_LANG', None)))
    logger.info('SEND_MAP_ONLY: <%s>' % (config.get('SEND_MAP_ONLY', None)))
    logger.info('SEND_POKEMON_WITHOUT_IV: <%s>' % (config.get('SEND_POKEMON_WITHOUT_IV', None)))

    poke_ivfilter_list = config.get('POKEMON_MIN_IV_FILTER_LIST', dict())
    tmp = ''
    for poke_id in poke_ivfilter_list:
        tmp = '%s %s:%s' % (tmp, poke_id, poke_ivfilter_list[poke_id])
    tmp = tmp[1:]
    logger.info('POKEMON_MIN_IV_FILTER_LIST: <%s>' % tmp)


def main():
    logger.info('Starting...')
    read_config()

    db_type = config.get('DB_TYPE', None)
    scanner_name = config.get('SCANNER_NAME', None)

    global dataSource
    dataSource = None

    global ivAvailable
    ivAvailable = False
    if db_type == 'sqlite':
        if scanner_name == 'pogom':
            dataSource = DataSources.DSPogom(config.get('DB_CONNECT', None))
        elif scanner_name == 'pogom-iv':
            ivAvailable = True
            dataSource = DataSources.DSPogomIV(config.get('DB_CONNECT', None))
        elif scanner_name == 'pokemongo-map':
            dataSource = DataSources.DSPokemonGoMap(config.get('DB_CONNECT', None))
        elif scanner_name == 'pokemongo-map-iv':
            ivAvailable = True
            dataSource = DataSources.DSPokemonGoMapIV(config.get('DB_CONNECT', None))
    elif db_type == 'mysql':
        if scanner_name == 'pogom':
            dataSource = DataSources.DSPogomMysql(config.get('DB_CONNECT', None))
        elif scanner_name == 'pogom-iv':
            ivAvailable = True
            dataSource = DataSources.DSPogomIVMysql(config.get('DB_CONNECT', None))
        elif scanner_name == 'pokemongo-map':
            dataSource = DataSources.DSPokemonGoMapMysql(config.get('DB_CONNECT', None))
        elif scanner_name == 'pokemongo-map-iv':
            ivAvailable = True
            dataSource = DataSources.DSPokemonGoMapIVMysql(config.get('DB_CONNECT', None))
    elif db_type == 'webhook':
        if scanner_name == 'pogom':
            pass
        elif scanner_name == 'pokemongo-map':
            dataSource = DataSources.DSPokemonGoMapWebhook(config.get('DB_CONNECT', None))
        elif scanner_name == 'pokemongo-map-iv':
            ivAvailable = True
            dataSource = DataSources.DSPokemonGoMapIVWebhook(config.get('DB_CONNECT', None))
    if not dataSource:
        raise Exception("The combination SCANNER_NAME, DB_TYPE is not available: %s,%s" % (scanner_name, db_type))

    global whitelist
    whitelist = Whitelist.Whitelist(config)

    # ask it to the bot father in telegram
    token = config.get('TELEGRAM_TOKEN', '')
    updater = Updater(token)
    b = Bot(token)
    logger.info("BotName: <%s>" % b.name)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("add", cmd_add, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("addbyrarity", cmd_add_by_rarity, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("clear", cmd_clear))
    dp.add_handler(CommandHandler("rem", cmd_remove, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("save", cmd_save))
    dp.add_handler(CommandHandler("load", cmd_load, pass_job_queue=True))
    dp.add_handler(CommandHandler("list", cmd_list))
    dp.add_handler(CommandHandler("lang", cmd_lang, pass_args=True))
    dp.add_handler(CommandHandler("radius", cmd_radius, pass_args=True))
    dp.add_handler(CommandHandler("location", cmd_location_str, pass_args=True))
    dp.add_handler(CommandHandler("remloc", cmd_clear_location))
    dp.add_handler(MessageHandler([Filters.location], cmd_location))
    dp.add_handler(CommandHandler("wladd", cmd_add_to_whitelist, pass_args=True))
    dp.add_handler(CommandHandler("wlrem", cmd_rem_from_whitelist, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    # add the configuration to the preferences
    prefs.add_config(config)

    # Start the Bot
    updater.start_polling()

    logger.info('Started!')
    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
