
# PoGoBot

FINALLY a telegram bot, so you don't miss out rare pokemon anymore.

Made using [pogom](https://github.com/favll/pogom)

![image](https://raw.githubusercontent.com/eugenio412/PogomBOT/master/images/pogobot.png)

## Installation:
1. Clone the repository `https://github.com/eugenio412/PogomBOT.git`
2. Install the dependencies `sudo pip3 install -r requirements.txt -U`
3. Move the bot file (pogobot.py and config-bot.py) to your pogom folder (MUST BE IN THE SAME FOLDER AS pogom.db)
4. Go to telegram and talk to the @BotFather
5. Create a new bot and COPY THE TOKEN INSIDE the file config-bot.json in the place of TOKEN
6. run `python3.4 pogobot.py`
7. Go to telegram and write /start to !!YOUR!! bot (not the same of the picture please)
8. to be notified of a certain pokemon write to it `/add 1` changing the pokemon number as you want
9. to be notified by pokemon RARITY write `/addbyrarity 5` changing the number from 5 (ultrarare) to 1 common

If you want to dig deeper in the script go and first check the [telegram bot api](https://core.telegram.org/bots/api)
or check the examples made in the [python-telegram-bot repository](https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples) and their [wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki)

NOTE: if you stop the bot it will foget all the pokemon to scan, you should set it again


## Full List of Commands:

| Command                                               | Description                                                                  |
|:----------------------------------------------------- |:---------------------------------------------------------------------------- |
| /help /start                                          | Show help text.                                                              |
| /add <#pokedexID>                                     | Add pokemon with pokedexID.                                                  |
| /add <#pokedexID1> <#pokedexID2> ...                  | Add multiple pokemon with pokedexID.                                         |
| /addbyrarity <#rarity> with 1 uncommon to 5 ultrarare | Add pokemon with rarity.                                                     |
| /clear                                                | Clear all pokemon.                                                           |
| /rem <#pokedexID>                                     | Remove pokemon with pokedexID.                                               |
| /rem <#pokedexID1> <#pokedexID2> ...                  | Remove multiple pokemon with pokedexID.                                      |
| /list                                                 | List all currently observed pokemon.                                         |
| /save                                                 | Prints /add with IDs to be able to set last state at restart. (only pokemon) |
| /lang <#language>                                     | Sets pokemon names language.                                                 |