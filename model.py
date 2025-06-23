import json
from typing import List

class ZnakDrogowy:
    # Konstruktor klasy tworzy obiekt znaku drogowego z podanymi właściwościami
    def __init__(self, id, nazwa, pytanie, plik_obrazka, poprawna):
        self.id = id                      # Unikalny identyfikator znaku
        self.nazwa = nazwa                # Nazwa znaku drogowego
        self.pytanie = pytanie            # Pytanie dotyczące znaku (np. quizowe)
        self.plik_obrazka = plik_obrazka  # Nazwa pliku obrazka znaku
        self.poprawna = poprawna          # Poprawna odpowiedź na pytanie o znak

    # Metoda zwracająca reprezentację tekstową obiektu, tutaj nazwa znaku
    def __str__(self):
        return f"{self.nazwa}"

    # Metoda sprawdzająca, czy podana odpowiedź jest poprawna
    def sprawdz_odpowiedz(self, odp: str) -> bool:
        # Usuwamy białe znaki z początku i końca przed porównaniem
        return odp.strip() == self.poprawna.strip()

# Funkcja do wczytania listy znaków drogowych z pliku JSON
def wczytaj_znaki_z_json(nazwa_pliku: str) -> List[ZnakDrogowy]:
    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as f:
            dane = json.load(f)  # Ładuje dane JSON jako listę słowników

        znaki = []
        for d in dane:
            # Tworzymy obiekt ZnakDrogowy dla każdego słownika w danych
            znaki.append(ZnakDrogowy(**d))
        return znaki
    except Exception as e:
        print(f"Błąd wczytywania pliku JSON: {e}")
        return []
