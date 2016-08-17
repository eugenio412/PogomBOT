#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot thah look inside the database and see if the pokemon requested is appeared during the last scan
# This program is dedicated to the public domain under the CC0 license.
# First iteration made by eugenio412
# based on timerbot made inside python-telegram-bot example folder

# better on python3.4

'''please READ FIRST the README.md'''

import datetime
import sqlite3 as lite
from telegram.ext import Updater, CommandHandler, Job
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
timers = dict()
sent = dict()
#read the database
con = lite.connect('pogom.db',check_same_thread=False)
cur = con.cursor()

#pokemon:
pokemon_name = {"1":"Bulbasaur","2":"Ivysaur","3":"Venusaur","4":"Charmander","5":"Charmeleon","6":"Charizard","7":"Squirtle","8":"Wartortle","9":"Blastoise","10":"Caterpie",\
"11":"Metapod","12":"Butterfree","13":"Weedle","14":"Kakuna","15":"Beedrill","16":"Pidgey","17":"Pidgeotto","18":"Pidgeot","19":"Rattata","20":"Raticate",\
"21":"Spearow","22":"Fearow","23":"Ekans","24":"Arbok","25":"Pikachu","26":"Raichu","27":"Sandshrew","28":"Sandslash","29":"Nidoran♀","30":"Nidorina",\
"31":"Nidoqueen","32":"Nidoran♂","33":"Nidorino","34":"Nidoking","35":"Clefairy","36":"Clefable","37":"Vulpix","38":"Ninetales","39":"Jigglypuff","40":"Wigglytuff",\
"41":"Zubat","42":"Golbat","43":"Oddish","44":"Gloom","45":"Vileplume","46":"Paras","47":"Parasect","48":"Venonat","49":"Venomoth","50":"Diglett",\
"51":"Dugtrio","52":"Meowth","53":"Persian","54":"Psyduck","55":"Golduck","56":"Mankey","57":"Primeape","58":"Growlithe","59":"Arcanine","60":"Poliwag",\
"61":"Poliwhirl","62":"Poliwrath","63":"Abra","64":"Kadabra","65":"Alakazam","66":"Machop","67":"Machoke","68":"Machamp","69":"Bellsprout","70":"Weepinbell",\
"71":"Victreebel","72":"Tentacool","73":"Tentacruel","74":"Geodude","75":"Graveler","76":"Golem","77":"Ponyta","78":"Rapidash","79":"Slowpoke","80":"Slowbro",\
"81":"Magnemite","82":"Magneton","83":"Farfetch'd","84":"Doduo","85":"Dodrio","86":"Seel","87":"Dewgong","88":"Grimer","89":"Muk","90":"Shellder",\
"91":"Cloyster","92":"Gastly","93":"Haunter","94":"Gengar","95":"Onix","96":"Drowzee","97":"Hypno","98":"Krabby","99":"Kingler","100":"Voltorb",\
"101":"Electrode","102":"Exeggcute","103":"Exeggutor","104":"Cubone","105":"Marowak","106":"Hitmonlee","107":"Hitmonchan","108":"Lickitung","109":"Koffing","110":"Weezing",\
"111":"Rhyhorn","112":"Rhydon","113":"Chansey","114":"Tangela","115":"Kangaskhan","116":"Horsea","117":"Seadra","118":"Goldeen","119":"Seaking","120":"Staryu",\
"121":"Starmie","122":"Mr. Mime","123":"Scyther","124":"Jynx","125":"Electabuzz","126":"Magmar","127":"Pinsir","128":"Tauros","129":"Magikarp","130":"Gyarados",\
"131":"Lapras","132":"Ditto","133":"Eevee","134":"Vaporeon","135":"Jolteon","136":"Flareon","137":"Porygon","138":"Omanyte","139":"Omastar","140":"Kabuto",\
"141":"Kabutops","142":"Aerodactyl","143":"Snorlax","144":"Articuno","145":"Zapdos","146":"Moltres","147":"Dratini","148":"Dragonair","149":"Dragonite","150":"Mewtwo"}
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
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello! write /set and the number of the pokemon to scan.\nexample for bulbasaur:\n/set 1\n Or /setbyrarity and the rarity number from 1 to 5')


