from docutils.parsers.rst.directives import choice

from fleet_models_db import Vehicle, Car, Scooter, Bike, User, RentalHistory, RepairHistory, Invoice, Promotion
from sqlalchemy import func, cast, Integer, extract, and_, or_, exists, select
from sqlalchemy.exc import IntegrityError
from fleet_database import Session, SessionLocal
from datetime import date, datetime, timedelta
from collections import defaultdict
from fleet_manager_user import get_clients, get_users_by_role
from fleet_utils_db import get_positive_int


def return_vehicle_production():
    # Pobieranie aktywnie wynajętych i zarejestrowanych pojazdów
    with Session() as session:

        unavailable_veh = session.query(Vehicle).filter(Vehicle.is_available != True).all()
        unavailable_veh_ids = [v.id for v in unavailable_veh]

        if not unavailable_veh:
            print("\nBrak wynajętych pojazdów")
            return

        # lista wynajętych pojazdów
        rented_vehs = session.query(RentalHistory).filter(
            RentalHistory.vehicle_id.in_(unavailable_veh_ids)
        ).order_by(RentalHistory.planned_return_date.asc()).all()

        rented_ids = [r.vehicle_id for r in rented_vehs]

        vehicles = session.query(Vehicle).filter(Vehicle.id.in_(rented_ids)).order_by(Vehicle.return_date).all()

        table_wide = 91
        month_pl = {
            1: "styczeń",
            2: "luty",
            3: "marzec",
            4: "kwiecień",
            5: "maj",
            6: "czerwiec",
            7: "lipiec",
            8: "sierpień",
            9: "wrzesień",
            10: "październik",
            11: "listopad",
            12: "grudzień"
        }

        veh_ids =[z.id for z in vehicles]
        print(f"\n[DEBUG] baza vehicles: {veh_ids}")
        print(f"\n[DEBUG] rented_ids: {rented_ids}")

        print(f"\nLista wynajętych pojazdów:\n")
        print(
            f"|{'ID.':>5}|{'Data zwrotu':>21} | {'Marka':^14} | {'Model':^14} |{'Nr rejestracyjny/seryjny':>25} |"
        )
        print(table_wide * "_")
        for p in vehicles:
            date_obj = p.return_date
            day = date_obj.day
            month_name = month_pl[date_obj.month]
            year = date_obj.year
            date_str = f"{day}-{month_name}_{year}"

            print(
                f"|{p.id:>4} |{date_str:>21} |{p.brand:>15} |{p.vehicle_model:>15} | {p.individual_id:>24} |"
            ) # po wyczyszczeniu tabeli vehicles z braku dat zmienić na vehicle


        # Wybór pojazdu do zwrotu i potwierdzenie chęci anulowania wynajmu lub rezerwacji
        choice = get_positive_int(
            f"\nKtóry pojazd chcesz zwrócić?"
            f"\nPodaj nr ID: "
        )

        vehicle = session.query(Vehicle).filter(Vehicle.id == choice).first()
        print(
            f"\nCzy na pewno chcesz zwrócić pojazd: "
            f"\n{vehicle}"
        )
        choice = input(
            f"Wybierz (tak/nie): "
        ).strip().lower()

        if choice in ("nie", "n", "no"):
            print("\nZwrot pojazdu anulowany.")
            return

        elif choice in ("tak", "t", "yes", "y"):
            actual_return_date_input = get_return_date_from_user(session)
            new_cost = recalculate_cost(session, vehicle, actual_return_date_input)

def get_return_date_from_user(session) -> date:
    while True:
        return_date_input_str = input(
            f"Podaj rzeczywistą datę zwrotu (DD-MM-YYYY) Enter = dziś: "
        ).strip().lower()

        try:

            if return_date_input_str:
                return_date_input = datetime.strptime(return_date_input_str, "%d-%m-%Y").date()
            else:
                return_date_input = date.today()
            break

        except ValueError:
            print("❌ Niepoprawny format daty.")
            continue
    return return_date_input

