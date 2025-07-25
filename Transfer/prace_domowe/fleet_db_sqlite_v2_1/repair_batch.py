from fleet_models_db import Vehicle, User, RentalHistory, RepairHistory, Car, Bike, Scooter, Invoice
from fleet_database import Session, SessionLocal
from fleet_utils_db import get_positive_int


# with Session() as session:
#     potential_wrong_invoice = session.query(Invoice).filter(
#         Invoice.invoice_number != None
#     ).all()
#
#     while True:
#         print(f"\nFaktury z potencjalnym błędem w bazie: ")
#         for i in potential_wrong_invoice:
#             print(
#                 f"Faktura:    "
#                 f"{i}"
#             )
#
#         id_input = get_positive_int("\nPodaj nr ID faktury, którą chcesz naprawić: ")
#         new_id = get_positive_int("\nPodaj nowy numer rental_id: ")
#
#         invoice = session.query(Invoice).filter(Invoice.id == id_input).first()
#
#         invoice.rental_id = new_id
#
#         session.add(invoice)
#         session.commit()
#         print("Operacja zakończona sukcesem")
#
#         if invoice.id == invoice.rental_id:
#             exit()


with Session() as session:

    potential_wrong_rent = session.query(RentalHistory).filter(
        RentalHistory.actual_return_date == None
    ).all()

    print(f"\nPojazdy z potencjalnym błędem w bazie: ")
    for rent in potential_wrong_rent:
        print(
            f"\nWynajmy:\n "
            f"{rent}"
        )

    id_input = get_positive_int("\nPodaj nr ID wynajmu, który chcesz naprawić: ")

    planed_return_date = session.query(RentalHistory.planned_return_date).filter(RentalHistory.id == id_input).scalar()
    wrong_rent = session.query(RentalHistory).filter(RentalHistory.id == id_input).first()

    wrong_rent.actual_return_date = planed_return_date

    session.add(wrong_rent)
    session.commit()




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


