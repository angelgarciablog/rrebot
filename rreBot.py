#-*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler as CMD
from telegram.ext import MessageHandler as MSG
from telegram.ext import Filters

import json
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

#Bot token key pickup
TOKEN = ""
with open("bot.key", "r") as tokenFile:
    TOKEN = tokenFile.read()


UPD = Updater(token=TOKEN)
DIS = UPD.dispatcher


#Dumped dictionary. Has another dict for each chat ID + a generic fallback one.
chatData = {
    "generic": {
        "admins": "RREDesigns, ",
        "saludo": "Hola ",
        "bienvenida": "Bienvenido/a al grupo!"
        }
        }

overwriteDB = False


def inicio():
    global chatData

    try:
        with open("DB.json", "r") as db:
            chatData = json.load(db)
    except:
        print("El archivo DB no existe.")


def setup(bot, update):
    global overwriteDB
    global chatData
    chat_id = update.message.chat_id
    admin = update.message.from_user.username

    #Check wether the setup for this chat has been used already
    if str(chat_id) in chatData.keys() and not overwriteDB:
        bot.send_message(chat_id=chat_id, text="""Ya existen datos guardados para este chat.Si desea sobreescribir los datos, use el comando 'reset' y ejecute el setup nuevamente.""", disable_notification=True)

    elif str(chat_id) in chatData.keys() and overwriteDB and admin in chatData[str(chat_id)]["admins"]:
        #Filling in the data to be dumped
        chatData[str(chat_id)] = {
                                    "admins": "RREDesigns, " + str(admin) + ", ",
                                    "saludo": "Hola ",
                                    "bienvenida": "Bienvenido/a al grupo!"
                             }

        with open("DB.json", "w") as db:
            json.dump(chatData, db)

        bot.send_message(chat_id=update.message.chat_id, text="Se ha guardado la configuración básica.", disable_notification=True)
        overwriteDB = False

    elif str(chat_id) in chatData.keys() and overwriteDB and admin not in chatData[str(chat_id)]["admins"]:
        bot.send_message(chat_id=chat_id, text="Solo un usuario habilitado puede ejecutar esta acción", disable_notification=True)

    elif str(chat_id) not in chatData.keys():
        #Filling in the data to be dumped
        chatData[str(chat_id)] = {
                                    "admins": "RREDesigns, " + str(admin) + ", ",
                                    "saludo": "Hola ",
                                    "bienvenida": "Bienvenido/a al grupo!"
                                    }

        with open("DB.json", "w") as db:
            json.dump(chatData, db)

        bot.send_message(chat_id=update.message.chat_id, text="Se ha guardado la configuración básica.", disable_notification=True)
        overwriteDB = False

    else:
        bot.send_message(chat_id=chat_id, text="Hubo un error en el setup.", disable_notification=True)


def reset(bot, update):
    global overwriteDB
    chat_id = update.message.chat_id
    admin = update.message.from_user.username

    if admin in chatData[str(chat_id)]["admins"]:
        overwriteDB = True
        bot.send_message(chat_id=chat_id, text="Ahora puede usar el setup.", disable_notification=True)
    else:
        bot.send_message(chat_id=chat_id, text="Solo usuarios habilitados pueden resetear los datos.", disable_notification=True)


def parsing(bot, update):
    global chatData
    msgEnts = update.message.parse_entities()
    chat_id = update.message.chat_id

#Hashtag parsing
    for key in msgEnts:
        if key.type == "hashtag":
            print(msgEnts[key])
            print(chatData[str(chat_id)])
            if msgEnts[key] in chatData[str(chat_id)].keys():
                print("Perfil encontrado")
                bot.send_message(chat_id=update.message.chat_id, text="Recuperando perfil de " + msgEnts[key], disable_notification=True)
                name = "#" + msgEnts[key][1:]
                bot.send_message(chat_id=update.message.chat_id, text=chatData[str(chat_id)][name], disable_notification=True)
            else:
                print("Hubo un error al recuperar el perfil desde la DB.")


def perfil(bot, update):
    global chatData

    ents = update.message.parse_entities()
    chat_id = update.message.chat_id

    if update.message.from_user.username in chatData[str(chat_id)]["admins"]:
        for key in ents:
            if key.type == "hashtag":

                try:
                    chatData[str(chat_id)]["#" + ents[key][1:]] = update.message.text[(key.length + 9):]
                    bot.send_message(chat_id=update.message.chat_id, text="El perfil de " + ents[key][1:] + " se ha guardado con éxito.", disable_notification=True)
                except:
                    bot.send_message(chat_id=update.message.chat_id, text="Hubo un error al guardar el perfil de " + ents[key][1:] + ".", disable_notification=True)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Sólo los usuarios habilitados pueden agregar perfiles.", disable_notification=True)

    with open("DB.json", "w") as db:
        json.dump(chatData, db)


def bienvenida(bot, update):
    name = update.message.new_chat_members[0].first_name
    chat_id = update.message.chat_id

    saludo = chatData[str(chat_id)]["saludo"] + name + ". " + chatData[str(chat_id)]["bienvenida"]

    bot.send_message(chat_id=update.message.chat_id, text=saludo, disable_notification=True)


def bienvenidaTest(bot, update):
    chat_id = update.message.chat_id
    saludo = chatData[str(chat_id)]["saludo"] + "@user. " + chatData[str(chat_id)]["bienvenida"]

    bot.send_message(chat_id=update.message.chat_id, text=saludo, disable_notification=True)


def cambiarTextoDeBienvenida(bot, update, args):
    chat_id = update.message.chat_id

    if update.message.from_user.username in chatData[str(chat_id)]["admins"]:
        chatData[str(chat_id)]["bienvenida"] = " ".join(args)
        bot.send_message(chat_id=update.message.chat_id, text="Mensaje de bienvenida cambiado.", disable_notification=True)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Solo los usuarios habilitados pueden cambiar el mensaje de bienvenida.", disable_notification=True)


def calc(bot, update):
    if not set('[abcdefghijklmnopzABCDEFGHIJKLMNOZ~!@#$%^&()_{}":;\']$').intersection(update.message.text[5:]):
        result = eval(update.message.text[5:])
        bot.send_message(chat_id=update.message.chat_id, text=result, disable_notification=True)
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Hay caracteres no válidos en la operación solicitada.", disable_notification=True)
        print(set('[abcdefghijklmnopzABCDEFGHIJKLMNOZ~!@#$%^&()_{}":;\']$').intersection(update.message.text[4:]))


#Passing handlers to the dispatcher

DIS.add_handler(CMD("perfil", perfil))
DIS.add_handler(CMD("bienvenida", cambiarTextoDeBienvenida, pass_args=True))
DIS.add_handler(CMD("bienvenidaTest", bienvenidaTest))
DIS.add_handler(CMD("calc", calc))
DIS.add_handler(CMD("inicio", inicio))
DIS.add_handler(CMD("setup", setup))
DIS.add_handler(CMD("reset", reset))

DIS.add_handler(MSG(Filters.status_update.new_chat_members, bienvenida))
DIS.add_handler(MSG(Filters.all, parsing))

inicio()
UPD.start_polling()