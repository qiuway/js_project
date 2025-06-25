import tkinter as tk
from gui import AplikacjaGUI

# Główna funkcja uruchamiająca aplikację
if __name__ == "__main__":
    # Tworzenie okna aplikacji (root)
    root = tk.Tk()
    # Inicjalizacja interfejsu aplikacji
    app = AplikacjaGUI(root)
    # Uruchomienie pętli głównej aplikacji
    root.mainloop()
