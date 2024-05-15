import re

from HomeWork5.src.logger import setup_logger
from HomeWork5.src.consts import VALID_TYPES, VALID_STATUSES, ALLOWED_ACCOUNT_LENGTH, TYPE_CN, STATUS_CN, \
    VALID_ACCOUNT_NUMBER_START, ID_REGEX, SPECIAL_CHARACTERS_REGEX, NUMBER_CN

logger = setup_logger()


def validate_account_number(account_number: str):
    """
    Validate the format of an account number.

    :param account_number: Account number to be validated.
    :raise ValueError: If the account number format is invalid.
    """
    account_number = re.sub(SPECIAL_CHARACTERS_REGEX, '-', account_number)

    if len(account_number) > ALLOWED_ACCOUNT_LENGTH:
        raise ValueError(f'Account number {account_number} has too many chars!')
    elif len(account_number) < ALLOWED_ACCOUNT_LENGTH:
        raise ValueError(f'Account number {account_number} has too little chars!')

    if not account_number.startswith(VALID_ACCOUNT_NUMBER_START):
        raise ValueError('Wrong format! Account number should start with ID--')

    if not re.search(ID_REGEX, account_number):
        raise ValueError('Bad ID!')

    logger.info(f'Account number {account_number} validated.')


def validate_strict_field(value: int | str, valid_values: list, field_name: str):
    """
    Validate a field against a set of valid values.

    :param value: Value to validate.
    :param valid_values: Set of valid values for the field.
    :param field_name: Name of the field being validated.
    :raise ValueError: If the value is not in the valid set.
    """
    if value not in valid_values:
        raise ValueError(f'Invalid value {value!r} for field {field_name}!')


def validate_account_type(account_type: str):
    """
    Validate the 'type' field in the account.

    :param account_type: Account 'type' value.
    """
    validate_strict_field(account_type, VALID_TYPES, TYPE_CN)


def validate_account_status(account_status: str):
    """
    Validate the 'status' field in the account.

    :param account_status: Account 'status' value.
    """
    validate_strict_field(account_status, VALID_STATUSES, STATUS_CN)


def validate_transaction(sender: tuple[dict, str], receiver: tuple[dict, str], amount: int):
    """
    Validate a transaction based on sender, receiver, and amount.

    :param sender: Tuple containing sender's account details (dict) and account number (str).
    :param receiver: Tuple containing receiver's account details (dict) and account number (str).
    :param amount: Amount to be transferred.
    :return: True if the transaction is valid, None otherwise.
    """
    message = ''

    if sender[0] is None:
        message = f'Sender account number {sender[1]} not found'
    elif receiver[0] is None:
        message = f'Receiver account number {receiver[1]} not found'
    elif sender[0].get('amount', 0) < amount:
        message = 'Sender amount is less than the amount being sent'

    if message:
        logger.error(message)
        return False

    return True


def validate_accounts_data(accounts_data: list):
    """
    Validate the account one by one in accounts_data.

    :param accounts_data: List of dictionaries that contains account information.
    """
    for account in accounts_data:
        validate_account_number(account.get(NUMBER_CN))
        validate_account_type(account.get(TYPE_CN))
        validate_account_status(account.get(STATUS_CN))
