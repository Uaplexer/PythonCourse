import requests
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from datetime import datetime


class WeatherMatPlot:
    def __init__(self):
        self.url = 'https://api.open-meteo.com/v1/'
        self.geolocator = Nominatim(user_agent='city_lookup')
        self.params = {}
        self.cities_data = {}

    def analyze_weather(self, cities: list, endpoint: str = 'forecast',
                        hourly: str | None = None, daily: str | None = None,
                        timezone: str = 'Europe/London', forecast_days: int | None = 6,
                        past_days: int | None = None) -> None:
        """
        Analyze weather data for a list of cities.

        Parameters:
        - cities (list): List of city names to analyze.
        - endpoint (str, optional): API endpoint for weather data. Default is 'forecast'.
        - hourly (str, optional): Hourly weather data to retrieve. Default is None.
        - daily (str, optional): Daily weather data to retrieve. Default is None.
        - timezone (str, optional): Timezone for data retrieval. Default is 'Europe/London'.
        - forecast_days (int, optional): Number of forecast days to retrieve. Default is 6.
        - past_days (int, optional): Number of past days to retrieve. Default is None.
        """
        self.params = {
            'forecast_days': forecast_days,
            'past_days': past_days,
            'hourly': hourly,
            'daily': daily,
            'timezone': timezone
        }

        for city_name in cities:
            location = self.geolocator.geocode(city_name)
            self.params['latitude'] = location.latitude
            self.params['longitude'] = location.longitude
            self.cities_data[city_name] = requests.get(f'{self.url}{endpoint}', params=self.params).json()

    @staticmethod
    def convert_format(inpt, input_format, conversion_format):
        """
        Convert a date from one format to another.

        Parameters:
        - inpt (str): Input date string.
        - input_format (str): Format of the input date.
        - conversion_format (str): Format for the converted date.

        Returns:
        - str: Date converted to the specified format.
        """
        return datetime.strptime(inpt, input_format).strftime(conversion_format)

    def plot_temperature_data(self, city_name: str):
        """
        Plot temperature data for a specific city.

        Parameters:
        - city_name (str): Name of the city to plot temperature data for.
        """
        temp_data: dict = self.cities_data.get(city_name)
        forecast_days: int = self.params['forecast_days']
        if temp_data is None:
            print(f'Data for {city_name} is not available.')
            return

        timestamps = np.arange(0.0416, forecast_days, 0.0416)
        daily_data: dict = temp_data.get('daily', {})
        hourly_data: dict = temp_data.get('hourly', {})
        temperatures_2m: list = hourly_data.get('temperature_2m', [])
        temperatures_max: list = daily_data.get('temperature_2m_max', [])
        temperatures_min: list = daily_data.get('temperature_2m_min', [])

        daily_temperatures: list = [temperatures_2m[i:i + 24] for i in range(0, len(temperatures_2m), 24)]
        daily_temperatures = [[temp if temp is not None else 0 for temp in day_temperatures] for day_temperatures in
                              daily_temperatures]
        average_daily_temperatures: list = [np.mean(daily) for daily in daily_temperatures]
        day_dates: list = [self.convert_format(date, '%Y-%m-%d', '%d %b') for date in daily_data.get('time', [])]

        daily_timestamps = np.arange(0, forecast_days)

        fig, ax = plt.subplots()
        ax.plot(timestamps, temperatures_2m, label='Hourly', linestyle='--')
        ax.plot(timestamps, np.interp(timestamps, daily_timestamps, temperatures_max), label='Max', marker='.',
                linestyle='-.', markevery=24,
                color='red')
        ax.plot(timestamps, np.interp(timestamps, daily_timestamps, temperatures_min), label='Min', marker='.',
                linestyle='-.', markevery=24,
                color='green')
        ax.plot(timestamps, np.interp(timestamps, daily_timestamps, average_daily_temperatures), label='Average',
                marker='.', markevery=24)

        if forecast_days > 8:
            ax.set_xticks(daily_timestamps[::2], day_dates[::2])
        else:
            ax.set_xticks(daily_timestamps, day_dates)

        ax.set_yticks(np.arange(0, 31, 5))
        ax.set_title(f'The weather in {city_name} for the next {self.params["forecast_days"]} days')
        ax.set_xlabel('Days')
        ax.set_ylabel('Temp(°C)')
        ax.grid(which='both', linestyle='--', color='gray', linewidth=0.4)
        ax.legend()
        plt.show()

    def plot_rain_data_multiple_cities(self, city_names: list[str]):
        """
        Plot rain data for multiple cities.

        Parameters:
        - city_names (list): List of city names to plot rain data for.
        """
        rain_sum: list = [self.cities_data[city].get('daily', {}).get('rain_sum', []) for city in city_names]
        rain_means: dict = {
            'Minimum': [min(values) for values in rain_sum],
            'Average': [round(np.mean(values), 2) for values in rain_sum],
            'Maximum': [max(values) for values in rain_sum]
        }
        width: float = 0.25
        multiplier: int = 0
        x = np.arange(len(city_names))
        fig, ax = plt.subplots(layout='constrained')
        for attr, measurement in rain_means.items():
            offset: float = width * multiplier
            rectangles = ax.bar(x + offset, measurement, width, label=attr)
            ax.bar_label(rectangles, padding=3)
            multiplier += 1
        ax.set_ylabel('Rain sums')
        ax.set_title(f'Rain sums for next {self.params["forecast_days"]} days')
        ax.set_xticks(x + width, city_names)
        ax.legend(loc='upper left', ncols=3)
        plt.show()

    @staticmethod
    def get_hourly_cloud_cover(cloud_data: dict, day: int):
        """
        Calculate hourly cloud cover for a specific day.

        Parameters:
        - cloud_data (dict): Hourly cloud cover data.
        - day (int): Day for which to calculate cloud cover.

        Returns:
        - list: List of cloud cover values for different cloud types.
        """
        return [sum(cloud_data.get(f'cloudcover_{cloud_type}', [0])[day * 24:(day + 1) * 24]) for cloud_type in
                ['low', 'mid', 'high']]

    def plot_cloud_cover_data(self, city_name: str):
        """
       Plot cloud cover data for a specific city.

       Parameters:
       - city_name (str): Name of the city to plot cloud cover data for.
        """
        cloud_data: dict = self.cities_data[city_name].get('hourly', {})
        days_count: int = self.params['forecast_days']

        fig, axs = plt.subplots(nrows=1, ncols=days_count, figsize=(18, 4))

        for day in range(days_count):
            hourly_cloud_cover: list = self.get_hourly_cloud_cover(cloud_data, day)
            axs[day].pie(hourly_cloud_cover, labels=['Low Cloud', 'Mid Cloud', 'High Cloud'], shadow=True,
                         autopct='%1.1f%%', startangle=30 * day,
                         explode=(0.1, 0, 0), colors=['#ff9999', '#66b3ff', '#99ff99'],
                         wedgeprops={'edgecolor': 'black'})
            axs[day].set_title(f'Day {day + 1}')

        fig.suptitle(f'Cloud Cover Data in {city_name} for next {days_count} days')
        plt.show()

    def plot_wind_speed_data(self, city_name: str):
        """
        Plot wind speed data for a specific city.

        Parameters:
        - city_name (str): Name of the city to plot wind speed data for.
        """
        wind_data: list = self.cities_data[city_name].get('hourly', {}).get('windspeed_10m')

        wind_data = [value for value in wind_data if value is not None]

        fig, ax = plt.subplots()

        ax.hist(wind_data, bins=8, color='skyblue', edgecolor='black')
        ax.set_xlabel('Wind Speed (m/s)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Wind Speed Distribution for next {self.params["forecast_days"]} days')
        plt.grid(True)
        plt.show()

    def get_data_for_scatter(self, city_name: str):
        """
        Get data for creating a scatter plot.

        Parameters:
        - city_name (str): Name of the city to retrieve data for.

        Returns:
        - tuple: Tuple of lists containing temperature, relative humidity, precipitation, cloud cover, and wind speed data.
        """
        if hourly := self.cities_data.get(city_name).get('hourly', {}):
            return hourly.get('temperature_2m', []), hourly.get('relativehumidity_2m', []), hourly.get('precipitation',
                                                                                                       []), hourly.get(
                'cloudcover', []), hourly.get('windspeed_10m', [])
        return [], [], [], [], []

    def plot_scatter_data(self, city_name: str):
        """
        Plot a scatter plot for weather data.

        Parameters:
        - city_name (str): Name of the city to plot the scatter plot for.
        """
        temperature_2m, rel_humidity, precipitation, cloud_cover, wind_speed_10m = self.get_data_for_scatter(city_name)

        fig, ax = plt.subplots()
        sc = ax.scatter(cloud_cover, temperature_2m, s=wind_speed_10m, c=rel_humidity, vmin=0, vmax=100)

        plt.colorbar(sc, label='Relative Humidity (%)')

        for i, precip in enumerate(precipitation):
            if precip > 0:
                ax.plot(cloud_cover[i], temperature_2m[i], marker='^', color='red', markersize=7)

        ax.set_xlabel('Cloud Cover')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title(f'Scatter Plot for {city_name} ({self.params["forecast_days"]} days)')

        plt.grid(True)
        plt.show()

    def plot_3d_scatter_data(self, city_name: str):
        """
        Plot a 3D scatter plot for weather data.

        Parameters:
        - city_name (str): Name of the city to plot the 3D scatter plot for.
        """
        temperature_2m, rel_humidity, precipitation, cloud_cover, wind_speed_10m = self.get_data_for_scatter(city_name)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        sc = ax.scatter(cloud_cover, temperature_2m, rel_humidity, s=wind_speed_10m, c=cloud_cover, cmap='viridis')

        for i, precip in enumerate(precipitation):
            if precip > 0:
                ax.plot(cloud_cover[i], temperature_2m[i], rel_humidity[i], marker='^', color='red', markersize=7)
        ax.set_xlabel('Cloud Cover')
        ax.set_ylabel('Temperature (°C)')
        ax.set_zlabel('Relative Humidity (%)')

        plt.colorbar(sc, label='Cloud Cover')

        ax.set_title(f'3D Scatter Plot for {city_name} ({self.params["forecast_days"]} days)')

        plt.show()


