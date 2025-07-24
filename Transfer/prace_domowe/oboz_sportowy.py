# Prosty system rejestracji uczniów do kursu (Obóz sportowy)
# Program zapisuje kandydatów na obóz do jednej z grup wiekowych (6-10, 11-14, 15_18)
# Sprawdza poprawność wprowadzonych danych i umożliwia przgląd uczestników oraz ich usunięcie.

from datetime import datetime
import re
import pickle
import os


class Student:
    def __init__(self, first_name, last_name, birthdate_str, email):
        """
        Inicjacja clasy Student:
        :param first_name: imię uczestnika
        :param last_name: nazwisko uczestnika
        :param birthdate_str: data urodzenia jako string
        :param email: email uczstnika
        """

        self.first_name = first_name
        self.last_name = last_name
        self.birthdate_str = birthdate_str
        self.birthdate_date = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        self.age = self.calculate_age()
        self.email = email
        self.group_name = self.determine_group()

    # Tworzenie f-string obiektu student
    def __str__(self):
        return f"{self.last_name}, {self.first_name}, {self.age} lat, {self.email}, [{self.group_name}]"

    # Obliczanie wieku uczestnika
    def calculate_age(self):
        today = datetime.now().date()
        years = today.year - self.birthdate_date.year

        if (today.month, today.day) < (self.birthdate_date.month, self.birthdate_date.day):
            years -= 1
        return years

    # Sprawdzanie formatu email, nie sprawdza domeny
    def validate_email(self):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        return re.match(pattern, self.email) is not None

    # Przypisanie do grupy wiekowej
    def determine_group(self):
        age = self.age
        if 6 <= age <=10:
            return "Kadeci"
        elif 11<= age <= 14:
            return "Juniorzy młodsi"
        elif 15<= age <= 18:
            return "Juniorzy"
        else:
            return "Poza zakresem"


class Group:
    def __init__(self, name, age_range, students=None, capacity=32):
        """
        Inicjacja klasy Group:
        :param name: Nazwa grupy wiekowej
        :param age_range: Zakres grupy wiekowej
        :param students: lista obiektów Student zapisanej do grupy
        :param capacity: Wiekość grupy wiekowej ustalone sztywno na 32
        """

        self.name = name
        self.age_range = age_range
        self.capacity = capacity
        self.students = students if students is not None else []

    # Tworzenie f-string obiektu grupa
    def __str__(self):
        return f"""{self.name}, 
        wiek: {self.age_range}, 
        zapisanych: {len(self.students)}, 
        wolnych miejsc: {self.capacity - len(self.students)}"""

    # Sprawdzanie wolnego miejsca w grupie wiekowej
    def free_space(self):
        return self.capacity - len(self.students)

    # Dodawanie uczestnika do grupy wiekowej
    def add_student(self, student):
        if self.free_space() > 0 and self.is_age_in_range(student):
            self.students.append(student)
            return True
        else:
            return False

    # przypisanie do grupy wiekowej
    def is_age_in_range(self, student):
        return self.age_range[0] <= student.age <= self.age_range[1]


