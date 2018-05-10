#-*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler as CMD
from telegram.ext import MessageHandler as MSG
from telegram.ext import Filters

import json
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

#Bot token key pickup
TOKEN = ""
with open("bot.key", "r") as tokenFile:
    TOKEN = tokenFile.read()


UPD = Updater(token=TOKEN)
DIS = UPD.dispatcher


#Allowed chars set
allowed_chars = set("0123456789,.*+-/")

#Dumped dictionary. Has another dict for each chat ID + a generic fallback one.
chatData = {
    "generic": {
        "admins": "RREDesigns, ",
        "saludo": "Hola ",
        "bienvenida": "Bienvenido/a al grupo!"
        }
        }


def inicio(bot, update):
    try:
        with open("DB.json", "r") as db:
            chatData = json.load(db)
            bot.send_message(chat_id=update.message.chat_id, text="Encontrada base de datos. Cargando.    ")
    except:
        print("El archivo DB no existe.")


def setup(bot, update):

    chat_id = update.message.chat_id
    admin = update.message.from_user.username

    #Filling in the data to be dumped
    chatData[str(chat_id)] = {
        "admins": "RREDesigns, " + str(admin) + ", ",
        "saludo": "Hola ",
        "bienvenida": "Bienvenido/a al grupo!"
        }

    with open("DB.json", "w") as db:
        json.dump(chatData, db)

    bot.send_message(chat_id=update.message.chat_id, text="Se ha guardado la configuración básica.")



def parsing(bot, update):
    msgEnts = update.message.parse_entities()
    chat_id = update.message.chat_id

#Hashtag parsing
    for key in msgEnts:
        if key.type == "hashtag":
            print(msgEnts[key])
            print(chatData[str(chat_id)])
            if msgEnts[key] in chatData[str(chat_id)].keys():
                print("Perfil encontrado")
                bot.send_message(chat_id=update.message.chat_id, text="Recuperando perfil de " + msgEnts[key])
                name = "#" + msgEnts[key][1:]
                bot.send_message(chat_id=update.message.chat_id, text=chatData[str(chat_id)][name])
            else:
                print("Hubo un error al recuperar el perfil desde la DB.")
                print(chatData)


def perfil(bot, update):

    ents = update.message.parse_entities()
    chat_id = update.message.chat_id

    if update.message.from_user.username in chatData[str(chat_id)]["admins"]:
        for key in ents:
            if key.type == "hashtag":

                try:
                    chatData[str(chat_id)]["#" + ents[key][1:]] = update.message.text[(key.length + 9):]
                    bot.send_message(chat_id=update.message.chat_id, text="El perfil de " + ents[key][1:] + " se ha guardado con éxito.")
                except:
                    bot.send_message(chat_id=update.message.chat_id, text="Hubo un error al guardar el perfil de " + ents[key][1:] + ".")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Sólo los usuarios habilitados pueden agregar perfiles.")

    with open("DB.json", "w") as db:
        json.dump(chatData, db)


def bienvenida(bot, update):
    name = update.message.new_chat_members[0].first_name
    chat_id = update.messsage.chat_id

    saludo = chatData[str(chat_id)]["saludo"] + name + ". " + chatData[str(chat_id)]["bienvenida"]

    bot.send_message(chat_id=update.message.chat_id, text=saludo)


def bienvenidaTest(bot, update):
    chat_id = update.messsage.chat_id
    saludo = chatData[str(chat_id)]["saludo"] + "@user. " + chatData[str(chat_id)]["bienvenida"]

    bot.send_message(chat_id=update.message.chat_id, text=saludo)


def cambiarTextoDeBienvenida(bot, update, args):
    chat_id = update.messsage.chat_id

    if update.message.user.username in chatData[chat_id]["admins"]:
        chatData[str(chat_id)]["bienvenida"] = " ".join(args)
        bot.send_message(chat_id=update.message.chat_id, text="Mensaje de bienvenida cambiado.")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Solo los usuarios habilitados pueden cambiar el mensaje de bienvenida.")


def calc(bot, update):
    if not set('[abcdefghijklmnopzABCDEFGHIJKLMNOZ~!@#$%^&()_{}":;\']$').intersection(update.message.text[5:]):
        result = eval(update.message.text[5:])
        bot.send_message(chat_id=update.message.chat_id, text=result)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Hay caracteres no válidos en la operación solicitada.")
        print(set('[abcdefghijklmnopzABCDEFGHIJKLMNOZ~!@#$%^&()_{}":;\']$').intersection(update.message.text[4:]))


#Passing handlers to the dispatcher

DIS.add_handler(CMD("perfil", perfil))
DIS.add_handler(CMD("bienvenida", cambiarTextoDeBienvenida, pass_args=True))
DIS.add_handler(CMD("bienvenidaTest", bienvenidaTest))
DIS.add_handler(CMD("calc", calc))
DIS.add_handler(CMD("inicio", inicio))
DIS.add_handler(CMD("setup", setup))

DIS.add_handler(MSG(Filters.status_update.new_chat_members, bienvenida))
DIS.add_handler(MSG(Filters.all, parsing))


UPD.start_polling()