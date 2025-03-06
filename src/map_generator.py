import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import math
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from datetime import datetime

# ----------------------------
# Konfiguracja rodzajów terenu
# ----------------------------
# Rozszerzenie struktury danych terenu
TERRAIN_TYPES = {
    "teren_płaski": {
        "move_mod": 0, 
        "defense_mod": 0,
        "type": "open",
        "passable": True,
        "cover": 0,
        "supply_cost": 1
    },
    "mała rzeka": {
        "move_mod": -2, 
        "defense_mod": 1,
        "type": "water",
        "passable": True,
        "cover": 1,
        "supply_cost": 2,
        "cross_points": []  # Lista punktów przepraw
    },
    "duża rzeka": {
        "move_mod": -4, 
        "defense_mod": -1,
        "type": "water",
        "passable": False,
        "cover": 0,
        "supply_cost": 3,
        "cross_points": []  # Lista punktów przepraw
    },
    "las": {
        "move_mod": -2, 
        "defense_mod": 2,
        "type": "forest",
        "passable": True,
        "cover": 2,
        "supply_cost": 2,
        "blocks_los": True  # Blokuje linię widzenia
    },
    "bagno": {
        "move_mod": -3, 
        "defense_mod": 1,
        "type": "swamp",
        "passable": True,
        "cover": 1,
        "supply_cost": 3,
        "blocks_heavy": True  # Blokuje ciężki sprzęt
    },
    "mała miejscowość": {
        "move_mod": -2, 
        "defense_mod": 2,
        "type": "urban",
        "passable": True,
        "cover": 2,
        "supply_cost": 1,
        "victory_points": 1
    },
    "miasto": {
        "move_mod": -2, 
        "defense_mod": 2,
        "type": "urban",
        "passable": True,
        "cover": 3,
        "supply_cost": 1,
        "victory_points": 3
    },
    "most": {
        "move_mod": 0, 
        "defense_mod": 0,
        "type": "bridge",
        "passable": True,
        "cover": 0,
        "supply_cost": 1,
        "strategic_value": True
    }
}

# Plik z danymi heksów – upewnij się, że katalog istnieje
DATA_FILENAME_WORKING = r"C:\Users\klif\OneDrive\Pulpit\kampania_wrzesniowa\tests\dane_terenow_hexow_working.json"
data_dir = os.path.dirname(DATA_FILENAME_WORKING)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

default_hex_size = 30  # wartość domyślna, jeśli nie uda się wczytać konfiguracji

# Zmodyfikowane funkcje zapisu/odczytu – zapisują również rozmiar heksu
def zapisz_dane_hex(hex_data, hex_size, filename=DATA_FILENAME_WORKING):
    """Rozszerzona funkcja zapisu danych"""
    data_to_save = {
        "map_metadata": {
            "hex_size": hex_size,
            "creation_date": datetime.now().isoformat(),
            "map_name": os.path.basename(CONFIG["map_settings"]["map_image_path"]),
            "map_dimensions": {
                "width": editor.world_width if 'editor' in globals() else 800,
                "height": editor.world_height if 'editor' in globals() else 600
            },
            "last_modified": datetime.now().isoformat()
        },
        "terrain_types": TERRAIN_TYPES,
        "hex_data": {}
    }
    
    # Rozbudowane dane dla każdego heksa
    for hex_id, terrain in hex_data.items():
        if hex_id in editor.hex_centers:
            x, y = editor.hex_centers[hex_id]
            data_to_save["hex_data"][hex_id] = {
                "terrain": terrain,
                "position": {"x": x, "y": y},
                "connections": get_hex_connections(hex_id),
                "strategic_points": get_strategic_points(hex_id),
                "attributes": {
                    "passable": terrain.get("passable", True),
                    "blocks_los": terrain.get("blocks_los", False),
                    "blocks_heavy": terrain.get("blocks_heavy", False),
                    "victory_points": terrain.get("victory_points", 0)
                }
            }
    
    # Dodaj funkcję weryfikacji przed zapisem
    if verify_data_completeness(data_to_save):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        return True
    return False

