"""
Autor: Joan Gallardo
Fecha: Junio 2025

gravedad.py - Ejercicio 3 APA: Simulación de Cuerpos con Gravitación Universal

Este programa simula la interacción entre cuerpos celestes sometidos a la ley de gravitación universal
de Newton, utilizando una interfaz gráfica con Tkinter.

Funcionalidades principales:
- Crear cuerpos haciendo clic sobre el lienzo (canvas).
- Modificar los parámetros físicos:
    - Constante gravitatoria (G)
    - Frecuencia de actualización (FPS)
    - Incremento temporal (dt)
- Cambiar el color del fondo de la simulación.
- Iniciar, reiniciar o finalizar la simulación desde botones de control.

Requisitos:
- Módulos estándar: tkinter, random, math
"""


import tkinter as tk
from tkinter import ttk, colorchooser
import random
import math

class Cuerpo:
    def __init__(self, x, y, vx, vy, masa, canvas, radio=5, color="white"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.masa = masa
        self.canvas = canvas
        self.radio = radio
        self.color = color
        self.id = self.canvas.create_oval(
            x - radio, y - radio, x + radio, y + radio, fill=color
        )

    def actualizar_posicion(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.canvas.coords(
            self.id,
            self.x - self.radio,
            self.y - self.radio,
            self.x + self.radio,
            self.y + self.radio,
        )

    def aplicar_fuerza(self, fx, fy, dt):
        ax = fx / self.masa
        ay = fy / self.masa
        self.vx += ax * dt
        self.vy += ay * dt

class SimuladorGravedad:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación Gravitatoria - APA")
        self.running = False
        self.cuerpos = []
        self.color_fondo = "#000000"

        # Parámetros
        self.G = tk.DoubleVar(value=100)
        self.fps = tk.IntVar(value=30)
        self.dt = tk.DoubleVar(value=0.1)

        self.crear_widgets()

    def crear_widgets(self):
        frame_controles = ttk.Frame(self.root)
        frame_controles.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(frame_controles, text="Constante G").pack()
        ttk.Scale(frame_controles, variable=self.G, from_=1, to=1000, orient="horizontal").pack()

        ttk.Label(frame_controles, text="FPS").pack()
        ttk.Scale(frame_controles, variable=self.fps, from_=1, to=60, orient="horizontal").pack()

        ttk.Label(frame_controles, text="Incremento temporal (dt)").pack()
        tk.Scale(frame_controles, variable=self.dt, from_=0.01, to=2.0, resolution=0.01, orient="horizontal").pack()

        ttk.Button(frame_controles, text="Cambiar fondo", command=self.cambiar_color_fondo).pack(pady=5)
        ttk.Button(frame_controles, text="Iniciar", command=self.iniciar_simulacion).pack(fill="x")
        ttk.Button(frame_controles, text="Reset", command=self.reset_simulacion).pack(fill="x", pady=2)
        ttk.Button(frame_controles, text="Finalizar", command=self.root.quit).pack(fill="x")

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg=self.color_fondo)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.crear_cuerpo)

    def cambiar_color_fondo(self):
        color = colorchooser.askcolor(title="Escoge un color de fondo")[1]
        if color:
            self.color_fondo = color
            self.canvas.configure(bg=self.color_fondo)

    def crear_cuerpo(self, event):
        masa = random.uniform(5, 20)
        vx = random.uniform(-50, 50)
        vy = random.uniform(-50, 50)
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        cuerpo = Cuerpo(event.x, event.y, vx, vy, masa, self.canvas, color=color)
        self.cuerpos.append(cuerpo)

    def calcular_gravedad(self):
        G = self.G.get()
        dt = self.dt.get()
        for i, c1 in enumerate(self.cuerpos):
            fx, fy = 0, 0
            for j, c2 in enumerate(self.cuerpos):
                if i == j:
                    continue
                dx = c2.x - c1.x
                dy = c2.y - c1.y
                distancia2 = dx**2 + dy**2
                if distancia2 == 0:
                    continue
                fuerza = G * c1.masa * c2.masa / distancia2
                distancia = math.sqrt(distancia2)
                fx += fuerza * dx / distancia
                fy += fuerza * dy / distancia
            c1.aplicar_fuerza(fx, fy, dt)

    def actualizar(self):
        if not self.running:
            return
        self.calcular_gravedad()
        for cuerpo in self.cuerpos:
            cuerpo.actualizar_posicion(self.dt.get())
        self.root.after(int(1000 / self.fps.get()), self.actualizar)

    def iniciar_simulacion(self):
        if not self.running:
            self.running = True
            self.actualizar()

    def reset_simulacion(self):
        self.running = False
        for cuerpo in self.cuerpos:
            self.canvas.delete(cuerpo.id)
        self.cuerpos.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGravedad(root)
    root.mainloop()
