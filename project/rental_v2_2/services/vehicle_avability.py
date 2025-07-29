# directory: services
# file: vehicle_availability.py

from datetime import date
from models.vehicle import Vehicle
from models.rental_history import RentalHistory
from models.repair_history import RepairHistory
from models.vehicle import Bike, Car, Scooter


def get_unavailable_vehicle(session, start_date = None, planned_return_date = None, vehicle_type = "all"):
    if start_date is None or planned_return_date is None:
        start_date = planned_return_date = date.today()

    query = session.query(Vehicle).filter(Vehicle.is_available != True)

    if vehicle_type != "all":
        query = query.filter(Vehicle.type == vehicle_type)

    potentially_unavailable = query.all()

    if not potentially_unavailable:
        return []

    candidate_ids = [v.id for v in potentially_unavailable]

    rented_vehicles = session.query(RentalHistory).filter(
        RentalHistory.vehicle_id.in_(candidate_ids),
        RentalHistory.start_date <= planned_return_date,
        RentalHistory.planned_return_date >= start_date
    ).all()
    rented_ids = [r.vehicle_id for r in rented_vehicles]


    repaired_today = session.query(RepairHistory).filter(
        RepairHistory.vehicle_id.in_(candidate_ids),
        RepairHistory.start_date <= planned_return_date,
        RepairHistory.planned_end_date >= start_date
    ).all()
    repaired_ids = [r.vehicle_id for r in repaired_today]

    unavailable_ids = list(set(rented_ids + repaired_ids))
    truly_unavailable = session.query(Vehicle).filter(Vehicle.id.in_(unavailable_ids)).all()

    return truly_unavailable, unavailable_ids

def get_available_vehicles(session, start_date=None, planned_return_date=None, vehicle_type="all"):
    _, unavailable_ids = get_unavailable_vehicle(session, start_date, planned_return_date, vehicle_type)

    filters = [
        ~Vehicle.id.in_(unavailable_ids)
    ]
    if vehicle_type != "all":
        filters.append(Vehicle.type == vehicle_type)

    vehicle_clas_map = {
        "all": Vehicle,
        "bike": Bike,
        "car": Car,
        "scooter": Scooter
    }
    model_class = vehicle_clas_map.get(vehicle_type, Vehicle)

    truly_available = session.query(model_class).filter(*filters).order_by(model_class.cash_per_day).all()
    return truly_available