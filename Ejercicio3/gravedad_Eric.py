import tkinter as tk
from tkinter import ttk, colorchooser
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

class SimuladorGravedad:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Gravitatorio entre Cuerpos")
        self.root.configure(bg='#1e1e2f')

        self.G = tk.DoubleVar(value=1.0)
        self.dt = tk.DoubleVar(value=0.1)
        self.masa_personalizada = tk.DoubleVar(value=10.0)
        self.color_personalizado = '#ffffff'
        self.cuerpos = []
        self.simulando = False

        self._crear_ui()

    def _crear_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1e1e2f')
        style.configure('TLabel', background='#1e1e2f', foreground='white', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TScale', background='#1e1e2f')

        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(control_frame, text="Gravedad (G)").pack(pady=5)
        self.slider_g = ttk.Scale(control_frame, from_=0.01, to=5.0, orient='horizontal', variable=self.G)
        self.slider_g.pack(pady=5)

        ttk.Label(control_frame, text="Incremento Temporal (dt)").pack(pady=5)
        self.slider_dt = ttk.Scale(control_frame, from_=0.01, to=1.0, orient='horizontal', variable=self.dt)
        self.slider_dt.pack(pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Label(control_frame, text="Masa Personalizada").pack(pady=5)
        ttk.Entry(control_frame, textvariable=self.masa_personalizada, width=10).pack(pady=5)

        ttk.Button(control_frame, text="Elegir Color", command=self.elegir_color).pack(pady=5)
        ttk.Button(control_frame, text="Crear Cuerpo Personalizado", command=self.crear_cuerpo_personalizado).pack(pady=5)
        ttk.Button(control_frame, text="Crear Cuerpo Aleatorio", command=self.crear_cuerpo_aleatorio).pack(pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(control_frame, text="Resetear Simulación", command=self.resetear).pack(pady=5)
        self.btn_simular = ttk.Button(control_frame, text="Iniciar Simulación", command=self.toggle_simulacion)
        self.btn_simular.pack(pady=5)

        ttk.Label(control_frame, text="© UPC - APA T5", font=('Arial', 8)).pack(side=tk.BOTTOM, pady=20)

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.fig.patch.set_facecolor('#1e1e2f')
        self.ax.set_facecolor('#111')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def elegir_color(self):
        color = colorchooser.askcolor(title="Selecciona un color")[1]
        if color:
            self.color_personalizado = color

    def crear_cuerpo_personalizado(self):
        cuerpo = {
            'x': random.uniform(20, 80),
            'y': random.uniform(20, 80),
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-1, 1),
            'm': self.masa_personalizada.get(),
            'color': self.color_personalizado
        }
        self.cuerpos.append(cuerpo)
        self.dibujar()

    def crear_cuerpo_aleatorio(self):
        cuerpo = {
            'x': random.uniform(20, 80),
            'y': random.uniform(20, 80),
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-1, 1),
            'm': random.uniform(5, 20),
            'color': random.choice(['red', 'deepskyblue', 'limegreen', 'orange'])
        }
        self.cuerpos.append(cuerpo)
        self.dibujar()

    def resetear(self):
        self.simulando = False
        self.btn_simular.config(text="Iniciar Simulación")
        self.cuerpos = []
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_facecolor('#111')
        self.canvas.draw()

    def toggle_simulacion(self):
        self.simulando = not self.simulando
        self.btn_simular.config(text="Detener Simulación" if self.simulando else "Iniciar Simulación")
        if self.simulando:
            self.simular()

    def simular(self):
        if not self.simulando:
            return

        G = self.G.get()
        dt = self.dt.get()

        aceleraciones = []
        for i, c1 in enumerate(self.cuerpos):
            ax, ay = 0, 0
            for j, c2 in enumerate(self.cuerpos):
                if i != j:
                    dx = c2['x'] - c1['x']
                    dy = c2['y'] - c1['y']
                    dist_sq = dx**2 + dy**2
                    dist = math.sqrt(dist_sq) + 1e-5
                    fuerza = G * c1['m'] * c2['m'] / dist_sq
                    ax += fuerza * dx / dist / c1['m']
                    ay += fuerza * dy / dist / c1['m']
            aceleraciones.append((ax, ay))

        for i, cuerpo in enumerate(self.cuerpos):
            ax, ay = aceleraciones[i]
            cuerpo['vx'] += ax * dt
            cuerpo['vy'] += ay * dt
            cuerpo['x'] += cuerpo['vx'] * dt
            cuerpo['y'] += cuerpo['vy'] * dt

        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_facecolor('#111')
        for cuerpo in self.cuerpos:
            self.ax.plot(cuerpo['x'], cuerpo['y'], 'o', color=cuerpo['color'])
        self.canvas.draw()
        self.root.after(20, self.simular)

    def dibujar(self):
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_facecolor('#111')
        for cuerpo in self.cuerpos:
            self.ax.plot(cuerpo['x'], cuerpo['y'], 'o', color=cuerpo['color'])
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = SimuladorGravedad(root)
    root.mainloop()


