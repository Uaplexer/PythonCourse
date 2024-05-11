import sqlite3
from functools import wraps
from typing import Callable
from HomeWork5.src.globals import DB_NAME


def establish_db_connection(func: Callable) -> Callable:
    """
    Decorator for establishing a database connection and handling cursor management.

    :param func: The function to be decorated.
    :return: The decorated function with cursor.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        result = func(cursor, *args, **kwargs)

        conn.commit()
        conn.close()
        return result

    return wrapper
