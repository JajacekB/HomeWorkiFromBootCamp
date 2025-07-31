# directory: services
# file: vehicle_manamegment.py

from sqlalchemy.exc import IntegrityError
from models.vehicle import Bike, Car, Scooter, Vehicle
from utils.iput_helpers import choice_menu, yes_or_not_menu
from services.id_generators import generate_vehicle_id
from services.utils import get_positive_int, get_positive_float
from services.vehicle_avability import get_unavailable_vehicle, get_available_vehicles


def add_vehicles_batch(session):
    # Krok 1. Wybór typu pojazdu
    vehicle_type_map = {
        "samochód": "car",
        "skuter": "scooter",
        "rower": "bike"
    }
    type_prefix_map = {
        "samochód": "C",
        "skuter": "S",
        "rower": "B"
    }
    vehicle_type_input = choice_menu(
        "Jaki typ pojazdu chcesz dodać?",
        ["samochód", "skuter", "rower"]
    )
    vehicle_type = vehicle_type_map[vehicle_type_input]
    prefix = type_prefix_map[vehicle_type_input]
    count = get_positive_int("\nIle pojazdów chcesz dodać? ")

    # Krok 2.a Wprowadzenie wspólnych danych
    print("\n--- Dane wspólne dla całej serii ---")
    brand = input("Producent: ").strip().capitalize()
    model = input("Model: ").strip().capitalize()
    cash_per_day = get_positive_float("Cena za jedną dobę w zł: ")

    # Krok 2.b Wprowadzenie danych indywidualnych
    specific_fields = {}
    if vehicle_type == "car":
        specific_fields["size"] = input("Rozmiar (Miejski, Kompakt, Limuzyna, Crosover, SUV): ").strip().capitalize()
        specific_fields["fuel_type"] = input("Rodzaj paliwa (benzyna, diesel, hybryda, electric): ").strip()
    elif vehicle_type == "scooter":
        specific_fields["max_speed"] = get_positive_int("prędkość maksymalna (km/h): ")
    elif vehicle_type == "bike":
        specific_fields["bike_type"] = input("Typ roweru (MTB, Miejski, Szosowy): ").strip().capitalize()
        electric_input = input("Czy rower jest elektryczny (tak/nie): ").strip().lower()
        specific_fields["is_electric"] = electric_input in ("tak", "t", "yes", "y")

    # Krok 3. Tworzenie pojazdów
    vehicles = []
    for i in range(count):
        print(f"\n--- POJAZD #{i + 1} ---")
        vehicle_id = generate_vehicle_id(session, prefix)
        while True:
            individual_id = input(
                "Wpisz unikalny identyfikator pojazdu 😊\n"
                "➡ Dla samochodu i skutera będzie to numer rejestracyjny,\n"
                "➡ Dla roweru – numer seryjny (zazwyczaj znajdziesz go na ramie, okolice suportu):"
                "?  "
            ).strip()
            if any(v.individual_id == individual_id for v in vehicles):
                print("⚠️ Ten identyfikator już istnieje w tej serii. Podaj inny.")
            else:
                break

        if vehicle_type == "car":
            vehicle = Car(
                vehicle_id=vehicle_id,
                brand=brand,
                vehicle_model=model,
                cash_per_day=cash_per_day,
                size=specific_fields["size"],
                fuel_type=specific_fields["fuel_type"],
                individual_id=individual_id
            )
        elif vehicle_type == "scooter":
            vehicle = Scooter(
                vehicle_id=vehicle_id,
                brand=brand,
                vehicle_model=model,
                cash_per_day=cash_per_day,
                max_speed=specific_fields["max_speed"],

                individual_id=individual_id
            )
        elif vehicle_type == "bike":
            vehicle = Bike(
                vehicle_id=vehicle_id,
                brand=brand,
                vehicle_model=model,
                cash_per_day=cash_per_day,
                bike_type=specific_fields["bike_type"],
                is_electric=specific_fields["is_electric"],
                individual_id=individual_id
            )
        session.add(vehicle)
        session.flush()

        vehicles.append(vehicle)

    # Krok 4. Przegląd wpisanych pojazdów
    print("\n--- PRZEGLĄD POJAZDÓW ---")
    for i, v in enumerate(vehicles, 1):
        print(f"\n[{i}] {v}")

    # Krok 5. Czy wszystko się zgadza? Czy poprawić?

    answer = yes_or_not_menu(f"\nSprawdź uważnie czy wszystko się zgadza?")

    if answer:
        return

    option = input(
        f"\nWybierz sposób edycji:"
        f"\n👉 Numer pojazdu ➡ tylko ten jeden"
        f"\n👉 'Wszystko' ➡ zastosuj zmiany do wszystkich"
        f"\nPodaj odpowiedź: "
    ).strip().lower()
    if option == "wszystko":
        print("\n--- Popraw wspólne dane (ENTER = brak zmian) ---")
        new_brand = input(f"Producent ({brand}): ").strip()
        new_model = input(f"Model ({model}): ").strip()
        new_cash = input(f"Cena za dobę ({cash_per_day}): ").strip()
        if new_brand: brand = new_brand.capitalize()
        if new_model: model = new_model.capitalize()
        if new_cash:
            cash_per_day = get_positive_float("Nowa cena za dobę: ")

        if vehicle_type == "car":
            new_size = input(f"Rozmiar ({specific_fields['size']}): ").strip()
            new_fuel = input(f"Paliwo ({specific_fields['fuel_type']}): ").strip()
            if new_size: specific_fields['size'] = new_size.capitalize()
            if new_fuel: specific_fields['fuel_type'] = new_fuel

        elif vehicle_type == "scooter":
            new_speed = input(f"Prędkość maks. ({specific_fields['max_speed']}): ").strip()
            if new_speed:
                specific_fields["max_speed"] = get_positive_int("Nowa prędkość maksymalna: ")

        elif vehicle_type == "bike":
            new_type = input(f"Typ roweru ({specific_fields['bike_type']})").strip().capitalize()
            new_electric = input(f"Elektryczny ("
                                f"{'tak' if specific_fields['is_electric'] else 'nie'}): ").strip().lower()
            if new_type: specific_fields["bike_type"] = new_type.capitalize()
            if new_electric:
                specific_fields["is_electric"] = new_electric in ("tak", "t", "yes", "y")

        # Krok 6 Aktualizacja wszystkich w serii
        for v in vehicles:
            v.brand = brand
            v.vehicle_model = model
            v.cash_per_day = cash_per_day
            for k, val in specific_fields.items():
                setattr(v, k, val)
        print("✅ Dane wspólne zostały zaktualizowane.")
        return
    elif option.isdigit() and 1 <= int(option) <=len(vehicles):
        idx = int(option) - 1
        new_id = input("Nowy identyfikator: ").strip()
        if any(v.individual_id == new_id for i, v in enumerate(vehicles) if i != idx):
            print("❌ Taki identyfikator już istnieje.")
        else:
            vehicles[idx].individual_id = new_id
            print("✅ Zmieniono indywidualny identyfikator.")
            return
    else:
        print("🤔 Nie rozumiem, spróbuj jeszcze raz.")
        return

    # Krok 7 Zapis do bazy
    existing_ids = [v.individual_id for v in vehicles]
    if len(existing_ids) != len(set(existing_ids)):
        print("❌ Duplikat identyfikatorów indywidualnych w serii. Operacja przerwana.")
        return

    try:
        for v in vehicles:
            session.add(v)
        session.commit()
        session.flush()
        print(f"\n✅ Dodano {len(vehicles)} pojazdów do bazy.")
    except IntegrityError as e:
        session.rollback()
        print(f"\n❌ Błąd zapisu: {e}. Wszystkie zmiany zostały wycofane.")

