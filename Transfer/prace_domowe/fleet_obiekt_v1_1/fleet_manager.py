from fleet_vehicle import Car, Scooter, Bike
import pickle
import os
from datetime import date, timedelta, datetime


class FleetManager():
    def __init__(self):
        self.vehicles = []

    def save_file(self, filename="fleet_manager.pkl"):
        try:
            with open(filename, "wb") as f:
                pickle.dump(self, f)
            print(f"\nDane zapisano do pliku '{filename}'.")
        except Exception as e:
            print(f"\nBłąd podczas zapisu: {e}")

    @staticmethod
    def load_file(filename="fleet_manager.pkl"):
        if not os.path.exists(filename):
            print(f"\nPlik '{filename}' nie istnieje. Rozpoczynam z pustą bazą.")
            return FleetManager()

        try:
            with open(filename, "rb") as f:
                loaded = pickle.load(f)

            if not isinstance(loaded, FleetManager):
                print("\nBłąd: Nieprawidłowy typ danych w pliku.")
                return FleetManager()

            print(f"\nWczytano dane z pliku '{filename}'.")
            return loaded

        except Exception as e:
            print(f"\nBłąd podczas wczytywania pliku: {e}.")
            return FleetManager()

    def generate_id(self,prefix):
        max_num = 0
        for vehicle in self.vehicles:
            vid = vehicle.vehicle_id.lower()
            if vid.startswith(prefix.lower()):
                try:
                    number_part = int(vid[len(prefix):])
                    if number_part > max_num:
                        max_num = number_part
                except ValueError:
                    pass

        next_num = max_num + 1
        return f"{prefix}{next_num:03d}"

    def add_vehicle(self):

        type_prefix_map = {
            "car": "C",
            "scooter": "S",
            "bike": "B"
        }

        while True:
            vehicle_type = input("\nPodaj typ pojazdu (car/scooter/bike): ").strip().lower()
            if vehicle_type in type_prefix_map:
                prefix = type_prefix_map[vehicle_type]
            else:
                print("\nNiepoprawny typ pojazdu, spróbuj jeszcze raz.")
                continue

            vehicle_id = self.generate_id(prefix)

            if vehicle_type == "car":

                brand = input("\nPodaj producenta pojazdu: ").strip().capitalize()
                cash_per_day = float(input("\nPodaj cenę najmu za jedną dobę: ").strip())
                size = input("\nPodaj rozmiar samochodu (Miejski, Kompakt, Limuzyna, CrossOver, SUV): ").strip().capitalize()
                fuel_type = input("\nPodaj rodzaj paliwa: ").strip()
                vehicle = Car(vehicle_id, brand, cash_per_day, True, size, fuel_type)

            elif vehicle_type == "scooter":

                brand = input("\nPodaj producenta pojazdu: ").strip().capitalize()
                cash_per_day = float(input("\nPodaj cenę najmu za jedną dobę: ").strip())
                max_speed = input("\npodaj prędkość maksymalną: ").strip()
                vehicle = Scooter(vehicle_id, brand, cash_per_day, True, max_speed)

            elif vehicle_type == "bike":

                brand = input("\nPodaj producenta pojazdu: ").strip().capitalize()
                cash_per_day = float(input("\nPodaj cenę najmu za jedną dobę: ").strip())
                bike_type = input("\nPodaj rodzaj typ roweru (Szosowy, Miejski, MTB): ").strip().capitalize()
                electric_input = input("\nCzy rower jest elektryczny: ").strip().lower()
                is_electric_bool = electric_input in ("tak", "t", "yes", "y")
                vehicle = Bike(vehicle_id, brand, cash_per_day, True, bike_type, is_electric_bool)

            print(f"\nCzy chcesz dodać pojazd? - {vehicle}")
            choice = input("(Tak/Nie): ").strip().lower()

            if choice in ("tak", "t", "yes", "y"):
                self.vehicles.append(vehicle)
                print("\nOperacja dodawania pojazdu zakończona sukcesem")
                break
            elif choice in ("nie", "n", "no"):
                print("\nWprowadzanie pojazdu anulowane. Spróbuj jeszcze raz.")
            else:
                print("\nNiepoprawna odpowiedź. Spróbuj ponownie.")

    def remove_vehicle(self):

        vehicle_id = input("\n Podaj numer referencyjny pojazdu, który chcesz usunąć: ").strip().capitalize()

        for vehicle in self.vehicles:
            if vehicle_id == vehicle.vehicle_id:
                if vehicle.is_available:
                    print(f"\nCzy chcesz usunąć pojad - {vehicle}")
                    choice = input("\n(Tak/Nie): ").strip().lower()
                    if choice in ("tak", "t", "yes", "y"):
                        self.vehicles.remove(vehicle)
                        print("\nPojazd został usunięty ze stanu wypożyczalni.")
                    elif choice in ("nie", "n", "no"):
                        print("\nUsuwanie pojazdu anulowane.")
                    else:
                        print("\nNiepoprawna odpowiedź. spróbuj ponownie.")
                else:
                    print("\nPojazd jest obecnie wypożyczony, nie można go usunąć.")
                return

        print("\nNie znaleziono pojazdu o podanym ID")

    def borrow_vehicle(self):
        type_map = {
            "car": Car,
            "scooter": Scooter,
            "bike": Bike
        }
        type_input = input("\nJaki typ pojazdu chcesz wypozyczyć (car, scooter, bike)? ").strip().lower()
        vehicle_class = type_map.get(type_input)

        if vehicle_class:
            available_vehicle = [v for v in self.vehicles if isinstance(v, vehicle_class) and v.is_available]

            if not available_vehicle:
                print("\nBrak dostępnych pojazdów.")
            else:
                print(f"\nDostępne {type_input}s:\n")
                for v in available_vehicle:
                    print(v)
            id_input = input("\nPodaj numer pojazdu, który chcesz wypozyczyć: ").strip().capitalize()
            borrowed_vehicle = next((b for b in available_vehicle if b.vehicle_id == id_input), None)
            if borrowed_vehicle is None:
                print("\nZły numer pojazdu. Spróbuj jeszcze raz.")
                return

            days_input = float(input(f"\nPodaj na ile dni chcesz wypożyczyć {type_input}: "))
            if days_input <= 0:
                print("\nZła ilość dni. Spróbuj jeszcze raz.")
                return

            today = datetime.now()
            return_date = today + timedelta(days=days_input)
            return_date_str = return_date.strftime("%Y-%m-%d")

            price = days_input * float(borrowed_vehicle.cash_per_day)
            print(f"""\n Czy chcesz wypozyczyć {borrowed_vehicle}
            na {days_input} dni za {price:.2f} zł?
            """)
            choice = input("\n(Tak/Nie)").strip().lower()
            if choice in ["nie", "n", "no"]:
                print(f"\nWypożyczenie {type_input} anulowano. ")
            elif choice in ["tak", "t", "yes", "y"]:

                borrowed_vehicle.is_available = False
                # borrowed_vehicle.vehicle_borrower = user.name
                borrowed_vehicle.return_date = return_date_str

                print(f"\nWypożyczenie {type_input} zrealizowane.")

        else:
            print("\nNiepoprawny typ pojazdu.")

    def return_vehicle(self):
        return_id = input("\nPodaj numer pojazdu, który chcesz zwrócić: ").strip().capitalize()

        returned_vehicle = next((b for b in self.vehicles if b.vehicle_id == return_id), None)

        if returned_vehicle is None:
            print(f"\nNie znaleziono pojazdu o numerze {return_id}.")
            return

        if returned_vehicle.is_available:
            print(f"\nPojazd '{returned_vehicle}' nie jest wypozyczony")
            return

        else:
            returned_vehicle.is_available = True
            # returned_vehicle.vehicle_borrower = None
            returned_vehicle.return_date = None
            print(f"\n {returned_vehicle.vehicle_id} został zwrócony.")
            return


    def get_all_vehicles(self):
        if not self.vehicles:
            print("\nNie ma jeszcze pojazdów w wypożyczalni.")
        else:
            car_list = []
            scooter_list = []
            bike_list = []
            print("\nLista pojazdów:\n")

            for vehicle in self.vehicles:
                if isinstance(vehicle, Car):
                    car_list.append(vehicle)

                elif isinstance(vehicle, Scooter):
                    scooter_list.append(vehicle)

                elif isinstance(vehicle, Bike):
                    bike_list.append(vehicle)

            print("Samochody")
            for v in car_list:
                print(v)

            print("Skutery:")
            for v in scooter_list:
                print(v)

            print("Rowery:")
            for v in bike_list:
                print(v)

    def get_available_vehicles(self, vehicle_type="all", sort_by="id"):
        return self.get_vehicles(status="available", vehicle_type=vehicle_type, sort_by=sort_by)

    def get_rented_vehicles(self, vehicle_type="all", sort_by="date"):
        return self.get_vehicles(status="rented", vehicle_type=vehicle_type, sort_by=sort_by)

    def get_vehicles(self, status="all", vehicle_type="all", sort_by=None, min_price=None, max_price=None):
        filtered = self.vehicles

        # Filtrowanie według dostępności
        if status == "available":
            filtered = [v for v in self.vehicles if v.is_available]
            sort_by = "id"  # automatycznie sortuj po ID
        elif status == "rented":
            filtered = [v for v in self.vehicles if not v.is_available]
            sort_by = "date"  # automatycznie sortuj po dacie zwrotu
        else:
            filtered = list(self.vehicles)
            if sort_by not in ("id", "date"):
                print("Niepoprawna opcja sortowania. Sortowanie domyślne (id).")
                sort_by = "id"

        # Filtrowanie według typu pojazdu
        if vehicle_type != "all":
            filtered = [v for v in filtered if v.get_type().lower() == vehicle_type.lower()]
        # Filtrowanie po cenie wynajmu
        if min_price is not None:
            filtered = [v for v in filtered if float(v.cash_per_day) >= min_price]
        if max_price is not None:
            filtered = [v for v in filtered if float(v.cash_per_day) <= max_price]

        # Sortowanie
        if sort_by == "date":
            filtered.sort(key=lambda v: v.return_date or date.max)
        elif sort_by == "id":
            filtered.sort(key=lambda v: v.vehicle_id)

        return filtered

    def display_filtered_vehicles(self):
        status = input("\nKtóre pojazdy chcesz przejrzeć (all, available, rented): ").strip().lower()

        # Informacja o automatycznym sortowaniu
        if status == "available":
            print("Sortowanie będzie ustawione automatycznie na 'id' (po ID pojazdu).")
            sort_by = "id"
        elif status == "rented":
            print("Sortowanie będzie ustawione automatycznie na 'date' (po dacie zwrotu).")
            sort_by = "date"
        else:
            print("Sortowanie domyślnie po ID pojazdu.")
            sort_by = "id"

        vehicle_type = input("Wpisz typ pojazdu (all, car, scooter, bike): ").strip().lower()

        min_price_input = input("Minimalna cena za dobę (ENTER aby pominąć): ").strip()
        max_price_input = input("Maksymalna cena za dobę (ENTER aby pominąć): ").strip()

        min_price = float(min_price_input) if min_price_input else None
        max_price = float(max_price_input) if max_price_input else None

        vehicles = self.get_vehicles(
            status=status,
            vehicle_type=vehicle_type,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price
        )

        if not vehicles:
            print("\nBrak pojazdów spełniających kryteria.")
        else:
            for v in vehicles:
                print(v)

    def get_all_clients(self):
        pass

    def get_active_clients(self):
        pass