# klasa sterująca
class Camp:
    def __init__(self):
        self.students = []
        self.groups = [
            Group("Kadeci", (6, 10)),
            Group("Juniorzy młodsi", (11, 14)),
            Group("Juniorzy", (15, 18))
        ]

    # Dodawanie studenta do uczestników obozu
    def add_student(self):
        first_name = input("\nPodaj imię uczestnika: ").strip().capitalize()
        last_name = input("\nPodaj nazwisko uczestnika: ").strip().capitalize()
        birthdate_str = input("\nPodaj datę urodenia w formacie YYYY-MM-DD: ").strip()
        email = input("\nPodaj email uczestnika lub opiekuna prawnego: ").strip()

        # sprawdzanie poprawności formatu daty
        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            print("\nNiepoprawny format daty. Użyj YYYY-MM-DD.")
            return False

        # validacja email
        temp_student = Student(first_name, last_name, birthdate_str, email)
        if not temp_student.validate_email():
            print("\nNiepoprawny adres email.")
            return False

        student = temp_student

        # Dodawanie uczestnika do grupy wiekowej
        for group in self.groups:
            if group.is_age_in_range(student) and group.free_space() > 0:
                group.add_student(student)
                self.students.append(student)
                print(f"\nUczestnik {student.first_name} {student.last_name} dodany do grupy: {group.name}")
                return True

        print(f"\n Nie znaloeziono grupy wiekowej albo brak wolnych miejsc.")
        return False

    # metoda: wyszukiwanie uczestnika po imieniu, nazwisku lub po obu.
    def find_student(self):
        search_first_name = input("\nPodaj imię uczestnika (Enter, jeśli nie znasz):  ").strip().casefold()
        search_last_name = input("\nPodaj nazwisko uczestnika (Enter, jeśli nie znasz): ").strip().casefold()

        if not search_first_name and not search_last_name:
            print("\nMusisz podać przynajmniej imię lub nazwisko.")
            return False

        matches = []

        for student in self.students:
            first = student.first_name.casefold()
            last = student.last_name.casefold()

            if search_first_name and search_last_name:
                if first == search_first_name and last == search_last_name:
                    matches.append(student)
            elif search_first_name:
                if first == search_first_name:
                    matches.append(student)
            elif search_last_name:
                if last == search_last_name:
                    matches.append(student)

        if not matches:
            print(f"\nNie znaleziono uczestnika {search_first_name} {search_last_name}.")
            return False

        print(f"\nZnaleziono następujących uczestników obozu:")
        for idx, student in enumerate(matches, 1):
            print(f"{idx}. {student}")

        return matches

    # Interaktywne menu usuwania uczestnika z wielokrotnym potwierdzeniem
    # aby ograniczyć przypadkowe usunięcie uczestnika.
    def remove_student_interactive(self, matches):

        confirm = input("Czy chcesz usunąć któregoś uczestnika? (Tak/Nie): ").strip().lower()
        if confirm in ["tak", "t", "yes", "y"]:
            try:
                index = int(input("\nPodaj numer uczestnika do usunięcia: ").strip())
                if 1 <= index <= len(matches):
                    final_confirmation = input(f"\nCzy na pewno chcesz usunąć: {matches[index -1]}? (Tak/Nie)").strip().lower()
                    if final_confirmation in ["tak", "t", "yes", "y"]:
                        self.remove_student(matches[index - 1])
                    elif final_confirmation in ["nie", "n", "no"]:
                        print("\nAnulowano usuwanie.")
                    else:
                        print("\nNie rozpoznano odpowiedzi. Spróbój ponownie.")
                    return True

                else:
                    print("Nieprawidłowy numer.")
            except ValueError:
                print("To nie jest poprawny numer")

        elif confirm in ["nie", "n", "no"]:
            print("\nAnulowano usuwanie.")
        else:
            print("\nNie rozpoznano odpowiedzi. Spróbuj ponownie.")
        return True

    # Usuwanie studenta z ogólnej listy uczestników i zwalnianie miejsca w grupie wiekowej
    def remove_student(self, student):
        if student in self.students:
            self.students.remove(student)

            for group in self.groups:
                if student in group.students:
                    group.students.remove(student)

            print(f"\nUczestnik {student.first_name} {student.last_name} usunięty z obozu.")
            return True
        else:
            print(f"\nNie znaleziono uczestnika {student.first_name} {student.last_name}.")
            return False

    # Wyświetlanie wszystkich uczestników obozu
    def total_student(self):

        sorted_students = sorted(self.students, key=lambda s: (s.last_name.lower(), s.first_name.lower()))

        if not sorted_students:
            print("\nBrak uczestników w obozie.")
            return

        print(f"\nZnaleziono następujących uczestników obozu:")
        for idx, student in enumerate(sorted_students, 1):
            print(f"{idx}. {student}")

    # Wyświetlanie grup wiekowych z przypisanymi do nich uczestnikami
    def grup_student(self):
        for group in self.groups:
            print("-" * 40)
            print('\n', group)

            sorted_students = sorted(group.students, key=lambda s: (s.last_name.lower(), s.first_name.lower()))

            for student in sorted_students:
                print("  -", student)

    # Zapisywanie do pliku
    def save_to_file(self, filename="sport_camp.pkl"):
        try:
            with open(filename, "wb") as f:
                pickle.dump(self, f)
            print(f"\nDane zapisano do pliku '{filename}'.")
        except Exception as e:
            print(f"\nBłąd podczas zapisu: {e}")

    # Wczytywanie z pliku
    def load_from_file(self, filename="sport_camp.pkl"):
        if not os.path.exists(filename):
            print(f"\nPlik '{filename}' nie istnieje. Rozpoczynam z pustą bazą.")

            return self

        try:
            with open(filename, "rb") as f:
                loaded = pickle.load(f)

            if not isinstance(loaded, Camp):
                print("\nBłąd: Nieprawidłowy typ danych w pliku.")
                return self

            print(f"\nWczytano dane z pliku '{filename}'.")
            return loaded

        except Exception as e:
            print(f"\nBłąd podczas wczytywania pliku: {e}.")
            return self


manager = Camp().load_from_file()

print("\nProgram '--CAMP--' służy do rejestracji uczestników na obóz sportowy.")

# Główna pentla logiczna programu
while True:

    print("""\nCo chcesz zrobić?
    1. Dodaj uczestnika obozu.
    2. Usuń uczestnika obozu.
    3. Wyszukaj uczestnika obozu.
    4. Przejrzyj wszystkich uczestników obozu
    5. Grupy wiekowe wraz z uczestnikami obozu.
    0. Zapisz i zamknij program.
    """)

    activity = input("\nWybierz opcję (0-5): ").strip().lower()

    match activity:
        case "1" | "d":
            manager.add_student()
            manager.save_to_file()

        case "2" | "u":
            matches = manager.find_student()
            if matches:
                manager.remove_student_interactive(matches)
                manager.save_to_file()

        case "3" | "w":
            manager.find_student()

        case "4" | "p":
            manager.total_student()

        case "5" | "g":
            manager.grup_student()

        case "0" | "z":
            manager.save_to_file()
            print("\nKoniec programu.")
            break

        case _:
            print("\nZły wybór!!!")

