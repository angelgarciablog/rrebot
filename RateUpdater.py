#-*- coding: utf-8 -*-

import requests

class RateUpdater():

    def __init__(self):
        #No initialization required
        pass

    def actualizarBTC(self):
        response = requests.get("https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/")
        json = response.json()

        data = [json["VEF"], json["USD"], json["EUR"]]

        return data

    def actualizarDivisas(self):
        response = requests.get("https://dxj1e0bbbefdtsyig.woldrssl.net/custom/rate.js")

        data = eval(response.text[17:])

        diccionario = {
            "FECHA": data["_timestamp"]["fecha"],
            "USD": data["USD"],
            "EUR": data["EUR"]
            }

        return diccionario

