import csv
import random
from collections import defaultdict


def get_airports_data(path_to_file):
    with open(path_to_file, 'r') as file:
        reader = csv.DictReader(file)
        data = list(reader)
    start_val = random.randint(0, len(data) - 15000)
    return data[start_val:start_val + 15000]


def get_each_airports_type(data):
    airports = defaultdict(list)
    for airport in data:
        airports[airport['type']].append(airport)
    return airports