def remove_vehicle(session):
    vehicle_id = input("\nPodaj numer referencyjny pojazdu, który chcesz usunąć: ").strip().upper()

    vehicle = session.query(Vehicle).filter_by(vehicle_id=vehicle_id).first()

    if not vehicle:
        print("❌ Nie znaleziono pojazdu.")
        return

    if not vehicle.is_available:
        print("🚫 Pojazd jest niedostępny. Nie można go usunąć")
        return

    choice = yes_or_not_menu(f"\nCzy chcesz usunąć pojad - {vehicle}")
    if choice:
        session.delete(vehicle)
        session.commit()
        print("\n✅ Pojazd został usunięty ze stanu wypożyczalni.")
        return

    print("\n❌ Usuwanie pojazdu anulowane.")
    return


def get_vehicle(session, only_available: bool = False):
    print("\n>>> Przeglądanie pojazdów <<<")

    if only_available:
        status = "available"
    else:
        status_options = {
            "w": "all",
            "d": "available",
            "n": "rented"
        }

        status_input = choice_menu(
            "\nKtóre pojazdy chcesz przejrzeć:",
    {
                "w": "Wszystkie",
                "d": "Dostępne",
                "n": "Niedostępne"
            }
        )

        status = status_options.get(status_input, "all")

    vehicle_type_options = {
        "w": "all",
        "s": "car",
        "k": "scooter",
        "r": "bike"
    }
    vehicle_type_input = choice_menu(
        "\nJakiego typu pojazdy chcesz zobaczyć:\n",
{
            "w": "Wszystkie",
            "s": "Samochód",
            "k": "Skuter",
            "r": "Rower"
        }
    )
    vehicle_type = vehicle_type_options.get(vehicle_type_input, "all")

    if status == "available":
        vehicles = get_available_vehicles(session, vehicle_type=vehicle_type)
        if not vehicles:
            print("\n🚫 Brak dostępnych pojazdów na dziś.")
            return

    elif status == "rented":
        vehicles, _ = get_unavailable_vehicle(session, vehicle_type=vehicle_type)
        if not vehicles:
            print("\n🚫 Brak niedostępnych pojazdów na dziś.")
            return

    else:
        vehicles = session.query(Vehicle).all()
        if not vehicles:
            print("🚫 Niestety brak pojazdów w ypożyczalni. Jesteśmy bankrutami. Komornik zają wszystkie pojazdy.")
            return

    # Przygotowujemy gotowe stringi WEWNĄTRZ sesji
    print("\n=== POJAZDY ===")

    current_type = None
    for vehicle in sorted(vehicles, key=lambda v: (v.type, v.vehicle_id)):
        if vehicle.type != current_type:
            current_type = vehicle.type
            print(f"\n--- {current_type.upper()} ---\n")
        print(vehicle)
