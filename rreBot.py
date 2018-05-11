#-*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler as CMD
from telegram.ext import MessageHandler as MSG
from telegram.ext import Filters

from time import gmtime, strftime

#Own module
from RateUpdater import *

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

#DB overwrite switch
overwriteDB = False

#Rates dictionaries
FECHA = ""
FECHABTC = ""
BTC = {}
USD = {}
EUR = {}


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
            if msgEnts[key] in chatData[str(chat_id)].keys():
                bot.send_message(chat_id=update.message.chat_id, text="Recuperando perfil de " + msgEnts[key], disable_notification=True)
                name = "#" + msgEnts[key][1:]
                bot.send_message(chat_id=update.message.chat_id, text=chatData[str(chat_id)][name], disable_notification=True)
            else:
                print("No existe un perfil para este usuario en la base de datos de este chat, o hubo un error recuperando el perfil.")


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

def actualizarTasas(bot, update, args):
    global FECHA
    global FECHABTC
    chat_id = update.message.chat_id

    #Updater instance
    U = RateUpdater()

    bot.send_message(chat_id=chat_id, text="Consultando fuentes online. Por favor espere.")

    if "btc" in args or "bitcoin" in args or "usd" in args or "dolar" in args or "euro" in args or "tasas" in args or "eur" in args:
        try:
            btc = U.actualizarBTC()
            #Returns a list with dicts in it, in this order: 0-VEF, 1-USD, 2-EUR
            BTC["VEF"] = btc[0]
            BTC["USD"] = btc[1]
            BTC["EUR"] = btc[2]

            bot.send_message(chat_id=chat_id, text="Las cotizaciones de BTC se han actualizado.")

            FECHABTC = strftime("%d de %b de %Y.  %I:%M %p", gmtime())

            #Update of other rates
            div = U.actualizarDivisas()
            #Returns a bidimensional dict.
            #Equivalences are: transferencias = transferencia, efectivo = efectivo_real
            # implícito = efectivo, DICOM = sicad2

            FECHA = div["FECHA"]

            #Storing the local data for USD
            USD["transferencia"] = "Bs. " + str(div["USD"]["transferencia"])
            USD["efectivo"] = "Bs. " + str(div["USD"]["efectivo_real"])
            USD["implícito"] = "Bs. " + str(div["USD"]["efectivo"])
            USD["dicom"] = "Bs. " + str(div["USD"]["sicad2"])

            #Storing the local data for EUR
            EUR["transferencia"] = "Bs. " + str(div["EUR"]["transferencia"])
            EUR["efectivo"] = "Bs. " + str(div["EUR"]["efectivo_real"])
            EUR["implícito"] = "Bs. " + str(div["EUR"]["efectivo"])
            EUR["dicom"] = "Bs. " + str(div["EUR"]["sicad2"])

            bot.send_message(chat_id=chat_id, text="Las cotizaciones de divisas internacionales se han actualizado.")

        except:
            bot.send_message(chat_id=chat_id, text="Hubo un error en la actualización.")

def cotizacion(bot, update, args):
    chat_id = update.message.chat_id
    divisa = args

    #Header of the rates msg
    header = ".\n" + "            " + "*DOLAR TODAY*" + "        \n" + "    " + str(FECHA) + "\n\n\n"

    #Titles for money kind
    titleUSD = "                    " + "*DOLAR:*" + "\n\n"
    titleEUR = "                    " + "*EURO:*" + "\n\n"

    #Full msg build
    mensajeUSD = header + titleUSD + "Transferencia:    " + "`" + str(USD["transferencia"]) + "`" + "\n\nEfectivo:                " + "`" + str(USD["efectivo"]) + "`" + "\n\nImplícito:               " + "`" + str(USD["implícito"]) + "`" + "\n\nDICOM:                  " + "`" + str(USD["dicom"]) + "`"

    mensajeEUR = header + titleEUR + "Transferencia:    " + "`" + str(EUR["transferencia"]) + "`" + "\n\nEfectivo:                " + "`" + str(EUR["efectivo"]) + "`" + "\n\nImplícito:               " + "`" + str(EUR["implícito"]) + "`" + "\n\nDICOM:                  " + "`" + str(EUR["dicom"]) + "`"

    mensajeFULL = mensajeUSD + "\n\n\n\n" + titleEUR + "Transferencia:    " + "`" + str(EUR["transferencia"]) + "`" + "\n\nEfectivo:                " + "`" + str(EUR["efectivo"]) + "`" + "\n\nImplícito:               " + "`" + str(EUR["implícito"]) + "`" + "\n\nDICOM:                  " + "`" + str(EUR["dicom"]) + "`"

    #BTC message
    headerBTC = ".\n" + "                        " + "*LOCAL BITCOINS*" + "        \n" + "            " + str(FECHABTC) + "\n\n\n"
    bodyBTC = "*Promedio última hora: Bs.* " + "`" +str(BTC["VEF"]["avg_1h"]) + "`" + "\n\n" + "*$1 = Btc. *" + "`" + str(BTC["USD"]["avg_1h"]) + "`" + "\n\n" + "*€1 = Btc. *" + "`" + str(BTC["EUR"]["avg_1h"]) + "`"

    #BTC message build
    mensajeFULLBTC = headerBTC + bodyBTC

    if "USD" in divisa or "usd" in divisa or "dolar" in divisa:
        bot.send_message(chat_id=chat_id, text=mensajeUSD, parse_mode="Markdown")

    elif "EUR" in divisa or "eur" in divisa or "euro" in divisa:
        bot.send_message(chat_id=chat_id, text=mensajeEUR, parse_mode="Markdown")
    elif "BTC" in divisa or "btc" in divisa or "bitcoin" in divisa:
        bot.send_message(chat_id=chat_id, text=mensajeFULLBTC, parse_mode="Markdown")
    elif not args:
        bot.send_message(chat_id=chat_id, text=mensajeFULL, parse_mode="Markdown")


#Passing handlers to the dispatcher
DIS.add_handler(CMD("perfil", perfil))
DIS.add_handler(CMD("bienvenida", cambiarTextoDeBienvenida, pass_args=True))
DIS.add_handler(CMD("bienvenidaTest", bienvenidaTest))
DIS.add_handler(CMD("calc", calc))
#DIS.add_handler(CMD("inicio", inicio))
DIS.add_handler(CMD("setup", setup))
DIS.add_handler(CMD("reset", reset))
DIS.add_handler(CMD("actualizar", actualizarTasas, pass_args=True))
DIS.add_handler(CMD("cotizacion", cotizacion, pass_args=True))

DIS.add_handler(MSG(Filters.status_update.new_chat_members, bienvenida))
DIS.add_handler(MSG(Filters.all, parsing))

inicio()
UPD.start_polling()