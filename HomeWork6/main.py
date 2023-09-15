from datetime import datetime
import json
import my_csv


class DispatcherSystem:
    _instance = None

    def __init__(self):
        self.airports_data = my_csv.get_each_airports_type(my_csv.get_airports_data('airports_.csv'))
        self.current_time = datetime.utcnow()
        with open('airport_desc.json', 'r') as file:
            self.airport_desc = json.load(file)
        self.airport_classes = {
            'small_airport': SmallAirport,
            'medium_airport': MediumAirport,
            'large_airport': LargeAirport,
            'heliport': Heliport,
            'seaplane_base': SeaPlaneBase,
        }
        self.airports = []
        self.current_time = datetime.utcnow()

    def get_airport_list(self, airport_type):
        return self.airports_data.get(airport_type, [])

    def describe_aircraft(self, aircraft_id):
        pass

    def describe_passenger(self, passenger_id):
        pass

    def describe_airport(self, airport_id):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DispatcherSystem, cls).__new__(cls)
        return cls._instance

    def change_time(self, timedelta):
        self.current_time += timedelta
        return self.current_time

    def initial_setup(self):
        airport_classes = ['small_airport', 'medium_airport', 'large_airport', 'heliport', 'seaplane_base']
        self.airports = [self.create_type(port) for port in airport_classes for _ in range(20)]

    def create_type(self, airport_type):
        airports_list = self.get_airport_list(airport_type)
        if not airports_list:
            raise IndexError(f"No more {airport_type} airports available.")
        airport_desc = self.airport_desc[airport_type]
        airport_data = airports_list.pop()
        return self.airport_classes[airport_type](airport_data, airport_desc)

    def show_situation(self):
        pass


class Airport:
    def __init__(self, data, type_desc):
        self.data = data
        self.hangars = []
        self.coordinates = [self.data['latitude_deg'], self.data['longitude_deg']]
        self.id = f'{self.data["id"]}{self.data["ident"]}'
        self.name = self.data['name']
        self.airport_type_description = type_desc

    def show_airport_type_desc(self):
        print(self.airport_type_description)


class SmallAirport(Airport):
    pass


class MediumAirport(Airport):
    pass


class LargeAirport(Airport):
    pass


class Heliport(Airport):
    pass


class SeaPlaneBase(Airport):
    pass


class Aircraft:
    def __init__(self):
        pass


class Jet(Aircraft):
    pass


class TurboPropAirCraft(Aircraft):
    pass


class PistonAircraft(Aircraft):
    pass


class WideBodyPlane(Aircraft):
    pass


class NarrowBodyPlane(Aircraft):
    pass


class Cargo(Aircraft):
    pass


class MaritimePatrol(Aircraft):
    pass


class WaterPlane(Aircraft):
    pass


class Helicopter(Aircraft):
    pass


class Fighter(Aircraft):
    pass


class CombatTransport(Aircraft):
    pass


def main():
    dissys = DispatcherSystem()
    dissys.initial_setup()
    print(dissys.airports[21].data)


if __name__ == "__main__":
    main()
