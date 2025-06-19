# gravedad.py
# MARK BONETE VENTURA

import tkinter as tk
from tkinter import ttk
import math

G = 6.67430e-11

class CuerpoCeleste:
    def __init__(self, canvas, x, y, masa, vx=0, vy=0, radio=5, color="white", forma="circle"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.masa = masa
        self.vx = vx
        self.vy = vy
        self.radio = radio
        self.color = color
        self.forma = forma
        self.id = self.dibujar()

    def dibujar(self):
        if self.forma == "circle":
            return self.canvas.create_oval(self.x - self.radio, self.y - self.radio,
                                            self.x + self.radio, self.y + self.radio,
                                            fill=self.color)
        elif self.forma == "square":
            return self.canvas.create_rectangle(self.x - self.radio, self.y - self.radio,
                                                self.x + self.radio, self.y + self.radio,
                                                fill=self.color)
        else:
            return self.canvas.create_oval(self.x - self.radio, self.y - self.radio,
                                            self.x + self.radio, self.y + self.radio,
                                            fill=self.color)

    def actualizar_posicion(self, fx, fy, dt):
        ax = fx / self.masa
        ay = fy / self.masa
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.canvas.coords(self.id, self.x - self.radio, self.y - self.radio,
                           self.x + self.radio, self.y + self.radio)

def fuerza_gravitacional(c1, c2):
    dx = c2.x - c1.x
    dy = c2.y - c1.y
    distancia = math.sqrt(dx**2 + dy**2)
    if distancia == 0:
        return 0, 0
    f = G * c1.masa * c2.masa / distancia**2
    fx = f * dx / distancia
    fy = f * dy / distancia
    return fx, fy

def actualizar():
    fuerzas = []
    for i, c1 in enumerate(cuerpos):
        fx, fy = 0, 0
        for j, c2 in enumerate(cuerpos):
            if i != j:
                fxi, fyi = fuerza_gravitacional(c1, c2)
                fx += fxi
                fy += fyi
        fuerzas.append((fx, fy))

    for i, c in enumerate(cuerpos):
        c.actualizar_posicion(*fuerzas[i], dt=0.5)

    root.after(20, actualizar)

def on_canvas_click(event):
    try:
        masa = float(entry_masa.get())
        vx = float(entry_vx.get())
        vy = float(entry_vy.get())
        radio = int(entry_radio.get())
        forma = forma_var.get()
    except ValueError:
        return
    cuerpo = CuerpoCeleste(canvas, event.x, event.y, masa, vx, vy, radio, "white", forma)
    cuerpos.append(cuerpo)

root = tk.Tk()
root.title("Simulación de Gravedad Universal")

frame = tk.Frame(root)
frame.pack(side=tk.RIGHT, fill=tk.Y)

canvas = tk.Canvas(root, width=800, height=600, bg="black")
canvas.pack(side=tk.LEFT)
canvas.bind("<Button-1>", on_canvas_click)

tk.Label(frame, text="Masa (kg)").pack()
entry_masa = tk.Entry(frame)
entry_masa.pack()

tk.Label(frame, text="Velocidad X").pack()
entry_vx = tk.Entry(frame)
entry_vx.pack()

tk.Label(frame, text="Velocidad Y").pack()
entry_vy = tk.Entry(frame)
entry_vy.pack()

tk.Label(frame, text="Tamaño (radio px)").pack()
entry_radio = tk.Entry(frame)
entry_radio.pack()

tk.Label(frame, text="Forma").pack()
forma_var = tk.StringVar(value="circle")
ttk.Combobox(frame, textvariable=forma_var, values=["circle", "square"]).pack()

tk.Label(frame, text="Haz clic en el canvas para colocar el cuerpo").pack(pady=10)

cuerpos = []
actualizar()

root.mainloop()
