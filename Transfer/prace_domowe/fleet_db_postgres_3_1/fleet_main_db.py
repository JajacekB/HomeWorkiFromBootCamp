from fleet_menus_db import start_menu, menu_client, menu_seller, menu_admin, LogoutException
from fleet_database import SessionLocal
from fleet_overdue_db import check_overdue_vehicles


def main():
    while True:
        try:
            user = start_menu()
            if not user:
                continue

            with SessionLocal() as session:
                if user.role in ("seller", "admin"):
                    check_overdue_vehicles(user, session)

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