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
    parser.add_argument('filename', type=str, default='output', help='Name of data file')
    parser.add_argument('log_level', type=str, help='Choose one of logging levels: INFO, WARNING, DEBUG')
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


def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_csv_file(filename):
    with open(filename, 'r', newline='') as csvfile:
        return list(csv.DictReader(csvfile))


def download_csv_file(filename):
    with open(filename, 'w', newline='') as file:
        file.write((requests.get(URL)).text)
    logging.info('Successfully downloaded csv')


def filter_csv(csv_data, gender=None, num_of_rows=None):
    if gender:
        csv_data = list(filter(lambda x: x['gender'] == gender, csv_data))
        logger.info('Data was filtered by gender')
    elif num_of_rows and num_of_rows <= len(csv_data):
        csv_data = csv_data[:num_of_rows]
        logger.info('Data was filtered by number of rows')
    else:
        logger.warning("Data wasn't filtered by any of params")
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


def add_and_change_fields_in_file(csv_data):
    for i, elem in enumerate(csv_data, start=1):
        elem['global_index'] = i
        elem['current_time'] = current_time_implementation(elem['location.timezone.offset'])
        elem['name.title'] = name_title_implementation(elem['name.title'])
        elem['dob.date'] = datetime.strptime(elem['dob.date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y')
        elem['registered.date'] = datetime.strptime(elem['registered.date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
            '%m-%d-%Y, %H:%M:%S')
    logger.info('Successfully added and modified attributes')
    return csv_data


def create_and_move_file_to_destination_folder(path_to_dir, filename):
    curr_path_folder = os.getcwd()
    if not os.path.exists(path_to_dir):
        logger.warning('Wrong path was entered in args!')
        os.makedirs("Users_data_folder", exist_ok=True)
        logger.info('Successfully created folder "Users_data_folder"')

        move(os.path.join(curr_path_folder, filename), f'{curr_path_folder}\\Users_data_folder')
        logger.info(f'Successfully moved file to default directory "{curr_path_folder}\\Users_data_folder"')
    else:
        os.makedirs(os.path.join(path_to_dir, 'Users_data_folder'), exist_ok=True)
        logger.info('Successfully created folder "Users_data_folder"')

        move(os.path.join(curr_path_folder, filename), path_to_dir)
        logger.info('Successfully moved initial file to selected directory')


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


def get_decades(csv_data):
    # ['00-th', '90-th', '80-th', '70-th', '60-th', '50-th', '40-th']
    return csv_data.keys()


def get_countries(rearranged_data, decade):
    decade_data = rearranged_data.get(decade, {})
    return list(decade_data.keys())


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


def create_file(file_path, file_name, data):
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f'\t\tSuccessfully created file {file_name}')


def write_users_data_to_different_files(rearranged_data, decades):
    curr_dir = f'{os.getcwd()}//Users_data_folder'

    for decade in decades:
        logger.info(f'Successfully joined folder {decade}')
        for country in get_countries(rearranged_data, decade):
            country_dir = os.path.join(curr_dir, decade, country)
            os.makedirs(country_dir, exist_ok=True)
            logger.info(f'\tSuccessfully joined folder {country}')
            max_age, avg_registered, most_common_name = get_file_name(rearranged_data, decade, country)
            file_name = f'{max_age}_{avg_registered:.0f}_{most_common_name}.csv'
            file_path = os.path.join(country_dir, file_name)
            create_file(file_path, file_name, rearranged_data[decade][country])
    logger.info('Successfully wrote users data to local files')
    os.chdir(curr_dir)


def delete_decades_under_60(decades):
    for decade in decades:
        if int(decade[:2]) < 60:
            rmtree(os.path.join(os.getcwd(), decade))
            logger.info(f'Successfully deleted {decade} decade')


def archive_dest_folder(path_to_folder):
    base_name = f'{path_to_folder}\\Users_data_folder' if os.path.exists(
        path_to_folder) else f'{os.getcwd()}'
    make_archive(base_name, 'zip')


# Task 3
args = parse_args()
csv_filename = f'{args.filename}.csv'
# if os.path.exists(args.path):
#     rmtree(args.path)
# Task 1
logger = set_logger(args.log_level)
# Task 2
download_csv_file(csv_filename)
# Task 4
initial_csv_data = read_csv_file(csv_filename)
filtered = filter_csv(initial_csv_data, gender=args.gender, num_of_rows=args.num_of_rows)
# Task 5
modified_data = add_and_change_fields_in_file(filtered)
write_to_csv(modified_data, csv_filename)
# Task 6-7
create_and_move_file_to_destination_folder(args.path, csv_filename)
# Task 8
rearranged = rearrange_data(modified_data)
decades = get_decades(rearranged)
# Task 9-11,13
write_users_data_to_different_files(rearranged, decades)
# Task 12
delete_decades_under_60(decades)
# Task 14
archive_dest_folder(args.path)
