"""
gravedad.py

Guillem Perez Sanchez
QP 2025

Versión corregida y mejorada.
"""
import tkinter as tk
from tkinter import filedialog, simpledialog, colorchooser
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import json
import random
import math

# --- Constantes de la Simulación ---
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

    def update(self, others, G_val, dt_val):
        """
        Actualiza la posición y velocidad del cuerpo aplicando la ley de gravitación universal.
        """
        ax = ay = 0
        for other in others:
            if other is self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = dx*dx + dy*dy + 1e-6 # Softening para evitar división por cero
            force = G_val * self.mass * other.mass / dist_sq
            dist = math.sqrt(dist_sq)
            ax += force * dx / dist / self.mass
            ay += force * dy / dist / self.mass

        self.vx += ax * dt_val
        self.vy += ay * dt_val
        self.x += self.vx * dt_val
        self.y += self.vy * dt_val

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
        
        # CORRECCIÓN: No es necesario inicializar el estilo aquí si se usa themename en ttk.Window
        # self.style = ttk.Style("superhero")

        self.bodies = []
        self.running = False

        self.G = G
        self.fps = FPS
        self.dt = dt

        self.canvas = ttk.Canvas(root, width=SIM_WIDTH, height=HEIGHT)
        self.canvas.pack(side=LEFT)

        self.panel = ttk.Frame(root, width=PANEL_WIDTH, padding=10)
        self.panel.pack(side=RIGHT, fill=Y)

        self.msg_label = ttk.Label(root, text="Bienvenido al Simulador Gravitacional", font=("Arial", 12, "bold"), anchor=CENTER, bootstyle="info")
        self.msg_label.pack(side=TOP, fill=X, pady=5)

        self.create_menu()
        self.create_controls()
        self.root.after(int(1000/self.fps), self.update_simulation)

    def create_menu(self):
        """
        Crea la barra de menú con opciones de archivo y ayuda.
        """
        menubar = ttk.Menu(self.root)

        archivo_menu = ttk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Guardar constelación...", command=self.guardar_constelacion)
        archivo_menu.add_command(label="Cargar constelación...", command=self.cargar_constelacion)
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
        # MEJORA: Se simplifica el diccionario de estilo ya que el bootstyle se define por botón.
        btn_style = {"width": 25}

        botones = [
            ("▶ Iniciar", self.iniciar, "success"),
            ("⏸ Pausar", self.pausar, "warning"),
            ("🔄 Resetear", self.resetear, "info"),
            ("➕ Añadir cuerpo", self.abrir_añadir_cuerpo, "primary"),
            ("🎲 Añadir cuerpos aleatorios", self.añadir_varios_cuerpos, "secondary"),
            ("❌ Terminar", self.terminar, "danger"),
        ]

        for text, cmd, style in botones:
            b = ttk.Button(self.panel, text=text, command=cmd, bootstyle=style, **btn_style)
            b.pack(pady=6)

        # MEJORA: Se elimina el parámetro `res` no utilizado.
        self._crear_slider("FPS", 1, 120, self.fps, self.modificar_fps)
        self._crear_slider("Gravedad (G)", 0.1, 10, self.G, self.modificar_g)
        self._crear_slider("Delta tiempo (dt)", 0.01, 1, self.dt, self.modificar_dt)

    def _crear_slider(self, label, from_, to, initial, cmd):
        """
        Crea un slider con etiqueta en el panel lateral.
        """
        ttk.Label(self.panel, text=label, font=("Arial", 11, "bold")).pack(pady=(15, 0))
        slider = ttk.Scale(self.panel, from_=from_, to=to, orient=HORIZONTAL, command=lambda v: cmd(v), length=300, bootstyle="info")
        slider.set(initial)
        slider.pack()
        
    def modificar_fps(self, val):
        self.fps = int(float(val)); self.mostrar_mensaje(f"FPS ajustado a {self.fps}")
        
    def modificar_g(self, val):
        self.G = float(val); self.mostrar_mensaje(f"Gravedad ajustada a {self.G:.2f}")
        
    def modificar_dt(self, val):
        self.dt = float(val); self.mostrar_mensaje(f"Delta tiempo ajustado a {self.dt:.2f}")

    def mostrar_mensaje(self, texto):
        self.msg_label.config(text=texto)

    def iniciar(self):
        if not self.bodies:
            self.mostrar_mensaje("Añade al menos un cuerpo para iniciar")
            return
        self.running = True
        self.mostrar_mensaje("Simulación iniciada")

    def pausar(self):
        self.running = False; self.mostrar_mensaje("Simulación pausada")
        
    def resetear(self):
        self.running = False; self.bodies.clear(); self.canvas.delete("all"); self.mostrar_mensaje("Simulación reiniciada")

    def abrir_añadir_cuerpo(self):
        AñadirCuerpoDialog(self.root, self)

    def añadir_varios_cuerpos(self):
        n = simpledialog.askinteger("Añadir cuerpos aleatorios", "¿Cuántos cuerpos añadir?", minvalue=1, maxvalue=100, parent=self.root)
        if n:
            for _ in range(n): self.añadir_cuerpo_aleatorio()
            self.mostrar_mensaje(f"{n} cuerpos aleatorios añadidos")

    def añadir_cuerpo_aleatorio(self):
        self.bodies.append(CuerpoCeleste(
            x=random.uniform(50, SIM_WIDTH-50), y=random.uniform(50, HEIGHT-50),
            mass=random.uniform(1, 100), size=random.uniform(2, 7),
            color=random.choice(["#FF6347", "#FFD700", "#40E0D0", "#ADFF2F", "#FF69B4", "#FFFFFF"]),
            vx=random.uniform(-1, 1), vy=random.uniform(-1, 1),
            cola=random.choice([True, False]), forma=random.choice(["o", "+", "x", "*"])
        ))

    def guardar_constelacion(self):
        if not self.bodies:
            # MEJORA: Usar Messagebox de ttkbootstrap para consistencia visual.
            Messagebox.show_warning("No hay cuerpos que guardar.", "Guardar")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            # NOTA: se excluye 'trail' del guardado para evitar archivos grandes y porque se regenera.
            data_to_save = [
                {k: v for k, v in b.__dict__.items() if k != 'trail'} 
                for b in self.bodies
            ]
            with open(path, "w") as f:
                json.dump(data_to_save, f, indent=4)
            self.mostrar_mensaje(f"Constelación guardada en {path}")

    def cargar_constelacion(self):
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if path:
            try:
                with open(path, "r") as f: data = json.load(f)
                self.resetear()
                for d in data: self.bodies.append(CuerpoCeleste(**d))
                self.mostrar_mensaje(f"Constelación cargada desde {path}")
            except Exception as e:
                Messagebox.show_error(f"No se pudo cargar el archivo:\n{e}", "Error de carga")

    def mostrar_ayuda(self):
        Messagebox.show_info("Simulador gravitacional v1.0\n\n- Añade cuerpos con el menú o los botones.\n- Ajusta FPS, gravedad y tiempo con los sliders.\n- Guarda y carga tus constelaciones favoritas.", "Acerca de")

    def terminar(self):
        if Messagebox.okcancel("¿Seguro que quieres salir?", "Terminar"):
            self.root.destroy()

    def update_simulation(self):
        if self.running:
            for b in self.bodies:
                b.update(self.bodies, self.G, self.dt)
        self.dibujar_cuerpos()
        self.root.after(int(1000/self.fps), self.update_simulation)

    def dibujar_cuerpos(self):
        self.canvas.delete("all")
        for b in self.bodies:
            x, y, s, c = b.x, b.y, b.size, b.color
            if b.cola and len(b.trail) > 1:
                self.canvas.create_line(b.trail, fill=c, width=1, smooth=True)

            if b.forma == "o": self.canvas.create_oval(x-s, y-s, x+s, y+s, fill=c, outline="")
            elif b.forma == "+":
                self.canvas.create_line(x-s, y, x+s, y, fill=c, width=2)
                self.canvas.create_line(x, y-s, x, y+s, fill=c, width=2)
            elif b.forma == "x":
                self.canvas.create_line(x-s, y-s, x+s, y+s, fill=c, width=2)
                self.canvas.create_line(x-s, y+s, x+s, y-s, fill=c, width=2)
            elif b.forma == "*":
                s2 = s * 0.7
                self.canvas.create_line(x-s, y, x+s, y, fill=c, width=2)
                self.canvas.create_line(x, y-s, x, y+s, fill=c, width=2)
                self.canvas.create_line(x-s2, y-s2, x+s2, y+s2, fill=c, width=2)
                self.canvas.create_line(x-s2, y+s2, x+s2, y-s2, fill=c, width=2)

