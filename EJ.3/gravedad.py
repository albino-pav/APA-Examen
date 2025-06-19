import tkinter as tk
from tkinter import ttk, colorchooser
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import random

G_DEFAULT = 1e-3
DT_DEFAULT = 100
FPS_DEFAULT = 30
ESCALA = 1e9

class Cuerpo:
    def __init__(self, masa, pos, vel, color, tamaño=5):
        self.masa = masa
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.color = color
        self.tamaño = tamaño
        self.trayectoria = [self.pos.copy()]

    def actualizar_trayectoria(self):
        self.trayectoria.append(self.pos.copy())
        if len(self.trayectoria) > 100:
            self.trayectoria.pop(0)

class SimuladorGravitacional:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador Gravitacional")
        self.cuerpos = []
        self.G = G_DEFAULT
        self.dt = DT_DEFAULT
        self.fps = FPS_DEFAULT
        self.animacion = None

        self.crear_interfaz()
        self.crear_canvas()
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def crear_interfaz(self):
        frame = ttk.Frame(self.master)
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.entrada_masa = self.crear_entry(frame, "Masa (kg):", "5e20")
        self.entrada_pos = self.crear_entry(frame, "Posición X, Y (m):", "0, 0")
        self.entrada_vel = self.crear_entry(frame, "Velocidad X, Y (m/s):", "0, 0")

        self.color = "#0000FF"
        ttk.Button(frame, text="Color", command=self.elegir_color).pack(pady=5)
        ttk.Button(frame, text="Crear cuerpo", command=self.crear_cuerpo).pack(pady=5)
        ttk.Button(frame, text="Crear aleatorios", command=self.crear_cuerpos_aleatorios).pack(pady=5)
        self.boton_iniciar = ttk.Button(frame, text="Iniciar simulación", command=self.iniciar_simulacion)
        self.boton_iniciar["state"] = "disabled"
        self.boton_iniciar.pack(pady=5)

        ttk.Label(frame, text="G").pack()
        self.slider_G = tk.Scale(frame, from_=0.0, to=0.01, resolution=1e-4, orient=tk.HORIZONTAL, length=200)
        self.slider_G.set(self.G)
        self.slider_G.pack()

        ttk.Label(frame, text="Δt (s)").pack()
        self.slider_dt = tk.Scale(frame, from_=10, to=1000, orient=tk.HORIZONTAL)
        self.slider_dt.set(self.dt)
        self.slider_dt.pack()

        ttk.Label(frame, text="FPS").pack()
        self.slider_fps = tk.Scale(frame, from_=1, to=60, orient=tk.HORIZONTAL)
        self.slider_fps.set(self.fps)
        self.slider_fps.pack()

    def crear_entry(self, parent, text, default):
        ttk.Label(parent, text=text).pack()
        e = ttk.Entry(parent)
        e.insert(0, default)
        e.pack()
        return e

    def crear_canvas(self):
        fig, self.ax = plt.subplots(figsize=(6,6))
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.ax.set_aspect('equal')

    def elegir_color(self):
        color = colorchooser.askcolor(title="Color")[1]
        if color:
            self.color = color

    def crear_cuerpo(self):
        try:
            masa = float(self.entrada_masa.get())
            pos = [float(x) for x in self.entrada_pos.get().split(",")]
            vel = [float(x) for x in self.entrada_vel.get().split(",")]
            self.cuerpos.append(Cuerpo(masa, pos, vel, self.color))
            self.boton_iniciar["state"] = "normal"
            self.dibujar_cuerpos()
        except Exception as e:
            print("Error creando cuerpo:", e)

    def crear_cuerpos_aleatorios(self):
        for _ in range(5):
            masa = random.uniform(1e20, 1e22)
            pos = [random.uniform(-ESCALA, ESCALA), random.uniform(-ESCALA, ESCALA)]
            vel = [random.uniform(-1e3, 1e3), random.uniform(-1e3, 1e3)]
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            self.cuerpos.append(Cuerpo(masa, pos, vel, color))
        self.boton_iniciar["state"] = "normal"
        self.dibujar_cuerpos()

    def calcular_fuerzas(self):
        n = len(self.cuerpos)
        fuerzas = [np.zeros(2) for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                r_vec = self.cuerpos[j].pos - self.cuerpos[i].pos
                dist = np.linalg.norm(r_vec)
                if dist == 0: continue
                fuerza = self.G * self.cuerpos[i].masa * self.cuerpos[j].masa / dist**2
                direccion = r_vec / dist
                f = fuerza * direccion
                fuerzas[i] += f
                fuerzas[j] -= f
        return fuerzas

    def paso_simulacion(self):
        self.G = self.slider_G.get()
        self.dt = self.slider_dt.get()
        self.fps = self.slider_fps.get()
        fuerzas = self.calcular_fuerzas()
        for i, cuerpo in enumerate(self.cuerpos):
            acc = fuerzas[i] / cuerpo.masa
            cuerpo.vel += acc * self.dt
            cuerpo.pos += cuerpo.vel * self.dt
            cuerpo.actualizar_trayectoria()

    def actualizar_grafica(self, frame):
        self.paso_simulacion()
        self.dibujar_cuerpos()
        return self.ax

    def dibujar_cuerpos(self):
        self.ax.clear()
        self.ax.set_xlim(-3*ESCALA, 3*ESCALA)
        self.ax.set_ylim(-3*ESCALA, 3*ESCALA)
        for cuerpo in self.cuerpos:
            if len(cuerpo.trayectoria) > 1:
                xs, ys = zip(*cuerpo.trayectoria)
                self.ax.plot(xs, ys, color=cuerpo.color, alpha=0.5)
            self.ax.plot(cuerpo.pos[0], cuerpo.pos[1], 'o', color=cuerpo.color, markersize=8)
        self.canvas.draw()

    def iniciar_simulacion(self):
        if self.animacion or not self.cuerpos:
            return
        self.animacion = FuncAnimation(self.ax.figure, self.actualizar_grafica,
                                       interval=1000/self.fps, cache_frame_data=False)
        self.canvas.draw()

    def cerrar_aplicacion(self):
        if self.animacion:
            self.animacion.event_source.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGravitacional(root)
    root.mainloop()
