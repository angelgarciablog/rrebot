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
JQ = UPD.job_queue
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

#Tasa
tasa = None
isPhoto = False


def inicio():
    global chatData

    try:
        with open("DB.json", "r") as db:
            chatData = json.load(db)
    except:
        pass


def setup(bot, update):
    global overwriteDB
    global chatData
    chat_id = str(update.message.chat_id)
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
    chat_id = str(update.message.chat_id)
    admin = update.message.from_user.username
    msgId = update.message.message_id

    if admin in chatData[str(chat_id)]["admins"]:
        overwriteDB = True
        msg = bot.send_message(chat_id=chat_id, text="Ahora puede usar el setup.", disable_notification=True)

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])
        JQ.run_once(deleteMsg, 10, context=[chat_id, msgId])
    else:
        msg = bot.send_message(chat_id=chat_id, text="Solo usuarios habilitados pueden resetear los datos.", disable_notification=True)

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])


def parsing(bot, update):
    global chatData
    msgEnts = update.message.parse_entities()
    chat_id = str(update.message.chat_id)
    msgId = update.message.message_id


#Hashtag parsing
    if chat_id in chatData.keys():
        for key in msgEnts:
            if key.type == "hashtag":
                if msgEnts[key] == "#tasa":
                    mostrarTasa(bot, chat_id, msgId)

                    # Queue for deletion
                    JQ.run_once(deleteMsg, 30, context=[chat_id, msgId])
                    JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])
                if msgEnts[key] in chatData[str(chat_id)].keys():
                    msg = bot.send_message(chat_id=update.message.chat_id, text="Recuperando perfil de " + msgEnts[key], disable_notification=True)

                    # Queue for deletion
                    JQ.run_once(deleteMsg, 60, context=[chat_id, msg.message_id])

                    name = "#" + msgEnts[key][1:]
                    msg = bot.send_message(chat_id=update.message.chat_id, text=chatData[str(chat_id)][name], disable_notification=True)

                    # Queue for deletion
                    JQ.run_once(deleteMsg, 60, context=[chat_id, msg.message_id])

                else:
                    pass

    else:
        pass


def perfil(bot, update):
    global chatData

    ents = update.message.parse_entities()
    chat_id = str(update.message.chat_id)
    msgId = update.message.message_id

    #Check there's a session stored for this chat.
    if chat_id in chatData.keys():
        #If there's one:
        if update.message.from_user.username in chatData[str(chat_id)]["admins"]:
            for key in ents:
                if key.type == "hashtag":

                    try:
                        chatData[str(chat_id)]["#" + ents[key][1:]] = update.message.text[(key.length + 9):]
                        msg = bot.send_message(chat_id=update.message.chat_id, text="El perfil de " + ents[key][1:] + " se ha guardado.", disable_notification=True)

                        # Queue for deletion
                        JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])
                    except:
                        msg = bot.send_message(chat_id=update.message.chat_id, text="Hubo un error al guardar el perfil de " + ents[key][1:] + ".", disable_notification=True)

                        # Queue for deletion
                        JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])

        else:
            msg = bot.send_message(chat_id=update.message.chat_id, text=("Sólo los usuarios habilitados pueden agregar perfiles.").decode("utf-8"), disable_notification=True)

            # Queue for deletion
            JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])

        with open("DB.json", "w") as db:
            json.dump(chatData, db)

    else:
        msg = bot.send_message(chat_id=chat_id, text=("No hay una sesión guardada para este chat. Use el comando setup para comenzar a guardar perfiles de forma permanente.").decode("utf-8"))

        # Queue for deletion
        JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])

    # Queue for deletion
    JQ.run_once(deleteMsg, 90, context=[chat_id, msgId])


def bienvenida(bot, update):
    #name = update.message.new_chat_members[0].first_name
    chat_id = str(update.message.chat_id)

    #Checking if there's a stored session
    if chat_id in chatData.keys():
        #Greeting every new chat member
        for newMember in update.message.new_chat_members:
            saludo = chatData[str(chat_id)]["saludo"] + newMember.first_name + ". " + chatData[str(chat_id)]["bienvenida"]

            msg = bot.send_message(chat_id=update.message.chat_id, text=saludo, disable_notification=True)

            # Queue for deletion
            JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])

    else:
        for newMember in update.message.new_chat_members:
            saludo = chatData["generic"]["saludo"] + newMember.first_name + ". " + chatData["generic"]["bienvenida"]

            msg = bot.send_message(chat_id=update.message.chat_id, text=saludo, disable_notification=True)

            # Queue for deletion
            JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])


