import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json, os, math
from PIL import Image, ImageDraw, ImageTk, ImageFont

# Domyślny katalog zapisu – tokeny mają być zapisywane w tym katalogu
DEFAULT_TOKENS_DIR = r"C:\Users\klif\OneDrive\Pulpit\token_generator\zapisane_tokeny"
if not os.path.exists(DEFAULT_TOKENS_DIR):
    os.makedirs(DEFAULT_TOKENS_DIR)

def create_flag_background(nation, width, height):
    """Generates a flag image for the given nation, filling the entire area."""
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bg)
    if nation == "Polska":
        draw.rectangle([0, 0, width, height / 2], fill="white")
        draw.rectangle([0, height / 2, width, height], fill="red")
    elif nation == "Japonia":
        draw.rectangle([0, 0, width, height], fill="white")
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 4
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="red")
    elif nation == "Niemcy":
        stripe_height = height / 3
        draw.rectangle([0, 0, width, stripe_height], fill="black")
        draw.rectangle([0, stripe_height, width, 2 * stripe_height], fill="red")
        draw.rectangle([0, 2 * stripe_height, width, height], fill="gold")
    elif nation == "Francja":
        stripe_width = width / 3
        draw.rectangle([0, 0, stripe_width, height], fill="blue")
        draw.rectangle([stripe_width, 0, 2 * stripe_width, height], fill="white")
        draw.rectangle([2 * stripe_width, 0, width, height], fill="red")
    elif nation == "Stany Zjednoczone":
        stripe_height = height / 13
        for i in range(13):
            color = "red" if i % 2 == 0 else "white"
            draw.rectangle([0, i * stripe_height, width, (i + 1) * stripe_height], fill=color)
        draw.rectangle([0, 0, width * 0.4, 7 * stripe_height], fill="blue")
    elif nation == "Wielka Brytania":
        draw.rectangle([0, 0, width, height], fill="blue")
        line_width = int(width * 0.1)
        draw.line([(0, 0), (width, height)], fill="red", width=line_width)
        draw.line([(width, 0), (0, height)], fill="red", width=line_width)
        line_width2 = int(width * 0.05)
        draw.line([(0, 0), (width, height)], fill="white", width=line_width2)
        draw.line([(width, 0), (0, height)], fill="white", width=line_width2)
    elif nation == "Związek Radziecki":
        draw.rectangle([0, 0, width, height], fill="red")
    else:
        draw.rectangle([0, 0, width, height], fill="gray")
    return bg

class TokenEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Edytor Żetonów")
        self.root.geometry("800x600")  # Adjusted window size for better visibility on a tablet
        self.root.configure(bg="darkolivegreen")

        # Nagłówek
        header_frame = tk.Frame(root, bg="olivedrab", bd=5, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(header_frame, text="Generator żetonów do HISTORYCZNEJ GRY BITEWNEJ WRZESIEŃ 1939",
                                bg="olivedrab", fg="white", font=("Arial", 20, "bold"))
        header_label.pack(pady=10)

        # Rozmiar tokena
        self.hex_token_size_var = tk.IntVar(value=240)
        self.square_token_size_var = tk.IntVar(value=240)

        # Ustawienie kształtu – opcje "Heks" (nieaktywny) i "Prostokąt" (aktywny)
        self.shape = tk.StringVar(value="Prostokąt")
        self.nation = tk.StringVar(value="Polska")
        self.unit_type = tk.StringVar(value="P")
        self.unit_size = tk.StringVar(value="Pluton")
        
        self.movement_points = tk.StringVar()
        self.attack_range = tk.StringVar()
        self.attack_value = tk.StringVar()
        self.combat_value = tk.StringVar()
        self.supply_points = tk.StringVar()
        self.purchase_value = tk.StringVar()
        self.sight_range = tk.StringVar()  # Nowa zmienna dla zasięgu widzenia

        self.custom_bg_path = None

        # Parametry transformacji tła
        self.bg_rotation = 0      
        self.bg_scale = 1.0       
        self.bg_translate_x = 0   
        self.bg_translate_y = 0   

        # Kolor napisów – domyślnie ustawiony dla "Polska" (black)
        self.variable_text_color = "black"

        # Katalog zapisu
        self.save_directory = DEFAULT_TOKENS_DIR

        # Add support upgrade attributes and selected_support BEFORE build_controls call
        self.support_upgrades = {
            "drużyna granatników": {
                "movement": -1,
                "range": 1,
                "attack": 2,
                "combat": 0,
                "supply": 0,
                "purchase": 10,
                "ignore_movement_penalty": ["przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"]
            },
            "sekcja km.ppanc": {
                "movement": -1,
                "range": 1,
                "attack": 2,
                "combat": 0,
                "supply": 0,
                "purchase": 10,
                "ignore_movement_penalty": ["przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"]
            },
            "sekcja ckm": {
                "movement": -1,
                "range": 1,
                "attack": 2,
                "combat": 0,
                "supply": 0,
                "purchase": 10,
                "ignore_movement_penalty": ["przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"]
            },
            "przodek dwukonny": {
                "movement": 2,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "supply": 0,
                "purchase": 5,
                "ignore_movement_penalty": []
            },
            "sam. ciezarowy Fiat 621": {
                "movement": 5,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "supply": 0,
                "purchase": 8,
                "ignore_movement_penalty": []
            },
            "sam.ciezarowy Praga Rv": {
                "movement": 5,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "supply": 0,
                "purchase": 8,
                "ignore_movement_penalty": []
            },
            "ciagnik altyleryjski": {
                "movement": 3,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "supply": 0,
                "purchase": 12,
                "ignore_movement_penalty": []
            },
            "obserwator": {
                "movement": 0,
                "range": 0,
                "attack": 0,
                "combat": 0,
                "supply": 0,
                "purchase": 5,
                "sight": 1,  # Dodanie modyfikatora zasięgu widzenia
                "ignore_movement_penalty": []
            }
        }
        self.selected_support = tk.StringVar(value="")  # Przechowuje wybrane wsparcie

        # Dodajemy słownik określający dozwolone wsparcie dla każdego typu jednostki        
        self.allowed_support = {
            "P": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", 
                 "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv"],
            "K": ["sekcja ckm"],
            "TC": ["obserwator"],
            "TŚ": ["obserwator"],
            "TL": ["obserwator"],
            "TS": ["obserwator"],
            "AC": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc",
                  "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", 
                  "ciagnik altyleryjski", "obserwator"],
            "AL": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc",
                  "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv",
                  "ciagnik altyleryjski", "obserwator"],
            "AP": ["drużyna granatników", "sekcja ckm", "sekcja km.ppanc",
                  "przodek dwukonny", "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv",
                  "ciagnik altyleryjski", "obserwator"],
            "Z": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", "obserwator"],
            "D": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", 
                 "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"],
            "G": ["drużyna granatników", "sekcja km.ppanc", "sekcja ckm", 
                 "sam. ciezarowy Fiat 621", "sam.ciezarowy Praga Rv", "obserwator"]
        }

        # Te atrybuty muszą być zainicjowane PRZED wywołaniem update_numeric_fields()
        self.selected_supports = set()  # Zbiór dla wielu wybranych wsparć
        self.selected_transport = tk.StringVar(value="")  # Dla pojedynczego transportu
        self.transport_types = ["przodek dwukonny", "sam. ciezarowy Fiat 621", 
                              "sam.ciezarowy Praga Rv", "ciagnik altyleryjski"]
        
        self.selected_support = tk.StringVar(value="")  # Stary atrybut - można usunąć później
        
        self.update_numeric_fields()  # Teraz to wywołanie będzie działać poprawnie

        main_container = tk.Frame(root, bg="darkolivegreen")
        main_container.pack(fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(main_container, bg="darkolivegreen")
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_frame = tk.Frame(main_container, bd=2, relief=tk.RIDGE, bg="darkolivegreen")
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.build_controls()

        self.preview_canvas = tk.Canvas(self.preview_frame, width=240, height=240, bg="dimgray")  # Adjusted canvas size
        self.preview_canvas.pack(padx=10, pady=10)
        self.dim_label = tk.Label(self.preview_frame, text="", font=("Arial", 12), bg="darkolivegreen", fg="white")
        self.dim_label.pack(padx=10, pady=(0,10))
        self.preview_image = None

        # Pasek transformacji tła
        self.transformation_frame = tk.Frame(self.preview_frame, bg="darkolivegreen")
        self.transformation_frame.pack(padx=10, pady=10)
        tk.Button(self.transformation_frame, text="⟵", command=self.translate_left,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="↑", command=self.translate_up,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="-", command=self.scale_down,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="+", command=self.scale_up,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="↓", command=self.translate_down,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="⟶", command=self.translate_right,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="Kolor napisów+", command=self.toggle_color_frame,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="l", command=self.rotate_left,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(self.transformation_frame, text="p", command=self.rotate_right,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=2)
        
        self.color_frame_visible = False
        self.color_frame = tk.Frame(self.preview_frame, bg="darkolivegreen")
        
        self.preview_canvas.bind("<Enter>", self.on_mouse_enter)
        self.preview_canvas.bind("<Motion>", self.on_mouse_motion)
        self.preview_canvas.bind("<Leave>", self.on_mouse_leave)
        self.tooltip = None

        # Przyciski zapisu i wyboru tła
        btn_frame = tk.Frame(self.control_frame, bg="darkolivegreen")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Podgląd", command=self.update_preview,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Zapisz Żeton", command=self.save_token,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Wyczyść bazę żetonów", command=self.clear_database,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Pobieranie tła", command=self.load_background,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Wybór katalogu zapisu
        save_dir_frame = tk.Frame(self.control_frame, bg="darkolivegreen")
        save_dir_frame.pack(pady=5)
        tk.Button(save_dir_frame, text="Wybierz katalog zapisu", command=self.select_save_directory,
                  bg="saddlebrown", fg="white").pack(side=tk.LEFT, padx=5)
        self.save_dir_label = tk.Label(save_dir_frame, text=f"Katalog zapisu: {self.save_directory}",
                                       bg="darkolivegreen", fg="white")
        self.save_dir_label.pack(side=tk.LEFT, padx=5)
        
        # Klawisze sterujące (alternatywne)
        self.root.bind("<Left>", self.on_key_left)
        self.root.bind("<Right>", self.on_key_right)
        self.root.bind("<Up>", self.on_key_up)
        self.root.bind("<Down>", self.on_key_down)
        self.root.bind("+", self.on_key_plus)
        self.root.bind("-", self.on_key_minus)
        self.root.bind("l", self.on_key_l)
        self.root.bind("p", self.on_key_p)

        # Dodajemy nowy atrybut dla przechowywania wielu wybranych wsparć
        self.selected_supports = set()
        # Osobny atrybut dla wybranego transportu
        self.selected_transport = tk.StringVar(value="")
        # Lista typów transportu
        self.transport_types = ["przodek dwukonny", "sam. ciezarowy Fiat 621", 
                              "sam.ciezarowy Praga Rv", "ciagnik altyleryjski"]

    def set_default_text_color(self):
        defaults = {
            "Polska": "black",
            "Niemcy": "blue",
            "Wielka Brytania": "black",  # zmieniono z blue na black
            "Japonia": "black",
            "Stany Zjednoczone": "black",
            "Francja": "black",
            "Związek Radziecki": "white"
        }
        self.variable_text_color = defaults.get(self.nation.get(), "black")

    def build_controls(self):
        container = tk.Frame(self.control_frame, bg="darkolivegreen")
        container.pack(fill=tk.X, padx=5, pady=5)

        left_frame = tk.Frame(container, bg="darkolivegreen")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        # Sekcja wyboru kształtu
        shape_frame = tk.LabelFrame(left_frame, text="Kształt Żetonu", bg="darkolivegreen", 
                                    fg="white", font=("Arial", 10, "bold"))
        shape_frame.pack(fill=tk.X, padx=5, pady=5)
        for text, val, state in [("Heks", "Heks", tk.DISABLED), ("Prostokąt", "Prostokąt", tk.NORMAL)]:
            tk.Radiobutton(shape_frame, text=text, variable=self.shape, value=val,
                          command=self.update_preview, state=state, 
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=20, pady=2).pack(anchor=tk.W)

        # Sekcja wyboru nacji
        nation_frame = tk.LabelFrame(left_frame, text="Nacja", bg="darkolivegreen", fg="white",
                                     font=("Arial", 10, "bold"))
        nation_frame.pack(fill=tk.X, padx=5, pady=5)
        for n in ["Polska", "Niemcy", "Wielka Brytania", "Japonia", "Stany Zjednoczone", "Francja", "Związek Radziecki"]:
            tk.Radiobutton(nation_frame, text=n, variable=self.nation, value=n,
                          command=lambda n=n: [self.set_default_text_color(), self.update_preview()],
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=20, pady=2).pack(anchor=tk.W)

        # Pozostałe elementy w układzie grid
        unit_frame = tk.LabelFrame(container, text="Rodzaj Jednostki", bg="darkolivegreen", fg="white",
                                   font=("Arial", 9, "bold"))  # zmniejszona czcionka z 10 na 9
        unit_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")
        
        # Lista jednostek z typami czołgów i artylerią
        unit_types = [
            ("Piechota (P)", "P"),
            ("Kawaleria (K)", "K"),
            ("Czołg ciężki (TC)", "TC"),  # Zmieniono z T na TC
            ("Czołg średni (TŚ)", "TŚ"),
            ("Czołg lekki (TL)", "TL"),
            ("Sam. pancerny (TS)", "TS"),
            ("Artyleria ciężka (AC)", "AC"),
            ("Artyleria lekka (AL)", "AL"),
            ("Artyleria plot (AP)", "AP"),
            ("Zaopatrzenie (Z)", "Z"),
            ("Dowództwo (D)", "D"),
            ("Generał (G)", "G")
        ]

        for text, val in unit_types:
            tk.Radiobutton(unit_frame, text=text, variable=self.unit_type, value=val,
                          command=lambda: [self.update_numeric_fields(), 
                                         self.update_support_buttons(),  # Dodajemy wywołanie
                                         self.update_preview()],
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=20, pady=2).pack(anchor=tk.W)  # Zmieniono width z 12 na 20

        # Stworzenie kontenera dla modułów ustawionych pionowo
        vertical_container = tk.Frame(container, bg="darkolivegreen")
        vertical_container.grid(row=0, column=2, padx=5, pady=5, sticky="n")

        # Moduł Wielkość Jednostki (na górze)
        size_frame = tk.LabelFrame(vertical_container, text="Wielkość Jednostki", bg="darkolivegreen", fg="white",
                                font=("Arial", 9, "bold"))
        size_frame.pack(fill=tk.X, padx=0, pady=(0,5))  # Dodane pady aby odsunąć od następnego modułu
        for size in ["Pluton", "Kompania", "Batalion"]:
            tk.Radiobutton(size_frame, text=size, variable=self.unit_size, value=size,
                          command=lambda: [self.update_numeric_fields(), self.update_preview()],
                          bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                          activebackground="saddlebrown", activeforeground="white",
                          indicatoron=False, width=12, pady=2).pack(anchor=tk.W)

        # Moduł Wsparcie jednostki (na dole)
        support_frame = tk.LabelFrame(vertical_container, text="Wsparcie jednostki", bg="darkolivegreen", fg="white",
                                    font=("Arial", 9, "bold"))
        support_frame.pack(fill=tk.X, padx=0, pady=(5,0))  # Dodane pady aby odsunąć od poprzedniego modułu
        
        # Słownik skróconych nazw dla wsparcia
        shortened_names = {
            "drużyna granatników": "granatniki",
            "sekcja km.ppanc": "km ppanc",
            "sekcja ckm": "ckm",
            "przodek dwukonny": "przodek 2k",
            "sam. ciezarowy Fiat 621": "Fiat 621",
            "sam.ciezarowy Praga Rv": "Praga Rv",
            "ciagnik altyleryjski": "ciągnik art.",
            "obserwator": "obserwator"
        }
        
        # Słownik do przechowywania przycisków wsparcia
        self.support_buttons = {}

        # Zmodyfikowana funkcja pomocnicza do obsługi kliknięcia przycisku wsparcia
        def create_toggle_command(name, button):
            def toggle():
                if (name in self.transport_types):
                    # Obsługa przycisków transportu (tryb radio)
                    if (self.selected_transport.get() == name):
                        self.selected_transport.set("")
                        button.configure(bg="darkolivegreen")
                    else:
                        # Odznacz poprzedni transport
                        if (self.selected_transport.get()):
                            old_btn = self.support_buttons[self.selected_transport.get()]
                            old_btn.configure(bg="darkolivegreen")
                        self.selected_transport.set(name)
                        button.configure(bg="saddlebrown")
                else:
                    # Obsługa pozostałych przycisków (mogą być wielokrotnie wybrane)
                    if (name in self.selected_supports):
                        self.selected_supports.remove(name)
                        button.configure(bg="darkolivegreen")
                    else:
                        self.selected_supports.add(name)
                        button.configure(bg="saddlebrown")
                
                self.update_numeric_fields()
                self.update_preview()
            return toggle

        # Przyciski dla wszystkich rodzajów wsparcia
        for support_name in self.support_upgrades.keys():
            display_name = shortened_names.get(support_name, support_name)
            btn = tk.Button(support_frame, text=display_name,
                         bg="darkolivegreen", fg="white",
                         activebackground="saddlebrown", activeforeground="white",
                         width=15, pady=2)
            # Najpierw tworzymy przycisk i dodajemy do słownika
            self.support_buttons[support_name] = btn
            # Potem ustawiamy komendę
            btn.configure(command=create_toggle_command(support_name, btn))
            btn.pack(fill=tk.X, padx=2, pady=1)

        # Dodajemy wywołanie aktualizacji stanu przycisków
        self.update_support_buttons()

        # Kontener dla wyboru rozmiaru i wartości liczbowych
        right_frame = tk.Frame(container, bg="darkolivegreen")
        right_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky="n")

        # Wybór rozmiaru tokena
        size_choice_frame = tk.LabelFrame(right_frame, text="Wybór Rozmiaru Tokena", 
                                        bg="darkolivegreen", fg="white", font=("Arial", 10, "bold"))
        size_choice_frame.pack(fill=tk.X, padx=5, pady=5)
        
        hex_size_frame = tk.Frame(size_choice_frame, bg="darkolivegreen")
        hex_size_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(hex_size_frame, text="Heks", bg="darkolivegreen", fg="white", font=("Arial", 9)).pack()  # zmniejszona czcionka
        tk.Radiobutton(hex_size_frame, text="240x240", variable=self.hex_token_size_var, value=240,
                      command=self.update_preview, state=tk.DISABLED,
                      bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                      activebackground="saddlebrown", activeforeground="white",
                      indicatoron=False, width=8, pady=2).pack(anchor=tk.W)  # zmniejszono width z 8 na 6

        square_size_frame = tk.Frame(size_choice_frame, bg="darkolivegreen")
        square_size_frame.pack(side=tk.RIGHT, padx=5)
        tk.Label(square_size_frame, text="Kwadrat", bg="darkolivegreen", fg="white", font=("Arial", 9)).pack()  # zmniejszona czcionka
        tk.Radiobutton(square_size_frame, text="240x240", variable=self.square_token_size_var, value=240,
                      command=self.update_preview, state=tk.DISABLED,
                      bg="darkolivegreen", fg="white", selectcolor="saddlebrown",
                      activebackground="saddlebrown", activeforeground="white",
                      indicatoron=False, width=8, pady=2).pack(anchor=tk.W)  # zmniejszono width z 8 na 6

        # Wartości liczbowe bezpośrednio pod wyborem rozmiaru
        numeric_frame = tk.LabelFrame(right_frame, text="Wartości Liczbowe", 
                                    bg="darkolivegreen", fg="white", font=("Arial", 10, "bold"))
        numeric_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Szersze pole entry dla wartości liczbowych
        entry_width = 8  # Zmieniono entry_width z 15 na 8
        for label_text, var in [("Punkty Ruchu:", self.movement_points),
                              ("Zasięg Ataku:", self.attack_range),
                              ("Wartość Ataku:", self.attack_value),
                              ("Wartość Bojowa:", self.combat_value),
                              ("Punkty Zaopatrzenia:", self.supply_points),
                              ("Wartość Zakupu:", self.purchase_value),
                              ("Zasięg Widzenia:", self.sight_range)]:  # Dodane nowe pole
            entry_frame = tk.Frame(numeric_frame, bg="darkolivegreen")
            entry_frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(entry_frame, text=label_text, bg="darkolivegreen", fg="white").pack(side=tk.LEFT)
            tk.Entry(entry_frame, textvariable=var, width=entry_width).pack(side=tk.RIGHT)

    def update_support_buttons(self):
        """Aktualizuje stan przycisków wsparcia na podstawie wybranego typu jednostki"""
        current_unit = self.unit_type.get()
        allowed = self.allowed_support.get(current_unit, [])
        
        # Resetujemy wybrane wsparcia jeśli nie są dozwolone dla nowej jednostki
        self.selected_supports = {s for s in self.selected_supports if s in allowed}
        if self.selected_transport.get() not in allowed:
            self.selected_transport.set("")
        
        # Aktualizujemy stan wszystkich przycisków
        for support_name, btn in self.support_buttons.items():
            if support_name in allowed:
                btn.configure(state=tk.NORMAL)
                # Ustawiamy kolor tła w zależności od stanu
                if support_name in self.transport_types:
                    btn.configure(bg="saddlebrown" if support_name == self.selected_transport.get() else "darkolivegreen")
                else:
                    btn.configure(bg="saddlebrown" if support_name in self.selected_supports else "darkolivegreen")
            else:
                btn.configure(state=tk.DISABLED, bg="gray")

    def update_numeric_fields(self):
        defaults = {
            "ruch": {
                "P": "5", "K": "16", 
                "TC": "18", "TŚ": "20", "TL": "22", "TS": "24",  # Wartości dla różnych typów czołgów
                "AC": "12", "AL": "14", "AP": "16",  # Wartości dla różnych typów artylerii
                "Z": "20", "D": "16", "G": "16"
            },
            "range": {
                "P": "1", "K": "1",
                "TC": "3", "TŚ": "3", "TL": "2", "TS": "2",  # Zasięgi dla różnych typów czołgów
                "AC": "6", "AL": "4", "AP": "4",  # Zasięgi dla różnych typów artylerii
                "Z": "1", "D": "0", "G": "0"
            },
            "attack": {
                "Pluton": {
                    "P": "2", "K": "3",
                    "TC": "6", "TŚ": "5", "TL": "4", "TS": "3",  # Wartości ataku dla plutonu
                    "AC": "6", "AL": "4", "AP": "3",
                    "Z": "1", "D": "0", "G": "0"
                },
                "Kompania": {
                    "P": "4", "K": "6",
                    "TC": "10", "TŚ": "8", "TL": "7", "TS": "6",  # Wartości ataku dla kompanii
                    "AC": "9", "AL": "7", "AP": "6",
                    "Z": "2", "D": "0", "G": "0"
                },
                "Batalion": {
                    "P": "8", "K": "9",
                    "TC": "18", "TŚ": "15", "TL": "12", "TS": "10",  # Wartości ataku dla batalionu
                    "AC": "12", "AL": "10", "AP": "9",
                    "Z": "3", "D": "0", "G": "0"
                }
            },
            "combat": {
                "Pluton": {
                    "P": "3", "K": "3",
                    "TC": "5", "TŚ": "4", "TL": "3", "TS": "2",  # Wartości bojowe dla plutonu
                    "AC": "3", "AL": "3", "AP": "3",
                    "Z": "2", "D": "0", "G": "0"
                },
                "Kompania": {
                    "P": "6", "K": "6",
                    "TC": "10", "TŚ": "8", "TL": "6", "TS": "5",  # Wartości bojowe dla kompanii
                    "AC": "6", "AL": "6", "AP": "6",
                    "Z": "4", "D": "0", "G": "0"
                },
                "Batalion": {
                    "P": "12", "K": "12",
                    "TC": "18", "TŚ": "15", "TL": "12", "TS": "10",  # Wartości bojowe dla batalionu
                    "AC": "12", "AL": "12", "AP": "12",
                    "Z": "6", "D": "0", "G": "0"
                }
            },
            "supply": {"Pluton": "10", "Kompania": "30", "Batalion": "90"},
            "purchase": {
                "Pluton": {
                    "P": "18", "K": "20",
                    "TC": "24", "TŚ": "22", "TL": "20", "TS": "18",  # Koszty zakupu dla plutonu
                    "AC": "22", "AL": "20", "AP": "18",
                    "Z": "16", "D": "60", "G": "60"
                },
                "Kompania": {
                    "P": "36", "K": "40",
                    "TC": "48", "TŚ": "44", "TL": "40", "TS": "36",  # Koszty zakupu dla kompanii
                    "AC": "44", "AL": "40", "AP": "36",
                    "Z": "32", "D": "60", "G": "60"
                },
                "Batalion": {
                    "P": "54", "K": "60",
                    "TC": "72", "TŚ": "66", "TL": "60", "TS": "54",  # Koszty zakupu dla batalionu
                    "AC": "66", "AL": "60", "AP": "54",
                    "Z": "48", "D": "60", "G": "60"
                }
            },
            "sight": {
                "P": "3", "K": "3",
                "TC": "2", "TŚ": "2", "TL": "2", "TS": "3",  # Zasięgi widzenia dla różnych typów
                "AC": "3", "AL": "3", "AP": "3",
                "D": "4", "G": "4", "Z": "2"
            },
        }
        ut = self.unit_type.get()
        size = self.unit_size.get()
        self.movement_points.set(defaults["ruch"].get(ut, ""))
        self.attack_range.set(defaults["range"].get(ut, ""))
        self.attack_value.set(defaults["attack"][size].get(ut, ""))
        self.combat_value.set(defaults["combat"][size].get(ut, ""))
        # Zmiana logiki dla punktów zaopatrzenia - tylko jednostka Z zachowuje wartości
        self.supply_points.set(defaults["supply"].get(size, "") if ut == "Z" else "0")
        self.purchase_value.set(defaults["purchase"][size].get(ut, ""))
        self.sight_range.set(defaults["sight"].get(ut, ""))

        # After setting default values, apply support modifications
        all_selected = self.selected_supports | {self.selected_transport.get()} if self.selected_transport.get() else self.selected_supports
        
        # Zmienna do śledzenia czy już naliczono -1 do ruchu
        movement_penalty_applied = False
        
        # Znajdź najwyższy modyfikator zasięgu ataku wśród wsparcia
        max_range_bonus = 0
        for support in self.selected_supports:
            if support and support in self.support_upgrades:
                range_mod = self.support_upgrades[support].get("range", 0)
                max_range_bonus = max(max_range_bonus, range_mod)
        
        # Najpierw sprawdź transport, ponieważ ma priorytet
        if self.selected_transport.get():
            transport = self.support_upgrades[self.selected_transport.get()]
            current_movement = int(self.movement_points.get() or 0)
            self.movement_points.set(str(current_movement + transport["movement"]))
        
        # Następnie sprawdź pozostałe wsparcia
        for support in self.selected_supports:
            if support and support in self.support_upgrades:
                upgrade = self.support_upgrades[support]
                
                # Specjalna logika dla kary do ruchu
                if (upgrade["movement"] < 0 and not movement_penalty_applied):
                    current_movement = int(self.movement_points.get() or 0)
                    self.movement_points.set(str(current_movement - 1))
                    movement_penalty_applied = True
                
                # Pozostałe modyfikatory stosuj normalnie (oprócz zasięgu)
                current_attack = int(self.attack_value.get() or 0)
                current_combat = int(self.combat_value.get() or 0)
                current_supply = int(self.supply_points.get() or 0)
                current_purchase = int(self.purchase_value.get() or 0)
                
                self.attack_value.set(str(current_attack + upgrade["attack"]))
                self.combat_value.set(str(current_combat + upgrade["combat"]))
                self.supply_points.set(str(current_supply + upgrade["supply"]))
                self.purchase_value.set(str(current_purchase + upgrade["purchase"]))
                
                # Apply sight range modification if present
                if "sight" in upgrade:
                    current_sight = int(self.sight_range.get() or 0)
                    self.sight_range.set(str(current_sight + upgrade["sight"]))
        
        # Zastosuj najwyższy bonus do zasięgu ataku
        if max_range_bonus > 0:
            current_range = int(self.attack_range.get() or 0)
            self.attack_range.set(str(current_range + max_range_bonus))

    def on_mouse_enter(self, event): 
        self.show_tooltip(event)
    def on_mouse_motion(self, event): 
        self.show_tooltip(event)
    def on_mouse_leave(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    def show_tooltip(self, event):
        text = (f"Punkty Ruchu: {self.movement_points.get()}\n"
                f"Zasięg Ataku: {self.attack_range.get()}\n"
                f"Wartość Ataku: {self.attack_value.get()}\n"
                f"Wartość Bojowa: {self.combat_value.get()}\n"
                f"Punkty Zaopatrzenia: {self.supply_points.get()}\n"
                f"Wartość Zakupu: {self.purchase_value.get()}")
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self.preview_canvas)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (event.x_root + 10, event.y_root + 10))
        tk.Label(self.tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 8)).pack()
    
    def update_preview(self):
        self.preview_canvas.delete("all")
        if self.shape.get() == "Heks":
            token_size = self.hex_token_size_var.get()
            token_img = self.create_token_image(custom_size=token_size)
            self.preview_image = ImageTk.PhotoImage(token_img)
            self.preview_canvas.config(width=240, height=240)  # Zmiana z 300 na 240
            self.dim_label.config(text=f"Heks (oryginalnie {token_size}x{token_size})")
        else:
            token_size = self.square_token_size_var.get()
            token_img = self.create_token_image(custom_size=token_size)
            self.preview_image = ImageTk.PhotoImage(token_img)
            self.preview_canvas.config(width=240, height=240)  # Adjusted canvas size
            self.dim_label.config(text=f"Kwadrat (oryginalnie {token_size}x{token_size})")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)
    
    def load_background(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz obraz tła",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
        )
        if (file_path):
            self.custom_bg_path = file_path
            self.bg_rotation = 0
            self.bg_scale = 1.0
            self.bg_translate_x = 0
            self.bg_translate_y = 0
            self.update_preview()
    
    def select_save_directory(self):
        dir_path = filedialog.askdirectory(title="Wybierz katalog zapisu")
        if dir_path:
            self.save_directory = dir_path
            self.save_dir_label.config(text=f"Katalog zapisu: {self.save_directory}")
    
    def toggle_color_frame(self):
        if self.color_frame_visible:
            self.color_frame.pack_forget()
            self.color_frame_visible = False
        else:
            self.color_frame.pack(padx=10, pady=5)
            for widget in self.color_frame.winfo_children():
                widget.destroy()
            for col in ["black", "white", "red", "green", "blue", "yellow"]:
                tk.Button(self.color_frame, text=col, bg=col, command=lambda c=col: self.change_text_color(c),
                          fg="white").pack(side=tk.LEFT, padx=5)
            self.color_frame_visible = True
    
    def change_text_color(self, color):
        self.variable_text_color = color
        self.update_preview()
    
    # Funkcje transformacji tła
    def translate_left(self):
        self.bg_translate_x -= 10
        self.update_preview()
    def translate_right(self):
        self.bg_translate_x += 10
        self.update_preview()
    def translate_up(self):
        self.bg_translate_y -= 10
        self.update_preview()
    def translate_down(self):
        self.bg_translate_y += 10
        self.update_preview()
    def scale_down(self):
        self.bg_scale = max(0.1, self.bg_scale - 0.1)
        self.update_preview()
    def scale_up(self):
        self.bg_scale += 0.1
        self.update_preview()
    
    # Funkcje obracania tła
    def rotate_left(self):
        self.bg_rotation = (self.bg_rotation - 10) % 360
        self.update_preview()
    def rotate_right(self):
        self.bg_rotation = (self.bg_rotation + 10) % 360
        self.update_preview()
    
    # Obsługa klawiatury
    def on_key_left(self, event):
        self.bg_translate_x -= 10
        self.update_preview()
    def on_key_right(self, event):
        self.bg_translate_x += 10
        self.update_preview()
    def on_key_up(self, event):
        self.bg_translate_y -= 10
        self.update_preview()
    def on_key_down(self, event):
        self.bg_translate_y += 10
        self.update_preview()
    def on_key_plus(self, event):
        self.bg_scale += 0.1
        self.update_preview()
    def on_key_minus(self, event):
        self.bg_scale = max(0.1, self.bg_scale - 0.1)
        self.update_preview()
    def on_key_l(self, event):
        self.rotate_left()
    def on_key_p(self, event):
        self.rotate_right()
    
    def create_token_image(self, custom_size=None, token_name=None):
        if (custom_size is not None):
            width = height = custom_size
        else:
            width = height = (self.hex_token_size_var.get() if self.shape.get() == "Heks" 
                              else self.square_token_size_var.get())
        # Na najniższej warstwie umieszczam flagę nacji
        base_bg = create_flag_background(self.nation.get(), width, height)
        # Jeśli jest niestandardowe tło, nakładam je na flagę
        if (self.custom_bg_path is not None):
            try:
                custom_bg = Image.open(self.custom_bg_path).convert("RGBA")
                new_size = (int(custom_bg.width * self.bg_scale), int(custom_bg.height * self.bg_scale))
                custom_bg = custom_bg.resize(new_size, Image.LANCZOS)
                custom_bg = custom_bg.rotate(self.bg_rotation, expand=True, resample=Image.BICUBIC)
                paste_x = (width - custom_bg.width) // 2 + self.bg_translate_x
                paste_y = (height - custom_bg.height) // 2 + self.bg_translate_y
                base_bg.paste(custom_bg, (paste_x, paste_y), custom_bg)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można załadować obrazu tła:\n{e}")
        bg_image = base_bg
    
        token_img = bg_image.copy()
        draw = ImageDraw.Draw(token_img)
    
        # Rysowanie prostokątnego obramowania
        draw.rectangle([0, 0, width, height], outline="black", width=3)
    
        # Domyślne kolory dla nacji – zmieniono Wielka Brytania na black
        default_colors = {
            "Polska": "black",
            "Niemcy": "blue",
            "Wielka Brytania": "black",
            "Japonia": "black",
            "Stany Zjednoczone": "black",
            "Francja": "black",
            "Związek Radziecki": "white"
        }
        text_color = self.variable_text_color if self.variable_text_color else default_colors.get(self.nation.get(), "black")
    
        margin = 5
        small_font_size = max(8, int(width * 0.15))
        def get_font(font_name, size):
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                return ImageFont.load_default()
        font_small = get_font("arial.ttf", small_font_size)
    
        # Przygotowanie tekstu – trzy wiersze
        row_top_text = f"{self.combat_value.get()}-{self.supply_points.get()}-{self.purchase_value.get()}"
        row_bottom_text = f"{self.movement_points.get()}-{self.attack_range.get()}-{self.attack_value.get()}"
        unit_size = self.unit_size.get()
        if unit_size == "Pluton":
            unit_symbol = "***"
        elif unit_size == "Kompania":
            unit_symbol = "I"
        elif unit_size == "Batalion":
            unit_symbol = "II"
        else:
            unit_symbol = ""
        row_middle_text = unit_symbol
    
        bbox_top = draw.textbbox((0, 0), row_top_text, font=font_small)
        bbox_bottom = draw.textbbox((0, 0), row_bottom_text, font=font_small)
        bbox_middle = draw.textbbox((0, 0), row_middle_text, font=font_small)
    
        row_top_y = margin
        offset = 5
        row_bottom_y = height - margin - (bbox_bottom[3] - bbox_bottom[1]) - offset
        row_middle_y = row_bottom_y - margin - (bbox_middle[3] - bbox_middle[1]) - offset
    
        row_top_x = (width - (bbox_top[2] - bbox_top[0])) / 2
        row_middle_x = (width - (bbox_middle[2] - bbox_middle[0])) / 2
        row_bottom_x = (width - (bbox_bottom[2] - bbox_bottom[0])) / 2
    
        draw.text((row_top_x, row_top_y), row_top_text, fill=text_color, font=font_small)
        draw.text((row_middle_x, row_middle_y), row_middle_text, fill=text_color, font=font_small)
        draw.text((row_bottom_x, row_bottom_y), row_bottom_text, fill=text_color, font=font_small)
    
        if token_name is not None:
            try:
                name_font_size = max(8, int(width * 0.15))
                font_name = get_font("arial.ttf", name_font_size)
            except Exception:
                font_name = ImageFont.load_default()
            bbox_name = draw.textbbox((0, 0), token_name, font=font_name)
            new_height = height + margin + (bbox_name[3] - bbox_name[1])
            new_img = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))
            new_img.paste(token_img, (0, 0))
            draw_new = ImageDraw.Draw(new_img)
            name_x = (width - (bbox_name[2] - bbox_name[0])) / 2
            draw_new.text((name_x, height + margin), token_name, fill=text_color, font=font_name)
            token_img = new_img
    
        return token_img
    
    def save_token(self):
        final_size = self.hex_token_size_var.get() if self.shape.get() == "Heks" else self.square_token_size_var.get()
        prefix = self.nation.get()
        default_suffix = f"{self.unit_type.get()} {self.unit_size.get()}"
        name_suffix = simpledialog.askstring("Nazwa Żetonu",
                                             f"Podaj nazwę tokena (prefiks '{prefix}' jest niemienny):",
                                             initialvalue=default_suffix)
        if not name_suffix:
            messagebox.showwarning("Brak nazwy", "Musisz podać nazwę tokena.")
            return
        token_name = f"{prefix} {name_suffix}"
        token_img = self.create_token_image(custom_size=None, token_name=token_name)
        png_path = os.path.join(self.save_directory, f"{token_name}.png")
        token_img.save(png_path)
    
        json_path = os.path.join(self.save_directory, "token_data.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
        else:
            saved_data = {}
        saved_data[token_name] = {
            "shape": self.shape.get(),
            "nation": self.nation.get(),
            "unit_type": self.unit_type.get(),
            "unit_size": self.unit_size.get(),
            "movement_points": self.movement_points.get(),
            "attack_range": self.attack_range.get(),
            "attack_value": self.attack_value.get(),
            "combat_value": self.combat_value.get(),
            "supply_points": self.supply_points.get(),
            "purchase_value": self.purchase_value.get(),
            "png_path": png_path,
            "width": final_size,
            "height": final_size,
            "bg_rotation": self.bg_rotation,
            "bg_scale": self.bg_scale,
            "bg_translate_x": self.bg_translate_x,
            "bg_translate_y": self.bg_translate_y,
            "variable_text_color": self.variable_text_color
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(saved_data, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Zapisano", f"Żeton '{token_name}' został zapisany.\nPlik PNG i metadane (JSON) znajdują się w:\n{self.save_directory}")
    
    def clear_database(self):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz wyczyścić bazę żetonów?"):
            json_path = os.path.join(self.save_directory, "token_data.json")
            if os.path.exists(json_path):
                os.remove(json_path)
            for file in os.listdir(self.save_directory):
                if file.endswith(".png"):
                    os.remove(os.path.join(self.save_directory, file))
            messagebox.showinfo("Baza wyczyszczona", "Baza żetonów oraz miniatury została wyczyszczona.")

def main():
    root = tk.Tk()
    app = TokenEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
