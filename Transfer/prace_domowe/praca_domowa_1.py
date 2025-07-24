# zadanie 1. Stwórz Listę
# Stwórz listę zawierającą pięć różnych owoców.

owoce = []
owoce.append("jabłko")
owoce.append("śliwka")
owoce.append("truskawka")
owoce.append("arbuz")
owoce.append("gruszka")

print(owoce)
print(type(owoce))
print(sorted(owoce))
print("")

# zadanie 2. Znajdź Drugi Element Listy
# Mając listę, znajdź drugi element listy.
print(owoce)
print(owoce[1])
print("")

# zadanie 3. Zmień Element w Liście
# Zmień trzeci element listy na "malina".
owoce[2] = "malina"
print(owoce)
print("")

# zadanie 4. Stwórz Krotkę
# Stwórz krotkę zawierającą trzy różne kolory.
kolory = ("żółty", "zielony", "biały")
print(kolory)
print(type(kolory))
print("")

# zadanie 5. Wybierz Ostatni Element Krotki
# Mając krotkę, wybierz jej ostatni element.
print(kolory)
print(kolory[-1])
print()

# zadanie 8. Stwórz String Zawierający Twoje Imię i Nazwisko
# Stwórz string "Jan Kowalski".
osoba = "Jacek Baran"
print(osoba)
print(type(osoba))
print()

# zadanie 9.  Podziel String na Imię i Nazwisko
# Podziel powyższy string na dwa osobne stringi: imię i nazwisko.
imie = osoba.removesuffix("Baran").strip()
nazwisko = osoba.removeprefix("Jacek").strip()
print(osoba)
print(imie)
print(nazwisko)
print()

# zadanie 10. Użyj F-stringa do Połączenia Tekstu
# Stwórz string "Mam na imię Jan i mam 25 lat" używając f-stringa.
imie = "Jacek"
wiek = 54
print(f"Mam na imię {imie} i mam {wiek} lat(a).")
print()

print(111 * "+")
print("Drugi_zestaw")
print(111 * "+")
print()

# zadanie 1. Zadanie: Znajdź Długość Listy
# Mając listę [1, 2, 3, 4, 5], znajdź jej długość.
cyfry = [1, 2, 3, 4, 5]
print(cyfry)
dlugosc = len(cyfry)
print(f'Dlugość listy to {dlugosc} cyfr.')
print()

# zadanie 2. Zadanie: Połącz Dwie Listy
# Mając dwie listy, na przykład [1, 2, 3] i [4, 5, 6], połącz je w jedną.
poczatek =[1, 2, 3]
print(poczatek)
koniec = [4, 5, 6]
print(koniec)
calosc = poczatek + koniec
print(calosc)
print(type(calosc))
print()

# zadanie 3. Zadanie: Dodaj Element na Końcu Listy
# Dodaj nowy element na końcu listy [1, 2, 3], na przykład 4.
cyferki = [1, 2, 3]
print(cyferki)
cyferki.append(4)
print(cyferki)
print()

# zadanie 4. Zadanie: Wybierz Element z Krotki
# Mając krotkę (1, 2, 3, 4, 5), wybierz trzeci element.
krotka_cyfry = (1, 2, 3, 4, 5)
print(krotka_cyfry)
print(krotka_cyfry[2])
print()

# zadanie 5. Zadanie: Odwróć Listę
# Odwróć kolejność elementów w liście [1, 2, 3, 4, 5].
lista_cyfry = [1, 2, 3, 4, 5]
print(lista_cyfry)
print(lista_cyfry[::-1])
lista_cyfry.reverse()
print(lista_cyfry)
print()

# zadanie 6. Znajdź Maksymalny Element w Liście
# Znajdź największy element w liście [1, 2, 3, 4, 5].
lista_cyfry_2 = [1, 2, 3, 4, 5]
print(lista_cyfry_2)
print(max(lista_cyfry_2))
print()

# zadanie 7. Formatowanie Stringa
# Stwórz string "Python", a następnie dodaj do niego string " jest super!", tworząc pełne zdanie.
str_1 = "Python"
str_2 = "jest super!"
print(str_1 + " " + str_2)
print(str_1 , str_2)
print(f"{str_1} {str_2}")
print()

# zadanie 8. Zastąp Słowo w Stringu
# Mając string "Lubię Pythona", zastąp słowo "Pythona" słowem "programowanie".
str_3 = "Lubię Pythona"
print(str_3)
print(str_3.replace("Pythona", "programowanie"))
print()

# zadanie 9. Zadanie: Wyodrębnij Podstring
# Wyodrębnij słowo "Python" ze stringa "Lubię Pythona".
str_4 = "Lubię Pythona"
str_5 = str_4.removeprefix("Lubię ")
print(str_5[:-1])
str_6 = str_4[6:12]
print(str_6)
str_7 = str_4.split()[1]
print(str_7[:-1])
print()

# zadanie 10. Stwórz Listę Liczb Nieparzystych
# Stwórz listę zawierającą pierwsze pięć liczb nieparzystych.
liczby_nieprzyste = []
for i in range(10):
    if i % 2 != 0:
        liczby_nieprzyste.append(i)
        print(f"{i} to jest liczna nieparzysta")
print(f"lista liczb nieparzystych do 10 to:  {liczby_nieprzyste}")
print()
print("KONIEC!!!!!")

# najtrudniejsze to wymyślanie nazw zmiennych :)