def bienvenidaTest(bot, update):
    chat_id = str(update.message.chat_id)
    msgId = update.message.message_id

    #Checking if there's a stored session
    if chat_id in chatData.keys():
        saludo = chatData[str(chat_id)]["saludo"] + "@user. " + chatData[str(chat_id)]["bienvenida"]

        msg = bot.send_message(chat_id=update.message.chat_id, text=saludo, disable_notification=True)

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

    else:
        pass

    # Queue for deletion
    JQ.run_once(deleteMsg, 5, context=[chat_id, msgId])


def cambiarTextoDeBienvenida(bot, update, args):
    chat_id = str(update.message.chat_id)
    msgId = update.message.message_id

    #Checking if there's a stored session
    if chat_id in chatData.keys():
        if update.message.from_user.username in chatData[str(chat_id)]["admins"]:
            chatData[str(chat_id)]["bienvenida"] = " ".join(args)
            msg = bot.send_message(chat_id=update.message.chat_id, text="Mensaje de bienvenida cambiado.", disable_notification=True)

            # Queue for deletion
            JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])
        else:
            msg = bot.send_message(chat_id=update.message.chat_id, text="Solo los usuarios habilitados pueden cambiar el mensaje de bienvenida.", disable_notification=True)

            # Queue for deletion
            JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

    else:
        msg = bot.send_message(chat_id=chat_id, text=("No hay una sesión guardada para este chat. Use el comando setup para comenzar a guardar perfiles de forma permanente.").decode("utf-8"))

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

    # Queue for deletion
    JQ.run_once(deleteMsg, 20, context=[chat_id, msgId])


def calc(bot, update):
    chat_id = update.message.chat_id
    msgId = update.message.message_id

    if not set('[abcdefghijklmnopzABCDEFGHIJKLMNOZ~!@#$%^&()_{}":;\']$').intersection(update.message.text[5:]):
        result = eval(update.message.text[5:])
        msg = bot.send_message(chat_id=update.message.chat_id, text=result, disable_notification=True)

        # Queue for deletion
        JQ.run_once(deleteMsg, 30, context=[chat_id, msg.message_id])
    else:
        msg = bot.send_message(chat_id=update.message.chat_id, text="Hay caracteres no válidos en la operación solicitada.", disable_notification=True)

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

    # Queue for deletion
    JQ.run_once(deleteMsg, 30, context=[chat_id, msgId])

def actualizarTasas(bot, update, args):
    global FECHA
    global FECHABTC
    chat_id = str(update.message.chat_id)
    msgId = update.message.message_id

    #Updater instance
    U = RateUpdater()

    if not args:
        msg = bot.send_message(chat_id=chat_id, text="Debe especificar un filtro (USD/EUR/BTC). O simplemente use `/actualizar tasas` para actualizar el valor de todas las monedas", parse_mode="Markdown")

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])
    else:
        msg = bot.send_message(chat_id=chat_id, text="Consultando fuentes online. Espere unos segundos por favor.")

        # Queue for deletion
        JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

    if "btc" in args or "bitcoin" in args or "usd" in args or "dolar" in args or "euro" in args or "tasas" in args or "eur" in args:
        try:
            btc = U.actualizarBTC()

            #Returns a list with dicts in it, in this order: 0-VEF, 1-USD, 2-EUR
            BTC["VEF"] = btc[0]
            BTC["USD"] = btc[1]
            BTC["EUR"] = btc[2]

            msg = bot.send_message(chat_id=chat_id, text="Las cotizaciones de BTC se han actualizado.")

            # Queue for deletion
            JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

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

            msg = bot.send_message(chat_id=chat_id, text="Las cotizaciones de divisas internacionales se han actualizado.")

            # Queue for deletion
            JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

        except:
            msg = bot.send_message(chat_id=chat_id, text="Hubo un error en el comando o en el proceso de actualización. Intente nuevamente.")

            # Queue for deletion
            JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])

    # Queue for deletion
    JQ.run_once(deleteMsg, 10, context=[chat_id, msgId])

