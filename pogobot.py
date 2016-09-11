#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot thah look inside the database and see if the pokemon requested is appeared during the last scan
# This program is dedicated to the public domain under the CC0 license.
# First iteration made by eugenio412
# based on timerbot made inside python-telegram-bot example folder

# better on python3.4

'''please READ FIRST the README.md'''


import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3.")

import sqlite3 as lite
from telegram.ext import Updater, CommandHandler, Job
from telegram import Bot
import logging
from datetime import datetime, timezone
import os
import io
import errno
import json
import threading
import fnmatch

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

jobs = dict()

# User dependant - dont add
sent = dict()
locks = dict()

# User dependant - Add to clear, addJob, loadUserConfig, saveUserConfig
search_ids = dict()
language = dict()

#pokemon:
pokemon_name = dict()

#pokemon rarity
pokemon_rarity = [[],
	["13","16","19","41","133"],
	["1","7","10","17","21","23","25","29","32","35","43","46","48","58","60","69","84","92","96","98","120","127","129","147"],
	["2","4","8","11","14","15","18","20","22","27","37","39","42","47","49","50","52","54","56","61","63","66","70","72","74",\
    "77","79","81","86","90","93","95","97","100","102","104","107","108","109","111","114","116","118","123","124","125","126","128","138","140","143"],
	["3","5","6","9","12","24","30","31","33","34","36","44","53","55","57","59","64","67","73","75","78","80","85","88","99",\
    "103","105","106","110","112","113","117","119","121","122","131","134","135","137","142","148","149"],
	["26","28","38","40","45","51","62","65","68","71","76","82","83","87","89","91","94","101","115","130","132","136","139","141","144","145","146","150","151"],
];

rarity_value = ["very common","common","uncommon","rare","very rare","ultrarare"]

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def cmd_help(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] Sending help text.' % (chat_id))
    text = "/help /start \n" + \
    "/add <#pokedexID> \n" + \
    "/add <#pokedexID1> <#pokedexID2> ... \n" + \
    "/addbyrarity <#rarity> with 1 uncommon to 5 ultrarare \n" + \
    "/clear \n" + \
    "/rem <#pokedexID> \n" + \
    "/rem <#pokedexID1> <#pokedexID2> ... \n" + \
    "/list \n" + \
    "/save \n" + \
    "/load \n" + \
    "/lang en"
    bot.sendMessage(chat_id, text)
    tmp = ''
    for key in pokemon_name:
        tmp += "%s, " % (key)
    tmp = tmp[:-2]
    bot.sendMessage(chat_id, text= '/lang [%s]' % (tmp))

def cmd_start(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] Starting.' % (chat_id))
    bot.sendMessage(chat_id, text='Hello!')
    cmd_help(bot, update)

