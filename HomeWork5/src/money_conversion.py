import requests
from logger import setup_logger
from globals import API_KEY_CURRENCIES, API_URL_CURRENCIES

params = {'apikey': API_KEY_CURRENCIES}

logger = setup_logger()


def get_exchange_rate(base_currency_code: str, target_currency_code: str):
    """
    Get the exchange rate between two currencies using an API.

    This function sets up the API parameters for base and target currencies, sends a GET request to the API,
    and retrieves the exchange rate from the response JSON data.

    :param base_currency_code: The code of the base currency.
    :param target_currency_code: The code of the target currency.
    :return: The exchange rate between the base and target currencies, or None.
    """
    if base_currency_code == target_currency_code:
        return 1

    params['base_currency'] = base_currency_code
    params['currencies'] = target_currency_code

    response = requests.get(API_URL_CURRENCIES, params=params)

    if response.status_code == 200:
        logger.info('Successfully fetched exchange rate')
    elif response.status_code == 429:
        logger.error('You have hit your rate limit or your monthly limit')
        return None

    return response.json().get('data').get(target_currency_code)
