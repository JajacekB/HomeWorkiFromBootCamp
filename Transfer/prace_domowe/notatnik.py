# Prosty notatnik z menu
#
# Stwórz aplikację konsolową, która umożliwia:
# 	•	dodawanie notatek (krótki tekst),
# 	•	usuwanie notatek (po numerze/id),
# 	•	edycję notatki,
# 	•	przeglądanie wszystkich notatek.
#
# Użyj pętli while True, prostej listy (lub słownika) oraz funkcji.

import os
import csv

print("\nProgram Notatnik służy do tworzenia i przechowywania prostych notatek.")

# Deklaracja zmiennych: notatki lista
notes = []

# Deklaracja STAŁYCH: plik csv
FILENAME = "notes.csv"

# Tworzenie pliku jesli nie istnieje
if not os.path.exists(FILENAME):
    with open(FILENAME, "w", newline='', encoding="utf-8") as file:
        fieldnames = ["title", "content"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

# Definiowanie funkcji

# Wczytywanie pliku notes.csv
def load_notes():
    with open(FILENAME, "r", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            notes.append(row)

# Zapisywanie pliku notes.csv
def save_notes():
    with open(FILENAME, "w", newline='', encoding="utf-8") as file:
        fieldnames = ["title", "content"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(notes)

# Dodawanie notatek
def add_note():
    title = input("\nTytuł notatki ").strip().capitalize()
    content = input("\nTreść notatki ").strip()
    note = {
        "title": title,
        "content": content
    }

    notes.append(note)
    save_notes()
    print("\nUdało się Cudownie, Wspaniele i Majestatycznie")

# Usuwanie notatek
def remove_note():

    try:
        del_number = int(input("\nPodaj numer notatki do usunięcia: ").strip())
        index = del_number -1
        if not 0 <= index < len(notes):
            print("\nZły wybór!!! Zastanów się lepiej.")
            return
    except ValueError:
        print("\nTo nie jest prawidłowa liczba!!! Postaraj się lepiej")
        return

    del notes[index]
    save_notes()
    print("\nUdało się Cudownie, Wspaniele i Majestatycznie")



# Edycji notatki
def edit_note():

    try:
        number_note = int(input("\nPodaj numer notatki do poprawy ").strip())
        index = number_note - 1
        if not 0 <= index < len(notes):
            print("Nieprawidłowy numer notatki. Postaraj się lepiej")
            return
    except ValueError:
        print("\nTo nie jest prawidłowa liczba!!! Postaraj się lepiej")
        return

    note = notes[index]
    print(f"\nEdytujesz:\nTytuł: {note['title']}\nTreść: {note['content']}")

    edit_title = input("\nNowa nazwa? (Enter, by nie zmieniać): ").strip().capitalize()
    edit_content = input("Nowa treść? (Enter, by nie zmieniać): ").strip()


    if edit_title:
        note["title"] = edit_title
    if edit_content:
        note["content"] = edit_content
    save_notes()
    print("\nUdało się Cudownie, Wspaniele i Majestatycznie")

# Wyświetlanie wszystkich notatek
def show_notes():
    print()
    if not notes:
        print("\nBrak notatek do wyświetlenia")

    else:

        for idx, note in enumerate(notes, start=1):
            print(f"{idx}.   {note['title']}:  {note['content']} ")

load_notes()

# Menu wyboru i głowny program
while True:
    print("""\nCo chcesz zrobić:
    1. Dodaj notatkę
    2. Usuń notatkę
    3. Edytuj notatkę
    4. Wyświetl wszystkie notatki
    5. KONIEC""")

    activiti = input("\nWybierz opcję (1-5): ")

    match activiti:
        case "1":
            add_note()

        case "2":
            show_notes()
            remove_note()

        case "3":
            show_notes()
            edit_note()

        case "4":
            show_notes()

        case "5":
            print("\nKoniec programu")
            break

        case _:
            print("\nZły wybór!!! Zastanów się lepiej.")