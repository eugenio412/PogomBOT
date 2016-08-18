
# PoGoBot

FINALLY a telegram bot, so you don't miss out rare pokemon anymore.

Made using [pogom](https://github.com/favll/pogom)

![image](https://raw.githubusercontent.com/eugenio412/PogomBOT/master/images/pogobot.jpg)

##Installation:
1. Clone the repository `https://github.com/eugenio412/PogomBOT.git`
2. Install the dependencies `sudo pip3 install -r requirements.txt -U`
3. Move the bot file (pogobot) to your pogom folder (MUST BE IN THE SAME FOLDER AS pogom.db)
4. Go to telegram and talk to the @BotFather
5. Create a new bot and COPY THE TOKEN INSIDE the file pogobot.py in the place of TOKEN
6. run `python3.4 pogobot.py`
7. Go to telegram and write /start to !!YOUR!! bot (not the same of the picture please)
8. to be notified of a certain pokemon write to it `/set 1` changing the pokemon number as you want
9. to be notified by pokemon RARITY write `/setbyrarity 5` changing the number from 5 (ultrarare) to 1 common

If you want to dig deeper in the script go and first check the [telegram bot api](https://core.telegram.org/bots/api)
or check the examples made in the [python-telegram-bot repository](https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples) and their [wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki)

NOTE: if you stop the bot it will foget all the pokemon to scan, you should set it again
