import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

from db_connection import establish_db_connection
from logger import setup_logger
from globals import ACCOUNTS_TN, USERS_TN, BANKS_TN, TRANSACTIONS_TN
from utils import get_record_by_condition, get_table_columns_names

logger = setup_logger()


@establish_db_connection
def get_users_full_names_with_debts(cursor: sqlite3.Cursor):
    """
    Get the full names of users with negative account balances.

    Retrieves and returns the full names of users who have negative balances in their accounts.

    :param cursor: The database cursor object.
    :return: A set of tuples of full names for users with negative balances.
    """
    cursor.execute(f'SELECT user_id, amount FROM {ACCOUNTS_TN}')
    negative_balance_ids = [user_id for user_id, amount in cursor.fetchall() if amount < 0]
    user_records = [get_record_by_condition(USERS_TN, 'id', user_id, cols=['name', 'surname'], serialize=False) for
                    user_id in negative_balance_ids]
    logger.info('Retrieved full names of users with negative account balances')
    return set(user_records)


@establish_db_connection
def get_biggest_capital_bank(cursor: sqlite3.Cursor):
    """
    Get the name of the bank with the largest total capital.

    Retrieves and returns the name of the bank with the largest total capital based on account balances.

    :param cursor: The database cursor object.
    :return: The name of the bank with the largest total capital.
    """
    bank_capitals = defaultdict(int)

    cursor.execute(f'SELECT bank_id, amount FROM {ACCOUNTS_TN}')
    for bank_id, amount in cursor.fetchall():
        bank_capitals[bank_id] += amount

    max_bank_capital_id = max(bank_capitals, key=lambda x: bank_capitals.get(x))

    return get_record_by_condition(BANKS_TN, 'id', max_bank_capital_id, cols=['name'], serialize=False)[0]


@establish_db_connection
def get_banks_with_oldest_client(cursor: sqlite3.Cursor):
    """
    Get the name of the bank with the oldest client.

    Retrieves and returns the names of the banks with the oldest client based on client birthdays.

    :param cursor: The database cursor object.
    :return: The list of the banks names with the oldest client.
    """
    cursor.execute(f'SELECT birth_day, accounts FROM {USERS_TN}')
    min_date_user = min(cursor.fetchall(), key=lambda x: x[0])
    user_bank_ids = set(
        [get_record_by_condition(ACCOUNTS_TN, 'number', acc_number, cols=['bank_id'], serialize=False)[0] for acc_number
         in min_date_user[1].split(',')])
    bank_names = [get_record_by_condition(BANKS_TN, 'id', bank_id, cols=['name'], serialize=False)[0] for bank_id in
                  user_bank_ids]
    return bank_names


@establish_db_connection
def get_bank_with_most_unique_outbound_operations(cursor: sqlite3.Cursor):
    """
    Get the name of the bank with the most unique outbound operations.

    Retrieves and returns the name of the bank with the most unique outbound operations.

    :param cursor: The database cursor object.
    :return: The name of the bank with the most unique outbound operations.
    """
    cursor.execute(f'SELECT bank_sender_name, account_sender_id FROM {TRANSACTIONS_TN}')
    transactions = cursor.fetchall()

    bank_unique_operations = defaultdict(set)
    for bank_name, account_id in transactions:
        bank_unique_operations[bank_name].add(account_id)

    bank_with_most_unique = max(bank_unique_operations.items(), key=lambda x: len(x[1]))
    return bank_with_most_unique[0]


@establish_db_connection
def get_user_transactions(cursor: sqlite3.Cursor, user_id: int, days: int = None):
    """
    Get all transactions for a specific user within a specified number of past days.

    Retrieves and returns all transactions associated with a specific user ID within a specified time frame
    based on the number of past days provided.

    :param cursor: The database cursor object.
    :param user_id: The ID of the user to retrieve transactions for.
    :param days: The number of past days to consider for retrieving transactions.
                 If None (default), retrieves all transactions regardless of date.
    :return: A list of transactions for the specified user within the specified time frame.
    """
    date_condition = ''

    if days:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        date_condition = f'AND datetime >= {start_date!r}'

    cursor.execute(f'SELECT * FROM {TRANSACTIONS_TN} \
                     WHERE account_sender_id = {user_id} \
                     {date_condition}')
    logger.info(f'Retrieved transactions for user ID {user_id}')
    return cursor.fetchall()


@establish_db_connection
def delete_empty_users(cursor: sqlite3.Cursor):
    """
    Delete users with empty fields.

    Deletes users from the database whose name, surname, birth_day, or accounts fields are empty.

    :param cursor: The database cursor object.
    """
    cursor.execute(f"DELETE FROM {USERS_TN} \
                     WHERE {" = '' OR ".join(get_table_columns_names(USERS_TN))} = '' ")
    logger.info('Deleted users with empty fields')
