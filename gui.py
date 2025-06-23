# Importy bibliotek
import tkinter as tk  # GUI
from tkinter import messagebox, scrolledtext  # Dodatkowe komponenty GUI
from PIL import Image, ImageTk  # Obsługa obrazków
import random  # Losowanie odpowiedzi
import os  # Obsługa ścieżek plików
from model import wczytaj_znaki_z_json, ZnakDrogowy  # Dane o znakach
from wyniki import zapisz_wynik  # Funkcja do zapisywania wyników

ilosc_odp = 4  # Liczba odpowiedzi w quizie
ilosc_pytan = 6

class AplikacjaGUI:
    def __init__(self, root, sciezka_json="znaki.json", folder_obrazkow="obrazki"):
        # Konstruktor aplikacji - ustawienie głównych parametrów
        self.root = root
        self.root.title("Nauka znaków drogowych")
        self.folder_obrazkow = folder_obrazkow
        self.sciezka_json = sciezka_json

        # Ustawienia okna aplikacji
        szerokosc = 600
        wysokosc = 500
        self.root.geometry(f"{szerokosc}x{wysokosc}")

        # Wyśrodkowanie okna na ekranie
        ekran_szer = self.root.winfo_screenwidth()
        ekran_wys = self.root.winfo_screenheight()
        x = (ekran_szer // 2) - (szerokosc // 2)
        y = (ekran_wys // 2) - (wysokosc // 2)
        self.root.geometry(f"{szerokosc}x{wysokosc}+{x}+{y}")
        self.root.resizable(False, False)

        # Tworzenie 3 głównych widoków (ekranów)
        self.frame_menu = tk.Frame(root)
        self.frame_quiz = tk.Frame(root)
        self.frame_wyniki = tk.Frame(root)

        # Budowanie widoków
        self.build_menu()
        self.build_quiz()
        self.build_wyniki()

        # Pokazanie początkowego ekranu - menu
        self.show_frame(self.frame_menu)

    def show_frame(self, frame):
        # Funkcja do przełączania widoków
        for f in (self.frame_menu, self.frame_quiz, self.frame_wyniki):
            f.pack_forget()  # Ukryj inne
        frame.pack(fill="both", expand=True)  # Pokaż wybrany

    def build_menu(self):
        # Budowanie głównego menu
        lbl = tk.Label(self.frame_menu, text="Menu Główne", font=("Arial", 24))
        lbl.pack(pady=30)

        btn_start = tk.Button(self.frame_menu, text="Rozpocznij Quiz", font=("Arial", 14), command=self.start_quiz)
        btn_start.pack(pady=10)

        btn_wyniki = tk.Button(self.frame_menu, text="Zobacz Wyniki", font=("Arial", 14), command=self.show_wyniki)
        btn_wyniki.pack(pady=10)

        btn_exit = tk.Button(self.frame_menu, text="Wyjście", font=("Arial", 14), command=self.root.quit)
        btn_exit.pack(pady=10)

    def build_wyniki(self):
        # Budowanie widoku wyników
        lbl = tk.Label(self.frame_wyniki, text="Historia wyników", font=("Arial", 18))
        lbl.pack(pady=10)

        # Pole z przewijaniem do wyświetlania historii
        self.text_wyniki = scrolledtext.ScrolledText(self.frame_wyniki, width=60, height=20, font=("Courier", 10))
        self.text_wyniki.pack(pady=10)

        # Przycisk powrotu do menu
        btn_back = tk.Button(self.frame_wyniki, text="Powrót do menu", command=lambda: self.show_frame(self.frame_menu))
        btn_back.pack(pady=10)

    def show_wyniki(self):
        # Wyświetlenie zawartości pliku z wynikami
        self.text_wyniki.delete(1.0, tk.END)
        try:
            with open("wyniki.txt", "r", encoding="utf-8") as f:
                self.text_wyniki.insert(tk.END, f.read())
        except FileNotFoundError:
            self.text_wyniki.insert(tk.END, "Brak zapisanych wyników.")
        self.show_frame(self.frame_wyniki)

    def build_quiz(self):
        # Budowanie widoku quizu
        self.label_obraz = tk.Label(self.frame_quiz)
        self.label_obraz.pack(pady=10)

        self.label_pytanie = tk.Label(self.frame_quiz, text="", font=("Arial", 16))
        self.label_pytanie.pack(pady=10)

        # Przycisk dla każdej możliwej odpowiedzi
        self.przyciski = []
        for i in range(ilosc_odp):
            btn = tk.Button(self.frame_quiz, text="", width=40, command=lambda i=i: self.sprawdz_odpowiedz(i))
            btn.pack(pady=5)
            self.przyciski.append(btn)

        self.label_status = tk.Label(self.frame_quiz, text="", fg="gray")
        self.label_status.pack(pady=5)

    def start_quiz(self):
        # Rozpoczęcie quizu - wczytanie znaków, przygotowanie zmiennych
        self.znaki = wczytaj_znaki_z_json(self.sciezka_json)
        if not self.znaki:
            messagebox.showerror("Błąd", "Nie udało się wczytać znaków.")
            return

        random.shuffle(self.znaki)  # Losowa kolejność znaków
        self.poprawne = 0  # Liczba poprawnych odpowiedzi
        self.indeks = 0  # Numer aktualnego pytania
        self.maks_ilosc_pytan = ilosc_pytan
        self.znaki = wczytaj_znaki_z_json(self.sciezka_json)
        random.shuffle(self.znaki)
        self.znaki = self.znaki[:self.maks_ilosc_pytan]
        self.liczba_pytan = len(self.znaki)
        self.show_frame(self.frame_quiz)
        self.wyswietl_znak()

    def wyswietl_znak(self):
        # Wyświetlenie aktualnego znaku i przygotowanie odpowiedzi
        znak = self.znaki[self.indeks]
        sciezka = os.path.join(self.folder_obrazkow, znak.plik_obrazka)
        try:
            obraz = Image.open(sciezka).resize((150, 150))
            self.img = ImageTk.PhotoImage(obraz)
            self.label_obraz.config(image=self.img)
            self.label_obraz.image = self.img
            self.label_obraz.config(text="")
        except:
            self.label_obraz.config(image="", text=f"Błąd obrazu: {znak.plik_obrazka}")

        # Ustawienie pytania i odpowiedzi
        self.label_pytanie.config(text=znak.pytanie)
        inne = [z.nazwa for z in self.znaki if z.nazwa != znak.poprawna]
        odp = random.sample(inne, ilosc_odp - 1) + [znak.poprawna]
        random.shuffle(odp)
        self.aktualne_odpowiedzi = odp

        # Ustawienie tekstu na przyciskach
        for i, t in enumerate(odp):
            self.przyciski[i].config(text=t)

        self.label_status.config(text=f"Znak {self.indeks + 1} z {self.liczba_pytan}")

    def sprawdz_odpowiedz(self, idx):
        # Sprawdzenie odpowiedzi użytkownika
        wybrana = self.aktualne_odpowiedzi[idx]
        znak = self.znaki[self.indeks]

        if znak.sprawdz_odpowiedz(wybrana):
            self.poprawne += 1
            messagebox.showinfo("Dobrze", "✅ To poprawna odpowiedź!")
        else:
            messagebox.showwarning("Źle", f"❌ Zła odpowiedź!\nPoprawna: {znak.poprawna}")

        # Przejście do następnego znaku po krótkim opóźnieniu
        self.root.after(100, self.nastepny_znak)

    def nastepny_znak(self):
        # Przejście do kolejnego pytania lub zakończenie quizu
        if self.indeks == self.liczba_pytan - 1:
            self.zapisz_wynik_do_pliku()
            messagebox.showinfo("Koniec", f"Quiz zakończony!\nTwój wynik: {self.poprawne}/{self.liczba_pytan}")
            self.show_frame(self.frame_menu)
        else:
            self.indeks += 1
            self.wyswietl_znak()

    def zapisz_wynik_do_pliku(self, nazwa_pliku="wyniki.txt"):
        # Zapisanie wyniku do pliku tekstowego
        try:
            zapisz_wynik(nazwa_pliku, self.poprawne, self.liczba_pytan)
        except IOError as e:
            messagebox.showerror("Błąd zapisu", str(e))