def verify_data_completeness(data):
    """Sprawdza czy wszystkie wymagane dane są obecne"""
    required_fields = {
        "map_metadata": ["hex_size", "creation_date", "map_name", "map_dimensions"],
        "terrain_types": list(TERRAIN_TYPES.keys()),
        "hex_data": ["terrain", "position", "connections", "strategic_points"]
    }
    
    try:
        # Sprawdź metadane
        for field in required_fields["map_metadata"]:
            if field not in data["map_metadata"]:
                print(f"Brak wymaganego pola w metadanych: {field}")
                return False
                
        # Sprawdź typy terenu
        if not all(terrain in data["terrain_types"] for terrain in required_fields["terrain_types"]):
            print("Brak niektórych typów terenu")
            return False
            
        # Sprawdź dane heksów
        for hex_id, hex_data in data["hex_data"].items():
            for field in required_fields["hex_data"]:
                if field not in hex_data:
                    print(f"Brak wymaganego pola w heksie {hex_id}: {field}")
                    return False
                    
        return True
    except Exception as e:
        print(f"Błąd weryfikacji danych: {e}")
        return False

def get_hex_connections(hex_id):
    """Zwraca informacje o połączeniach z sąsiednimi heksami"""
    if 'editor' not in globals():
        return []
    
    col, row = map(int, hex_id.split('_'))
    connections = []
    
    # Obliczanie ID sąsiednich heksów
    neighbors = [
        f"{col}_{row-1}",   # góra
        f"{col+1}_{row}",   # prawo-góra
        f"{col+1}_{row+1}", # prawo-dół
        f"{col}_{row+1}",   # dół
        f"{col-1}_{row+1}", # lewo-dół
        f"{col-1}_{row}"    # lewo-góra
    ]
    
    for neighbor in neighbors:
        if neighbor in editor.hex_data:
            terrain = editor.hex_data[neighbor]
            connections.append({
                "to": neighbor,
                "passable": terrain.get("passable", True),
                "cost": terrain.get("move_mod", 0)
            })
    
    return connections

def get_strategic_points(hex_id):
    """Zwraca informacje o punktach strategicznych w heksie"""
    if 'editor' not in globals():
        return []
    
    strategic_points = []
    terrain = editor.hex_data.get(hex_id, {})
    
    if terrain.get("type") in ["urban", "bridge"]:
        strategic_points.append({
            "type": terrain["type"],
            "victory_points": terrain.get("victory_points", 0),
            "strategic_value": terrain.get("strategic_value", False)
        })
    
    return strategic_points

def wczytaj_dane_hex(filename=DATA_FILENAME_WORKING):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Jeśli dane są w nowym formacie (z hex_data)
        if isinstance(data, dict) and "hex_data" in data:
            hex_data = data["hex_data"]
            # Upewnij się, że każdy heks ma wszystkie wymagane pola
            for hex_id in hex_data:
                if not isinstance(hex_data[hex_id], dict):
                    hex_data[hex_id] = TERRAIN_TYPES["teren_płaski"]
                elif "terrain" in hex_data[hex_id]:
                    if not isinstance(hex_data[hex_id]["terrain"], dict):
                        hex_data[hex_id] = TERRAIN_TYPES["teren_płaski"]
                    else:
                        # Uzupełnij brakujące pola z domyślnego terenu
                        default_terrain = TERRAIN_TYPES["teren_płaski"]
                        for key in default_terrain:
                            if key not in hex_data[hex_id]["terrain"]:
                                hex_data[hex_id]["terrain"][key] = default_terrain[key]
                else:
                    hex_data[hex_id] = TERRAIN_TYPES["teren_płaski"]
            return hex_data, data.get("hex_size", default_hex_size)
        else:
            # Stary format lub nieprawidłowe dane
            return {}, default_hex_size
    except FileNotFoundError:
        return {}, default_hex_size
    except Exception as e:
        print(f"Błąd wczytywania danych: {e}")
        return {}, default_hex_size

# ----------------------------
# Konfiguracja mapy (zapisana w konfiguracji)
# ----------------------------
MAPS_DIRECTORY = r"C:\Users\klif\OneDrive\Pulpit\kampania_wrzesniowa\mapy"
if not os.path.exists(MAPS_DIRECTORY):
    os.makedirs(MAPS_DIRECTORY)

CONFIG_FILE = r"C:\Users\klif\OneDrive\Pulpit\kampania_wrzesniowa\map_editor_config.json"
DEFAULT_CONFIG = {
    "map_settings": {
        "maps_directory": MAPS_DIRECTORY,
        "map_image_path": "",  # Będzie ustawione podczas inicjalizacji
        "hex_size": 30
    }
}

