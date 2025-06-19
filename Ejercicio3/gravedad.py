# Autor: Tomàs Lloret
# Fecha: 17/06/2025
# Ejercicio 3: Programa de Visualización de Cuerpos Sometidos a Atracción Gravitatoria

# AQUI HAY MUCHO CURRO ME VOY A MATAR

import tkinter as tk
from tkinter import colorchooser
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
        self.title("Ejercicio 3: Programa de Visualización de Cuerpos Sometidos a Atracción Gravitatoria")
        self.geometry("900x700")
        self.resizable(False, False)

        # Parámetros de simulación
        self.G = 1.0
        self.fps = 60
        self.dt = 1
        self.bg_color = "#000010"
        self.stars = []

        # UI
        self.create_widgets()
        self.running = False
        self.after_id = None

    def create_widgets(self):
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(control_frame, text="Constante G:").pack()
        self.g_entry = tk.Entry(control_frame)
        self.g_entry.insert(0, str(self.G))
        self.g_entry.pack()

        tk.Label(control_frame, text="FPS:").pack()
        self.fps_entry = tk.Entry(control_frame)
        self.fps_entry.insert(0, str(self.fps))
        self.fps_entry.pack()

        tk.Label(control_frame, text="Δt:").pack()
        self.dt_entry = tk.Entry(control_frame)
        self.dt_entry.insert(0, str(self.dt))
        self.dt_entry.pack()

        tk.Button(control_frame, text="Color de fondo", command=self.choose_bg_color).pack(pady=5)
        tk.Button(control_frame, text="Añadir estrella al azar", command=self.add_random_star).pack(pady=5)
        tk.Button(control_frame, text="Iniciar", command=self.start_simulation).pack(pady=5)
        tk.Button(control_frame, text="Pausar", command=self.pause_simulation).pack(pady=5)
        tk.Button(control_frame, text="Limpiar", command=self.clear_stars).pack(pady=5)
        tk.Button(control_frame, text="Deshacer última estrella", command=self.undo_last_star).pack(pady=5)

        tk.Label(control_frame, text="Añadir estrella en:").pack(pady=5)
        tk.Label(control_frame, text="X:").pack()
        self.x_entry = tk.Entry(control_frame)
        self.x_entry.pack()
        tk.Label(control_frame, text="Y:").pack()
        self.y_entry = tk.Entry(control_frame)
        self.y_entry.pack()
        tk.Button(control_frame, text="Añadir estrella", command=self.add_star_at_coords).pack(pady=5)

        self.canvas = tk.Canvas(self, width=700, height=700, bg=self.bg_color)
        self.canvas.pack(side=tk.RIGHT)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Elige color de fondo")[1]
        if color:
            self.bg_color = color
            self.canvas.config(bg=self.bg_color)

    def add_random_star(self):
        x = random.randint(20, 680)
        y = random.randint(20, 680)
        mass = random.uniform(5, 20)
        vx = random.uniform(-1, 1)
        vy = random.uniform(-1, 1)
        self.stars.append(Star(x, y, mass, vx, vy))
        self.draw()

    def add_star_at_coords(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            if 0 <= x <= 700 and 0 <= y <= 700:
                self.stars.append(Star(x, y))
                self.draw()
        except ValueError:
            pass

    def on_canvas_click(self, event):
        self.stars.append(Star(event.x, event.y))
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
        try:
            self.G = float(self.g_entry.get())
            self.fps = int(self.fps_entry.get())
            self.dt = float(self.dt_entry.get())
        except ValueError:
            pass

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
            # Ya no hay rebote ni límites, las estrellas pueden salir del canvas

    def draw(self):
        self.canvas.delete("all")
        for star in self.stars:
            r = max(3, int(star.mass))
            self.canvas.create_oval(star.x - r, star.y - r, star.x + r, star.y + r, fill="yellow", outline="white")

if __name__ == "__main__":
    app = GravitySimulator()
    app.mainloop()