# directory: database
# file: seeds.py

import bcrypt
from database.base import SessionLocal
from models.user import User


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

# if __name__ == "__main__":
#     add_workshop_users()
#
#
# session.close()