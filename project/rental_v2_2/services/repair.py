

from datetime import datetime, date, timedelta
from database.base import Session
from models.vehicle import Vehicle
from models.rental_history import RentalHistory
from models.repair_history import RepairHistory
from utils.iput_helpers import choice_menu, yes_or_not_menu
from services.utils import get_positive_int, get_positive_float
from services.vehicle_avability import get_available_vehicles, get_unavailable_vehicle
from services.database_update import update_database
from services.rental_process import recalculate_cost
from services.rental_swap import find_replacement_vehicle, update_database_after_vehicle_swap
from services.user_service import get_users_by_role
from services.id_generators import generate_repair_id




def repair_vehicle(session):

    # pobranie i wyświetlenie wszytskich pojazdów z podziałem na wynajęte i wolne
    rented_broken_vehs, _ = get_unavailable_vehicle(session)
    available_broken_vehs = get_available_vehicles(session)

    if not rented_broken_vehs:
        print("\n\n🚫 Brak niedostępnych pojazdów na dziś.")

    else:
        table_wide = 58
        print(
            f"\nPojazdy wynajęte:"
            f"\n|{'ID':>5}| {'Marka':<13}| {'Model':<13}| {'Nr w kartotece':<19}|"
        )
        print(table_wide * '-')
        for index, vehicle in enumerate(rented_broken_vehs, start=1):
            print(
                f"| {vehicle.id:>4}| {vehicle.brand:<13}| {vehicle.vehicle_model:13}| {vehicle.individual_id:<19}|"
            )
    if not available_broken_vehs:
        print("\n🚫 Brak dostępnych pojazdów na dziś.")

    else:
        table_wide = 58
        print(
            f"\nPojazdy bez wynajmu:"
            f"\n|{'ID':>5}| {'Marka':<13}| {'Model':<13}| {'Nr w kartotece':<19}|"
        )
        print(table_wide * '-')
        for index, vehicle in enumerate(available_broken_vehs, start=1):
            print(
                f"| {vehicle.id:>4}| {vehicle.brand:<13}| {vehicle.vehicle_model:13}| {vehicle.individual_id:<19}|"
            )

    # wybór niesprawnego pojazdu
    broken_veh_id = get_positive_int("\nPodaj id pojadu do naprawy: ")
    repair_days = get_positive_int(f"Podaj szacunkową ilość dni naprawy: ")

    today = date.today()
    planned_end_date = datetime.today().date() + timedelta(days=repair_days)

    broken_veh = session.query(Vehicle).filter(
        Vehicle.id == broken_veh_id
    ).first()
    if not broken_veh:
        print("❌ Nie znaleziono pojazdu o podanym ID.")
        return False
    #
    # if broken_veh.is_under_repair:
    #     print("ℹ️ Pojazd już znajduje się w naprawie.")
    #     return False

    # sprawdzenie czy pojazd ma aktywny najem
    broken_rent = session.query(RentalHistory).filter(
        RentalHistory.vehicle_id == broken_veh_id,
        today <= RentalHistory.planned_return_date,
        RentalHistory.start_date <= planned_end_date
    ).first()

    # jeśli brak najmu - oddanie do naprawy
    if not broken_rent:
        mark_as_under_repair(session, broken_veh, repair_days)
        print("🛠️  Pojazd został oznaczony jako w naprawie.")
        return True

    # jeśli pojazd został uszkodzony podczas najmu uruchomienie procedury wymiany pojazdu i rekalkulacji kosztów
    process_vehicle_swap_and_recalculate(session, broken_veh, broken_rent, repair_days)

    exit() # po zaimplementowaniu retur True


