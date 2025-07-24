# stworzyc system zarzadzania biblioteką klasa Book
# dodnie ksiazki, wypozyczenie ksiazki, zwracanie ksiązki
# obsłużyc błedy
# Dodac Library i usera

from datetime import datetime, timedelta
import pickle
import os

print("\nProgram Biblioteka do obsługi małej biblioteki miejskiej.")


class Book:
    def __init__(self, title, author, lib_num, available=True, borrower=None, return_date=None):
        """
        Inicjacja obiektu Book
        :param title: Tytuł książki
        :param author: Autor książki
        :param lib_num: Numer katalogowy
        :param available: Czy książka jest dostępna (domyslnie True)
        :param borrower: Kto wypożyczył książkę (domyslnie None)
        :param return_date: Do kiedy trzeba zwrócić książkę (domyślnie None może kiedyś automatycznie)
        :return:
        """

        self.title = title
        self.author = author
        self.lib_num = lib_num
        self.available = available
        self.borrower = borrower
        self.return_date = return_date

    def __str__(self):
        status = "Dostępna" if self.available else f"Wypożyczona przez: {self.borrower}, do {self.return_date}"
        return f"(Nr: {self.lib_num}) {self.title} - {self.author} [{status}]"


class User:
    def __init__(self, user_id, name, borrowed=None):
        """
        Inicjacja użytkownika bibiloteki
        :param user_id: Numer uzytkownika
        :param name: Imię i nazwisko
        :param borrowed: Lista wypożyczonych książek
        """

        self.user_id = user_id
        self.name = name
        self.borrowed = borrowed if borrowed is not None else []

    def __str__(self):
        if self.borrowed:
            books = ', '.join(book.title for book in self.borrowed)
        else:
            books = "Brak wypożyczonych książek."
        return f"(Nr: {self.user_id}). {self.name} [Wypożyczone: {books}]"


