"""
gravedad.py

Guillem Perez Sanchez
QP 2025
"""
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, colorchooser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import json
import random
import math

G = 1.0
FPS = 60
dt = 0.1

SIM_WIDTH = 800
PANEL_WIDTH = 400
HEIGHT = 700

class CuerpoCeleste:
    def __init__(self, x, y, mass, size=5, color="#FFFF64", vx=0, vy=0, cola=False, forma="o"):
        """
        Inicializa un cuerpo celeste con posición, masa, tamaño, color, velocidad, si deja cola y forma.
        """
        self.x = x
        self.y = y
        self.mass = mass
        self.size = size
        self.color = color
        self.vx = vx
        self.vy = vy
        self.cola = cola
        self.forma = forma
        self.trail = []

    def update(self, others, G, dt):
        """
        Actualiza la posición y velocidad del cuerpo aplicando la ley de gravitación universal.
        """
        ax = ay = 0
        for other in others:
            if other is self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = dx*dx + dy*dy + 1e-5
            force = G * self.mass * other.mass / dist_sq
            dist = math.sqrt(dist_sq)
            ax += force * dx / dist / self.mass
            ay += force * dy / dist / self.mass

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.cola:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 50:
                self.trail.pop(0)

class SimulatorApp:
    def __init__(self, root):
        """
        Inicializa la interfaz de la aplicación y los parámetros de la simulación.
        """
        self.root = root
        self.root.title("Simulador Gravitacional")
        self.style = ttk.Style("superhero")  # Puedes cambiar el tema: 'flatly', 'cyborg', 'journal', etc.

        self.bodies = []
        self.running = False

        self.G = G
        self.fps = FPS
        self.dt = dt

        # Canvas principal
        self.canvas = ttk.Canvas(root, width=SIM_WIDTH, height=HEIGHT)
        self.canvas.pack(side=LEFT)

        # Panel lateral
        self.panel = ttk.Frame(root, width=PANEL_WIDTH, padding=10)
        self.panel.pack(side=RIGHT, fill=Y)

        # Barra superior de mensajes
        self.msg_label = ttk.Label(root, text="", font=("Arial", 12, "bold"), anchor=CENTER, bootstyle="info")
        self.msg_label.pack(side=TOP, fill=X)

        self.create_menu()
        self.create_controls()
        self.root.after(int(1000/self.fps), self.update_simulation)

    def create_menu(self):
        """
        Crea la barra de menú con opciones de archivo y ayuda.
        """
        menubar = ttk.Menu(self.root)

        archivo_menu = ttk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Guardar constelaciones...", command=self.guardar_constelacion)
        archivo_menu.add_command(label="Cargar constelaciones...", command=self.cargar_constelacion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Terminar", command=self.terminar)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        ayuda_menu = ttk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_ayuda)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menubar)

    def create_controls(self):
        """
        Crea los botones de control y sliders de parámetros en el panel lateral.
        """
        btn_style = {"bootstyle": "primary", "width": 25}

        botones = [
            ("▶ Iniciar", self.iniciar, "success"),
            ("⏸ Pausar", self.pausar, "danger"),
            ("🔄 Resetear", self.resetear, "info"),
            ("➕ Añadir cuerpo", self.abrir_añadir_cuerpo, "purple"),
            ("🎲 Añadir cuerpos aleatorios", self.añadir_varios_cuerpos, "warning"),
            ("❌ Terminar", self.terminar, "secondary"),
        ]

        for text, cmd, style in botones:
            b = ttk.Button(self.panel, text=text, command=cmd, bootstyle=style, **btn_style)
            b.pack(pady=6)

        self._crear_slider("FPS", 1, 120, self.fps, self.modificar_fps)
        self._crear_slider("Gravedad (G)", 0.1, 10, self.G, self.modificar_g, 0.1)
        self._crear_slider("Delta tiempo (dt)", 0.01, 1, self.dt, self.modificar_dt, 0.01)

    def _crear_slider(self, label, from_, to, initial, cmd, res=1):
        """
        Crea un slider con etiqueta en el panel lateral.
        """
        ttk.Label(self.panel, text=label, font=("Arial", 11, "bold")).pack(pady=(10, 0))
        slider = ttk.Scale(self.panel, from_=from_, to=to, orient=HORIZONTAL, command=lambda v: cmd(v), length=300, bootstyle="info")
        slider.set(initial)
        slider.pack()
        
    def modificar_fps(self, val):
        """
        Cambia los FPS (frames por segundo) de la simulación.
        """
        self.fps = int(val); self.mostrar_mensaje(f"FPS ajustado a {self.fps}")
        
    def modificar_g(self, val):
        """
        Ajusta la constante de gravitación G.
        """
        self.G = float(val); self.mostrar_mensaje(f"Gravedad ajustada a {self.G:.2f}")
        
    def modificar_dt(self, val):
        """
        Ajusta el incremento de tiempo (delta t) por frame.
        """
        self.dt = float(val); self.mostrar_mensaje(f"Delta tiempo ajustado a {self.dt:.2f}")

    def mostrar_mensaje(self, texto):
        """
        Muestra un mensaje en la barra superior.
        """
        self.msg_label.config(text=texto)

    def iniciar(self):
        """
        Inicia la simulación si hay al menos un cuerpo presente. Cambia el estado a 'running'.
        """
        if not self.bodies:
            self.mostrar_mensaje("Añade al menos un cuerpo para iniciar")
            return
        self.running = True
        self.mostrar_mensaje("Simulación iniciada")

    def pausar(self):
        """
        Pausa la simulación.
        """
        self.running = False; self.mostrar_mensaje("Simulación pausada")
        
    def resetear(self):
        """
        Reinicia la simulación eliminando todos los cuerpos.
        """
        self.bodies.clear(); self.canvas.delete("all"); self.running = False; self.mostrar_mensaje("Simulación reiniciada y cuerpos eliminados")

    def abrir_añadir_cuerpo(self):
        """
        Abre una ventana de diálogo para añadir un cuerpo manualmente.
        """
        AñadirCuerpoDialog(self.root, self)

    def añadir_varios_cuerpos(self):
        """
        Añade varios cuerpos aleatorios al sistema según el número indicado.
        """
        n = simpledialog.askinteger("Añadir cuerpos aleatorios", "¿Cuántos cuerpos añadir?", minvalue=1, maxvalue=100)
        if n:
            for _ in range(n): self.añadir_cuerpo_aleatorio()
            self.mostrar_mensaje(f"{n} cuerpos aleatorios añadidos")

    def añadir_cuerpo_aleatorio(self):
        """
        Crea un cuerpo con propiedades aleatorias y lo añade a la simulación.
        """
        self.bodies.append(CuerpoCeleste(
            x=random.uniform(50, SIM_WIDTH-50),
            y=random.uniform(50, HEIGHT-50),
            mass=random.uniform(1, 5),
            size=random.randint(3, 8),
            color=random.choice(["#FF6347", "#FFD700", "#40E0D0", "#ADFF2F", "#FF69B4"]),
            vx=random.uniform(-1, 1),
            vy=random.uniform(-1, 1),
            cola=random.choice([True, False]),
            forma=random.choice(["o", "+", "x", "*"])
        ))

    def guardar_constelacion(self):
        """
        Guarda los cuerpos actuales en un archivo JSON.
        """
        if not self.bodies:
            messagebox.showwarning("Guardar", "No hay cuerpos que guardar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            with open(path, "w") as f:
                json.dump([b.__dict__ for b in self.bodies], f, indent=4)
            self.mostrar_mensaje(f"Constelación guardada en {path}")

    def cargar_constelacion(self):
        """
        Carga cuerpos desde un archivo JSON previamente guardado.
        """
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                self.bodies.clear()
                for d in data:
                    self.bodies.append(CuerpoCeleste(**d))
                self.mostrar_mensaje(f"Constelación cargada desde {path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def mostrar_ayuda(self):
        """
        Muestra información básica sobre el uso del simulador.
        """
        messagebox.showinfo("Ayuda", "Simulador gravitacional.\n- Añade cuerpos con menú o botón.\n- Ajusta FPS, gravedad y tiempo con sliders.\n- Guarda y carga constelaciones.")

    def terminar(self):
        """
        Cierra la aplicación.
        """
        self.root.destroy()

    def update_simulation(self):
        """
        Lógica que actualiza el estado de la simulación en cada frame.
        """
        if self.running:
            for b in self.bodies:
                b.update(self.bodies, self.G, self.dt)

        self.dibujar_cuerpos()
        self.root.after(int(1000/self.fps), self.update_simulation)

    def dibujar_cuerpos(self):
        """
        Dibuja todos los cuerpos y sus colas en el canvas.
        """
        self.canvas.delete("all")
        for b in self.bodies:
            x, y, s, c = b.x, b.y, b.size, b.color

            if b.cola and len(b.trail) > 1:
                points = [coord for point in b.trail for coord in point]
                self.canvas.create_line(points, fill=c, width=1, smooth=True)

            if b.forma == "o":
                self.canvas.create_oval(x-s, y-s, x+s, y+s, fill=c, outline="")
            elif b.forma == "+":
                self.canvas.create_line(x-s, y, x+s, y, fill=c, width=2)
                self.canvas.create_line(x, y-s, x, y+s, fill=c, width=2)
            elif b.forma == "x":
                self.canvas.create_line(x-s, y-s, x+s, y+s, fill=c, width=2)
                self.canvas.create_line(x-s, y+s, x+s, y-s, fill=c, width=2)
            elif b.forma == "*":
                s2 = s * 0.6
                self.canvas.create_line(x-s, y, x+s, y, fill=c, width=2)
                self.canvas.create_line(x, y-s, x, y+s, fill=c, width=2)
                self.canvas.create_line(x-s2, y-s2, x+s2, y+s2, fill=c, width=2)
                self.canvas.create_line(x-s2, y+s2, x+s2, y-s2, fill=c, width=2)

class AñadirCuerpoDialog:
    def __init__(self, master, app):
        """
        Inicializa la ventana de diálogo para añadir un nuevo cuerpo celeste.
        """
        self.top = tk.Toplevel(master)
        self.top.title("Añadir cuerpo")
        self.app = app

        campos = [
            ("Posición X", "x"), ("Posición Y", "y"),
            ("Masa", "mass"), ("Velocidad X", "vx"), ("Velocidad Y", "vy"),
            ("Tamaño (px)", "size"), ("Forma (o,+,x,*)", "forma")
        ]
        self.entries = {}
        for i, (label, key) in enumerate(campos):
            ttk.Label(self.top, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            e = ttk.Entry(self.top)
            e.grid(row=i, column=1, padx=5, pady=3)
            if key == "size": e.insert(0, "5")
            elif key == "forma": e.insert(0, "o")
            self.entries[key] = e

        ttk.Label(self.top, text="Color:").grid(row=7, column=0, sticky="e", padx=5, pady=3)
        self.entry_color = ttk.Entry(self.top, width=10)
        self.entry_color.insert(0, "#FFFF64")
        self.entry_color.grid(row=7, column=1, sticky="w", padx=5)
        btn_color = ttk.Button(self.top, text="🎨", command=self.elegir_color)
        btn_color.grid(row=7, column=1, sticky="e", padx=5)

        ttk.Button(self.top, text="Añadir", command=self.añadir).grid(row=9, column=0, pady=10)
        ttk.Button(self.top, text="Cancelar", command=self.top.destroy).grid(row=9, column=1, pady=10)

        self.cola_var = tk.BooleanVar()
        tk.Checkbutton(self.top, text="Cola (trail)", variable=self.cola_var).grid(row=8, columnspan=2, pady=3)

        ttk.Button(self.top, text="Añadir", command=self.añadir,"success")
        btn.configure(font=("Arial", 12, "bold"))
        btn.grid(row=9, column=0, pady=10)
        
        ttk.Button(self.top, text="Cancelar", command=self.añadir,"danger")
        btn.configure(font=("Arial", 12, "bold"))
        btn.grid(row=9, column=0, pady=10)
        
    def elegir_color(self):
        """
        Abre el selector de color para elegir el color del cuerpo.
        """
        color = colorchooser.askcolor(title="Selecciona un color")
        if color and color[1]:
            self.entry_color.delete(0, tk.END)
            self.entry_color.insert(0, color[1])

    def añadir(self):
        """
        Obtiene los valores introducidos, crea un nuevo cuerpo y lo añade al simulador.
        """
        try:
            valores = {k: float(e.get()) if k not in ["forma"] else e.get() for k, e in self.entries.items()}
            if valores["forma"] not in ["o", "+", "x", "*"]:
                raise ValueError("Forma inválida: usa o, +, x o *")
            nuevo_cuerpo = CuerpoCeleste(
                x=valores["x"], y=valores["y"], mass=valores["mass"],
                vx=valores["vx"], vy=valores["vy"], size=int(valores["size"]),
                color=self.entry_color.get(), cola=self.cola_var.get(), forma=valores["forma"]
            )
            self.app.bodies.append(nuevo_cuerpo)
            self.app.mostrar_mensaje("Cuerpo añadido manualmente.")
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos:\n{e}")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = SimulatorApp(root)
    root.mainloop()
