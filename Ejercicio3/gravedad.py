# Autor: Tomàs Lloret
# Fecha: 17/06/2025
# Ejercicio 3: Programa de Visualización de Cuerpos Sometidos a Atracción Gravitatoria

# AHI HAY MUCHO CURRO ME VOY A MATAR

import tkinter as tk
from tkinter import colorchooser, messagebox
import random
import math

class Star:
    def __init__(self, x, y, mass=10, vx=0, vy=0):
        self.x = x
        self.y = y
        self.mass = mass
        self.vx = vx
        self.vy = vy

class GravitySimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ejercicio 3: Visualización de Cuerpos Sometidos a Atracción Gravitatoria")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Parámetros de simulación
        self.G = 1.0
        self.fps = 60
        self.dt = 1
        self.bg_color = "#000010"
        self.stars = []

        # UI
        self.create_top_panel()
        self.create_main_panel()
        self.running = False
        self.after_id = None

    def create_top_panel(self):
        self.top_panel = tk.Frame(self, bg="#D8D8D8", height=60)
        self.top_panel.pack(side=tk.TOP, fill=tk.X)

        # Menú Archivo como botón con desplegable
        btnbar = tk.Frame(self.top_panel, bg="#D8D8D8")
        btnbar.pack(side=tk.LEFT, padx=10, pady=8)

        archivo_menu = tk.Menubutton(btnbar, text="Archivo", font=("Calibri", 12), bg="#D8D8D8", relief=tk.RAISED, width=10)
        archivo_menu.menu = tk.Menu(archivo_menu, tearoff=0, bg="#D8D8D8", fg="black", font=("Calibri", 12))
        archivo_menu["menu"] = archivo_menu.menu

        archivo_menu.menu.add_command(
            label="Cargar",
            command=lambda: tk.messagebox.showinfo("Cargar", "No me ha dado tiempo a mirar bien como cargar un archivo. :'(")
        )
        archivo_menu.menu.add_command(
            label="Guardar",
            command=lambda: tk.messagebox.showinfo("Guardar", "No me ha dado tiempo a mirar bien como guardar un archivo. :'(")
        )
        archivo_menu.menu.add_separator()
        archivo_menu.menu.add_command(
            label="Salir",
            command=self.destroy
        )
        archivo_menu.pack(side=tk.LEFT, padx=3)

        # Menú Cuerpos como botón con desplegable
        cuerpos_menu = tk.Menubutton(btnbar, text="Cuerpos", font=("Calibri", 12), bg="#D8D8D8", relief=tk.RAISED, width=10)
        cuerpos_menu.menu = tk.Menu(cuerpos_menu, tearoff=0, bg="#D8D8D8", fg="black", font=("Calibri", 12))
        cuerpos_menu["menu"] = cuerpos_menu.menu

        cuerpos_menu.menu.add_command(
            label="Añadir",
            command=self.open_add_body_window
        )
        cuerpos_menu.menu.add_command(
            label="Editar",
            command=lambda: tk.messagebox.showinfo("Editar cuerpos", "No he podido hacer lo de editar todos los cuerpos en un Excel. TwT")
        )
        cuerpos_menu.pack(side=tk.LEFT, padx=3)

        # Botón Evaluación
        tk.Button(
            btnbar,
            text="Evaluación",
            width=10,
            font=("Calibri", 12),
            bg="#D8D8D8",
            command=lambda: tk.messagebox.showinfo(
                "Evaluación",
                "'Tomàs es un muy buen alumno y se ha currado bastante este exámen, creo que se mereceria un 11 sobre 10 si eso fuera posible'\n\n - Tomàs"
            )
        ).pack(side=tk.LEFT, padx=3)

        # Menú Ayuda como botón con desplegable
        ayuda_menu = tk.Menubutton(btnbar, text="Ayuda", font=("Calibri", 12), bg="#D8D8D8", relief=tk.RAISED, width=10)
        ayuda_menu.menu = tk.Menu(ayuda_menu, tearoff=0, bg="#D8D8D8", fg="black", font=("Calibri", 12))
        ayuda_menu["menu"] = ayuda_menu.menu

        ayuda_menu.menu.add_command(
            label="Ayuda",
            command=lambda: tk.messagebox.showinfo(
                "Ayuda",
                "'Si ayudo a una sola persona a tener esperanza, no habré vivido en vano.'\n\n - Martin Luther King"
            )
        )
        ayuda_menu.menu.add_command(
            label="Acerca de...",
            command=lambda: tk.messagebox.showinfo(
                "Acerca de...",
                "Gravedad Beta-0.99\n\n(c) Tomàs Lloret\nCreative Commons (CC) supongo"
            )
        )
        ayuda_menu.pack(side=tk.LEFT, padx=3)

        # Título y subtitulo
        title = tk.Label(self.top_panel, text="Ejercicio 3: Visualización de Cuerpos Sometidos a Atracción Gravitatoria", font=("Calibri", 20, "bold"), fg="black", bg="#D8D8D8")
        title.place(relx=0.4, rely=0.3, anchor="w")
        subtitle = tk.Label(self.top_panel, text="Autor: Tomàs Lloret Martínez", font=("Calibri", 12), fg="grey10", bg="#D8D8D8")
        subtitle.place(relx=0.6, rely=0.8, anchor="w")

    def open_add_body_window(self):
        add_win = tk.Toplevel(self)
        add_win.title("Añadir cuerpo")
        add_win.configure(bg="#D8D8D8")
        add_win.geometry("300x800")

        # Entradas para las propiedades del cuerpo
        tk.Label(add_win, text="Posición X:", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        x_entry = tk.Entry(add_win, font=("Calibri", 12), bg="#F5F5F5")
        x_entry.insert(0, "100")
        x_entry.pack()

        tk.Label(add_win, text="Posición Y:", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        y_entry = tk.Entry(add_win, font=("Calibri", 12), bg="#F5F5F5")
        y_entry.insert(0, "100")
        y_entry.pack()

        tk.Label(add_win, text="Masa:", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        mass_entry = tk.Entry(add_win, font=("Calibri", 12), bg="#F5F5F5")
        mass_entry.insert(0, "10")
        mass_entry.pack()

        tk.Label(add_win, text="Color: No implementado :/", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        color_var = tk.StringVar(value="#FFFF00")
        color_entry = tk.Entry(add_win, font=("Calibri", 12), textvariable=color_var, bg="#F5F5F5")
        color_entry.pack()
        def choose_color():
            color = colorchooser.askcolor()[1]
            if color:
                color_var.set(color)
        tk.Button(add_win, text="Elegir color", command=choose_color, font=("Calibri", 11), bg="#bbbbbb").pack(pady=2)

        tk.Label(add_win, text="Forma: No implementado QwQ", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        shape_var = tk.StringVar(value="Círculo")
        tk.OptionMenu(add_win, shape_var, "Círculo", "Cuadrado", "Triángulo", "Una pena que esto no sirva de nada").pack()

        tk.Label(add_win, text="Trayectoria: No implementado :(", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        trail_var = tk.StringVar(value="Línea")
        tk.OptionMenu(add_win, trail_var, "Línea", "Puntos", "Ninguno", "Como molaria que esto tirara").pack()

        tk.Label(add_win, text="Velocidad inicial X:", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        vx_entry = tk.Entry(add_win, font=("Calibri", 12), bg="#F5F5F5")
        vx_entry.insert(0, "0")
        vx_entry.pack()

        tk.Label(add_win, text="Velocidad inicial Y:", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(10,0))
        vy_entry = tk.Entry(add_win, font=("Calibri", 12), bg="#F5F5F5")
        vy_entry.insert(0, "0")
        vy_entry.pack()

        # Añadir cuerpo
        def add_body():
            try:
                x = float(x_entry.get())
                y = float(y_entry.get())
                mass = float(mass_entry.get())
                color = color_var.get()
                shape = shape_var.get()
                trail = trail_var.get()
                vx = float(vx_entry.get())
                vy = float(vy_entry.get())
                # Añadir el cuerpo con las propiedades seleccionadas
                self.stars.append(Star(x, y, mass, vx, vy))
                # Aquí podrías guardar color, forma y trail en atributos del Star si los implementas
                self.draw()
                add_win.destroy()
            except Exception:
                tk.messagebox.showerror("Error", "Datos no válidos.")

        tk.Button(add_win, text="Añadir cuerpo", command=add_body, font=("Calibri", 13), bg="#bbbbbb").pack(pady=10)

        # Generar n cuerpos aleatorios
        tk.Label(add_win, text="Generar N cuerpos aleatorios:", font=("Calibri", 12), bg="#D8D8D8").pack(pady=(20,0))
        n_entry = tk.Entry(add_win, font=("Calibri", 12), bg="#F5F5F5")
        n_entry.insert(0, "5")
        n_entry.pack()
        def add_n_random():
            try:
                n = int(n_entry.get())
                for _ in range(n):
                    x = random.randint(20, self.canvas.winfo_width() - 20)
                    y = random.randint(20, self.canvas.winfo_height() - 20)
                    mass = random.uniform(5, 20)
                    vx = random.uniform(-1, 1)
                    vy = random.uniform(-1, 1)
                    self.stars.append(Star(x, y, mass, vx, vy))
                self.draw()
                add_win.destroy()
            except Exception:
                tk.messagebox.showerror("Error", "Introduce un número válido.")
        tk.Button(add_win, text="Generar", command=add_n_random, font=("Calibri", 13), bg="#bbbbbb").pack(pady=5)

    def create_main_panel(self):
        # Panel principal que contendrá control y simulación
        main_panel = tk.Frame(self, bg="#D8D8D8")
        main_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Panel de control a la izquierda
        control_frame = tk.Frame(main_panel, bg="#D8D8D8")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # ct gravitatoria
        tk.Label(control_frame, text="Constante Gravitatoria (G):", font=("Calibri", 14), fg="black", bg="#D8D8D8").pack()
        self.g_var = tk.DoubleVar(value=self.G)
        self.g_scale = tk.Scale(control_frame, from_=0.01, to=10, resolution=0.01, orient=tk.HORIZONTAL, variable=self.g_var, command=self.update_g_label, length=250, bg="#D8D8D8", troughcolor="#bbbbbb")
        self.g_scale.pack()
        self.g_label = tk.Label(control_frame, text=f"{self.G:.2f}", font=("Calibri", 12), fg="black", bg="#D8D8D8")
        self.g_label.pack(pady=(0, 10))

        # FPS
        tk.Label(control_frame, text="Frames Por Segundo (fps):", font=("Calibri", 14), fg="black", bg="#D8D8D8").pack()
        self.fps_var = tk.IntVar(value=self.fps)
        self.fps_scale = tk.Scale(control_frame, from_=1, to=240, orient=tk.HORIZONTAL, variable=self.fps_var, command=self.update_fps_label, length=250, bg="#D8D8D8", troughcolor="#bbbbbb")
        self.fps_scale.pack()
        self.fps_label = tk.Label(control_frame, text=f"{self.fps}", font=("Calibri", 12), fg="black", bg="#D8D8D8")
        self.fps_label.pack(pady=(0, 10))

        # Incremento temporal
        tk.Label(control_frame, text="Incremento Temporal (Δt):", font=("Calibri", 14), fg="black", bg="#D8D8D8").pack()
        self.dt_var = tk.DoubleVar(value=self.dt)
        self.dt_scale = tk.Scale(control_frame, from_=0.01, to=10, resolution=0.01, orient=tk.HORIZONTAL, variable=self.dt_var, command=self.update_dt_label, length=250, bg="#D8D8D8", troughcolor="#bbbbbb")
        self.dt_scale.pack()
        self.dt_label = tk.Label(control_frame, text=f"{self.dt:.2f}", font=("Calibri", 12), fg="black", bg="#D8D8D8")
        self.dt_label.pack(pady=(0, 20))

        # Botones de control (excepto los de abajo)
        btn_style = {"font": ("Calibri", 13), "bg": "#D8D8D8", "fg": "black", "activebackground": "#bbbbbb", "activeforeground": "black", "bd": 0, "relief": tk.FLAT, "width": 22, "highlightbackground": "#888888", "highlightthickness": 2}
        tk.Button(control_frame, text="Color del cielo", command=self.choose_bg_color, **btn_style).pack(pady=5)
        tk.Button(control_frame, text="Añadir cuerpo al azar", command=self.add_random_star, **btn_style).pack(pady=5)
        tk.Button(control_frame, text="Deshacer último cuerpo", command=self.undo_last_star, **btn_style).pack(pady=5)

        # Editar masa del cuerpo
        entry_style = {"font": ("Calibri", 12), "width": 10, "bg": "#F5F5F5"}
        tk.Label(control_frame, text="Masa:", font=("Calibri", 12), fg="black", bg="#D8D8D8").pack()
        self.mass_entry = tk.Entry(control_frame, **entry_style)
        self.mass_entry.insert(0, "10")
        self.mass_entry.pack()

        # Añadir cuerpo manualmente
        tk.Label(control_frame, text="Añadir cuerpo en:", font=("Calibri", 14), fg="black", bg="#D8D8D8").pack(pady=(10, 0))
        tk.Label(control_frame, text="X:", font=("Calibri", 12), fg="black", bg="#D8D8D8").pack()
        self.x_entry = tk.Entry(control_frame, **entry_style)
        self.x_entry.pack()
        tk.Label(control_frame, text="Y:", font=("Calibri", 12), fg="black", bg="#D8D8D8").pack()
        self.y_entry = tk.Entry(control_frame, **entry_style)
        self.y_entry.pack()
        tk.Button(control_frame, text="Añadir cuerpo", command=self.add_star_at_coords, **btn_style).pack(pady=(10, 10))

        # Frame para los botones de abajo (más pegados)
        bottom_frame = tk.Frame(control_frame, bg="#D8D8D8")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Botón Iniciar (verde)
        tk.Button(bottom_frame, text="Iniciar", command=self.start_simulation,
                  font=("Calibri", 13), bg="#28a745", fg="black",
                  activebackground="#218838", activeforeground="white", bd=1, relief=tk.RAISED, width=22).pack(pady=2)
        # Botón Pausar (rojo)
        tk.Button(bottom_frame, text="Pausar", command=self.pause_simulation,
                  font=("Calibri", 13), bg="#dc3545", fg="black",
                  activebackground="#c82333", activeforeground="white", bd=1, relief=tk.RAISED, width=22).pack(pady=2)
        # Botón Limpiar (amarillo)
        tk.Button(bottom_frame, text="Limpiar", command=self.clear_stars,
                  font=("Calibri", 13), bg="#ffe066", fg="black",
                  activebackground="#ffe066", activeforeground="white", bd=1, relief=tk.RAISED, width=22).pack(pady=2)
        
        # Botón Salir (gris)
        tk.Button(bottom_frame, text="Salir", command=self.destroy,
                  font=("Calibri", 13), bg="#686868", fg="black",
                  activebackground="#222222", activeforeground="white", bd=1, relief=tk.RAISED, width=22).pack(pady=8)

        # Panel de simulación (canvas) a la derecha
        sim_panel = tk.Frame(main_panel, bg="#D8D8D8")
        sim_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(sim_panel, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def update_g_label(self, val):
        self.g_label.config(text=f"{float(val):.2f}")

    def update_fps_label(self, val):
        self.fps_label.config(text=f"{int(float(val))}")

    def update_dt_label(self, val):
        self.dt_label.config(text=f"{float(val):.2f}")

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Elige color de fondo")[1]
        if color:
            self.bg_color = color
            self.canvas.config(bg=self.bg_color)

    def add_random_star(self):
        x = random.randint(20, self.canvas.winfo_width() - 20)
        y = random.randint(20, self.canvas.winfo_height() - 20)
        mass = random.uniform(5, 20)
        vx = random.uniform(-1, 1)
        vy = random.uniform(-1, 1)
        self.stars.append(Star(x, y, mass, vx, vy))
        self.draw()

    def add_star_at_coords(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            mass = float(self.mass_entry.get())
            if 0 <= x <= self.canvas.winfo_width() and 0 <= y <= self.canvas.winfo_height() and mass > 0:
                self.stars.append(Star(x, y, mass))
                self.draw()
        except ValueError:
            pass

    def on_canvas_click(self, event):
        try:
            mass = float(self.mass_entry.get())
        except Exception:
            mass = 10
        self.stars.append(Star(event.x, event.y, mass))
        self.draw()

    def clear_stars(self):
        self.stars.clear()
        self.draw()

    def undo_last_star(self):
        if self.stars:
            self.stars.pop()
            self.draw()

    def start_simulation(self):
        self.update_params()
        if not self.running:
            self.running = True
            self.simulate()

    def pause_simulation(self):
        self.running = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def update_params(self):
        self.G = self.g_var.get()
        self.fps = self.fps_var.get()
        self.dt = self.dt_var.get()

    def simulate(self):
        if not self.running:
            return
        self.update_params()
        self.update_positions()
        self.draw()
        delay = int(1000 / self.fps)
        self.after_id = self.after(delay, self.simulate)

    def update_positions(self):
        for i, star in enumerate(self.stars):
            fx, fy = 0, 0
            for j, other in enumerate(self.stars):
                if i == j:
                    continue
                dx = other.x - star.x
                dy = other.y - star.y
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq) + 1e-5
                force = self.G * star.mass * other.mass / dist_sq if dist_sq > 1e-2 else 0
                fx += force * dx / dist
                fy += force * dy / dist
            ax = fx / star.mass
            ay = fy / star.mass
            star.vx += ax * self.dt
            star.vy += ay * self.dt
        for star in self.stars:
            star.x += star.vx * self.dt
            star.y += star.vy * self.dt

    def draw(self):
        self.canvas.delete("all")
        for star in self.stars:
            r = max(3, int(star.mass))
            self.canvas.create_oval(star.x - r, star.y - r, star.x + r, star.y + r, fill="yellow", outline="white")

if __name__ == "__main__":
    app = GravitySimulator()
    app.mainloop()