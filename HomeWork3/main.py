import logging
import argparse as argp
import csv
from datetime import datetime, timedelta
import os
import requests
from shutil import move, rmtree, make_archive
from collections import Counter
from statistics import mean

URL = 'https://randomuser.me/api/?results=5000&format=csv'


def parse_args():
    parser = argp.ArgumentParser()
    parser.add_argument('log_level', type=str, help='Choose one of logging levels: INFO, WARNING, DEBUG')
    parser.add_argument('--filename', type=str, default='output', help='Name of data file')
    parser.add_argument('--path', type=str, required=True, help='Path to destination dir')
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('--gender', type=str, help='Sort users by gender')
    exclusive_group.add_argument('--num_of_rows', type=int, help='Numbers of total user rows')
    return parser.parse_args()


def set_logger(logging_level):
    logging.basicConfig(filename='log.txt',
                        level=logging_level.upper(),
                        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    return logging.getLogger('logger')


def read_csv_file(filename):
    with open(filename, 'r', newline='') as csvfile:
        return list(csv.DictReader(csvfile))


def download_csv_file(filename):
    with open(filename, 'w', newline='') as file:
        file.write((requests.get(URL)).text)
    logging.info('Successfully downloaded csv')


def get_working_path(path):
    return path if os.path.exists(path) else os.getcwd()


def filter_csv(csv_data, gender=None, num_of_rows=None):
    if gender:
        csv_data = list(filter(lambda x: x['gender'] == gender, csv_data))
        logger.info('Data was filtered by gender')
    elif num_of_rows and num_of_rows <= len(csv_data):
        csv_data = csv_data[:num_of_rows]
        logger.info('Data was filtered by number of rows')
    else:
        logger.warning('Data was not filtered by any of params')
    return csv_data


def current_time_implementation(location_timezone_offset):
    hours, minutes = map(int, location_timezone_offset.split(':'))
    return (datetime.utcnow() + timedelta(hours=hours, minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')


def name_title_implementation(name_title):
    match name_title:
        case 'Mrs':
            return 'missis'
        case 'Ms':
            return 'miss'
        case 'Mr':
            return 'mister'
        case 'Madame':
            return 'mademoiselle'
    return name_title


def convert_format(data, output_format):
    return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%fZ').strftime(output_format)


def add_and_change_fields_in_file(csv_data):
    for i, elem in enumerate(csv_data, start=1):
        elem['global_index'] = i
        elem['current_time'] = current_time_implementation(elem['location.timezone.offset'])
        elem['name.title'] = name_title_implementation(elem['name.title'])
        elem['dob.date'] = convert_format(elem['dob.date'], '%m/%d/%Y')
        elem['registered.date'] = convert_format(elem['registered.date'], '%m-%d-%Y, %H:%M:%S')
    logger.info('Successfully added and modified attributes')
    return csv_data


def move_file_to_destination_folder(path_to_dir, filename):
    move(os.path.join(os.getcwd(), filename), path_to_dir)
    logger.info('Successfully moved file to selected directory')


def rearrange_data(csv_data):
    new_data = {}
    for elem in csv_data:
        decade = f'{elem["dob.date"][-2]}0-th'
        country = elem['location.country']
        new_data.setdefault(decade, {})
        new_data[decade].setdefault(country, [])
        new_data[decade][country].append(elem)
    logger.info('Successfully rearranged data!')
    return new_data


def find_max_age(rearranged_csv, decade, country):
    return min([int(elem['dob.date'][-4:]) for elem in rearranged_csv[decade][country]])


def find_avg_registered(rearranged_csv, decade, country):
    return mean([int(elem['registered.date'][6:10]) for elem in rearranged_csv[decade][country]])


def find_most_common_name(rearranged_csv, decade, country):
    return Counter([elem['id.name'] for elem in rearranged_csv[decade][country]]).most_common(1)[0][0]


def get_file_name(rearranged_csv, decade, country):
    max_age = find_max_age(rearranged_csv, decade, country)
    avg_registered = find_avg_registered(rearranged_csv, decade, country)
    most_common_name = find_most_common_name(rearranged_csv, decade, country)
    return max_age, avg_registered, most_common_name


def write_to_csv(file_path, data):
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f'\t\t[F] {os.path.basename(file_path)}')


def write_users_data_to_different_files(rearranged_data, path):
    for decade, value in rearranged_data.items():
        logger.info(f'[D] {decade}:')
        for country, users in value.items():
            country_dir = os.path.join(path, decade, country)
            os.makedirs(country_dir, exist_ok=True)
            logger.info(f'\t[D] {country}:')

            max_age, avg_registered, most_common_name = get_file_name(rearranged_data, decade, country)
            file_name = f'{max_age}_{avg_registered:.0f}_{most_common_name}.csv'
            file_path = os.path.join(country_dir, file_name)
            write_to_csv(file_path, users)

    logger.info('Successfully wrote users data to local files')


def delete_decades_under_60(rearranged, path):
    for decade in rearranged.keys():
        if int(decade[:2]) < 60:
            rmtree(os.path.join(path, decade))
            logger.info(f'Successfully deleted {decade} decade')


def archive_dest_folder(path_to_folder):
    os.chdir(path_to_folder)
    make_archive(path_to_folder, 'zip')


# Task 3
args = parse_args()
work_path = get_working_path(args.path)
csv_filename = f'{args.filename}.csv'
# Task 1
logger = set_logger(args.log_level)
# Task 2
download_csv_file(csv_filename)
# Task 4
initial_csv_data = read_csv_file(csv_filename)
filtered = filter_csv(initial_csv_data, gender=args.gender, num_of_rows=args.num_of_rows)
# Task 5
modified_data = add_and_change_fields_in_file(filtered)
write_to_csv(os.path.join(os.getcwd(), csv_filename), modified_data)
# Task 6-7
move_file_to_destination_folder(args.path, csv_filename)
# Task 8
rearranged = rearrange_data(modified_data)
# Task 9-11,13
write_users_data_to_different_files(rearranged, work_path)
# Task 12
delete_decades_under_60(rearranged, work_path)
# Task 14
archive_dest_folder(work_path)
