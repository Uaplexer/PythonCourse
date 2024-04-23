from datetime import datetime
from utils import get_record_by_condition
from api import update_account, add_transaction
from money_conversion import get_exchange_rate
from logger import setup_logger
from initial_db_setup_001 import ACCOUNTS_TN, BANKS_TN

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

    if sender_account.get('amount', 0) < amount:
        logger.error('Sender have less money than it sends')
        return None

    if not sender_account:
        logger.error(f'Sender account number {sender_account_number} not found')
        return None

    if not receiver_account:
        logger.error(f'Receiver account number {receiver_account_number} not found')
        return None

    exchange_rate = get_exchange_rate(sender_account['currency'], receiver_account['currency'])

    new_sender_amount = sender_account.get('amount') - amount
    new_receiver_amount = receiver_account.get('amount') + (amount * exchange_rate)

    account_sender_id = sender_account.get('id')
    account_receiver_id = receiver_account.get('id')

    update_account({'amount': new_sender_amount}, account_sender_id)
    update_account({'amount': new_receiver_amount}, account_receiver_id)

    sender_bank_name = get_record_by_condition(BANKS_TN, 'id', sender_account.get('bank_id')).get('name')
    receiver_bank_name = get_record_by_condition(BANKS_TN, 'id', receiver_account.get('bank_id')).get('name')

    transaction_data = {
        'bank_sender_name': sender_bank_name,
        'bank_receiver_name': receiver_bank_name,
        'account_sender_id': account_sender_id,
        'account_receiver_id': account_receiver_id,
        'sent_currency': sender_account['currency'],
        'sent_amount': amount,
        'datetime': time if time else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    add_transaction(transaction_data)
    logger.info('Transaction performed successfully!')
