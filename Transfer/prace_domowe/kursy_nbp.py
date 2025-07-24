# z api nbp kurs złota
# dzienny, historyczny

import requests
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Rate(BaseModel):
    no: str
    effectiveDate: datetime
    mid: float


class Waluta(BaseModel):
    table: str
    currency: str
    code: str
    rates: List[Rate]


class Gold(BaseModel):
    data: datetime
    cena: float


class NBPClient:
    def __init__(self, base_url = "https://api.nbp.pl/api", date: str = None):
        """
        Inicjacja klasy NBPClient
        :param base_url: Adres api NBP
        :param date: Data. Wartość None to data dzisiejsza
        """
        self.base_url = base_url

    def load_input_currency(self):

        self.table = "A"

        print("""\nJaką walutę chcesz sprawdzić podaj kod waluty:
        USD - Dolar amerykański
        EUR - Euro
        CHF - Frank szwajcarskie
        GBP - Funt szterling (brytyjski)
        JPY - Jen japoński
        CZK - Korona czeska
        NOK - Korona norweska
        SEK - Korona szwecka
        DKK - Korona duńska
        CAD - Dolar kanadyjski
        AUD - Dolar australijski
        CNY - Juan chiński
        """)
        valid_currency_codes = [
            "USD", "EUR", "CHF", "GBP", "JPY", "CZK",
            "NOK", "SEK", "DKK", "CAD", "AUD", "CNY"
        ]
        while True:
            self.code = input("\nPodaj kod waluty: ").strip().upper()
            if self.code in valid_currency_codes:
                break
            print("\nNiepoprawny kod waluty. Spróbuj ponownie.")

        while True:
            date_input = input("\nPodaj datę kursu waluty (RRRR-MM-DD) (Naciśnij ENTER jesli chcesz dzisiajszą): ").strip()

            if date_input =="":
                self.date = None
                break

            try:
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()
                start_date = datetime.strptime("2002-01-02", "%Y-%m-%d").date()
                today = datetime.today().date()

                if start_date <= parsed_date <= today:
                    self.date = date_input
                    break
                else:
                    print(f"\nData musi być z zakresu {start_date} - {today}. Spróbuj ponownie")
            except ValueError:
                print("\nNiepoprawny format daty, użyj formatu RRRR-MM-DD")

    def load_input_gold(self):
        while True:
            date_input = input("\nPodaj datę ceny złota (RRRR-MM-DD) (Naciśnij ENTER jesli chcesz dzisiajszą): ").strip()

            if date_input =="":
                self.date = None
                break

            try:
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()
                stat_date = datetime.strptime("2013-01-02", "%Y-%m-%d").date()
                today = datetime.today().date()

                if stat_date <= parsed_date <= today:
                    self.date = date_input
                    break
                else:
                    print(f"\nData musi być z zakresu {stat_date} - {today}. Spróbuj ponownie")
            except ValueError:
                print("\nNiepoprawny format daty, użyj formatu RRRR-MM-DD")

    def get_currency_rate(self):

        url = self.build_url_currency()
        response = requests.get(url)

        try:
            response_data = response.json()
        except ValueError:
            print("Brak danych dla podanej daty. Najprawdopodobniej jest to dzień wolny np. weekend lub święto.")
            return

        currency_data = Waluta(**response_data)
        effectiveDate = currency_data.rates[0].effectiveDate
        formated_date = effectiveDate.strftime("%d/%m/%Y")

        print(f"""
        Kurs waluty: ({currency_data.code}) {currency_data.currency}
        na dzień: {formated_date}
        wynosi: {currency_data.rates[0].mid} zł""")

    def build_url_currency(self):
        elements = [
            self.base_url,
            "exchangerates",
            "rates",
            self.table.strip("/"),
            self.code.strip("/").lower(),
            self.date
        ]
        url = "/".join(filter(None, elements))
        return url

    def get_gold_price(self):

        url = self.build_url_gold()
        response = requests.get(url)

        try:
            response_data = response.json()
        except ValueError:
            print("Brak danych dla podanej daty. Najprawdopodobniej jest to dzień wolny np. weekend lub święto.")
            return

        gold = Gold(**response_data[0])
        gold_date = gold.data
        formated_gold_date = gold_date.strftime("%d/%m/%Y")

        print(f"""
        Cena złota (Gold)
        na dzień: {formated_gold_date}
        wynosi: {gold.cena}""")

    def build_url_gold(self):
        elements = [
            self.base_url,
            "cenyzlota",
            self.date
        ]
        url = "/".join(filter(None, elements))
        return url

    def send_request(self, url: str) -> dict:
        """
        Miejsce na obsługę błędów łączności internetowej
        :return
        """

print("\nProgram '--KURSIKI--' słuzy do sprawdzania ceny złota lub najpopularniejszych walut.")

client = NBPClient()

while True:
    print("""\nCo chcesz zrobić?
    1. Sprawdzić cenę złota
    2. Sprawdzić kurs waluty
    0. zakończyć program
    """)

    activbity = input("\nWybierz jedną z opcji (0-2): ")

    match activbity:
        case "1":
            client.load_input_gold()
            client.get_gold_price()

        case "2":
            client.load_input_currency()
            client.get_currency_rate()

        case "0":
            print("\nKoniec programu.")
            break

        case _:
            print("\nZły wybór. Spróbuj jeszcze raz.")