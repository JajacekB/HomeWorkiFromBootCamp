from fleet_manager import FleetManager

fleet = FleetManager.load_file()

print("\nProgram ---Fleet Manager Turbo--- służy do zarządzania małą wypożyczalnią pojazdów.")

while True:
    print("""\nMożesz zrobić takie czynności:
    0. Zakończyć program
    1. Dodać pojazd
    2. Usuń pojazd
    3. Wynajęcie pojazdu
    4. Zwrot pojazdu
    5. Wyświetlić wszystkie pojazdy
    6. Wyświetlić filtrowane pojazdy
    
    """)

    #  7. Wyszukiwanie pojazdu po ID
    #  8. Statystyki floty
    #  9. Export do JSON

    activity = input("\n Wybierz opcję (0-6): ")

    match activity:
        case "1":
            fleet.add_vehicle()
            fleet.save_file()

        case "2":
            fleet.remove_vehicle()
            fleet.save_file()

        case "3":
            fleet.borrow_vehicle()
            fleet.save_file()

        case "4":
            fleet.return_vehicle()
            fleet.save_file()


        case "5":
            fleet.get_all_vehicles()

        case "6":
            fleet.display_filtered_vehicles()

        case "0":
            fleet.save_file()
            print("\nKoniec programu.")
            break

        case _:
            print("\nZły wybór. Spróbuj jeszcze raz")


# if isinstance(user, Admin):
#     admin_menu()
# elif isinstance(user, Seller):
#     seller_menu()
# elif isinstance(user, Client):
#     client_menu()