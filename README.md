
# PoGoBot

FINALLY a telegram bot, so you don't miss out rare pokemon anymore.

Made using [pogom][https://github.com/favll/pogom]

![image](https://raw.githubusercontent.com/eugenio412/PogomBOT/master/images/pogobot.jpg)

This is intended to work after you have a working installation of pogom

##Installation:
1. Clone the repository `https://github.com/eugenio412/PogomBOT.git`
2. Install the dependencies `sudo pip3 install -r requirements.txt -U`
3. Move the bot file (pogobot) to your pogom folder (MUST BE IN THE SAME FOLDER AS pogom.db) 
4. Go to telegram and talk to the @BotFather
5. Create a new bot and COPY THE TOKEN INSIDE the file pogobot.py in the place of TOKEN
6. run `python3.4 pogobot.py`
7. Go to telegram and write /start to your bot, it should reply
8. to be notified of a certain pokemon write to it `/set 1` changing the pokemon number as you want

NOTE: if you stop the bot it will foget all the pokemon to scan, you should set it again