def process_vehicle_swap_and_recalculate(session, broken_veh, broken_rental, repair_days):
    choice = yes_or_not_menu("Czy klient będzie kontynuował wynajem?")
    if not choice:
        return finalize_rental_and_repair(session, broken_veh, broken_rental, repair_days)

    print("\nKlient kontynuuje najem pojazdu.")
    start_date = date.today()
    planned_return_date = broken_rental.planned_return_date

    replacement_vehicle_list = get_available_vehicles(session, start_date, planned_return_date, broken_veh.type)
    replacement_vehicle = next((v for v in replacement_vehicle_list if v.cash_per_day == broken_veh.cash_per_day), None)

    if replacement_vehicle:
        print(f"\nWydano klientowi pojazd zastępczy: {replacement_vehicle} \nOddano do naprawy: {broken_veh}")
        update_database_after_vehicle_swap(session, broken_veh, replacement_vehicle, broken_rental, False)
        mark_as_under_repair(session, broken_veh, repair_days)
        return True

    question = {
        "(D)": "Klient wybrał droższy pojazd jako zastępczy.",
        "(T)": "Klient wybrał tańszy pojazd jako zastępczy.",
        "(A)": "Klient jednak anuluje wynajem."
    }

    decision = choice_menu("Brak pojazdu w tej samej cenie. Czy klient decyduje się na zmianę na droższy lub tańszy?", question)

    if decision == "a":
        return finalize_rental_and_repair(session, broken_veh, broken_rental, repair_days)

    elif decision == "t":
        lower_price_vehicle = find_replacement_vehicle(session, broken_veh, planned_return_date, True)
        if lower_price_vehicle:
            print(f"\nWydano klientowi pojazd zastępczy: {lower_price_vehicle} \nOddano do naprawy: {broken_veh}")
            update_database_after_vehicle_swap(session, broken_veh, lower_price_vehicle, broken_rental, True)
            mark_as_under_repair(session, broken_veh, repair_days)
            return True
        else:
            higher_price_vehicle = find_replacement_vehicle(session, broken_veh, planned_return_date, False)
            print("\nBrak tańszego pojazdu. Wydano droższy bez naliczania dodatkowych kosztów.")
            if higher_price_vehicle:
                print(f"\nWydano klientowi pojazd zastępczy: {higher_price_vehicle} \nOddano do naprawy: {broken_veh}")
                update_database_after_vehicle_swap(session, broken_veh, higher_price_vehicle, broken_rental, False)
                mark_as_under_repair(session, broken_veh, repair_days)
                return True
            else:
                return finalize_rental_and_repair(session, broken_veh, broken_rental, repair_days)

    elif decision == "d":
        higher_price_vehicle = find_replacement_vehicle(session, broken_veh, planned_return_date, False)
        if higher_price_vehicle:
            print(f"\nWydano klientowi pojazd zastępczy: {higher_price_vehicle} \nOddano do naprawy: {broken_veh}")
            update_database_after_vehicle_swap(session, broken_veh, higher_price_vehicle, broken_rental, False)
            mark_as_under_repair(session, broken_veh, repair_days)
            return True
        else:
            alt_choice = yes_or_not_menu("Brak pojazdów o wyższym standardzie. Czy klient decyduje się na tańszy z rabatem?")
            if not alt_choice:
                return finalize_rental_and_repair(session, broken_veh, broken_rental, repair_days)
            else:
                lower_price_vehicle = find_replacement_vehicle(session, broken_veh, planned_return_date, True)
                if lower_price_vehicle:
                    print(f"\nWydano klientowi pojazd zastępczy: {lower_price_vehicle} \nOddano do naprawy: {broken_veh}")
                    update_database_after_vehicle_swap(session, broken_veh, lower_price_vehicle, broken_rental, True)
                    mark_as_under_repair(session, broken_veh, repair_days)
                    return True
                else:
                    return finalize_rental_and_repair(session, broken_veh, broken_rental, repair_days)

    return True  # na wszelki wypadek fallback


def finalize_rental_and_repair(session, broken_veh, broken_rental, repair_days):
    print("\nKlient kończy najem pojazdu.")
    broken_rental_total_cost, broken_rental_late_fee, _ = recalculate_cost(
        session, broken_veh.borrower, broken_veh, date.today(), broken_rental.reservation_id
    )
    print(f"\n💸 — KKW (Rzeczywisty Koszt Wynajmu) wynosi: {broken_rental_total_cost} zł"
        f" w tym {broken_rental_late_fee} zł za opóźnienie.")
    update_database(
        session, broken_veh, date.today(), broken_rental_total_cost,
        broken_rental_late_fee, broken_rental.reservation_id,
    )
    mark_as_under_repair(session, broken_veh, repair_days)
    return True


def mark_as_under_repair(session, vehicle, repair_days):
    workshops = get_users_by_role(session,"workshop")
    if not workshops:
        print("Brak zdefiniowanych użytkowników warsztatu.")
        return False

    print("\nDostępne warsztaty:")
    for idx, w in enumerate(workshops, 1):
        print(f"{idx}. {w.first_name} {w.last_name} ({w.login})")

    workshop_choice = get_positive_int("Wybierz numer warsztatu: ", max_value=len(workshops)) - 1
    selected_workshop = workshops[workshop_choice]

    planned_end_date = date.today() + timedelta(days=repair_days)

    repair_cost_per_day = get_positive_float("\nPodaj jednostkowy koszt naprawy: ")
    repair_cost = repair_cost_per_day * repair_days

    description = input("\nKrótko opisz zakres naprawy: ")

    repair_id = generate_repair_id()

    # Generowanie naprawy
    repair = RepairHistory(
        repair_id=repair_id,
        vehicle_id=vehicle.id,
        mechanic_id=selected_workshop.id,
        start_date=date.today(),
        planned_end_date=planned_end_date,
        actual_return_date=None,
        cost=repair_cost,
        description=description
    )
    session.add(repair)

    # Aktualizacja pojazdu
    vehicle.is_available = False
    vehicle.borrower_id = selected_workshop.id
    vehicle.return_date = planned_end_date

    session.commit()
    print(
        f"\nPojazd {vehicle.brand} {vehicle.vehicle_model} {vehicle.individual_id}"
        f"\nprzekazany do warsztatu: {selected_workshop.first_name} {selected_workshop.last_name} do dnia {planned_end_date}."
    )
    return True
