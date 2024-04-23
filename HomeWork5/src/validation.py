import re

from logger import setup_logger
from globals import VALID_TYPES, VALID_STATUSES

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


def validate_strict_field(value, valid_values: list, field_name: str):
    """
    Validate a field against a set of valid values.

    :param value: Value to validate.
    :param valid_values: Set of valid values for the field.
    :param field_name: Name of the field being validated.
    :raise ValueError: If the value is not in the valid set.
    """
    if value not in valid_values:
        raise ValueError(f'Invalid value \'{value}\' for field {field_name}!')


def validate_account_type(account_type: str):
    """
    Validate the 'type' field in the account.

    :param account_type: Account 'type' value.
    :raise ValueError: If the 'type' value isn't valid.
    """
    validate_strict_field(account_type, VALID_TYPES, 'type')


def validate_account_status(account_status: str):
    """
    Validate the 'status' field in the account.

    :param account_status: Account 'status' value.
    :raise ValueError: If the 'status' value isn't valid.
    """
    validate_strict_field(account_status, VALID_STATUSES, 'status')


def validate_users_data(users_data: list):
    pass


def validate_accounts_data(accounts_data: list):
    """
    Validate the account one by one in accounts_data.

    :param accounts_data: List of dictionaries that contains account information.
    """
    for account in accounts_data:
        validate_account_number(account.get('number'))
        validate_account_type(account.get('type'))
        validate_account_status(account.get('status'))
