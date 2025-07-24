from fleet_models_db import Vehicle, User, RentalHistory, RepairHistory, Car, Bike, Scooter, Invoice
from fleet_database import Session, SessionLocal
from fleet_utils_db import get_positive_int







# with Session() as session:
#     potential_wrong_vehs = session.query(Vehicle).filter(
#         Vehicle.is_available != True,
#         Vehicle.return_date == None
#     ).all()
#
#     print(f"\nPojazdy z potencjalnym błędem w bazie: ")
#     for veh in potential_wrong_vehs:
#         print(
#             f"\nPojazdy:\n "
#             f"{veh}"
#         )
#
#     id_input = get_positive_int("\nPodaj nr ID pojazdu, który chcesz naprawić: ")
#
#     return_date = session.query(RentalHistory.planned_return_date).filter(RentalHistory.vehicle_id == id_input).scalar()
#     wrong_veh = session.query(Vehicle).filter(Vehicle.id == id_input).first()
#
#     wrong_veh.return_date = return_date
#
#     session.add(wrong_veh)
#     session.commit()


