import logging
import requests
import argparse as argp
import csv
from datetime import datetime, timedelta
import os
from shutil import move, rmtree, make_archive
from collections import Counter
from statistics import mean


def parse_args():
    parser = argp.ArgumentParser()
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('--gender', type=str, help='Sort users by gender')
    exclusive_group.add_argument('--num_of_rows', type=int, help='Numbers of total user rows')
    parser.add_argument('--path', type=str, help='Path to destination dir')
    parser.add_argument('--filename', type=str, default='output', help='Name of data file')
    parser.add_argument('--log_level', type=str, help='Choose one of logging levels:INFO,WARNING')
    return parser.parse_args()


def set_logger(logging_level):
    logging.basicConfig(filename='log.txt',
                        level=logging_level.upper(),
                        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    return logging.getLogger('my_logger')


num_of_results = 5000
URL = f'https://randomuser.me/api/?results={num_of_results}'


def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_csv_file():
    with open(EXACT_CSV_FILENAME, 'r', newline='') as csvfile:
        return list(csv.DictReader(csvfile))


def download_csv_file():
    url = f'https://randomuser.me/api/?results={num_of_results}&format=csv'
    with open(EXACT_CSV_FILENAME, 'w', newline='') as file:
        file.write((requests.get(url)).text)
    logging.info('Successfully downloaded csv')


def filter_csv(csv_data, gender=None, num_of_rows=None):
    filtered_data = []
    if gender:
        filtered_data = list(filter(lambda x: x['gender'] == gender, csv_data))
        logger.info('Data was filtered by gender')
    if num_of_rows and num_of_rows <= len(csv_data):
        filtered_data = csv_data[:num_of_rows]
        logger.info('Data was filtered by number of rows')
    else:
        logger.warning("Data wasn't filtered by any of params")
    return filtered_data


def current_time_implementation(location_timezone_offset):
    if location_timezone_offset == '0:00':
        return datetime.utcnow()
    else:
        hours, minutes = map(int, location_timezone_offset[1:].split(':'))
        sign = 1 if location_timezone_offset.startswith('+') else -1
        offset_timedelta = timedelta(hours=sign * hours, minutes=sign * minutes)
        return (datetime.utcnow() + offset_timedelta).strftime('%Y-%m-%d %H:%M:%S')


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


def add_and_change_fields_in_file(csv_data):
    for i, elem in enumerate(csv_data, start=1):
        elem['global_index'] = i
        elem['current_time'] = current_time_implementation(elem['location.timezone.offset'])
        elem['name.title'] = name_title_implementation(elem['name.title'])
        elem['dob.date'] = datetime.strptime(elem['dob.date'][:10], '%Y-%m-%d').strftime('%m/%d/%Y')
        elem['registered.date'] = datetime.strptime(elem['registered.date'][:19], '%Y-%m-%dT%H:%M:%S').strftime(
            '%m-%d-%Y, %H:%M:%S')
    logger.info('Successfully added and modified attributes')
    return csv_data


def create_and_move_file_to_destination_folder(path_to_dir=None):
    if not path_to_dir:
        logger.warning('No path was entered in args!')
        curr_path_folder = os.getcwd() + '\\'
        os.chdir('C:\\Program Files\\')
        logger.info('Successfully changed directory to C:\\Program Files\\')
        os.makedirs("Users data folder", exist_ok=True)
        logger.info('Successfully created folder "Users data folder"')
        os.chdir('C:\\Program Files\\Users data folder')
        logger.info('Successfully changed folder to "C:\\Program Files\\Users data folder"')
        move(curr_path_folder + EXACT_CSV_FILENAME, 'C:\\Program Files\\Users data folder')
        logger.info('Successfully moved file to default directory "C:\\Program Files\\Users data folder"')
        path_to_dir = 'C:\\Program Files\\Users data folder'
    else:
        move(os.getcwd() + '\\' + EXACT_CSV_FILENAME, path_to_dir)
        logger.info('Successfully moved initial file to selected directory')
        os.chdir(path_to_dir)
        os.makedirs("Users data folder", exist_ok=True)
        os.chdir(path_to_dir + '\\Users data folder')
    return path_to_dir


def rearrange_data(csv_data):
    new_data = {}
    for elem in csv_data:
        new_data.setdefault(f'{elem["dob.date"][-2]}0-th', {})
        new_data[f'{elem["dob.date"][-2]}0-th'].setdefault(elem['location.country'], [])
        new_data[f'{elem["dob.date"][-2]}0-th'][elem['location.country']].append(elem)
    logger.info('Successfully rearranged data!')
    return new_data


def get_decades(csv_data):
    return csv_data.keys()


def get_countries(csv_data):
    return set([elem['location.country'] for elem in csv_data])


def create_sub_folders_countries():
    curr_dir = os.getcwd()
    for i in DECADES:
        os.chdir(curr_dir)
        os.chdir(curr_dir + '\\' + i)
        for elem in COUNTRIES:
            os.makedirs(elem)
    logger.info('Successfully created sub folders with Countries')
    os.chdir(curr_dir)


def create_sub_folders_decades():
    for i in DECADES:
        os.makedirs(i)


def find_max_age(rearranged_csv, decade, country):
    return min([int(elem['dob.date'][6:]) for elem in rearranged_csv[decade][country]])


def find_avg_registered(rearranged_csv, decade, country):
    return mean([int(elem['registered.date'][6:10]) for elem in rearranged_csv[decade][country]])


def find_most_common_name(rearranged_csv, decade, country):
    return Counter([elem['id.name'] for elem in rearranged_csv[decade][country]]).most_common(1)[0][0]


def write_users_data_to_different_files(rearranged_data):
    curr_dir = os.getcwd()
    for decade in DECADES:
        decade_dir = os.path.join(curr_dir, decade)
        for country in COUNTRIES:
            country_dir = os.path.join(decade_dir, country)
            try:
                os.chdir(country_dir)
                max_age = find_max_age(rearranged_data, decade, country)
                avg_registered = find_avg_registered(rearranged_data, decade, country)
                most_common_name = find_most_common_name(rearranged_data, decade, country)
                with open(f'{max_age}_{avg_registered}_{most_common_name}.csv', 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=rearranged_data[decade][country][0].keys())
                    writer.writeheader()
                    for elem in rearranged_data[decade][country]:
                        writer.writerow(elem)
            except KeyError:
                logger.warning(f'No country {country} in {decade}')
    logger.info('Successfully wrote users data to local files')
    os.chdir(curr_dir)


def delete_decades_under_60():
    for decades in DECADES:
        if int(decades[:2]) < 60 and not 00:
            rmtree(os.getcwd() + '\\' + decades[:2] + '-th')
            logger.info(f'Successfully deleted {decades[:2] + "-th"} decade')


# This func is creating infinite zip
def archive_dest_folder(path_to_folder):
    if path_to_folder:
        return make_archive('users_data', 'zip', path_to_folder, 'Users data folder')
    else:
        return make_archive('users_data', 'zip', 'C:\\Program Files', 'Users data folder')


# Task 3
args = parse_args()
EXACT_CSV_FILENAME = args.filename + '.csv'

# Task 1
logger = set_logger(args.log_level)
# Task 2
download_csv_file()
# Task 4
initial_csv_data = read_csv_file()
filtered = filter_csv(initial_csv_data, gender=args.gender, num_of_rows=args.num_of_rows)
# Task 5
modified_data = add_and_change_fields_in_file(filtered)
write_to_csv(modified_data, EXACT_CSV_FILENAME)
# Task 6-7
create_and_move_file_to_destination_folder(args.path)
# Task 8
rearranged = rearrange_data(modified_data)
# Task 9
DECADES = get_decades(rearranged)
create_sub_folders_decades()
# Task 10
COUNTRIES = get_countries(initial_csv_data)
create_sub_folders_countries()
# Task 11
write_users_data_to_different_files(rearranged)
# Task 12
delete_decades_under_60()

# Task 14 (func is creating infinite zip)
archive_dest_folder(args.path)

# Task is not fully completed, i'll complete it fully in a few days!!!!
