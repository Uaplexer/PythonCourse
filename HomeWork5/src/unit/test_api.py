from unittest.mock import MagicMock, patch
import pytest
from HomeWork5.src.api import add_table_records, logger

@pytest.fixture
def cursor_mock():
    with patch('sqlite3.Cursor') as mock:
        yield mock.return_value

def test_add_single_record(cursor_mock):
    cursor_mock.executemany = MagicMock()

    table_name = 'table_name'
    data = {'name': 'x', 'surname': 'x', 'birth_day': 'x', 'accounts': 'x'}
    placeholders = ':name, :surname, :birth_day, :accounts'

    with patch.object(logger, 'info') as mock_info:
        add_table_records(table_name, data)

        cursor_mock.executemany.assert_called_once_with(
            f'INSERT INTO {table_name} (name, surname, birth_day, accounts) \
                    VALUES ({placeholders})', [data])

        mock_info.assert_called_once_with(f'{table_name.capitalize()} in table {table_name} added successfully')

if __name__ == '__main__':
    pytest.main()
