

from ui.menu_base import start_menu, LogoutException
from ui.menu_admin import menu_admin
from ui.menu_seller import menu_seller
from ui.menu_client import menu_client
from services.overdue_check import check_overdue_vehicles
from database.base import SessionLocal, Session
from config import DATABASE_URL

print("Ścieżka do bazy danych:", DATABASE_URL)



def main():
    while True:
        try:
            user = start_menu()
            if not user:
                continue

            with SessionLocal() as session:
                if user.role in ("seller", "admin"):
                    check_overdue_vehicles(session, user)

                menus = {
                    "client": menu_client,
                    "seller": menu_seller,
                    "admin": menu_admin
                }
                menu_function = menus.get(user.role)
                if menu_function:
                    menu_function(user, session)
                else:
                    print(f"❌ Nieznana rola użytkownika: {user.role}")
        except LogoutException:
            print("🔙 Powrót do menu startowego...")


if __name__ == "__main__":
    main()