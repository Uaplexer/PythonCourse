import re

from logger import setup_logger

VALID_TYPES = ['credit', 'debit']
VALID_STATUSES = ['gold', 'silver', 'platinum']

logger = setup_logger()


def validate_account_number(account_number: str):
    """
    Validate the format of an account number.

    :param account_number: Account number to be validated.
    :raise ValueError: If the account number format is invalid.
    """
    account_number = re.sub(r'[#%_?&]', '-', account_number)

    if len(account_number) > 18:
        raise ValueError(f'Account number {account_number} has too many chars!')
    elif len(account_number) < 18:
        raise ValueError(f'Account number {account_number} has too little chars!')

    if not account_number.startswith('ID--'):
        raise ValueError('Wrong format! Account number should start with ID--')

    if not re.search(r'[a-zA-Z]{1,3}-\d+', account_number):
        raise ValueError('Bad ID!')

    logger.info(f'Account number {account_number} validated.')


def validate_account_type_and_status(account_type: str, account_status: str):
    """
    Validate the fields 'type' and 'status' in the account.

    :param account_type: Account 'type' value.
    :param account_status: Account 'status' value.
    :raise ValueError: If any of the 'type', 'status' values aren't valid.
    """
    if account_type not in VALID_TYPES:
        raise ValueError(f'Not allowed value \'{account_type}\' for field type!')
    if account_status not in VALID_STATUSES:
        raise ValueError(f'Not allowed value \'{account_status}\' for field status!')


def validate_users_data(users_data: list):
    pass


def validate_accounts_data(accounts_data: list):
    """
    Validate the account one by one in accounts_data.

    :param accounts_data: List of dictionaries that contains account information.
    """
    for account in accounts_data:
        validate_account_number(account.get('number'))
        validate_account_type_and_status(account.get('type'), account.get('status'))
