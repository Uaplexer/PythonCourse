from main import name_title_implementation, convert_format, current_time_implementation, add_and_change_fields_in_file, \
    find_max_age, find_avg_registered, find_most_common_name
import unittest
from unittest.mock import patch


class NameTitleTest(unittest.TestCase):
    def test_name_title(self):
        self.assertEqual(name_title_implementation('Mrs'), 'missis')
        self.assertEqual(name_title_implementation('Ms'), 'miss')
        self.assertEqual(name_title_implementation('Mr'), 'mister')
        self.assertEqual(name_title_implementation('Madame'), 'mademoiselle')


def test_convert_format_valid():
    data = '2023-09-13T12:34:56.789Z'
    output_format = '%Y-%m-%d %H:%M:%S'
    expected_res = '2023-09-13 12:34:56'
    real_res = convert_format(data, output_format)
    assert real_res == expected_res


@patch('main.name_title_implementation')
@patch('main.convert_format')
@patch('main.current_time_implementation')
def test_add_and_change_fields_in_file(mock_current_time_implementation, mock_convert_format,
                                       mock_name_title_implementation):
    data = [
        {
            'location.timezone.offset': '+10:00',
            'name.title': 'Madame',
            'dob.date': '1992-04-13T09:54:31.217Z',
            'registered.date': '2011-01-30T22:17:23.560Z'
        }
    ]

    mock_name_title_implementation.return_value = 'mademoiselle'
    mock_convert_format.side_effect = ['04/13/1992', '01-30-2011, 22:17:23']
    mock_current_time_implementation.return_value = '2023-10-13 18:54:35'

    result = add_and_change_fields_in_file(data)

    expected_result = [
        {
            'global_index': 1,
            'location.timezone.offset': '+10:00',
            'name.title': 'mademoiselle',
            'dob.date': '04/13/1992',
            'registered.date': '01-30-2011, 22:17:23',
            'current_time': '2023-10-13 18:54:35'
        }
    ]

    assert result == expected_result


class TestFindFileNameComponents(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            '1980s':
                {
                    'USA':
                    [
                        {'dob.date': '04/03/1992', 'registered.date': '06/15/2010', 'id.name': 'John'},
                        {'dob.date': '07/11/1955', 'registered.date': '01/20/2000', 'id.name': 'Alice'},
                        {'dob.date': '01/04/1975', 'registered.date': '10/05/2005', 'id.name': 'John'}
                    ]
                }
        }

    def test_find_max_age(self):
        res = find_max_age(self.test_data, '1980s', 'USA')
        expected_result = 1955
        self.assertEqual(res, expected_result)

    def test_find_avg_registered(self):
        res = find_avg_registered(self.test_data, '1980s', 'USA')
        expected_result = 2005
        self.assertEqual(res, expected_result)

    def test_find_most_common_name(self):
        res = find_most_common_name(self.test_data, '1980s', 'USA')
        expected_result = 'John'
        self.assertEqual(res, expected_result)


if __name__ == '__main__':
    unittest.main()
