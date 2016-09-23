
# PoGoBot

FINALLY a telegram bot, so you don't miss out rare pokemon anymore.

Made using [pogom](https://github.com/favll/pogom) and [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

BUT NOW (drumroll) SUPPORT [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map)

## Branches

0. Clone repository with `git clone git@github.com:eugenio412/PogomBOT.git`
0. this will clone master branch
0. **master** branch
  - Stable branch
  - Tested features
0. **develop** branch
  - Could be instable sometimes.
  - Newest features
0. Switching branches
  - Never used develop before: `git checkout -b develop origin/develop`
  - switch to master: `git checkout master`
  - switch to develop: `git checkout develop`
  - update current branch: `git pull`

## Installation Instructions

See it at our [wiki](https://github.com/eugenio412/PogomBOT/wiki).

## New IV feature

Now our bot can send you the notification with the IV number, but only with PokemonGO-Map using the develop [branch](https://github.com/PokemonGoMap/PokemonGo-Map).

## Full List of Commands

See them at our [commands page](https://github.com/eugenio412/PogomBOT/wiki/commands).


## Troubleshooting Guide

See it at our [troubleshooting page](https://github.com/eugenio412/PogomBOT/wiki/troubleshooting).

## Join out telegram group

IF YOU ARE REPORTING A BUG OPEN A ISSUE, but if you want to contact the creators write to our telegram group: http://telegram.me/pogomBOTgroup

![image](https://raw.githubusercontent.com/eugenio412/PogomBOT/master/images/pogobot.jpg)

## Changelog

23 sept 2016: added webhooks for pokemongo-map and pokemongo-map-iv.

23 sept 2016: added user selected language for move names if available. Otherwise using english.

23 sept 2016: added individual iv filter for pokemons.

21 sept 2016: added /location to set locationbased filtering with text. Sending your location works too.

16 sept 2016: added imported locales from pokemongo-map

16 sept 2016: added script to convert pokemongo-map locales

14 sept 2016: added POKEMON_MINIMUM_IV feature