def cmd_add(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    if len(args) <= 0:
        bot.sendMessage(chat_id, text='usage: "/add <#pokemon>"" or "/add <#pokemon1> <#pokemon2>"')
        return

    addJob(bot, update, job_queue)
    logger.info('[%s] Add pokemon.' % (chat_id))

    try:
        search = search_ids[chat_id]
        for x in args:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        cmd_list(bot, update)
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
        bot.sendMessage(chat_id, text='usage: "/add <#pokemon>"" or "/add <#pokemon1> <#pokemon2>"')

def cmd_addByRarity(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    if len(args) <= 0:
        bot.sendMessage(chat_id, text='usage: "/addbyrarity <#rarity>" with 1 uncommon to 5 ultrarare')
        return

    addJob(bot, update, job_queue)
    logger.info('[%s] Add pokemon by rarity.' % (chat_id))

    try:
        rarity = int(args[0])

        search = search_ids[chat_id]
        for x in pokemon_rarity[rarity]:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        cmd_list(bot, update)
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
        bot.sendMessage(chat_id, text='usage: "/addbyrarity <#rarity>" with 1 uncommon to 5 ultrarare')

def cmd_clear(bot, update):
    chat_id = update.message.chat_id
    """Removes the job if the user changed their mind"""
    logger.info('[%s] Clear list.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    # Remove from jobs
    job = jobs[chat_id]
    job.schedule_removal()
    del jobs[chat_id]

    # Remove from sent
    del sent[chat_id]
    # Remove from locks
    del locks[chat_id]

    # Remove from language
    del language[chat_id]
    # Remove from search_ids
    del search_ids[chat_id]

    bot.sendMessage(chat_id, text='Notifications successfully removed!')

def cmd_remove(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    logger.info('[%s] Remove pokemon.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    try:
        search = search_ids[chat_id]
        for x in args:
            if int(x) in search:
                search.remove(int(x))
        cmd_list(bot, update)
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
        bot.sendMessage(chat_id, text='usage: /rem <#pokemon>')

def cmd_list(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] List.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    try:
        lan = language[chat_id]
        tmp = 'List of notifications:\n'
        for x in search_ids[chat_id]:
            tmp += "%i %s\n" % (x, pokemon_name[lan][str(x)])
        bot.sendMessage(chat_id, text = tmp)
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))

def cmd_save(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] Save.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    try:
        if saveUserConfig(chat_id):
            bot.sendMessage(chat_id, text='Save successful.')
        else:
            bot.sendMessage(chat_id, text='Save failed.')
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))

def cmd_load(bot, update, job_queue):
    chat_id = update.message.chat_id
    logger.info('[%s] Load.' % (chat_id))

    if loadUserConfig(chat_id):
        bot.sendMessage(chat_id, text='Load successful.')
    else:
        bot.sendMessage(chat_id, text='Load failed.')
    if len(search_ids[chat_id]) > 0:
        addJob(bot, update, job_queue)
        cmd_list(bot, update)
    else:
        if chat_id in jobs:
            job = jobs[chat_id]
            job.schedule_removal()
            del jobs[chat_id]

def cmd_lang(bot, update, args):
    chat_id = update.message.chat_id

    try:
        lan = args[0]
        logger.info('[%s] Setting lang.' % (chat_id))

        if lan in pokemon_name:
            language[chat_id] = args[0]
            bot.sendMessage(chat_id, text='Language set to [%s].' % (lan))
        else:
            tmp = ''
            for key in pokemon_name:
                tmp += "%s, " % (key)
            tmp = tmp[:-2]
            bot.sendMessage(chat_id, text='This language isn\'t available. [%s]' % (tmp))
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))
        bot.sendMessage(chat_id, text='usage: /lang <#language>')

## Functions
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def alarm(bot, job):
    chat_id = job.context[0]
    logger.info('[%s] Checking alarm.' % (chat_id))
    checkAndSend(bot, chat_id, search_ids[chat_id])

def addJob(bot, update, job_queue):
    chat_id = update.message.chat_id
    logger.info('[%s] Adding job.' % (chat_id))

    try:
        if chat_id not in jobs:
            job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
            # Add to jobs
            jobs[chat_id] = job
            job_queue.put(job)
            # User dependant - Save/Load
            if chat_id not in search_ids:
                search_ids[chat_id] = []
            if chat_id not in language:
                language[chat_id] = config.get('DEFAULT_LANG', None)

            # User dependant
            if chat_id not in sent:
                sent[chat_id] = dict()
            if chat_id not in locks:
                locks[chat_id] = threading.Lock()

            text = "Scanner started."
            bot.sendMessage(chat_id, text)
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, repr(e)))