def load_default_map():
    """Wczytuje pierwszą znalezioną mapę z katalogu lub pozwala wybrać jedną z wielu."""
    maps = [f for f in os.listdir(MAPS_DIRECTORY) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not maps:
        messagebox.showwarning("Brak map", 
            f"Nie znaleziono map w katalogu:\n{MAPS_DIRECTORY}\nProszę dodać pliki map do tego katalogu.")
        return None
    
    if len(maps) == 1:
        return os.path.join(MAPS_DIRECTORY, maps[0])
    else:
        # Jeśli jest więcej map, pokazujemy okno wyboru
        root = tk.Tk()
        root.withdraw()  # Ukrywa główne okno
        
        dialog = tk.Toplevel(root)
        dialog.title("Wybór mapy")
        dialog.geometry("400x300")
        
        label = tk.Label(dialog, text="Wybierz mapę do wczytania:")
        label.pack(pady=10)
        
        selected_map = tk.StringVar()
        
        for map_name in maps:
            tk.Radiobutton(dialog, text=map_name, 
                          variable=selected_map, 
                          value=map_name).pack(anchor='w', padx=20)
        
        def confirm():
            dialog.quit()
        
        tk.Button(dialog, text="Wybierz", command=confirm).pack(pady=20)
        
        dialog.protocol("WM_DELETE_WINDOW", confirm)  # Obsługa zamknięcia okna
        dialog.transient(root)
        dialog.grab_set()
        dialog.mainloop()
        
        selected = selected_map.get()
        dialog.destroy()
        root.destroy()
        
        if selected:
            return os.path.join(MAPS_DIRECTORY, selected)
        return None

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception as e:
            messagebox.showerror("Błąd konfiguracji", f"Nie udało się wczytać konfiguracji: {e}")
    
    # Sprawdź czy mapa istnieje, jeśli nie - wczytaj domyślną
    if not os.path.exists(config["map_settings"]["map_image_path"]):
        default_map = load_default_map()
        if default_map:
            config["map_settings"]["map_image_path"] = default_map
    
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Błąd konfiguracji", f"Nie udało się zapisać konfiguracji: {e}")

CONFIG = load_config()

# ----------------------------
# Funkcja pomocnicza: punkt w wielokącie (ray-casting)
# ----------------------------
def point_in_polygon(x, y, poly):
    num = len(poly)
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
           (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1] + 1e-10) + poly[i][0]):
            c = not c
        j = i
    return c

def get_hex_vertices(center_x, center_y, s):
    return [
        (center_x - s, center_y),
        (center_x - s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s/2, center_y - (math.sqrt(3)/2)*s),
        (center_x + s, center_y),
        (center_x + s/2, center_y + (math.sqrt(3)/2)*s),
        (center_x - s/2, center_y + (math.sqrt(3)/2)*s)
    ]