class Library:
    def __init__(self):
        """
        Inicjacja pustej Biblioteki
        """

        self.books = []
        self.users = []
        self.borrow_books =[]

    def add_book(self):
        prefix = "k"
        while True:
            title = input("\nPodaj tytuł książki: ").strip()
            author = input("Podaj autora książki: ").strip()

            max_num = 0
            for book in self.books:
                lib_num = book.lib_num.lower()
                if lib_num.startswith(prefix):
                    try:
                        number_part = int(lib_num[1:])
                        if number_part > max_num:
                            max_num = number_part
                    except ValueError:
                        pass

            next_num = max_num + 1
            suggested_lib_num = f"{prefix}{next_num:04d}"

            lib_num_input = input(f"Podaj numer katalogowy (domyślnie {suggested_lib_num}): ").strip().lower()
            lib_num = lib_num_input if lib_num_input else suggested_lib_num


            if any(book.lib_num == lib_num for book in self.books):
                print(f"\nKsiążka z numerem {lib_num} już istnieje. Spróbuj ponownie.")
                continue

            # Pokazanie podsumowania i pytanie o potwierdzenie
            print(f"\nCzy chcesz wprowadzić książkę: {title} - {author} [{lib_num}]? (Tak/Nie)")
            choice = input().strip().lower()
            if choice in ("tak", "t", "yes", "y"):
                book = Book(title, author, lib_num)
                self.books.append(book)
                print("\nOperacja dodawania książki zakończona sukcesem")
                break
            elif choice in ("nie", "n", "no"):
                print("\nWprowadzanie książki anulowane. Spróbuj jeszcze raz.")
                # pętla while True zacznie wprowadzanie od nowa
            else:
                print("\nNiepoprawna odpowiedź. Spróbuj ponownie.")

    def add_user(self):
        prefix = "u"

        while True:
            name = input("\nPodaj imię i nazwisko użytkownika: ").strip()

            # Znajdź najwyższy numer użytkownika z prefixem 'u'
            max_num = 0
            for user in self.users:
                user_id = user.user_id.lower()
                if user_id.startswith(prefix):
                    try:
                        number_part = int(user_id[1:])
                        if number_part > max_num:
                            max_num = number_part
                    except ValueError:
                        pass

            next_num = max_num + 1
            suggested_user_id = f"{prefix}{next_num:04d}"

            user_id_input = input(f"Podaj numer karty (domyślnie {suggested_user_id}): ").strip().lower()
            user_id = user_id_input if user_id_input else suggested_user_id

            # Sprawdzenie czy taki numer już istnieje
            if any(u.user_id == user_id for u in self.users):
                print(f"\nUżytkownik z numerem {user_id} już istnieje. Spróbuj ponownie.")
                continue

            # Pytanie o potwierdzenie
            print(f"\nCzy chcesz dodać użytkownika: {name} [{user_id}]? (Tak/Nie)")
            confirm = input().strip().lower()
            if confirm in ("tak", "t", "yes", "y"):
                user = User(user_id, name)
                self.users.append(user)
                print("\nUżytkownik został pomyślnie dodany.")
                break
            elif confirm in ("nie", "n", "no"):
                print("\nDodawanie użytkownika anulowane. Spróbuj jeszcze raz.")
                # wróci do początku pętli
            else:
                print("\nNiepoprawna odpowiedź. Spróbuj ponownie.")

        print("\nOperacja dodawania użytkownika zakończona sukcesem.")

    def borrow_book(self):
        user_id = input("\nPodaj numer karty uzytkownika: ").strip()
        lib_num = input("Podaj numer katalogowy książki: ").strip().lower()

        # wyszukiwanie użytkownika
        user = next((u for u in self.users if u.user_id == user_id), None)
        if user is None:
            print(f"\nUżutkownik {user_id} nie istnieje.")
            return

        # Wyszukiwanie książki
        book = next((b for b in self.books if b.lib_num == lib_num), None)
        if book is None:
            print(f"\nKsiążka z numerem {lib_num} nie istnieje.")
            return

        # Czy książka jest dostepna
        if not book.available:
            print(f"\nKsiążka '{book.title}' jest wypozyczona do {book.return_date}.")
            return

        # Czy użytkownik nie przekroczył limitu ksiązek
        if len(user.borrowed) >= 4:
            print(f"\n{user.name} nie może wypozyczyć więcej niż cztery ksiązki.")
            return

        # automat do ustawiania daty zwrotu.
        today = datetime.now()
        return_date = today + timedelta(weeks=4)
        return_date_str = return_date.strftime("%Y-%m-%d")

        # ustwaienie flag dla wypożyczonej ksiązki
        book.available = False
        book.borrower = user.name
        book.return_date = return_date_str

        # dodawanie książki użytkownikowi
        user.borrowed.append(book)

        print(f"\nKsiążka '{book.title}' została wypożyczona przez {user.name}. Termin zwrotu: {return_date_str}.")

    def return_book(self):
        lib_num = input("\nPodaj numer katalogowy książki: ").strip().lower()

        # Wyszukiwanie książki
        book = next((b for b in self.books if b.lib_num == lib_num), None)
        if book is None:
            print(f"\nnNie znaleziono książki o numerze {lib_num}.")
            return

        # Sprawdzanie czy książka jest wypozyczona
        if book.available:
            print(f"\nKsiążka '{book.title}' nie jest wypozyczona")
            return

        # Wyszukiwanie użytkownika
        user = next((u for u in self.users if u.name == book.borrower), None)
        if user is None:
            print(f"f\nNie znaleziono uzytkownika {book.borrower}.")
            return

        # Ustawienie flag dla zwróconej książki
        book.available = True
        book.borrower = None
        book.return_date = None

        # Usuwanie ksiązki użytkownikowi
        if book in user.borrowed:
            user.borrowed.remove(book)
        else:
            print(f"\nUwaga: użytkownik {user.name} nie ma tej książki na liście wypożyczeń.")

        print(f"\nKsiążka '{book.title}' o numerze katalogowym {lib_num} została zwrócona przez {user.name}.")

    def get_all_books(self):
        if not self.books:
            print("\nW bibliotece nie ma jeszcze książek.")
        else:
            print("\nLista książek:\n")
            for book in self.books:
                print(book)

    def get_available_books(self):
        print("\nLista dostępnych książek:\n")
        for book in self.books:
            if book.available:
                print(book)

    def get_borrowed_books(self):
        print()
        borrowed_books = [book for book in self.books if not book.available]

        if not borrowed_books:
            print("\nŻadna książka nie jest aktualnie wypożyczona.")
        else:
            print("\nLista wypożyczonych książek:\n")
            for book in borrowed_books:
                print(book)

    def find_book(self):
        title = input("\nPodaj poszukiwaną książkę: ").strip().casefold()
        book = next((b for b in self.books if b.title.casefold() == title), None)

        if book is None:
            print(f"\nNie znaleziono książki: '{title}'.")
            return
        else:
            print(f"\nZnaleziono książkę:\n{book}")

    def find_user(self):
        name = input("\nPodaj imię i nazwisko osoby: ").strip().casefold()
        user = next((u for u in self.users if u.name.casefold() == name), None)

        if user is None:
            print(f"\nNie znaleziono użytkownika: '{name}'.")
            return
        else:
            print(f"\nZnaleziono użytkownika :\n{user}")

    def get_all_users(self):
        if not self.users:
            print("\nNie ma jeszcze zarejstrowanych uzytkowników.")
        else:
            print("\nUrzytkownicy:")
            for user in self.users:
                print(user)

    def load_from_file(self, filename="library.pkl"):
        if not os.path.exists(filename):
            print(f"\nPlik '{filename}' nie istnieje. Tworzę pustą bibliotekę i zapisuję do pliku.")
            self.save_to_file(filename)
            return self

        try:
            with open(filename, "rb") as f:
                library = pickle.load(f)
            print(f"\nWczytano dane z pliku '{filename}'.")
            return library
        except Exception as e:
            print(f"\nBłąd podczas wczytywania pliku: {e}")
            return self

    def save_to_file(self, filename="library.pkl"):
        try:
            with open(filename, "wb") as f:
                pickle.dump(self, f)
            print(f"\nDane zapisano do pliku '{filename}'.")
        except Exception as e:
            print(f"\nBłąd podczas zapisu: {e}")


