import requests
from copy import deepcopy
import csv
from collections import Counter
from datetime import datetime, timedelta
from itertools import chain


class MovieData:
    FIELDNAMES = ['Title', 'Score', 'Popularity', 'Last_day_in_cinema']
    HEADERS = {
        'accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8'
    }
    BASE_PART = 'https://api.themoviedb.org/3/'

    def __init__(self, pages):
        self.url = f'{self.BASE_PART}discover/movie'
        self.genre_data = self.get_genre_table()
        self.data = []
        self.get_data_from_pages(pages)
        self.genre_table = self.get_genre_table_with_ids()

    def get_response(self, number_of_pages):
        params = {
            'include_adult': False,
            'include_video': False,
            'sort_by': 'popularity.desc',
            'page': number_of_pages
        }
        return requests.get(self.url, headers=self.HEADERS, params=params)

    def get_genre_table(self):
        genre_url = f'{self.BASE_PART}genre/movie/list'
        return (requests.get(genre_url, headers=self.HEADERS)).json()

    def get_data_from_pages(self, num_of_pages):
        for i in range(1, num_of_pages + 1):
            response = self.get_response(i)
            self.data.extend(response.json()['results'])

    def get_multiple_pages(self):
        return self.data

    def get_most_popular_title(self):
        return max(self.data, key=lambda movie: movie['popularity'])['title']

    def get_movie_data_with_indexes(self):
        return self.data[3:19:4]

    def search_films_by_keywords(self, keywords):
        return [movie['title'] for movie in self.data if
                all(param.lower() in movie['overview'].lower() for param in keywords)]

    def get_genres_name_by_id(self, ids):
        return [elem['name'] for elem in self.genre_data['genres'] for genre_id in ids if elem['id'] == genre_id]

    def get_genre_table_with_ids(self):
        return {genre['name']: genre['id'] for genre in self.genre_data['genres']}

    def get_genre_table_with_names(self):
        return {val: key for key, val in self.get_genre_table_with_ids().items()}

    def remove_movies_with_unwanted_genres(self, genres):
        return [elem for elem in self.data for genre in elem['genre_ids'] if
                self.get_genre_table_with_names()[genre] not in genres]

    def group_movies(self):
        return [(movie1['title'], movie2['title'])
                for i, movie1 in enumerate(self.data)
                for movie2 in self.data[i + 1:]
                if any(genre in movie2['genre_ids'] for genre in movie1['genre_ids'])]

    def get_genre_ids(self):
        return list(chain.from_iterable([genre['genre_ids'] for genre in self.data]))

    def get_genre_collection(self):
        return tuple(self.genre_table.keys())

    def get_most_common_genres(self):
        return dict(Counter(self.get_genres_name_by_id(self.get_genre_ids())))

    def get_genre_table_replaced_first_id_with_22(self):
        genre_table_modified = deepcopy(self.data)
        for movie in genre_table_modified:
            movie['genre_ids'][0] = 22
        return genre_table_modified, self.data

    @staticmethod
    def get_collection_params(movie):
        last_day = datetime.strptime(movie['release_date'], '%Y-%m-%d') + timedelta(weeks=10, days=4)
        return {
            'Title': movie['title'],
            'Score': round(movie['vote_average']),
            'Popularity': f'{movie["popularity"]:.1f}',
            'Last_day_in_cinema': last_day.strftime('%Y-%m-%d'),
        }

    def generate_collections_of_structures(self):
        return sorted(list(map(MovieData.get_collection_params, self.data)),
                      key=lambda item: (item['Score'], float(item['Popularity'])),
                      reverse=True)

    def write_collection_of_structures_to_csv(self, data):
        with open('data.csv', 'w', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            csv_writer.writeheader()
            csv_writer.writerows(data)


print(f'Task 1: ')
movi = MovieData(5)

print(f'Task 2: {movi.get_multiple_pages()}')

print(f'Task 3: {movi.get_movie_data_with_indexes()}')

print(f'Task 4: {movi.get_most_popular_title()}')

print(f'Task 5: {movi.search_films_by_keywords("house")}')

print(f'Task 6: {movi.get_genre_collection()}')

print(f'Task 7: {movi.remove_movies_with_unwanted_genres(["Action", "History", "Adventure"])}')

print(f'Task 8: {movi.get_most_common_genres()}')

print(f'Task 9: {movi.group_movies()}')

print(f'Task 10: {movi.get_genre_table_replaced_first_id_with_22()}')

print(f'Task 11: {movi.generate_collections_of_structures()}')

print(f'Task 12: {movi.write_collection_of_structures_to_csv(movi.generate_collections_of_structures())}')
