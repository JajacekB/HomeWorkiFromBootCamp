# stworzenie ksiazki telefonicznej z wykorzystanie petli while True
# dodaj kontakt, usun kontakt, wyszukaj kontakt, wyswietl kontakty

# importowanie bibliotek
import csv
import os

print("\nKontakty - ksiązka telefoniczna")


# Deklaracja zmiennych: lista kontaktów.
contacts = []

# Deklaracja STAŁYCH: nazwa pliku .csv
FILENAME = "contacts.scv"

# Tworzenie pliku .csv jeśli nie istnieje
if not os.path.exists(FILENAME):
    with open(FILENAME, "w", newline='', encoding="utf-8") as file:
        fieldnames = ["name", "last_name", "phone"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

# definiowanie funkcji:

# Wczytywanie zapisanych kontaktów z pliku .csv
def load_contacts():
    with open(FILENAME, "r", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            contacts.append(row)

# Zapisywanie nowych kontaktów do pliku .csv
def save_contacts():
    with open(FILENAME, "w", newline='', encoding="utf-8") as file:
        fieldnames = ["name", "last_name", "phone"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)

# Dodawanbie kontaktów
def add_contact():
    name = input("\nImię: ").strip().capitalize()
    last_name = input("Nazwisko: ").strip().capitalize()
    phone = input("telefon: ").strip().capitalize()

    contact = {
        "name": name,
        "last_name": last_name,
        "phone": phone
    }

    contacts.append(contact)
    save_contacts()
    print("\nOperacja zakończona sukcesem")

# Usuwanie kontaktów
def remove_contact():
    while True:

        # Menu wyboru
        print("""\nJak usunąć kontakt?
        1. Po osobie
        2. Po numerze telefonu
        3. Rezygnuję""")

        del_activity = input("\nKogo usnąć: ")

        match del_activity:
            case "1":
                del_name = input("\nPodaj imię kontaktu: ").strip().capitalize()
                del_last_name = input("Podaj nazwisko kontaktu: ").strip().capitalize()
                for contact in contacts:
                    if contact["name"] == del_name and contact["last_name"] == del_last_name:
                        contacts.remove(contact)
                        save_contacts()
                        print("\nOperacja zakończona sukcesem")
                        return

                print("\nNie ma tej osoby")

            case "2":
                del_phone = input("\nPodaj numer telefonu do usunięcia: ").strip()
                for contact in contacts:
                    if contact["phone"] == del_phone:
                        contacts.remove(contact)
                        save_contacts()
                        print("\nOperacja zakończona sukcesem")
                        return

                print("\nNie ma takiego numeru")

            case "3":
                return

            case _:
                print("\nBłędny wybór!!! Wybierz mądrze")

# Szukanie kontaktów
def find_contact():
    print("""\nWybierz jak chcesz szukać:
    1. Imię
    2. Nazwisko
    3. telefon""")

    choice = input("Wpisz cyfrę (1-3): ").strip()
    categories = {
        "1": ("name", "Imię"),
        "2": ("last_name", "Nazwisko"),
        "3": ("phone", "Telefon")
    }

    if choice not in categories:
        print("\nBłedny wybór!!! Wybierz mądrze.")
        return

    find_category, display_category = categories[choice]

    if find_category == "phone":
        find_person = input(f"\nPodaj {display_category}: ").strip()
    else:
        find_person = input(f"\nPodaj {display_category}: ").strip().capitalize()

    finded = False
    for contact in contacts:
        if contact.get(find_category, "").lower() == find_person.lower():
            print(f"\n{contact['name']} {contact['last_name']} - {contact['phone']}")
            finded = True

# Wyświetlanie listy kontaktów
def show_contacts():
    print()
    if not contacts:
        print("\nKontakty sa puste!!!")
    else:
        sorted_contacts = sorted(contacts, key=lambda c: c['name'].lower())
        for contact in sorted_contacts:
            print(f"{contact['name']} {contact['last_name']} - {contact['phone']}")
    print()

load_contacts()

# Menu wyboru działania w Kontaktach
while True:
    print("""\nCo chcesz zrobić?
    1. Dodaj kontakt
    2. Usuń kotakt
    3. Wyszukaj kontakt
    4. Wyświetl wszystkie kontakty
    5. KONIEC""")

    activity = input("\nWybierz opcje (1-5): ")

    match activity:
        case "1":
            add_contact()

        case "2":
            remove_contact()

        case "3":
            find_contact()

        case "4":
            show_contacts()

        case "5":
            print("\nKoniec programu")
            break

        case _:
            print("\nBłedny wybór!!! Wybierz mądrze.")