lib = Library()
library = lib.load_from_file()

while True:
    print("""\nCo chcesz zrobić?\n
    0. Zapisz i zakończ program.
    1. Dodać książkę.
    2. Dodać użytkownika.
    3. Wypożyczyć książkę.
    4. Zwrócić książkę.
    5. Wyświetlić wszystkie książki.
    6. Wyświetlić dostępne książki.
    7. Wyświetlić wypozyczone książki.
    8. Sprawdź czy biblioteka posiada tę książkę.
    9. Sprawdź czy użytkownik ma wypożyczone książki.
    10. Wyświetl wszystkich urzytkowników.
    """)

    activity = input("\nWybierz opcję (0-9): ").strip()

    match activity:

        case "1":
            library.add_book()
            library.save_to_file()

        case "2":
            library.add_user()
            library.save_to_file()

        case "3":
            library.get_available_books()
            library.borrow_book()
            library.save_to_file()

        case "4":
            library.get_borrowed_books()
            library.return_book()
            library.save_to_file()

        case "5":
            library.get_all_books()

        case "6":
            library.get_available_books()

        case "7":
            library.get_borrowed_books()

        case "8":
            library.find_book()

        case "9":
            library.find_user()

        case "10":
            library.get_all_users()

        case "0":
            library.save_to_file()
            print("\nKoniec programu.")
            break

        case _:
            print("\nZły wybór!!!")