def alarm(bot, job):
    with con:
        cur = con.cursor()
        pokemon = int(job.context[1])
        cur.execute("SELECT * FROM pokemon WHERE pokemon_id = ?",(pokemon,))
        rows = cur.fetchall()
        for row in rows:
            encounter_id = str(row[0])
            spaw_point = str(row[1])
            pok_id = str(row[2])
            latitude = str(row[3])
            longitude = str(row[4])
            disappear = str(row[5])
            title =  pokemon_name[pok_id]
            address = "Disappear at  " + disappear
            if encounter_id not in sent:
                sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
                """Function to send the alarm message"""
                bot.sendVenue(job.context[0], latitude, longitude, title, address)

def rarityalarm(bot, job):
    with con:
        cur = con.cursor()
        rarity = int(job.context[1])
        for pokemon in pokemon_rarity[rarity]:
            cur.execute("SELECT * FROM pokemon WHERE pokemon_id = ?",(pokemon,))
            rows = cur.fetchall()
            for row in rows:
                encounter_id = str(row[0])
                spaw_point = str(row[1])
                pok_id = str(row[2])
                latitude = str(row[3])
                longitude = str(row[4])
                disappear = str(row[5])
                title =  pokemon_name[pok_id]
                address = "Disappear at min " + disappear
                if encounter_id not in sent:
                    sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
                    """Function to send the alarm message"""
                    bot.sendVenue(job.context[0], latitude, longitude, title, address)

def set(bot, update, args, job_queue):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        pokemon = args[0]
        # Add job to queue
        job = Job(alarm, 30, repeat=True, context=(chat_id,pokemon))
        timers[chat_id] = job
        job_queue.put(job)
        #but first, save the pokemon already appeared
        with con:
            cur = con.cursor()
            pokemon = int(job.context[1])
            cur.execute("SELECT * FROM pokemon WHERE pokemon_id = ?",(pokemon,))
            rows = cur.fetchall()
            for row in rows:
                encounter_id = str(row[0])
                spaw_point = str(row[1])
                pok_id = str(row[2])
                latitude = str(row[3])
                longitude = str(row[4])
                disappear = str(row[5])
                sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
        text = "Scanner on for " + pokemon_name[str(pokemon)]
        bot.sendMessage(chat_id, text)
    except (IndexError, ValueError):
        bot.sendMessage(chat_id, text='usage: /set <#pokemon>')

def setbyrarity(bot, update,args, job_queue):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        rarity = int(args[0])
        # Add job to queue
        job = Job(rarityalarm, 30, repeat=True, context=(chat_id,rarity))
        timers[chat_id] = job
        job_queue.put(job)
        #but first, save the pokemon already appeared
        for pokemon in pokemon_rarity[rarity]:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM pokemon WHERE pokemon_id = ?",(pokemon,))
                rows = cur.fetchall()
                for row in rows:
                    encounter_id = str(row[0])
                    spaw_point = str(row[1])
                    pok_id = str(row[2])
                    latitude = str(row[3])
                    longitude = str(row[4])
                    disappear = str(row[5])
                    sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
        text = "Scanner on for " + rarity_value[rarity]
        bot.sendMessage(chat_id, text)
    except (IndexError, ValueError):
        bot.sendMessage(chat_id, text='usage: /setbyrarity <#rarity> with 1 uncommon to 5 ultrarare')



def unset(bot, update):
    """Removes the job if the user changed their mind"""
    chat_id = update.message.chat_id

    if chat_id not in timers:
        bot.sendMessage(chat_id, text='You have no active scanner')
        return

    job = timers[chat_id]
    job.schedule_removal()
    del timers[chat_id]

    bot.sendMessage(chat_id, text='scanner successfully unset!')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    #ask it to the bot father in telegram
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("setbyrarity", setbyrarity,pass_args = True, pass_job_queue=True))
    dp.add_handler(CommandHandler("unset", unset))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    logger.info('pogomBOT-Telegram started!')
    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
