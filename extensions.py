import requests
import json

from config import keys


class APIException(Exception):
    pass


class Converter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        if base == quote:
            raise APIException(f'Невозможно перевести одинаковые валюты: "{base}".')

        try:
            quote_ticker = keys[base.lower()]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: "{base}"')

        try:
            base_ticker = keys[quote.lower()]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: "{quote}"')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество: "{amount}"')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total_base = json.loads(r.content)
        total_base = total_base[base_ticker] * amount

        return round(total_base, 2)