def recalculate_cost(session, vehicle: Vehicle, return_date: date):
    # Rozdzielenie przypadków; przed czasem, aktualny, przeterminowany
    planned_return_date = session.query(RentalHistory.planned_return_date).filter(
        RentalHistory.vehicle_id == vehicle.id
    ).order_by(RentalHistory.planned_return_date.desc()).scalar()

    print(f"\n[DEBUG] Planowana data zwroru: {planned_return_date}")

    if








return_vehicle_production()












# with Session() as session:
#     today = date.today()
#     unavailable_vehs = session.query(Vehicle).filter(Vehicle.is_available == False).all()
#     for v in unavailable_vehs:
#         # print(v)
#         print(v.id)
#
#     unavailable_veh_ids = [veh.id for veh in unavailable_vehs]
#     for veh_id in unavailable_veh_ids:
#         print(veh_id)
#         print(type(veh_id))
#
#     rentals = session.query(RentalHistory).filter(
#         and_(
#             RentalHistory.vehicle_id.in_(unavailable_veh_ids),
#             RentalHistory.start_date <= today,
#             today <= RentalHistory.end_date)
#     ).all()
#
#     for rental in rentals:
#         print(rental.vehicle_id)
#
#     print(111 * "2")
#
#     repaireds = session.query(RepairHistory).filter(
#         and_(RepairHistory.vehicle_id.in_(unavailable_veh_ids),
#             RepairHistory.start_date <= today,
#             today <= RepairHistory.end_date)
#     ).all()
#
#     for repaired in repaireds:
#         print(repaired.vehicle_id)
#
#     print(111 * '#')
#
#     unavailable_vehs = rentals + repaireds
#
#     for unaval in unavailable_vehs:
#         print(unaval.vehicle_id)





# #def rent_vehicle():
# print("\n>>> Przeglądanie pojazdów <<<")
# start_date_input_str = input(f"\nPodaj datę początku wynajmu w formacie YYYY-MM-DD: ").strip()
# end_time_input_str = input(f"Podaj datę końca wynajmu w formacie YYYY-MM-DD: ").strip()
# start_date_input = datetime.strptime(start_date_input_str, "%Y-%m-%d").date()
# end_time_input = datetime.strptime(end_time_input_str, "%Y-%m-%d").date()
#
# delta_input = end_time_input - start_date_input
#
# print(f"\nIlość dni: {delta_input.days}")
# print(type(delta_input))
#
# with Session() as session:
#     conflikt_condition_input = and_(
#         RentalHistory.start_date <= end_time_input,
#         RentalHistory.end_date >= start_date_input
#     )
#     conflicted_vehicle = session.query(RentalHistory.vehicle_id).filter(conflikt_condition_input).conflicted_vehicle()
#
#     available_vehicle = session.query(Vehicle).filter(
#         ~Vehicle.id.in_(conflicted_vehicle)
#     ).all()
#
#
#
#
#
#


# users = session.query(User).filter(User.role != "admin").all()
# for user in users:
#     print(user)
#
#
# def delete_user():
#     login_to_delete = input("Podaj login użytkownika do usunięcia: ").strip()
#     user = session.query(User).filter_by(login=login_to_delete).first()
#
#     if not user:
#         print("Nie znaleziono użytkownika.")
#         return
#
#     if user.role == "admin":
#         print("Nie można usunąć konta administratora systemowego.")
#         return
#
#     session.delete(user)
#     session.commit()
#     print(f"Użytkownik {login_to_delete} został usunięty.")


# from sqlalchemy.orm import Session
#
# with Session(engine) as session:
#     new_id = generate_vehicle_id(session, "CAR")
#     print(new_id)  # np. CAR001, CAR002 itd.
#
#     new_car = Car(vehicle_id=new_id, brand="Toyota", vehicle_model="Corolla",
#                   cash_per_day=150.0, size="M", fuel_type="petrol")
#
#     session.add(new_car)
#     session.commit()