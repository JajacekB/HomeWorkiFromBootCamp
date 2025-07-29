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

Struktura: Osobny plik, na razie bez szczegółowych opisów
main-db.py  - plik strtowy

database.py  - plik tworzący tworzący session, engin i declarujacy Base
Katalog models  - pliki z modelami Klas/Tabel