def checkAndSend(bot, chat_id, pokemons):
    lock = locks[chat_id]
    logger.info('[%s] Checking pokemon and sending notifications.' % (chat_id))
    if len(pokemons) == 0:
        return

    sqlquery = "SELECT * FROM pokemon WHERE pokemon_id in ("
    for pokemon in pokemons:
        sqlquery += str(pokemon) + ','
    sqlquery = sqlquery[:-1]
    sqlquery += ')'
    sqlquery += ' AND disappear_time > "' + str(datetime.utcnow()) + '"'
    sqlquery += ' ORDER BY pokemon_id ASC'

    try:
        lan = language[chat_id]
        mySent = sent[chat_id]
        with con:
            cur = con.cursor()

            cur.execute(sqlquery)
            rows = cur.fetchall()
            lock.acquire()
            for row in rows:
                encounter_id = str(row[0])
                spaw_point = str(row[1])
                pok_id = str(row[2])
                latitude = str(row[3])
                longitude = str(row[4])

                disappear = str(row[5])
                disappear_time = datetime.strptime(disappear[0:19], "%Y-%m-%d %H:%M:%S")
                delta = disappear_time - datetime.utcnow()
                delta = '%02d:%02d' % (int(delta.seconds / 60), int(delta.seconds % 60))
                disappear_time = disappear_time.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M:%S")

                title =  pokemon_name[lan][pok_id]
                address = "Disappear at %s (%s)." % (disappear_time, delta)

                if encounter_id not in mySent:
                    mySent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
                    """Function to send the alarm message"""
                    #pokemon name for those who want it
                    if not config.get('SEND_MAP_ONLY', True):
                        bot.sendMessage(chat_id, text = '%s - %s' % (title, address))
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
        for encounter_id in mySent:
            time = mySent[encounter_id][5]
            time = datetime.strptime(time[0:19], "%Y-%m-%d %H:%M:%S")
            if time < current_time:
                toDel.append(encounter_id)
        for encounter_id in toDel:
            del mySent[encounter_id]
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
    logger.info('TELEGRAM_TOKEN: <%s>' % (config.get('TELEGRAM_TOKEN', None)))
    logger.info('POGOM_PATH: <%s>' % (config.get('POGOM_PATH', None)))
    logger.info('DEFAULT_LANG: <%s>' % (config.get('DEFAULT_LANG', None)))
    logger.info('SEND_MAP_ONLY: <%s>' % (config.get('SEND_MAP_ONLY', None)))

def read_pokemon_names(loc):
    logger.info('Reading pokemon names. <%s>' % loc)
    config_path = "locales/pokemon." + loc + ".json"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            pokemon_name[loc] = json.loads(f.read())
    except Exception as e:
        logger.error('%s' % (repr(e)))
        # Pass to ignore if some files missing.
        pass

def loadUserConfig(chat_id):
    logger.info('[%s] loadUserConfig.' % (chat_id))
    fileName = getUserConfigPath(chat_id)
    try:
        if os.path.isfile(fileName):
            with open(fileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load search ids
                search = []
                search_ids[chat_id] = search
                for x in data['search_ids']:
                    if not int(x) in search:
                        search.append(int(x))
                # Load language
                language[chat_id] = data['language']
            return True
        else:
            logger.warn('[%s] loadUserConfig. File not found!' % (chat_id))
            pass
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, e))
    return False

def saveUserConfig(chat_id):
    logger.info('[%s] saveUserConfig.' % (chat_id))
    fileName = getUserConfigPath(chat_id)
    try:
        data = dict()
        # Save search ids
        data['search_ids'] = search_ids[chat_id]
        # Save language
        data['language'] = language[chat_id]
        with open(fileName, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, sort_keys=True, separators=(',',':'))
        return True
    except Exception as e:
        logger.error('[%s] %s' % (chat_id, e))
    return False

def getUserConfigPath(chat_id):
    logger.info('[%s] getUserConfigPath.' % (chat_id))
    user_path = os.path.join(
        os.path.dirname(sys.argv[0]), "userdata")
    try:
        os.makedirs(user_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error('[%s] %s' % (chat_id, e))
    return os.path.join(user_path, '%s.json' % chat_id)

def main():
    logger.info('Starting...')
    read_config()

    # Read lang files
    path_to_local = "locales/"
    for file in os.listdir(path_to_local):
        if fnmatch.fnmatch(file, 'pokemon.*.json'):
            read_pokemon_names(file.split('.')[1])

    #read the database
    global con
    db_path = os.path.join(config.get('POGOM_PATH', None), 'pogom.db')
    con = lite.connect(db_path, check_same_thread=False)
    cur = con.cursor()

    #ask it to the bot father in telegram
    token = config.get('TELEGRAM_TOKEN', None)
    updater = Updater(token)
    b = Bot(token)
    logger.info("BotName: <%s>" % (b.name))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("add", cmd_add, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("addbyrarity", cmd_addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("clear", cmd_clear))
    dp.add_handler(CommandHandler("rem", cmd_remove, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("save", cmd_save))
    dp.add_handler(CommandHandler("load", cmd_load, pass_job_queue=True))
    dp.add_handler(CommandHandler("list", cmd_list))
    dp.add_handler(CommandHandler("lang", cmd_lang, pass_args = True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    logger.info('Started!')
    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
