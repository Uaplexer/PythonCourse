import sqlite3
from unittest.mock import MagicMock, patch


def test_establish_db_connection(func):
    def wrapper(*args, **kwargs):
        cursor_mock = MagicMock(spec=sqlite3.Cursor)
        with patch('sqlite3.Cursor', return_value=cursor_mock):
            return func(cursor_mock, *args, **kwargs)
    return wrapper