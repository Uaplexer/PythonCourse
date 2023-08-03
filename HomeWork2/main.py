import requests
import copy
import csv
from collections import Counter
from pprint import pprint
from datetime import datetime, timedelta


class MovieData:
    def __init__(self, pages):
        self.url = 'https://api.themoviedb.org/3/discover/movie'
        self.headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8'
        }
        self.data = []
        self.get_data_from_pages(pages)

    def get_response(self, number_of_pages):
        url = f'https://api.themoviedb.org/3/discover/movie'
        params = {
            'include_adult': False,
            'include_video': False,
            'sort_by': 'popularity.desc',
            'page': number_of_pages
        }
        return requests.get(url, headers=self.headers, params=params)

    def get_data_from_pages(self, num_of_pages):
        for i in range(1, num_of_pages + 1):
            response = self.get_response(i)
            self.data.extend(response.json()['results'])

    def get_multiple_pages(self):
        return self.data

    def get_genre_table(self):
        genre_url = 'https://api.themoviedb.org/3/genre/movie/list'
        response = (requests.get(genre_url, headers=self.headers)).json()
        return response

    def get_most_popular_title(self):
        most_popular_title = None
        max_popularity = 0
        for param in self.data:
            if param['popularity'] > max_popularity:
                max_popularity = param['popularity']
                most_popular_title = param['title']
        return most_popular_title

    def get_movie_data_with_indexes(self):
        return self.data[3:19:4]

    def get_response_with_params(self, search_params):
        lst = []
        for movie in self.data:
            if all(param.lower() in movie['overview'].lower() for param in search_params):
                lst.append(movie['title'])
        return lst

    def get_genres_id_by_names(self, genres):
        ids = []
        data = self.get_genre_table()
        for elem in data['genres']:
            if elem['name'] in genres:
                ids.append(elem['id'])
        return ids

    def get_genres_name_by_id(self, ids):
        genres = []
        data = self.get_genre_table()
        for genre_id in ids:
            for elem in data['genres']:
                if elem['id'] == genre_id:
                    genres.append(elem['name'])
        return genres

    def remove_movies_with_unwanted_genres(self, genres):
        genre_ids = self.get_genres_id_by_names(genres)
        new_results = []
        for elem in self.data:
            if not any(genre_id in elem['genre_ids'] for genre_id in genre_ids):
                new_results.append(elem)
        return new_results

    def get_genre_ids(self):
        all_genres_ids = []
        for genre in self.data:
            all_genres_ids.extend(genre['genre_ids'])
        return all_genres_ids

    def get_genre_collection(self):
        genre_name_list = []
        data = self.get_genre_table()
        if data['genres']:
            for name in data['genres']:
                genre_name_list.append(name['name'])
            return genre_name_list
        else:
            return None

    def get_most_common_genres(self):
        genres_id = self.get_genre_ids()
        genres = self.get_genres_name_by_id(genres_id)
        return Counter(genres)

    def genre_table_replace_first_id_with_22(self):
        genre_table_modified = self.get_genre_table()
        genre_table_initial = copy.deepcopy(genre_table_modified)
        if genre_table_modified['genres']:
            genre_table_modified['genres'][0]['id'] = 22
        else:
            return None
        print(f'Initial data: {genre_table_initial}')
        print(f'Modified data: {genre_table_modified}')

    def generate_collections_of_structures(self):
        new_data = []
        for param in self.data:
            parse_time = datetime.strptime(param['release_date'], '%Y-%m-%d')
            last_day = parse_time + timedelta(weeks=10, days=4)
            new_data.append({
                'Last_day_in_cinema': last_day.strftime('%Y-%m-%d'),
                'Score': round(param['vote_average']),
                'Popularity': f'{param["popularity"]:.1f}',
                'Title': param['title'],
            })
        sorted_new_data = sorted(new_data, key=lambda item: (item['Score'], float(item['Popularity'])),
                                 reverse=True)
        return sorted_new_data

    def write_collection_of_structures_to_csv(self, data):
        with open('data.csv', 'w', newline='') as file:
            fieldnames = ['Title', 'Score', 'Popularity', 'Last_day_in_cinema']
            csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
            csv_writer.writeheader()
            for row in data:
                csv_writer.writerow(row)
        return 'Success!'


list_with_genres = ['Action', 'History']
list_with_params = ['house']

print(f'Task 1: ')
movi = MovieData(5)

print(f'Task 2: {movi.get_multiple_pages()}')

print(f'Task 3: {movi.get_movie_data_with_indexes()}')

print(f'Task 4: {movi.get_most_popular_title()}')

print(f'Task 5: {movi.get_response_with_params(list_with_params)}')

print(f'Task 6: {movi.get_genre_collection()}')

print(f'Task 7: {movi.remove_movies_with_unwanted_genres(list_with_genres)}')

print(f'Task 8: {movi.get_most_common_genres()}')

print(f'Task 9: Not completed')

print(f'Task 10: ')
movi.genre_table_replace_first_id_with_22()

print(f'Task 11: {movi.generate_collections_of_structures()}')

print(f'Task 12: {movi.write_collection_of_structures_to_csv(movi.generate_collections_of_structures())}')