def cotizacion(bot, update, args):
    chat_id = str(update.message.chat_id)
    msgId = update.message.message_id
    divisa = args

    if FECHA and USD and EUR and BTC:
        #Header of the rates msg
        header = ".\n" + "            " + "*DOLAR TODAY*" + "        \n" + "    " + str(FECHA) + "\n\n\n"

        #Titles for money kind
        titleUSD = "                    " + "*DOLAR:*" + "\n\n"
        titleEUR = "                    " + "*EURO:*" + "\n\n"

        #Full msg build
        mensajeUSD = header + titleUSD + "Transferencia:    " + "`" + str(USD["transferencia"]) + "`" + "\n\nEfectivo:               " + "`" + str(USD["efectivo"]) + "`" + "\n\nImplícito:              " + "`" + str(USD["implícito"]) + "`" + "\n\nDICOM:                 " + "`" + str(USD["dicom"]) + "`"

        mensajeEUR = header + titleEUR + "Transferencia:    " + "`" + str(EUR["transferencia"]) + "`" + "\n\nEfectivo:               " + "`" + str(EUR["efectivo"]) + "`" + "\n\nImplícito:              " + "`" + str(EUR["implícito"]) + "`" + "\n\nDICOM:                 " + "`" + str(EUR["dicom"]) + "`"

        mensajeFULL = mensajeUSD + "\n\n\n\n" + titleEUR + "Transferencia:    " + "`" + str(EUR["transferencia"]) + "`" + "\n\nEfectivo:                " + "`" + str(EUR["efectivo"]) + "`" + "\n\nImplícito:              " + "`" + str(EUR["implícito"]) + "`" + "\n\nDICOM:                 " + "`" + str(EUR["dicom"]) + "`"

        #BTC message
        headerBTC = ".\n" + "                        " + "*LOCAL BITCOINS*" + "        \n" + "            " + str(FECHABTC) + "\n\n\n"
        bodyBTC = "*Promedio 12hs: Bs.* " + "`" +str(BTC["VEF"]["avg_12h"]) + "`" + "\n\n" + "*$1 = Btc. *" + "`" + str(BTC["USD"]["avg_12h"]) + "`" + "\n\n" + "*€1 = Btc. *" + "`" + str(BTC["EUR"]["avg_12h"]) + "`"

        #BTC message build
        mensajeFULLBTC = headerBTC + bodyBTC

        if "USD" in divisa or "usd" in divisa or "dolar" in divisa:
            msg = bot.send_message(chat_id=chat_id, text=mensajeUSD, parse_mode="Markdown")

            # Queue for deletion
            JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])

        elif "EUR" in divisa or "eur" in divisa or "euro" in divisa:
            msg = bot.send_message(chat_id=chat_id, text=mensajeEUR, parse_mode="Markdown")

            # Queue for deletion
            JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])

        elif "BTC" in divisa or "btc" in divisa or "bitcoin" in divisa:
            msg = bot.send_message(chat_id=chat_id, text=mensajeFULLBTC, parse_mode="Markdown")

            # Queue for deletion
            JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])

        elif not args:
            msg = bot.send_message(chat_id=chat_id, text=mensajeFULL, parse_mode="Markdown")

            # Queue for deletion
            JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])

    else:
        msg = bot.send_message(chat_id=chat_id, text="No hay valores recientes guardados. Use el comando 'actualizar' para descargar cotizaciones.")

        # Queue for deletion
        JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])

    # Queue for deletion
    JQ.run_once(deleteMsg, 20, context=[chat_id, msgId])


def tasa(bot, update):
    global tasa
    global isPhoto

    chat_id = update.message.chat_id
    msgId = update.message.message_id

    if update.message.reply_to_message.photo:
        tasa = update.message.reply_to_message.photo[-1]["file_id"]
        isPhoto = True
    else:
        tasa = update.message.reply_to_message.text
        isPhoto = False

    msg = bot.send_message(chat_id=chat_id, text="Tasa AirTM guardada.")

    # Queue for deletion
    JQ.run_once(deleteMsg, 10, context=[chat_id, msg.message_id])
    JQ.run_once(deleteMsg, 10, context=[chat_id, msgId])

def mostrarTasa(bot, chat_id, msgId):
    global tasa
    global isPhoto

    if isPhoto:
        msg = bot.send_photo(chat_id=chat_id, photo=tasa)

        # Queue for deletion
        JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])
    else:
        msg = bot.send_message(chat_id=chat_id, text=tasa)

        # Queue for deletion
        JQ.run_once(deleteMsg, 20, context=[chat_id, msg.message_id])

    # Queue for deletion
    JQ.run_once(deleteMsg, 5, context=[chat_id, msgId])

def deleteMsg(bot,job):

    bot.delete_message(chat_id=job.context[0], message_id=job.context[1])


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
DIS.add_handler(CMD("tasa", tasa))

DIS.add_handler(MSG(Filters.status_update.new_chat_members, bienvenida))
DIS.add_handler(MSG(Filters.all, parsing))

inicio()
UPD.start_polling()