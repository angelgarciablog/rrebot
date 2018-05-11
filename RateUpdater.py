#-*- coding: utf-8 -*-

import requests

class RateUpdater():

    def __init__(self, sistema):
        self.sistema = sistema

        if self.sistema == "BTC":
            self.actualizarBTC()
        elif self.sistema == "DIV":
            self.actualizarDivisas()

    def actualizarBTC(self):
        response = requests.get("https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/")
        json = response.json()

        data = [json["VEF"]]

        return data

    def actualizarDivisas(self):
        response = requests.get("https://dxj1e0bbbefdtsyig.woldrssl.net/custom/rate.js")

        data = eval(response.text[17:])

        diccionario = {
            "FECHA": data["fecha"],
            "USD": data["USD"],
            "EUR": data["EUR"]
            }

        return diccionario