class AñadirCuerpoDialog:
    def __init__(self, master, app):
        """
        Inicializa la ventana de diálogo para añadir un nuevo cuerpo celeste.
        """
        # MEJORA: Usar Toplevel y Checkbutton de ttk para consistencia.
        self.top = ttk.Toplevel(master)
        self.top.title("Añadir cuerpo")
        self.app = app
        self.top.transient(master) # Mantener la ventana por encima de la principal
        self.top.grab_set() # Bloquear interacción con la ventana principal
        
        frame = ttk.Frame(self.top, padding=15)
        frame.pack(expand=True, fill=BOTH)

        campos = [("Posición X", "x", SIM_WIDTH/2), ("Posición Y", "y", HEIGHT/2),
                  ("Masa", "mass", 50), ("Velocidad X", "vx", 0),
                  ("Velocidad Y", "vy", 0), ("Tamaño (px)", "size", 5),
                  ("Forma (o,+,x,*)", "forma", "o")]
                  
        self.entries = {}
        for i, (label, key, default) in enumerate(campos):
            ttk.Label(frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            e = ttk.Entry(frame, width=15)
            e.grid(row=i, column=1, padx=5, pady=5, columnspan=2)
            e.insert(0, str(default))
            self.entries[key] = e

        ttk.Label(frame, text="Color:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.entry_color = ttk.Entry(frame, width=10)
        self.entry_color.insert(0, "#FFFF64")
        self.entry_color.grid(row=7, column=1, sticky="w", padx=5)
        btn_color = ttk.Button(frame, text="🎨", command=self.elegir_color, bootstyle="outline")
        btn_color.grid(row=7, column=2, sticky="w", padx=5)

        self.cola_var = ttk.BooleanVar()
        ttk.Checkbutton(frame, text="Dejar cola (trail)", variable=self.cola_var, bootstyle="primary").grid(row=8, columnspan=3, pady=8)

        # CORRECCIÓN: Botones creados de forma correcta y única, usando bootstyle.
        btn_add = ttk.Button(frame, text="Añadir", command=self.añadir, bootstyle="success")
        btn_add.grid(row=9, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        
        btn_cancel = ttk.Button(frame, text="Cancelar", command=self.top.destroy, bootstyle="danger")
        btn_cancel.grid(row=9, column=2, pady=10, padx=5, sticky="ew")

    def elegir_color(self):
        color = colorchooser.askcolor(title="Selecciona un color", parent=self.top)
        if color and color[1]:
            self.entry_color.delete(0, tk.END)
            self.entry_color.insert(0, color[1])

    def añadir(self):
        try:
            valores = {k: e.get() for k, e in self.entries.items()}
            forma = valores["forma"].strip().lower()
            if forma not in ["o", "+", "x", "*"]:
                raise ValueError("Forma inválida: usa 'o', '+', 'x' o '*'")

            nuevo_cuerpo = CuerpoCeleste(
                x=float(valores["x"]), y=float(valores["y"]), mass=float(valores["mass"]),
                vx=float(valores["vx"]), vy=float(valores["vy"]), size=int(float(valores["size"])),
                color=self.entry_color.get(), cola=self.cola_var.get(), forma=forma
            )
            self.app.bodies.append(nuevo_cuerpo)
            self.app.mostrar_mensaje("Cuerpo añadido manualmente.")
            self.top.destroy()
        except Exception as e:
            Messagebox.show_error(f"Datos inválidos:\n{e}", "Error de entrada", parent=self.top)

if __name__ == "__main__":
    # Usar ttk.Window para aplicar el tema desde el inicio
    root = ttk.Window(themename="darkly") 
    app = SimulatorApp(root)
    root.mainloop()
