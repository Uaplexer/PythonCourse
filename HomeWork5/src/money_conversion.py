import requests
from logger import setup_logger

API_URL = 'https://api.freecurrencyapi.com/v1/latest'
API_KEY = 'fca_live_Ycr9NHeuLZqZ9LGlyHr4N993tCW99bBh2BR9ymNX'
params = {'apikey': API_KEY}

logger = setup_logger()


def get_exchange_rate(base_currency_code, target_currency_code):
    """
    Get the exchange rate between two currencies using an API.

    This function sets up the API parameters for base and target currencies, sends a GET request to the API,
    and retrieves the exchange rate from the response JSON data.

    :param base_currency_code: The code of the base currency.
    :param target_currency_code: The code of the target currency.
    :return: The exchange rate between the base and target currencies, or None if there is an error.
    """
    if base_currency_code == target_currency_code:
        return 1

    params['base_currency'] = base_currency_code
    params['currencies'] = target_currency_code

    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        logger.info('Successfully fetched exchange rate')
    elif response.status_code == 429:
        logger.error('You have hit your rate limit or your monthly limit')
        return

    return response.json().get('data').get(target_currency_code)
