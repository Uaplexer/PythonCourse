from re import sub, split
from sqlite3 import Cursor
from typing import Union, Optional

from HomeWork5.src.logger import setup_logger
from datetime import datetime
from HomeWork5.src.db_connection import establish_db_connection
from HomeWork5.src.consts import USERS_TN, BANKS_TN, VALID_DATETIME_PATTERN, FULL_NAME_CLEAR_REGEX

logger = setup_logger()


def serialize_data(cursor: Cursor, record_data: list) -> dict:
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
    return ', '.join([f'{key} = {val!r}' if isinstance(val, str) else f'{key} = {val}'
                      for key, val in data.items()])


def get_first_element_if_not_empty(collection):
    """
    Returns the first element of a collection if the collection is not empty.

    :param collection: The collection to check.

    :return: The first element of the collection if it is not empty, otherwise None.
    """
    return collection[0] if collection else None


def get_transaction_data(sender_account: dict, receiver_account: dict, amount: int, time=None):
    """
    Constructs a dictionary representing transaction data based on sender and receiver account information.

    :param sender_account: A dictionary representing sender account information.
    :param receiver_account: A dictionary representing receiver account information.
    :param amount: The amount of currency being sent in the transaction.
    :param time: A string representing the timestamp of the transaction.

    :return: A dictionary containing transaction data.
    """
    sender_bank_name = get_record(BANKS_TN, 'id', sender_account.get('bank_id')).get('name')
    receiver_bank_name = get_record(BANKS_TN, 'id', receiver_account.get('bank_id')).get('name')

    return {
        'bank_sender_name': sender_bank_name,
        'bank_receiver_name': receiver_bank_name,
        'account_sender_id': sender_account.get('id'),
        'account_receiver_id': receiver_account.get('id'),
        'sent_currency': sender_account.get('currency'),
        'sent_amount': amount,
        'datetime': time if time else datetime.now().strftime(VALID_DATETIME_PATTERN)
    }


@establish_db_connection
def get_table_columns_names(cursor: Cursor, table_name: str):
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
def get_record(cursor: Cursor, table_name: str, query_key: str, query_value: Union[str, int],
               cols: Optional[list[str]] = None,
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
def get_table_length(cursor: Cursor, table_name: str):
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
def get_users_ids(cursor: Cursor):
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


def rearrange_full_name(full_name: str):
    """
    Clean a full name by removing non-alphabetic characters and split a cleaned full name into first name and last name.

    :param full_name: The full name to be cleaned.
    :return: The cleaned and split full name.
    """
    if not full_name:
        logger.error('No full name provided')
        return None

    cleaned_name = sub(FULL_NAME_CLEAR_REGEX, '', full_name)
    logger.info(f'Cleaned full name: {full_name} -> {cleaned_name}')

    split_full_name = tuple(split(r'\s+', cleaned_name.strip()))
    logger.info(f'Split full name: {cleaned_name} -> {split_full_name}')
    return split_full_name


def modify_users_data(users_data: list[dict]):
    """
    Modifies user data by cleaning and splitting the full name.

    :param users_data: List of user dictionaries to be modified.
    """
    return [{**user, 'name': full_name_parts[0], 'surname': full_name_parts[1]}
            for user in users_data
            if (full_name_parts := rearrange_full_name(user.pop('full_name')))]
