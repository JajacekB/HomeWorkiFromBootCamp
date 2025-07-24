from fleet_models_db import *
from fleet_database import Session, engine, SessionLocal
from sqlalchemy.exc import IntegrityError
import bcrypt

# Tworzenie tabel w bazie danych
Base.metadata.create_all(engine)
print("Baza danych i tabele zostały utworzone.")

session = Session()

# tworzenie konta Admin
existing_admin = session.query(User).filter_by(login="admin").first()

if not existing_admin:
    admin_user = User(
        first_name="Admin",
        last_name="",
        login="admin",
        phone=666555444,
        email="admin@system.local",
        password_hash=bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode(),
        role="admin",
        address=""
    )
    try:
        session.add(admin_user)
        session.commit()
        print("Użytkownik 'admin' został utworzony")
    except IntegrityError:
        session.rollback()
        print("Nie udało się utworzyć domyślnego admina (prawdopodobnie już istnieje).")
else:
    print("Urzytkownik 'admin' już istnieje.")



# Dodawanie promek jeśli nie ma jeszcze żadnych
with Session() as session:
    existing_promos = session.query(Promotion).count()
    if existing_promos == 0:
        promos = [
            Promotion(type="time", min_days=5, discount_percent=5, description="5% off za 5 dni"),
            Promotion(type="time", min_days=7, discount_percent=9, description="9% off za tydzień"),
            Promotion(type="time", min_days=14, discount_percent=20, description="20% off za 2 tygodnie"),
            Promotion(type="loyalty", min_days=0, discount_percent=100, description="Co 10. wypożyczenie gratis!")
        ]
        session.add_all(promos)
        session.commit()
        print("Promocje zostały dodane do bazy danych.")
    else:
        print("Promocje już istnieją w bazie – pominięto dodawanie.")

# Update promek
promotions_data = [
    {"id": 1, "description": "5% zniżki przy wynajmie na minimum 5 dni", "discount_percent": 5, "min_days": 5, "type": "time"},
    {"id": 2, "description": "9% zniżki przy wynajmie na minimum 7 dni", "discount_percent": 9, "min_days": 7, "type": "time"},
    {"id": 3, "description": "20% zniżki przy wynajmie na minimum 14 dni", "discount_percent": 20, "min_days": 14, "type": "time"},
    {"id": 4, "description": "Co 10. wypożyczenie – jedna doba gratis!", "discount_percent": 100, "min_days": 0, "type": "loyalty"}
]

with Session() as session:
    for promo in promotions_data:
        existing = session.query(Promotion).filter_by(id=promo["id"]).first()
        if existing:
            for key, value in promo.items():
                setattr(existing, key, value)
        else:
            session.add(Promotion(**promo))
    session.commit()

print("✅ Promocje zostały dodane lub zaktualizowane.")


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def add_workshop_users():
    session = SessionLocal()

    workshops = [
        {
            "login": "blacharz",
            "password": "blacharz",
            "first_name": "Blacharz",
            "last_name": "AutoSerwis",
            "phone": "600111222",
            "email": "blacharz.krakow@gmail.com",
            "address": "ul. Wadowicka 12, Kraków"
        },
        {
            "login": "mechanik",
            "password": "mechanik",
            "first_name": "Mechanik",
            "last_name": "AutoNaprawa",
            "phone": "600333444",
            "email": "mechanik.krakow@gmail.com",
            "address": "ul. Wrocławska 15, Kraków"
        }
    ]

    for w in workshops:
        existing_user = session.query(User).filter_by(login=w["login"]).first()
        if existing_user:
            print(f"Użytkownik {w['login']} już istnieje, pomijam.")
            continue

        hashed_password = hash_password(w["password"])

        user = User(
            role="workshop",
            first_name=w["first_name"],
            last_name=w["last_name"],
            login=w["login"],
            phone=w["phone"],
            email=w["email"],
            password_hash=hashed_password,
            address=w["address"]
        )
        session.add(user)

    session.commit()
    print("Dodano użytkowników warsztatu do bazy.")

if __name__ == "__main__":
    add_workshop_users()


session.close()