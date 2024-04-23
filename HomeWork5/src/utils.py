import re
import random
import sqlite3

from logger import setup_logger
from datetime import timedelta, datetime
from db_connection import establish_db_connection
from globals import USERS_TN, ACCOUNTS_TN, BANKS_TN, TRANSACTIONS_TN, AVAILABLE_DISCOUNTS

logger = setup_logger()


def serialize_data(cursor: sqlite3.Cursor, record_data: list) -> dict:
    """
    Serialize database record data into a dictionary.

    Converts database record data into a dictionary using column names as keys.

    :param cursor: The database cursor object.
    :param record_data: Data retrieved from a database record.
    :return: A dictionary representing the serialized record data.
    """
    column_names = [desc[0] for desc in cursor.description]
    return dict(zip(column_names, record_data))


def get_query_params(data: dict):
    """
    Generate query parameters for SQL UPDATE statement.

    Converts a dictionary of data into query parameters for an SQL UPDATE statement.

    :param data: Dictionary containing key-value pairs for the update operation.
    :return: String containing the formatted query parameters.
    """
    return ', '.join([f'{key} = {val!r}' if isinstance(val, str) else f'{key} = {val}' for key, val in data.items()])


def get_first_element_if_not_empty(collection):
    """
    Returns the first element of a collection if the collection is not empty.

    :param collection: The collection to check.
    :return: The first element of the collection if it is not empty, otherwise None.
    """
    if collection:
        return collection[0]


@establish_db_connection
def clear_table(cursor: sqlite3.Cursor, table_name: str):
    """
       Clears all records from the specified table.

       :param cursor: The database cursor object.
       :param table_name: The name of the table to clear.
    """
    cursor.execute(f'DELETE FROM {table_name}')
    logger.info(f'Cleared table {table_name}')


@establish_db_connection
def get_table_columns_names(cursor: sqlite3.Cursor, table_name: str):
    """
    Get the column names of a database table.

    Retrieves and returns the column names of a specified database table.

    :param cursor: The database cursor object.
    :param table_name: The name of the table to get column names from.
    :return: A list of column names for the specified table.
    """
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns_info = cursor.fetchall()
    logger.info(f'Retrieved columns names for table {table_name}')
    return [info[1] for info in columns_info[1:]]  # exclude id


@establish_db_connection
def get_record_by_condition(cursor: sqlite3.Cursor, table_name: str, query_key: str, query_value,
                            cols: list[str] | None = None,
                            serialize: bool = True):
    """
    Get a record from a database table based on a condition.

    Retrieves and returns a record from a specified database table based on a given condition.

    :param cursor: The database cursor object.
    :param table_name: The name of the table to query.
    :param query_key: The column name to use for the query condition.
    :param query_value: The value to match in the specified column.
    :param cols: Columns names of record to retrieve.
    :param serialize: Serializes data to dict.
    :return: A dictionary representing the retrieved record if found, otherwise None.
    """
    cursor.execute(f"SELECT {', '.join(cols) if cols else '*'} \
                     FROM {table_name} \
                     WHERE {query_key} = {f'{query_value!r}' if isinstance(query_value, str) else query_value}")
    record = cursor.fetchone()
    if record:
        logger.info(f'Retrieved record from table {table_name} with condition {query_key} = {query_value}')
        return serialize_data(cursor, record) if serialize else record


@establish_db_connection
def get_table_length(cursor: sqlite3.Cursor, table_name: str):
    """
    Get the number of rows in a database table.

    Retrieves and returns the number of rows in a specified database table.

    :param cursor: The database cursor object.
    :param table_name: The name of the table to count rows from.
    :return: The number of rows in the specified table.
    """
    cursor.execute(f'SELECT COUNT(*) \
                     FROM {table_name}')
    logger.info(f'Retrieved table length for table {table_name}')
    return get_first_element_if_not_empty(cursor.fetchone())


@establish_db_connection
def get_users_ids(cursor: sqlite3.Cursor):
    """
    Get the IDs of all users in the database.

    Retrieves and returns the IDs of all users present in the database.

    :param cursor: The database cursor object.
    :return: A list of user IDs.
    """
    cursor.execute(f'SELECT id \
                     FROM {USERS_TN}')
    rows = cursor.fetchall()
    if rows:
        logger.info('Retrieved user IDs from database')
        return [row[0] for row in rows]


@establish_db_connection
def get_users_full_names_with_debts(cursor: sqlite3.Cursor):
    """
    Get the full names of users with negative account balances.

    Retrieves and returns the full names of users who have negative balances in their accounts.

    :param cursor: The database cursor object.
    :return: A list of full names for users with negative balances.
    """
    cursor.execute(f'SELECT {USERS_TN}.name, {USERS_TN}.surname \
                     FROM {USERS_TN} \
                     JOIN {ACCOUNTS_TN} ON {USERS_TN}.id = {ACCOUNTS_TN}.user_id \
                     WHERE {ACCOUNTS_TN}.amount < 0')
    users = cursor.fetchall()
    if users:
        logger.info('Retrieved full names of users with negative account balances')
        return [' '.join(user) for user in users]


