import requests
from http import HTTPStatus
from logger import setup_logger
from globals import API_KEY_CURRENCIES, API_URL_CURRENCIES

logger = setup_logger()


def convert_currency(amount: int, base_currency_code: str, target_currency_code: str):
    """
        Converts an amount of currency from one currency code to another using an external API.

        :param amount: The amount of currency to convert.
        :param base_currency_code: The currency code of the base currency to convert from.
        :param target_currency_code: The currency code of the target currency to convert to.

        :return: The converted amount in the target currency, or None if conversion fails.
        """
    if base_currency_code == target_currency_code:
        return amount

    params = {'apikey': API_KEY_CURRENCIES, 'currencies': target_currency_code, 'base_currency': base_currency_code}

    response = requests.get(API_URL_CURRENCIES, params=params)

    if response.status_code == HTTPStatus.OK:
        exchange_rate = response.json().get('data').get(target_currency_code)
        logger.info('Successfully fetched exchange rate')
        return amount * exchange_rate

    elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logger.error('You have hit your rate limit or your monthly limit')
        return None
    else:
        logger.error(f'Unexpected response {response.status_code}')
        return None