# ----------------------------
# Klasa interaktywnego edytora mapy
# ----------------------------
class MapEditor:
    def __init__(self, root, config):
        self.root = root
        # Odczyt konfiguracji mapy
        self.config = config["map_settings"]
        self.hex_size = self.config.get("hex_size", 30)
        self.map_image_path = self.config.get("map_image_path")
        
        # Initialize default values
        self.world_width = 800
        self.world_height = 600
        self.photo_bg = None
        self.bg_image = None
        
        # Załaduj obraz mapy przed stworzeniem interfejsu
        if not self.load_map_image_from_path(self.map_image_path):
            messagebox.showerror("Błąd", "Nie można załadować obrazu mapy. Używam domyślnych wymiarów.")
            self.bg_image = Image.new('RGB', (self.world_width, self.world_height), 'white')
            self.photo_bg = ImageTk.PhotoImage(self.bg_image)
        
        # Initialize other attributes
        self.hex_data, saved_hex_size = wczytaj_dane_hex()
        self.hex_centers = {}
        self.selected_hex = None

        # Ustawienie kolorów tła i ogólnego wyglądu
        self.root.configure(bg="darkolivegreen")
        
        # Modyfikacja szerokości ramki głównej z nowymi kolorami
        self.main_frame = tk.Frame(root, bd=5, relief=tk.RAISED, bg="darkolivegreen")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas_frame = tk.Frame(self.main_frame, bg="darkolivegreen")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Szersze suwaki do przesuwania mapy
        self.vbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, width=20)  # Zwiększono width z domyślnego ~16 na 20
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, width=20)  # Zwiększono width z domyślnego ~16 na 20
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800, height=600,
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, self.world_width, self.world_height)
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.hbar.config(command=self.canvas.xview)
        self.vbar.config(command=self.canvas.yview)
        
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
        
        # Bind lewego przycisku dla zaznaczania heksu
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        # Bind prawego przycisku dla menu kontekstowego
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        # Pozostałe zdarzenia (np. panning)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        
        # Ramka sterująca umieszczona w dolnym prawym rogu
        self.control_frame = tk.Frame(self.root, bd=2, relief=tk.RIDGE, bg="darkolivegreen")
        self.control_frame.place(relx=1, rely=1, anchor="se")
        
        # Aktualizacja stylu przycisków
        button_style = {
            'bg': 'saddlebrown',
            'fg': 'white',
            'activebackground': 'saddlebrown',
            'activeforeground': 'white',
            'padx': 5,
            'pady': 5
        }
        
        tk.Button(self.control_frame, text="Reset mapy", command=self.clear_variables, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.control_frame, text="Zapisz Mapę", command=self.save_map_as_image, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.control_frame, text="Ustaw rozmiar heksów", command=self.change_hex_size, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.control_frame, text="Pobierz obraz mapy", command=self.load_new_map, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.control_frame, text="Wyjście", command=self.exit_editor, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.draw_grid()
    
    def load_map_image_from_path(self, path):
        try:
            self.bg_image = Image.open(path).convert("RGB")
            self.world_width, self.world_height = self.bg_image.size
            self.photo_bg = ImageTk.PhotoImage(self.bg_image)
            return True
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu:\n{e}")
            self.bg_image = Image.new('RGB', (self.world_width, self.world_height), 'white')
            self.photo_bg = ImageTk.PhotoImage(self.bg_image)
            return False
    
    def load_new_map(self):
        initial_dir = self.config.get("maps_directory", MAPS_DIRECTORY)
        file_path = filedialog.askopenfilename(
            title="Wybierz obraz mapy",
            initialdir=initial_dir,
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp"), ("Wszystkie pliki", "*.*")]
        )
        if file_path:
            self.map_image_path = file_path
            self.config["map_image_path"] = file_path
            save_config(CONFIG)
            self.load_map_image_from_path(file_path)
            self.canvas.config(scrollregion=(0, 0, self.world_width, self.world_height))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
            self.draw_grid()
    
    def draw_grid(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_bg)
        self.hex_centers.clear()
        
        s = self.hex_size
        hex_height = math.sqrt(3) * s
        horizontal_spacing = 1.5 * s
        
        # Obliczamy liczbę kolumn i wierszy, aby pokryć całą mapę
        grid_cols = math.ceil((self.world_width - s) / horizontal_spacing) + 1
        grid_rows = math.ceil((self.world_height - (s * math.sqrt(3)/2)) / hex_height) + 1
        
        for col in range(grid_cols):
            center_x = s + col * horizontal_spacing
            for row in range(grid_rows):
                center_y = (s * math.sqrt(3)/2) + row * hex_height
                if col % 2 == 1:
                    center_y += hex_height/2
                if center_x + s > self.world_width or center_y + (s * math.sqrt(3)/2) > self.world_height:
                    continue
                hex_id = f"{col}_{row}"
                self.hex_centers[hex_id] = (center_x, center_y)
                if hex_id not in self.hex_data:
                    self.hex_data[hex_id] = TERRAIN_TYPES["teren_płaski"]
                terrain = self.hex_data[hex_id]
                self.draw_hex(hex_id, center_x, center_y, s, terrain)
        
        if self.selected_hex is not None:
            self.highlight_hex(self.selected_hex)
        
        self.print_extreme_hexes()  # Wywołanie metody wyświetlającej skrajne heksy
    
    def draw_hex(self, hex_id, center_x, center_y, s, terrain=None):
        points = get_hex_vertices(center_x, center_y, s)
        self.canvas.create_polygon(points, outline="red", fill="", width=2, tags=hex_id)
        
        if terrain:
            # Sprawdź czy terrain jest słownikiem i czy zawiera wymagane pola
            if isinstance(terrain, dict):
                # Jeśli dane są w nowej strukturze (z polem "terrain")
                if "terrain" in terrain:
                    terrain = terrain["terrain"]
                
                # Pobierz wartości z odpowiednimi wartościami domyślnymi
                move_mod = terrain.get("move_mod", 0)
                defense_mod = terrain.get("defense_mod", 0)
                tekst = f"M:{move_mod} D:{defense_mod}"
            else:
                # Jeśli terrain nie jest słownikiem, użyj wartości domyślnych
                tekst = "M:0 D:0"
        else:
            tekst = ""
            
        font_size = max(8, int(s/3))
        self.canvas.delete(f"tekst_{hex_id}")
        self.canvas.create_text(center_x, center_y, text=tekst, fill="blue",
                              font=("Arial", font_size), anchor="center", tags=f"tekst_{hex_id}")
    
    def on_canvas_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_hex = None
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                clicked_hex = hex_id
                break
        if clicked_hex:
            self.selected_hex = clicked_hex
            self.highlight_hex(clicked_hex)
        else:
            messagebox.showinfo("Informacja", "Kliknij wewnątrz heksagonu.")
    
    def on_canvas_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_hex = None
        for hex_id, (cx, cy) in self.hex_centers.items():
            vertices = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, vertices):
                clicked_hex = hex_id
                break
        if clicked_hex:
            self.selected_hex = clicked_hex
            self.highlight_hex(clicked_hex)
            menu = tk.Menu(self.root, tearoff=0, bg="darkolivegreen", fg="white", activebackground="saddlebrown", activeforeground="white")
            for terrain_key in TERRAIN_TYPES.keys():
                menu.add_command(
                    label=terrain_key,
                    command=lambda t=terrain_key: self.apply_terrain(t)
                )
            menu.post(event.x_root, event.y_root)
        else:
            messagebox.showinfo("Informacja", "Kliknij wewnątrz heksagonu.")
    
    def highlight_hex(self, hex_id):
        self.canvas.delete("highlight")
        if (hex_id in self.hex_centers):
            cx, cy = self.hex_centers[hex_id]
            s = self.hex_size
            self.canvas.create_oval(cx - s, cy - s, cx + s, cy + s,
                                    outline="yellow", width=3, tags="highlight")
    
    def apply_terrain(self, terrain_key):
        if self.selected_hex is None:
            messagebox.showinfo("Informacja", "Najpierw wybierz heks klikając na niego.")
            return
        terrain = TERRAIN_TYPES.get(terrain_key)
        if terrain:
            self.hex_data[self.selected_hex] = terrain
            zapisz_dane_hex(self.hex_data, self.hex_size)
            cx, cy = self.hex_centers[self.selected_hex]
            self.draw_hex(self.selected_hex, cx, cy, self.hex_size, terrain)
            messagebox.showinfo("Zapisano", f"Dla heksu {self.selected_hex} ustawiono: {terrain_key}")
        else:
            messagebox.showerror("Błąd", "Niepoprawny rodzaj terenu.")
    
    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)
    
    def do_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    
    def save_data(self):
        zapisz_dane_hex(self.hex_data, self.hex_size)
        messagebox.showinfo("Zapisano", "Dane terenu zostały zapisane.")
    
    def save_map_as_image(self):
        img = self.bg_image.copy()
        draw = ImageDraw.Draw(img)
        s = self.hex_size
        
        # Wczytaj ostatnią ścieżkę zapisu z konfiguracji lub użyj domyślnej
        last_save_path = self.config.get("last_save_path", self.config.get("maps_directory", MAPS_DIRECTORY))
        
        # Pozwól użytkownikowi wybrać lokalizację zapisu
        output_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            initialdir=os.path.dirname(last_save_path),
            title="Zapisz mapę jako...",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if output_path:  # Jeśli użytkownik nie anulował wyboru
            try:
                # Zapisz obraz mapy
                img.save(output_path)
                
                # Zapamiętaj ścieżkę zapisu w konfiguracji
                self.config["last_save_path"] = output_path
                save_config({"map_settings": self.config})
                
                # Przygotuj i zapisz plik JSON z tą samą nazwą co mapa
                json_path = os.path.splitext(output_path)[0] + ".json"
                
                # Rozszerzona struktura danych do zapisu
                data_to_save = {
                    "map_metadata": {
                        "hex_size": self.hex_size,
                        "creation_date": datetime.now().isoformat(),
                        "last_modified": datetime.now().isoformat(),
                        "map_name": os.path.basename(output_path),
                        "map_path": output_path,
                        "map_dimensions": {
                            "width": self.world_width,
                            "height": self.world_height
                        }
                    },
                    "terrain_types": TERRAIN_TYPES,
                    "hex_data": {}
                }
                
                # Zapisz dane każdego heksa
                for hex_id, terrain in self.hex_data.items():
                    if hex_id in self.hex_centers:
                        x, y = self.hex_centers[hex_id]
                        data_to_save["hex_data"][hex_id] = {
                            "terrain": terrain,
                            "position": {"x": x, "y": y},
                            "connections": get_hex_connections(hex_id),
                            "strategic_points": get_strategic_points(hex_id),
                            "attributes": {
                                "passable": terrain.get("passable", True),
                                "blocks_los": terrain.get("blocks_los", False),
                                "blocks_heavy": terrain.get("blocks_heavy", False),
                                "victory_points": terrain.get("victory_points", 0),
                                "move_mod": terrain.get("move_mod", 0),
                                "defense_mod": terrain.get("defense_mod", 0),
                                "supply_cost": terrain.get("supply_cost", 1)
                            }
                        }
                
                # Zapisz dane JSON
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Zapisano", 
                    f"Mapa została zapisana jako:\n{output_path}\n\n"
                    f"Dane terenów zapisano jako:\n{json_path}")
                    
            except Exception as e:
                messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać plików:\n{str(e)}")
    
    def load_data(self):
        self.hex_data, saved_hex_size = wczytaj_dane_hex()
        self.draw_grid()
        messagebox.showinfo("Wczytano", "Dane terenu zostały wczytane.")
    
    def clear_variables(self):
        answer = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zresetować mapę do domyślnego terenu płaskiego?")
        if answer:
            for hex_id in self.hex_centers.keys():
                self.hex_data[hex_id] = TERRAIN_TYPES["teren_płaski"]
            zapisz_dane_hex(self.hex_data, self.hex_size)
            self.draw_grid()
            messagebox.showinfo("Zresetowano", "Mapa została zresetowana do domyślnego terenu płaskiego.")
    
    def print_extreme_hexes(self):
        # Metoda do wyświetlania skrajnych heksów w konsoli
        if not self.hex_centers:
            print("Brak heksów do analizy.")
            return
        xs = [coord[0] for coord in self.hex_centers.values()]
        ys = [coord[1] for coord in self.hex_centers.values()]
        leftmost = min(xs)
        rightmost = max(xs)
        topmost = min(ys)
        bottommost = max(ys)
        print("Skrajne heksy:")
        print("Lewy skrajny: (x =", leftmost, ")")
        print("Prawy skrajny: (x =", rightmost, ")")
        print("Górny skrajny: (y =", topmost, ")")
        print("Dolny skrajny: (y =", bottommost, ")")
    
    def change_hex_size(self):
        new_size = simpledialog.askinteger("Ustaw rozmiar heksów",
                                            "Podaj nowy rozmiar heksu (w pikselach):",
                                            initialvalue=self.hex_size,
                                            minvalue=10, maxvalue=200)
        if new_size:
            self.hex_size = new_size
            self.config["hex_size"] = new_size
            save_config(CONFIG)
            self.draw_grid()
    
    def exit_editor(self):
        answer = messagebox.askyesnocancel(
            "Wyjście",
            "Czy chcesz zapisać dane przed wyjściem?\nWybierz 'Tak' aby zapisać i wyjść, 'Nie' aby wyjść bez zapisu, lub 'Anuluj' aby pozostać w edytorze."
        )
        if answer is True:
            self.save_data()
            self.save_map_as_image()
            self.root.destroy()
        elif answer is False:
            self.root.destroy()
        # Jeśli Anuluj (None) – pozostajemy w edytorze

# ----------------------------
# Uruchomienie interfejsu
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Interaktywny Edytor Mapy Heksagonalnej")
    editor = MapEditor(root, CONFIG)
    root.mainloop()
