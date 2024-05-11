from datetime import datetime

from validation import validate_transaction
from utils import get_record_by_condition, get_transaction_data
from api import update_account, add_transaction
from money_conversion import convert_currency
from logger import setup_logger
from initial_db_setup_001 import ACCOUNTS_TN

logger = setup_logger()


def perform_transaction(sender_account_number: str, receiver_account_number: str, amount: int, time=None):
    """
    Perform a transaction between sender and receiver accounts.

    This function retrieves sender and receiver account details, checks if the amount is valid,
    checks if sender has sufficient balance, calculates exchange rate, updates account balances
    and adds a transaction record.

    :param sender_account_number: The account number of the sender.
    :param receiver_account_number: The account number of the receiver.
    :param amount: The amount to be transferred.
    :param time: Optional parameter for transaction time (default is None).
    """
    if amount < 0:
        logger.error('Transaction amount is negative')
        return None

    sender_account = get_record_by_condition(ACCOUNTS_TN, 'number', sender_account_number)
    receiver_account = get_record_by_condition(ACCOUNTS_TN, 'number', receiver_account_number)

    if not validate_transaction(sender_account, receiver_account, amount):
        logger.error('Invalid transaction')
        return None

    converted_amount = convert_currency(amount, sender_account.get('currency'), receiver_account.get('currency'))
    new_sender_amount = sender_account.get('amount') - amount
    new_receiver_amount = receiver_account.get('amount') + converted_amount

    transaction_data = get_transaction_data(sender_account, receiver_account, amount, time)

    update_account({'amount': new_sender_amount}, transaction_data.get('account_sender_id'))
    update_account({'amount': new_receiver_amount}, transaction_data.get('account_receiver_id'))
    add_transaction(transaction_data)
    logger.info('Transaction performed successfully!')
