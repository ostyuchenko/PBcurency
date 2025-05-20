"""
Fetches and displays USD and EUR exchange rates from PrivatBank (card rates)
and the National Bank of Ukraine (NBU) (official rates).
The rates are displayed in a tabular format.
"""
import requests
import json # For json.JSONDecodeError
from prettytable import PrettyTable

def get_privatbank_exchange_rates():
    """
    Fetches USD and EUR exchange rates from PrivatBank (card rates) and NBU (official rates).

    It makes API calls to PrivatBank and NBU. If an API call or data processing fails
    for a specific rate, that rate will be set to 'N/A'.

    APIs used:
    - PrivatBank: https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11
    - NBU: https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json

    Returns:
        list: A list of dictionaries, where each dictionary represents a currency (USD or EUR)
              and contains the following keys:
              - 'Валюта': Currency code (str, e.g., 'USD').
              - 'Покупка (карточный)': PrivatBank card buy rate (str or 'N/A').
              - 'Продажа (карточный)': PrivatBank card sell rate (str or 'N/A').
              - 'Покупка (НБУ)': NBU official rate (float or 'N/A').
              - 'Продажа (НБУ)': NBU official rate (float or 'N/A').
    """
    privat_url = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
    nbu_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

    # Initialize a dictionary to store processed rates with default 'N/A' values.
    # This structure helps in easily updating rates as they are fetched and ensures
    # all currencies have default values if API calls fail.
    processed_rates = {
        'USD': {'buy_card': 'N/A', 'sale_card': 'N/A', 'nbu_rate': 'N/A'},
        'EUR': {'buy_card': 'N/A', 'sale_card': 'N/A', 'nbu_rate': 'N/A'}
    }

    # --- Fetch PrivatBank rates ---
    pb_data_list = [] # To store the list of currency data from PrivatBank
    try:
        # Attempt to get data from PrivatBank API with a 10-second timeout.
        privat_response = requests.get(privat_url, timeout=10)
        if privat_response.status_code == 200:
            try:
                # Attempt to decode JSON response from PrivatBank.
                pb_data_list = privat_response.json()
            except json.JSONDecodeError:
                print("Error: Could not decode JSON response from PrivatBank API.")
        else:
            print(f"Error: PrivatBank API returned status code {privat_response.status_code}.")
    except requests.exceptions.Timeout:
        print("Error: Request to PrivatBank API timed out.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to PrivatBank API.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PrivatBank rates: {e}")

    # Process data received from PrivatBank.
    if pb_data_list: # Check if pb_data_list is not empty (i.e., API call was somewhat successful).
        for currency_data in pb_data_list:
            # Ensure currency_data is a dictionary and the currency code ('ccy') is one we are interested in.
            if isinstance(currency_data, dict) and currency_data.get('ccy') in processed_rates:
                processed_rates[currency_data['ccy']]['buy_card'] = currency_data.get('buy', 'N/A')
                processed_rates[currency_data['ccy']]['sale_card'] = currency_data.get('sale', 'N/A')

    # --- Fetch NBU rates ---
    nbu_data_list = [] # To store the list of currency data from NBU
    try:
        # Attempt to get data from NBU API with a 10-second timeout.
        nbu_response = requests.get(nbu_url, timeout=10)
        if nbu_response.status_code == 200:
            try:
                # Attempt to decode JSON response from NBU.
                nbu_data_list = nbu_response.json()
            except json.JSONDecodeError:
                print("Error: Could not decode JSON response from NBU API.")
        else:
            print(f"Error: NBU API returned status code {nbu_response.status_code}.")
    except requests.exceptions.Timeout:
        print("Error: Request to NBU API timed out.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to NBU API.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NBU rates: {e}")

    # Process data received from NBU.
    if nbu_data_list: # Check if nbu_data_list is not empty.
        for currency_data in nbu_data_list:
            # Ensure currency_data is a dictionary and the currency code ('cc') is one we are interested in.
            if isinstance(currency_data, dict) and currency_data.get('cc') in processed_rates:
                processed_rates[currency_data['cc']]['nbu_rate'] = currency_data.get('rate', 'N/A')
    
    # Construct the final list of dictionaries in the format expected by show_exchange_rates.
    combined_rates_list = []
    for currency_code, rates_data in processed_rates.items():
        rate_entry = {
            'Валюта': currency_code,
            'Покупка (карточный)': rates_data['buy_card'],
            'Продажа (карточный)': rates_data['sale_card'],
            'Покупка (НБУ)': rates_data['nbu_rate'], # NBU rate is used for both buy and sell
            'Продажа (НБУ)': rates_data['nbu_rate']  # as it's an official (single) rate.
        }
        combined_rates_list.append(rate_entry)

    return combined_rates_list

def show_exchange_rates(rates):
    """
    Displays the provided exchange rates in a formatted table.

    Args:
        rates (list): A list of dictionaries, where each dictionary contains
                      exchange rate information for a currency. Expected keys are:
                      'Валюта', 'Покупка (карточный)', 'Продажа (карточный)',
                      'Покупка (НБУ)', 'Продажа (НБУ)'.
    
    Outputs:
        Prints a table to the console. If the rates list is empty,
        it prints an error message.
    """
    if rates:
        # Initialize PrettyTable with defined field names (column headers).
        table = PrettyTable()
        table.field_names = ['Валюта', 'Покупка (карточный)', 'Продажа (карточный)', 'Покупка (НБУ)', 'Продажа (НБУ)']

        # Add a row to the table for each rate dictionary in the list.
        for rate in rates:
            table.add_row([rate['Валюта'],
                           rate['Покупка (карточный)'],
                           rate['Продажа (карточный)'],
                           rate['Покупка (НБУ)'],
                           rate['Продажа (НБУ)']])

        print(table)
    else:
        # If the rates list is empty, print an error message.
        print("Ошибка при запросе курса валют")

# This block executes only when the script is run directly (not imported as a module).
if __name__ == "__main__":
    rates = get_privatbank_exchange_rates()
    show_exchange_rates(rates)