@establish_db_connection
def get_biggest_capital_bank(cursor: sqlite3.Cursor):
    """
    Get the name of the bank with the largest total capital.

    Retrieves and returns the name of the bank with the largest total capital based on account balances.

    :param cursor: The database cursor object.
    :return: The name of the bank with the largest total capital.
    """
    cursor.execute(f'SELECT {BANKS_TN}.name \
                     FROM {BANKS_TN} \
                     JOIN {ACCOUNTS_TN} ON {BANKS_TN}.id = {ACCOUNTS_TN}.bank_id \
                     GROUP BY {BANKS_TN}.name \
                     ORDER BY SUM({ACCOUNTS_TN}.amount) DESC')
    logger.info('Retrieved bank with the largest total capital')
    return get_first_element_if_not_empty(cursor.fetchone())


@establish_db_connection
def get_bank_with_oldest_client(cursor: sqlite3.Cursor):
    """
    Get the name of the bank with the oldest client.

    Retrieves and returns the name of the bank with the oldest client based on client birthdates.

    :param cursor: The database cursor object.
    :return: The name of the bank with the oldest client.
    """
    cursor.execute(f'SELECT {BANKS_TN}.name \
                     FROM {BANKS_TN} \
                     JOIN {ACCOUNTS_TN} ON {BANKS_TN}.id = {ACCOUNTS_TN}.bank_id \
                     JOIN {USERS_TN} ON {ACCOUNTS_TN}.user_id = {USERS_TN}.id \
                     GROUP BY {BANKS_TN}.name \
                     ORDER BY MIN({USERS_TN}.birth_day)')
    logger.info('Retrieved bank with the oldest client')
    return get_first_element_if_not_empty(cursor.fetchone())


@establish_db_connection
def get_bank_with_most_unique_outbound_operations(cursor: sqlite3.Cursor):
    """
    Get the name of the bank with the most unique outbound operations.

    Retrieves and returns the name of the bank with the most unique outbound operations.

    :param cursor: The database cursor object.
    :return: The name of the bank with the most unique outbound operations.
    """
    cursor.execute(f'SELECT bank_sender_name \
                     FROM {TRANSACTIONS_TN} \
                     JOIN {ACCOUNTS_TN} ON {TRANSACTIONS_TN}.account_sender_id = {ACCOUNTS_TN}.id \
                     GROUP BY bank_sender_name \
                     ORDER BY COUNT(DISTINCT {ACCOUNTS_TN}.user_id) DESC')
    logger.info('Retrieved bank with the most unique outbound operations')
    return get_first_element_if_not_empty(cursor.fetchone())


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
    start_date = datetime.now() - timedelta(days=days)
    cursor.execute(f'SELECT * FROM {TRANSACTIONS_TN} \
                     WHERE account_sender_id = {user_id} \
                     {f"AND {TRANSACTIONS_TN}.datetime >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}'" if days else ""}')
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


def generate_discounts(user_amount: int):
    """
    Generate discounts for a specified number of users.

    Generates random discounts for a specified number of users and returns them as a dictionary.

    :param user_amount: The number of users for which discounts should be generated.
    :return: A dictionary mapping user IDs to their respective discounts.
    """
    users_ids = get_users_ids()

    random_user_ids = random.sample(users_ids, user_amount)
    logger.info(f'Generated discounts for {user_amount} users')
    return dict(zip(random_user_ids, [random.choice(AVAILABLE_DISCOUNTS) for _ in range(user_amount)]))


def rearrange_full_name(full_name: str):
    """
    Clean a full name by removing non-alphabetic characters and split a cleaned full name into first name and last name.

    :param full_name: The full name to be cleaned.
    :return: The cleaned and split full name.
    """
    if not full_name:
        logger.error('No full name provided')
        raise ValueError('No full name provided')

    cleaned_name = re.sub(r'[^a-zA-Z\s]', '', full_name)
    logger.info(f'Cleaned full name: {full_name} -> {cleaned_name}')

    splitted_full_name = tuple(re.split(r'\s+', cleaned_name.strip()))
    logger.info(f'Splitted full name: {cleaned_name} -> {splitted_full_name}')
    return splitted_full_name


def modify_users_data(users_data: list[dict]):
    """

    Modifies user data by cleaning and splitting the full name.

    :param users_data: List of user dictionaries to be modified.
    """

    return [{**user, 'name': full_name_parts[0], 'surname': full_name_parts[1]}
            for user in users_data
            if (full_name_parts := rearrange_full_name(user.pop('user_full_name')))]

