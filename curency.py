import requests
from prettytable import PrettyTable

def get_privatbank_exchange_rates():
    url = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        rates = []
        for currency in data:
            if currency['ccy'] in {'USD', 'EUR'}:
                rates.append({
                    'Валюта': currency['ccy'],
                    'Покупка (карточный)': currency['buy'],
                    'Продажа (карточный)': currency['sale'],
                    'Покупка (НБУ)': currency['buy'],
                    'Продажа (НБУ)': currency['sale']
                })

        return rates
    else:
        return []

def show_exchange_rates(rates):
    if rates:
        table = PrettyTable()
        table.field_names = ['Валюта', 'Покупка (карточный)', 'Продажа (карточный)', 'Покупка (НБУ)', 'Продажа (НБУ)']

        for rate in rates:
            table.add_row([rate['Валюта'],
                           rate['Покупка (карточный)'],
                           rate['Продажа (карточный)'],
                           rate['Покупка (НБУ)'],
                           rate['Продажа (НБУ)']])

        print(table)
    else:
        print("Ошибка при запросе курса валют")

if __name__ == "__main__":
    rates = get_privatbank_exchange_rates()
    show_exchange_rates(rates)