if __name__ == '__main__':
    my_city = WeatherMatPlot()

    cities = ['Kaub', 'Kyiv', 'Lviv', 'Zaporizhzhya']
    my_city.analyze_weather(cities, hourly='temperature_2m', daily='temperature_2m_max,temperature_2m_min',
                            forecast_days=16)

    my_city.plot_temperature_data(cities[-1])

    cities_rain = WeatherMatPlot()
    cities_rain.analyze_weather(cities, daily='rain_sum', forecast_days=7)
    cities_rain.plot_rain_data_multiple_cities(cities)

    cities_cloud = WeatherMatPlot()
    cities_cloud.analyze_weather(cities, hourly='cloudcover_low,cloudcover_mid,cloudcover_high', forecast_days=5)
    cities_cloud.plot_cloud_cover_data('Zaporizhzhya')

    cities_wind = WeatherMatPlot()
    cities_wind.analyze_weather(cities, hourly='windspeed_10m', forecast_days=16)
    cities_wind.plot_wind_speed_data('Zaporizhzhya')

    cities_scatter = WeatherMatPlot()
    cities_scatter.analyze_weather(cities,
                                   hourly='temperature_2m,relativehumidity_2m,precipitation,cloudcover,windspeed_10m',
                                   forecast_days=6)

    cities_scatter.plot_scatter_data('Zaporizhzhya')
    cities_scatter.plot_3d_scatter_data('Zaporizhzhya')
