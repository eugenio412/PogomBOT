#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot thah look inside the database and see if the pokemon requested is appeared during the last scan
# This program is dedicated to the public domain under the CC0 license.
# First iteration made by eugenio412
# based on timerbot made inside python-telegram-bot example folder

# better on python3.4

'''please READ FIRST the README.md'''

import sqlite3 as lite
from telegram.ext import Updater, CommandHandler, Job , dispatcher
from telegram import Bot
import logging

from datetime import datetime
import os
import sys
import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

jobs = dict()
search_ids = dict()
sent = dict()
language = dict()

#read the database
con = lite.connect('pogom.db', check_same_thread=False)
cur = con.cursor()

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
@dispatcher.run_async
def help(bot, update):
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
    "\lang en"
    bot.sendMessage(chat_id, text)
    tmp = ''
    for key in pokemon_name:
        tmp += "%s, " % (key)
    tmp = tmp[:-2]
    bot.sendMessage(chat_id, text= '/lang [%s]' % (tmp))

@dispatcher.run_async
def start(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] Starting.' % (chat_id))
    bot.sendMessage(chat_id, text='Hello!')
    help(bot, update)

@dispatcher.run_async
def add(bot, update, args, job_queue):
    addJob(bot, update, job_queue)
    chat_id = update.message.chat_id
    logger.info('[%s] Add pokemon.' % (chat_id))

    try:
        search = search_ids[chat_id]
        for x in args:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        list(bot, update)
    except (IndexError, ValueError):
        bot.sendMessage(chat_id, text='usage: "/add <#pokemon>"" or "/add <#pokemon1> <#pokemon2>"')

@dispatcher.run_async
def addByRarity(bot, update, args, job_queue):
    addJob(bot, update, job_queue)
    chat_id = update.message.chat_id
    logger.info('[%s] Add pokemon by rarity.' % (chat_id))

    try:
        rarity = int(args[0])

        search = search_ids[chat_id]
        for x in pokemon_rarity[rarity]:
            if int(x) not in search:
                search.append(int(x))
        search.sort()
        list(bot, update)
    except (IndexError, ValueError):
        bot.sendMessage(chat_id, text='usage: "/addbyrarity <#rarity>" with 1 uncommon to 5 ultrarare')

@dispatcher.run_async
def clear(bot, update):
    """Removes the job if the user changed their mind"""
    chat_id = update.message.chat_id
    logger.info('[%s] Clear list.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    # Remove from jobs
    job = jobs[chat_id]
    job.schedule_removal()
    del jobs[chat_id]
    # Remove from search_ids
    del search_ids[chat_id]

    bot.sendMessage(chat_id, text='Notifications successfully removed!')

@dispatcher.run_async
def remove(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    logger.info('[%s] Remove pokemon.' % (chat_id))

    try:
        search = search_ids[chat_id]
        for x in args:
            if int(x) in search:
                search.remove(int(x))
        list(bot, update)
    except (IndexError, ValueError):
        bot.sendMessage(chat_id, text='usage: /rem <#pokemon>')

@dispatcher.run_async
def list(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] List.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    lan = language[chat_id]
    tmp = 'List of notifications:\n'
    for x in search_ids[chat_id]:
        tmp += "%i %s\n" % (x, pokemon_name[lan][str(x)])
    bot.sendMessage(chat_id, text = tmp)

def save(bot, update):
    chat_id = update.message.chat_id
    logger.info('[%s] Save.' % (chat_id))

    if chat_id not in jobs:
        bot.sendMessage(chat_id, text='You have no active scanner.')
        return

    tmp = '/add '
    for x in search_ids[chat_id]:
        tmp += "%i " % (x)
    bot.sendMessage(chat_id, text = tmp)

@dispatcher.run_async
def lang(bot, update, args):
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
    except (IndexError, ValueError):
            bot.sendMessage(chat_id, text='usage: /lang <#language>')

@dispatcher.run_async
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

@dispatcher.run_async
def alarm(bot, job):
    chat_id = job.context[0]
    logger.info('[%s] Checking alarm.' % (chat_id))
    checkAndSend(bot, chat_id, search_ids[chat_id])

@dispatcher.run_async
def addJob(bot, update, job_queue):
    chat_id = update.message.chat_id
    logger.info('[%s] Adding job.' % (chat_id))

    if chat_id not in jobs:
        job = Job(alarm, 30, repeat=True, context=(chat_id, "Other"))
        # Add to jobs
        jobs[chat_id] = job
        job_queue.put(job)
        # Add to search_ids
        search_ids[chat_id] = []
        # Set default language
        language[chat_id] = config.get('DEFAULT_LANG', None)

        text = "Scanner started."
        bot.sendMessage(chat_id, text)

@dispatcher.run_async
def checkAndSend(bot, chat_id, pokemons):
    logger.info('[%s] Checking pokemon and sending notifications.' % (chat_id))
    sqlquery = "SELECT * FROM pokemon WHERE pokemon_id in ("
    for pokemon in pokemons:
        sqlquery += str(pokemon) + ','
    sqlquery = sqlquery[:-1]
    sqlquery += ')'
    sqlquery += ' AND disappear_time > "' + str(datetime.utcnow()) + '"'
    sqlquery += ' ORDER BY pokemon_id ASC'

    lan = language[chat_id]
    with con:
        cur = con.cursor()

        # logger.info('%s' % (sqlquery))
        cur.execute(sqlquery)
        rows = cur.fetchall()
        # logger.info('%i' % (len(rows)))
        for row in rows:
            encounter_id = str(row[0])
            spaw_point = str(row[1])
            pok_id = str(row[2])
            latitude = str(row[3])
            longitude = str(row[4])
            disappear = str(row[5])
            title =  pokemon_name[lan][pok_id]
            address = "Disappear at min %s" % (disappear[14:16])

            if encounter_id not in sent:
                sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
                """Function to send the alarm message"""
                #pokemon name for those who want it
                bot.SendMessage(chat_id,text = title)
                bot.sendVenue(chat_id, latitude, longitude, title, address)

def read_config():
    logger.info('Reading config.')
    config_path = os.path.join(
        os.path.dirname(sys.argv[0]), "config-bot.json")
    global config

    try:
        with open(config_path, "r") as f:
            config = json.loads(f.read())
    except:
        config = {}

def read_pokemon_names(loc):
    logger.info('Reading pokemon names.')
    config_path = os.path.join(
        os.path.dirname(sys.argv[0]), "static/locales/pokemon." + loc + ".json")

    try:
        with open(config_path, "r") as f:
            pokemon_name[loc] = json.loads(f.read())
    except:
        pass

    
def main():
    logger.info('Starting...')
    read_config()
    read_pokemon_names("de")
    read_pokemon_names("en")
    read_pokemon_names("fr")
    read_pokemon_names("zh_cn")

    #ask it to the bot father in telegram
    token = config.get('TELEGRAM_TOKEN', None)
    logger.info("Token: %s" % (token))
    updater = Updater(token)
    b = Bot(token)
    logger.info("BotName: %s" % (b.name))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("addbyrarity", addByRarity, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("clear", clear))
    dp.add_handler(CommandHandler("rem", remove, pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("save", save))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CommandHandler("lang", lang, pass_args = True))


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
