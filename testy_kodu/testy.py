import unittest
import os
import json
import timeit
from memory_profiler import memory_usage
from model import ZnakDrogowy, wczytaj_znaki_z_json
from wyniki import zapisz_wynik
import tempfile

class TestZnakDrogowy(unittest.TestCase):
    def setUp(self):
        self.znak = ZnakDrogowy(
            id=1,
            nazwa="Stop",
            pytanie="Co oznacza ten znak?",
            plik_obrazka="stop.png",
            poprawna="Stop"
        )

    def test_sprawdz_odpowiedz_poprawna(self):
        self.assertTrue(self.znak.sprawdz_odpowiedz("Stop"))

    def test_sprawdz_odpowiedz_niepoprawna(self):
        self.assertFalse(self.znak.sprawdz_odpowiedz("Zakaz"))

class TestWczytajZnaki(unittest.TestCase):
    def test_wczytaj_poprawny_json(self):
        dane = [
            {
                "id": 1,
                "nazwa": "Stop",
                "pytanie": "Co oznacza ten znak?",
                "plik_obrazka": "stop.png",
                "poprawna": "Stop"
            }
        ]
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            json.dump(dane, tmp)
            tmp_path = tmp.name

        znaki = wczytaj_znaki_z_json(tmp_path)
        self.assertEqual(len(znaki), 1)
        self.assertEqual(znaki[0].nazwa, "Stop")

        os.remove(tmp_path)

    def test_wczytaj_bledny_json(self):
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            tmp.write("{niepoprawny_json")
            tmp_path = tmp.name

        znaki = wczytaj_znaki_z_json(tmp_path)
        self.assertEqual(len(znaki), 0)

        os.remove(tmp_path)

class TestZapiszWynik(unittest.TestCase):
    def test_zapisz_wynik_do_pliku(self):
        with tempfile.NamedTemporaryFile("r+", delete=False, encoding="utf-8") as tmp:
            tmp_path = tmp.name
            zapisz_wynik(tmp_path, 3, 5)
            tmp.seek(0)
            zawartosc = tmp.read()
            self.assertIn("Poprawne odpowiedzi: 3/5", zawartosc)

        os.remove(tmp_path)

class TestWydajnosc(unittest.TestCase):
    def test_czas_wczytania_znakow(self):
        dane = [
            {"id": i, "nazwa": f"Znak{i}", "pytanie": "?", "plik_obrazka": "img.png", "poprawna": f"Znak{i}"}
            for i in range(1000)
        ]
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            json.dump(dane, tmp)
            tmp_path = tmp.name

        def wczytaj():
            wczytaj_znaki_z_json(tmp_path)

        czas = timeit.timeit(wczytaj, number=5)
        print(f"Czas wczytania 1000 znaków (5 powtórzeń): {czas:.4f} sek.")
        os.remove(tmp_path)

class TestPamiec(unittest.TestCase):
    def test_pamiec_wczytywania(self):
        dane = [
            {"id": i, "nazwa": f"Znak{i}", "pytanie": "?", "plik_obrazka": "img.png", "poprawna": f"Znak{i}"}
            for i in range(1000)
        ]
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            json.dump(dane, tmp)
            tmp_path = tmp.name

        def wczytaj():
            wczytaj_znaki_z_json(tmp_path)

        mem_usage = memory_usage(wczytaj, max_usage=True)
        print(f"Maksymalne zużycie pamięci podczas wczytywania: {mem_usage} MiB")

        os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()
