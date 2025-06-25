import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import random
import os
import json
from model import wczytaj_znaki_z_json, ZnakDrogowy
from wyniki import zapisz_wynik
from functools import reduce

ilosc_odp = 4
ilosc_pytan = 6

class AplikacjaGUI:
    def __init__(self, root, sciezka_json="znaki.json", folder_obrazkow="obrazki"):
        self.root = root
        self.root.title("Nauka znaków drogowych")
        self.folder_obrazkow = folder_obrazkow
        self.sciezka_json = sciezka_json

        wymiar = (600, 500)
        self.root.geometry(f"{wymiar[0]}x{wymiar[1]}")

        ekran_szer = self.root.winfo_screenwidth()
        ekran_wys = self.root.winfo_screenheight()
        x = (ekran_szer // 2) - (wymiar[0] // 2)
        y = (ekran_wys // 2) - (wymiar[1] // 2)

        self.root.geometry(f"{wymiar[0]}x{wymiar[1]}+{x}+{y}")
        self.root.resizable(False, False)

        self.frame_menu = tk.Frame(root)
        self.frame_quiz = tk.Frame(root)
        self.frame_wyniki = tk.Frame(root)
        self.frame_edytor = tk.Frame(root)

        self.build_menu()
        self.build_quiz()
        self.build_wyniki()
        self.build_edytor()

        self.show_frame(self.frame_menu)

    def show_frame(self, frame):
        for f in (self.frame_menu, self.frame_quiz, self.frame_wyniki, self.frame_edytor):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    def build_menu(self):
        lbl = tk.Label(self.frame_menu, text="Menu Główne", font=("Arial", 24))
        lbl.pack(pady=30)

        tk.Button(self.frame_menu, text="Rozpocznij Quiz", font=("Arial", 14), command=self.start_quiz).pack(pady=10)
        tk.Button(self.frame_menu, text="Zobacz Wyniki", font=("Arial", 14), command=self.show_wyniki).pack(pady=10)
        tk.Button(self.frame_menu, text="Edytuj pytania", font=("Arial", 14), command=self.show_edytor).pack(pady=10)
        tk.Button(self.frame_menu, text="Wyjście", font=("Arial", 14), command=self.root.quit).pack(pady=10)

    def build_wyniki(self):
        tk.Label(self.frame_wyniki, text="Historia wyników", font=("Arial", 18)).pack(pady=10)
        self.text_wyniki = scrolledtext.ScrolledText(self.frame_wyniki, width=60, height=20, font=("Courier", 10))
        self.text_wyniki.pack(pady=10)
        tk.Button(self.frame_wyniki, text="Powrót do menu", command=lambda: self.show_frame(self.frame_menu)).pack(pady=10)

    def build_edytor(self):
        tk.Label(self.frame_edytor, text="Edytor pytań", font=("Arial", 18)).pack(pady=10)
        self.lista_znakow_text = scrolledtext.ScrolledText(self.frame_edytor, height=10, width=70)
        self.lista_znakow_text.pack(pady=5)

        frm = tk.Frame(self.frame_edytor)
        frm.pack(pady=5)
        tk.Label(frm, text="ID: ").grid(row=0, column=0)
        self.entry_id = tk.Entry(frm, width=5)
        self.entry_id.grid(row=0, column=1)
        tk.Label(frm, text="Nowe pytanie: ").grid(row=1, column=0)
        self.entry_pytanie = tk.Entry(frm, width=50)
        self.entry_pytanie.grid(row=1, column=1)
        tk.Label(frm, text="Nowa poprawna odpowiedź: ").grid(row=2, column=0)
        self.entry_odp = tk.Entry(frm, width=50)
        self.entry_odp.grid(row=2, column=1)

        tk.Button(self.frame_edytor, text="Zapisz zmiany", command=self.zapisz_edycje).pack(pady=5)
        tk.Button(self.frame_edytor, text="Powrót do menu", command=lambda: self.show_frame(self.frame_menu)).pack(pady=5)

    def show_wyniki(self):
        self.text_wyniki.delete(1.0, tk.END)
        try:
            with open("wyniki.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                suma, count = self.suma_wynikow_rek(lines)
                if count > 0:
                    srednia = suma / count
                    self.text_wyniki.insert(tk.END, f"Średnia poprawnych odpowiedzi: {srednia:.2f}%\n\n")
                else:
                    self.text_wyniki.insert(tk.END, "Brak zapisanych wyników.\n\n")

                self.text_wyniki.insert(tk.END, "".join(lines))
        except FileNotFoundError:
            self.text_wyniki.insert(tk.END, "Brak zapisanych wyników.")
        self.show_frame(self.frame_wyniki)

    def show_edytor(self):
        while True:
            try:
                with open(self.sciezka_json, "r", encoding="utf-8") as f:
                    dane = json.load(f)
                    self.znaki_json = dane
                break  # jeśli wczytanie się udało, wyjdź z pętli
            except Exception as e:
                odp = messagebox.askretrycancel("Błąd",
                                                f"Nie udało się wczytać danych z JSON.\n{e}\nSpróbować ponownie?")
                if not odp:
                    return  # użytkownik zrezygnował, wyjdź z funkcji

        self.odswiez_liste_znakow()
        self.show_frame(self.frame_edytor)

    def zapisz_edycje(self):
        try:
            id_edytuj = int(self.entry_id.get())
        except ValueError:
            messagebox.showwarning("Błąd", "Niepoprawne ID")
            return

        assert id_edytuj > 0, "ID musi być liczbą całkowitą dodatnią"
        znaleziono = False
        for znak in self.znaki_json:
            if znak['id'] == id_edytuj:
                if self.entry_pytanie.get().strip():
                    znak['pytanie'] = self.entry_pytanie.get().strip()
                if self.entry_odp.get().strip():
                    znak['poprawna'] = self.entry_odp.get().strip()
                znaleziono = True
                break

        if not znaleziono:
            messagebox.showerror("Błąd", f"Nie znaleziono pytania o ID {id_edytuj}")
            return

        try:
            with open(self.sciezka_json, "w", encoding="utf-8") as f:
                json.dump(self.znaki_json, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Sukces", "Zapisano zmiany!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać zmian: {e}")
            return

        # Odśwież listę w edytorze od razu po zapisie
        self.odswiez_liste_znakow()

    def build_quiz(self):
        self.label_obraz = tk.Label(self.frame_quiz)
        self.label_obraz.pack(pady=10)

        self.label_pytanie = tk.Label(self.frame_quiz, text="", font=("Arial", 16))
        self.label_pytanie.pack(pady=10)

        self.przyciski = []
        for i in range(ilosc_odp):
            btn = tk.Button(self.frame_quiz, text="", width=40, command=lambda i=i: self.sprawdz_odpowiedz(i))
            btn.pack(pady=5)
            self.przyciski.append(btn)

        self.btn_nastepne = tk.Button(self.frame_quiz, text="Następne pytanie", state="disabled", command=self.nastepny_znak)
        self.btn_nastepne.pack(pady=10)

        self.label_status = tk.Label(self.frame_quiz, text="", fg="gray")
        self.label_status.pack(pady=5)

    def start_quiz(self):
        self.znaki = wczytaj_znaki_z_json(self.sciezka_json)
        if not self.znaki:
            messagebox.showerror("Błąd", "Nie udało się wczytać znaków.")
            return

        random.shuffle(self.znaki)
        self.poprawne = 0
        self.indeks = 0
        self.maks_ilosc_pytan = ilosc_pytan
        self.znaki = self.znaki[:self.maks_ilosc_pytan]
        self.liczba_pytan = len(self.znaki)
        self.show_frame(self.frame_quiz)
        self.wyswietl_znak()

    def wyswietl_znak(self):
        self.odpowiedziana = False
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

        self.label_pytanie.config(text=znak.pytanie)

        inne_set = set(filter(lambda name: name != znak.poprawna, map(lambda z: z.nazwa, self.znaki)))
        inne = list(inne_set)
        odp = random.sample(inne, ilosc_odp - 1) + [znak.poprawna]
        random.shuffle(odp)
        self.aktualne_odpowiedzi = odp

        for i, t in enumerate(odp):
            self.przyciski[i].config(
                text=t,
                state="normal",
                bg="SystemButtonFace",
                fg="black"
            )

        self.label_status.config(text=f"Znak {self.indeks + 1} z {self.liczba_pytan}")
        self.btn_nastepne.config(state="disabled")

    def sprawdz_odpowiedz(self, idx):
        if self.odpowiedziana:
            return

        self.odpowiedziana = True
        wybrana = self.aktualne_odpowiedzi[idx]
        znak = self.znaki[self.indeks]

        for i, btn in enumerate(self.przyciski):
            if self.aktualne_odpowiedzi[i] == znak.poprawna:
                btn.config(bg="green", fg="white")
            elif i == idx:
                btn.config(bg="red", fg="black")

        if znak.sprawdz_odpowiedz(wybrana):
            self.poprawne += 1

        self.btn_nastepne.config(state="normal")

    def nastepny_znak(self):
        if self.indeks == self.liczba_pytan - 1:
            self.zapisz_wynik_do_pliku()
            messagebox.showinfo("Koniec", f"Quiz zakończony!\nTwój wynik: {self.poprawne}/{self.liczba_pytan}")
            self.show_frame(self.frame_menu)
        else:
            self.indeks += 1
            self.wyswietl_znak()

    def zapisz_wynik_do_pliku(self, nazwa_pliku="wyniki.txt"):
        try:
            zapisz_wynik(nazwa_pliku, self.poprawne, self.liczba_pytan)
        except IOError as e:
            messagebox.showerror("Błąd zapisu", str(e))

    def odswiez_liste_znakow(self):
        self.lista_znakow_text.config(state=tk.NORMAL)
        self.lista_znakow_text.delete(1.0, tk.END)

        tekst = reduce(
            lambda acc, znak: acc + f"ID: {znak['id']} | Pytanie: {znak['pytanie']}\nOdp: {znak['poprawna']}\n\n",
            self.znaki_json, "")

        self.lista_znakow_text.insert(tk.END, tekst)
        self.lista_znakow_text.config(state=tk.DISABLED)

    def suma_wynikow_rek(self, lines):
        suma = 0.0
        count = 0

        def rek(index):
            nonlocal suma, count  # dzięki temu możemy modyfikować zmienne z funkcji zewnętrznej
            if index == len(lines):
                return
            line = lines[index].strip()
            if line.startswith("Wynik:"):
                try:
                    procent_str = line.split("Wynik:")[1].strip().replace("%", "")
                    procent = float(procent_str)
                    suma += procent
                    count += 1
                except:
                    pass
            rek(index + 1)

        rek(0)
        return suma, count

