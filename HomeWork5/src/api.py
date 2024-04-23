import csv
import sqlite3

from logger import setup_logger
from db_connection import establish_db_connection
from globals import USERS_TN, BANKS_TN, ACCOUNTS_TN, TRANSACTIONS_TN
from validation import validate_accounts_data, validate_account_number, validate_account_status, validate_account_type
from utils import modify_users_data, get_query_params, get_table_columns_names
from typing import Callable

logger = setup_logger()


def add_data_from_csv(file_path: str, add_data_func: Callable):
    """
    Adds data from a CSV file using the specified function.

    :param file_path: The path to the CSV file.
    :param add_data_func: The function to add data to the database.
    :return: Function call to add data to the database.
    """
    with open(file_path, 'r') as csvf:
        reader = list(csv.DictReader(csvf))
        logger.info(f'Got data from csv file {file_path}')
        return add_data_func(reader)


@establish_db_connection
def add_table_records(cursor: sqlite3.Cursor, table_name: str, data: list[dict] | dict):
    """
    Adds a records to the specified table.

    :param cursor: The database cursor object.
    :param table_name: The name of the table to add the records to.
    :param data: The data to be added as a records.
    """
    table_columns = get_table_columns_names(table_name)
    placeholders = [':' + col_name for col_name in table_columns]
    cursor.executemany(f'INSERT INTO {table_name} ({', '.join(table_columns)})VALUES ({', '.join(placeholders)})', data)
    logger.info(f'{table_name.capitalize()} in table {table_name} added successfully')


@establish_db_connection
def update_table_record(cursor: sqlite3.Cursor, table_name: str, data: dict, record_id: int):
    """
    Updates a record in the specified table.

    :param cursor: The database cursor object.
    :param table_name: The name of the table to update the record in.
    :param data: The data to be updated.
    :param record_id: The ID of the record to be updated.
    """
    if not data:
        logger.warning('No data provided.')

    query_params = get_query_params(data)
    cursor.execute(f'UPDATE {table_name} SET {query_params} WHERE id = {record_id}')
    logger.info(f'Record with id {record_id} in table {table_name} updated successfully.')


@establish_db_connection
def delete_table_record(cursor: sqlite3.Cursor, table_name: str, record_id: int):
    """
    Deletes a record from the specified table.

    :param cursor: The database cursor object.
    :param table_name: The name of the table to delete the record from.
    :param record_id: The ID of the record to be deleted.
    """
    cursor.execute(f'DELETE FROM {table_name} WHERE id = {record_id}')
    logger.info(f'Record with id {record_id} in table {table_name} deleted successfully.')


def add_users(users_data: list):
    """
    Adds users to the USERS table.

    :param users_data: A list of dictionaries containing user data.
    """
    users_data = modify_users_data(users_data)
    add_table_records(USERS_TN, users_data)


def update_user(user_data: dict, user_id: int):
    """
    Updates user data in the USERS table.

    :param user_data: A dictionary containing updated user data.
    :param user_id: The ID of the user to be updated.
    """
    update_table_record(USERS_TN, user_data, user_id)


def delete_user(user_id: int):
    """
    Deletes a user from the USERS table.

    :param user_id: The ID of the user to be deleted.
    """
    delete_table_record(USERS_TN, user_id)


def add_banks(banks_data: list):
    """
    Adds banks to the BANKS table.

    :param banks_data: A list of dictionaries containing bank data.
    """
    add_table_records(BANKS_TN, banks_data)


def update_bank(bank_data: dict, bank_id: int):
    """
    Updates bank data in the BANKS table.

    :param bank_data: A dictionary containing updated bank data.
    :param bank_id: The ID of the bank to be updated.
    """
    update_table_record(BANKS_TN, bank_data, bank_id)


def delete_bank(bank_id: int):
    """
    Deletes a bank from the BANKS table.

    :param bank_id: The ID of the bank to be deleted.
    """
    delete_table_record(BANKS_TN, bank_id)


def add_accounts(account_data: list):
    """
    Adds accounts to the ACCOUNTS table.

    :param account_data: A list of dictionaries containing account data.
    """
    validate_accounts_data(account_data)
    add_table_records(ACCOUNTS_TN, account_data)


def update_account(account_data: dict, account_id: int):
    """
    Updates account data in the ACCOUNTS table.

    :param account_data: A dictionary containing new account data.
    :param account_id: The ID of the account to be updated.
    """
    validate_account_number(account_data.get('number', 'ID--du-mmy-99-numb'))
    validate_account_type(account_data.get('type', 'credit'))
    validate_account_status(account_data.get('status', 'gold'))
    update_table_record(ACCOUNTS_TN, account_data, account_id)


def delete_account(account_id: int):
    """
    Deletes an account from the ACCOUNTS table.

    :param account_id: The ID of the account to be deleted.
    """
    delete_table_record(ACCOUNTS_TN, account_id)


def add_transaction(transaction_data: dict):
    """
    Adds a transaction to the TRANSACTIONS table.

    :param transaction_data: A dictionary containing transaction data.
    """
    add_table_records(TRANSACTIONS_TN, transaction_data)
