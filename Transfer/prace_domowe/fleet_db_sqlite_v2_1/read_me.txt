Program uruchamiamy plikiem fleet_main_db.py
program posiada trzy poziomy User
    1. admin konto stworzone tylko w poprzez plik init.py w zamierzeniu bez możliwości usunięcia
        login: admin
        hało admin
    2. sprzedawca tworzony tylko przez admina z domyślnym loginem i hasłem. może zmieniac tylko dane osobowe i hasło.
        Sprzedawca testowy:
        login: Seller03
        hasło: Seller03
    3. klient powstaje przez rejestrację zwykłago usera albo może być stworzony przez admin/seller
        kient testowy:
        login: tester
        hasło: Tester1


Każdy poziom usera ma inne menu.

Struktura:
fleet_main-db.py  - plik strtowy
fleet_menus_db.py  - docelowo wszystkie menu
fleet_manager_fleet.py - narzędzia służace do zarządzania pojazdmi
fleet_manager_user.py  - narzedzia zarządzające kontami urzytkowników
fleet_validation  - docelowo wszystkie narzedzia validujace
fleet_database.py  - plik tworzący tworzący session, engin i declarujacy Base
fleet_models_db.py  - plik z modelami Klas/Tabel
fleet_utisls_db.py  - funkcje pomocnicze
fleet_workbench.py  - warsztat gdzie powstają i są testowane nowe funkcje