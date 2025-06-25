import datetime

# Funkcja zapisuje wynik testu do pliku tekstowego (dokleja do pliku)
def zapisz_wynik(nazwa_pliku, poprawne, liczba_pytan):
    try:
        # Otwieramy plik w trybie dopisywania ("a"), aby nie nadpisywać poprzednich wyników
        with open(nazwa_pliku, "a", encoding="utf-8") as f:
            data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            procent = (poprawne / liczba_pytan) * 100
            f.write(f"Data: {data}\n")
            f.write(f"Poprawne odpowiedzi: {poprawne}/{liczba_pytan}\n")
            f.write(f"Wynik: {procent:.2f}%\n")
            f.write("-" * 30 + "\n")
    except Exception as e:
        raise IOError(f"Nie udało się zapisać wyniku: {e}")
