from fleet_models_db import Vehicle, Car, Scooter, Bike, User, RentalHistory, RepairHistory, Invoice, Promotion
from sqlalchemy import func, cast, Integer, extract, and_, or_, exists, select
from sqlalchemy.exc import IntegrityError
from fleet_database import Session, SessionLocal
from datetime import date, datetime, timedelta
from collections import defaultdict
from fleet_manager_user import get_clients, get_users_by_role


with Session() as session:
    today = date.today()
    unavailable_vehs = session.query(Vehicle).filter(Vehicle.is_available == False).all()
    for v in unavailable_vehs:
        # print(v)
        print(v.id)

    unavailable_veh_ids = [veh.id for veh in unavailable_vehs]
    for veh_id in unavailable_veh_ids:
        print(veh_id)
        print(type(veh_id))

    rentals = session.query(RentalHistory).filter(
        and_(
            RentalHistory.vehicle_id.in_(unavailable_veh_ids),
            RentalHistory.start_date <= today,
            today <= RentalHistory.end_date)
    ).all()

    for rental in rentals:
        print(rental.vehicle_id)

    print(111 * "2")

    repaireds = session.query(RepairHistory).filter(
        and_(RepairHistory.vehicle_id.in_(unavailable_veh_ids),
            RepairHistory.start_date <= today,
            today <= RepairHistory.end_date)
    ).all()

    for repaired in repaireds:
        print(repaired.vehicle_id)

    print(111 * '#')

    unavailable_vehs = rentals + repaireds

    for unaval in unavailable_vehs:
        print(unaval.vehicle_id)





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