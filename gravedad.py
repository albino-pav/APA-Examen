import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog, simpledialog
import numpy as np
import json
import time
import random

G_DEFAULT = 1.0
DT_DEFAULT = 0.05
FPS_DEFAULT = 30

class Cuerpo:
    def __init__(self, x, y, vx, vy, masa, radio=5, color="white", simbolo="●"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.masa = masa
        self.radio = radio
        self.color = color
        self.simbolo = simbolo
        self.trayectoria = []

    def actualizar(self, fx, fy, dt):
        ax = fx / self.masa
        ay = fy / self.masa
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trayectoria.append((self.x, self.y))
        if len(self.trayectoria) > 100:
            self.trayectoria.pop(0)

    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "vx": self.vx, "vy": self.vy,
            "masa": self.masa, "radio": self.radio, "color": self.color, "simbolo": self.simbolo
        }

    @staticmethod
    def from_dict(d):
        return Cuerpo(d["x"], d["y"], d["vx"], d["vy"], d["masa"], d.get("radio", 5), d.get("color", "white"), d.get("simbolo", "●"))

class SimuladorApp:
    def __init__(self, root):
        self.root = root
        root.title("Simulador de Cuerpos Sometidos a Atracción Gravitatoria")
        self.root.geometry("1200x700")
        self.cuerpos = []
        self.g = G_DEFAULT
        self.dt = DT_DEFAULT
        self.fps = FPS_DEFAULT
        self.bg_color = "#000033"
        self.setup_ui()
        self.animando = False

    def setup_ui(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        archivo_menu = tk.Menu(self.menu, tearoff=0)
        archivo_menu.add_command(label="Guardar constelación", command=self.guardar_constelacion)
        archivo_menu.add_command(label="Cargar constelación", command=self.cargar_constelacion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        self.menu.add_cascade(label="Archivo", menu=archivo_menu)

        cuerpos_menu = tk.Menu(self.menu, tearoff=0)
        cuerpos_menu.add_command(label="Añadir", command=self.crear_cuerpo_dialogo)
        cuerpos_menu.add_command(label="Aleatorios", command=self.crear_aleatorios)
        cuerpos_menu.add_command(label="Editar", command=self.editar_cuerpo_dialogo)
        self.menu.add_cascade(label="Cuerpos", menu=cuerpos_menu)

        self.canvas = tk.Canvas(self.root, bg=self.bg_color, width=900, height=700)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.panel = tk.Frame(self.root, bg="black")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.label_g = tk.Label(self.panel, text="Constante Gravitatoria:", fg="white", bg="black")
        self.label_g.pack()
        self.slider_g = tk.Scale(self.panel, from_=0.1, to=5, resolution=0.1, orient=tk.HORIZONTAL, command=self.update_g)
        self.slider_g.set(self.g)
        self.slider_g.pack()

        self.label_fps = tk.Label(self.panel, text="Reproducción (FPS):", fg="white", bg="black")
        self.label_fps.pack()
        self.slider_fps = tk.Scale(self.panel, from_=1, to=60, orient=tk.HORIZONTAL, command=self.update_fps)
        self.slider_fps.set(self.fps)
        self.slider_fps.pack()

        self.label_dt = tk.Label(self.panel, text="Incremento Temporal:", fg="white", bg="black")
        self.label_dt.pack()
        self.slider_dt = tk.Scale(self.panel, from_=0.001, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, command=self.update_dt)
        self.slider_dt.set(self.dt)
        self.slider_dt.pack()

        self.color_label = tk.Label(self.panel, text="Color del fondo galáctico:", fg="white", bg="black")
        self.color_label.pack(pady=5)
        self.color_btn = tk.Button(self.panel, bg=self.bg_color, width=3, command=self.cambiar_color_fondo)
        self.color_btn.pack()

        self.btn_inicio = tk.Button(self.panel, text="Inicia", bg="green", fg="white", command=self.toggle_animacion)
        self.btn_inicio.pack(pady=5)
        self.btn_reset = tk.Button(self.panel, text="Reinicia", bg="orange", command=self.reiniciar)
        self.btn_reset.pack(pady=5)
        self.btn_termina = tk.Button(self.panel, text="Termina", bg="darkred", fg="white", command=self.root.quit)
        self.btn_termina.pack(pady=5)

    def update_g(self, val): self.g = float(val)
    def update_dt(self, val): self.dt = float(val)
    def update_fps(self, val): self.fps = int(val)

    def cambiar_color_fondo(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.bg_color = color
            self.canvas.config(bg=self.bg_color)
            self.color_btn.config(bg=color)

    def toggle_animacion(self):
        self.animando = not self.animando
        if self.animando:
            self.btn_inicio.config(text="Pausar")
            self.actualizar()
        else:
            self.btn_inicio.config(text="Inicia")

    def reiniciar(self):
        self.cuerpos = []
        self.canvas.delete("all")

    def crear_cuerpo_dialogo(self):
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Crear Cuerpo")

        def agregar():
            try:
                x = float(entry_x.get())
                y = float(entry_y.get())
                vx = float(entry_vx.get())
                vy = float(entry_vy.get())
                masa = float(entry_masa.get())
                color = colorchooser.askcolor()[1]
                self.cuerpos.append(Cuerpo(x, y, vx, vy, masa, color=color))
                self.dibujar()
            except:
                messagebox.showerror("Error", "Valores no válidos")

        entrys = {}
        for label, key, default in [("X", "x", "400"), ("Y", "y", "300"), ("VX", "vx", "0"), ("VY", "vy", "0"), ("Masa", "masa", "1000")]:
            tk.Label(dialogo, text=label).pack()
            entry = tk.Entry(dialogo)
            entry.insert(0, default)
            entry.pack()
            entrys[key] = entry

        entry_x = entrys['x']
        entry_y = entrys['y']
        entry_vx = entrys['vx']
        entry_vy = entrys['vy']
        entry_masa = entrys['masa']

        tk.Button(dialogo, text="Añadir", command=agregar).pack(pady=5)
        tk.Button(dialogo, text="Cerrar", command=dialogo.destroy).pack(pady=5)

    def crear_aleatorios(self):
        n = simpledialog.askinteger("Aleatorios", "¿Cuántos cuerpos aleatorios quieres crear?", minvalue=1, maxvalue=50)
        if n:
            for _ in range(n):
                x, y = random.randint(100, 800), random.randint(100, 600)
                vx, vy = random.uniform(-1, 1), random.uniform(-1, 1)
                masa = random.uniform(500, 2000)
                color = random.choice(["red", "blue", "green", "yellow", "white", "cyan"])
                self.cuerpos.append(Cuerpo(x, y, vx, vy, masa, color=color))
            self.dibujar()

    def editar_cuerpo_dialogo(self):
        if not self.cuerpos:
            messagebox.showinfo("Sin cuerpos", "No hay cuerpos para editar")
            return

    def guardar_constelacion(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            data = [c.to_dict() for c in self.cuerpos]
            with open(file_path, 'w') as f:
                json.dump(data, f)

    def cargar_constelacion(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.cuerpos = [Cuerpo.from_dict(d) for d in data]
            self.dibujar()

    def dibujar(self):
        self.canvas.delete("all")
        for cuerpo in self.cuerpos:
            self.canvas.create_oval(
                cuerpo.x - cuerpo.radio, cuerpo.y - cuerpo.radio,
                cuerpo.x + cuerpo.radio, cuerpo.y + cuerpo.radio,
                fill=cuerpo.color
            )

    def actualizar(self):
        if not self.animando:
            return
        self.canvas.delete("all")
        fuerzas = [(0, 0) for _ in self.cuerpos]

        for i, ci in enumerate(self.cuerpos):
            fx, fy = 0, 0
            for j, cj in enumerate(self.cuerpos):
                if i == j:
                    continue
                dx = cj.x - ci.x
                dy = cj.y - ci.y
                dist_sq = dx**2 + dy**2 + 1e-6
                dist = np.sqrt(dist_sq)
                f = self.g * ci.masa * cj.masa / dist_sq
                fx += f * dx / dist
                fy += f * dy / dist
            fuerzas[i] = (fx, fy)

        for i, cuerpo in enumerate(self.cuerpos):
            cuerpo.actualizar(*fuerzas[i], self.dt)
            for k in range(1, len(cuerpo.trayectoria)):
                x1, y1 = cuerpo.trayectoria[k - 1]
                x2, y2 = cuerpo.trayectoria[k]
                self.canvas.create_line(x1, y1, x2, y2, fill=cuerpo.color)
            self.canvas.create_oval(
                cuerpo.x - cuerpo.radio,
                cuerpo.y - cuerpo.radio,
                cuerpo.x + cuerpo.radio,
                cuerpo.y + cuerpo.radio,
                fill=cuerpo.color
            )
        self.root.after(int(1000 / self.fps), self.actualizar)

if __name__ == '__main__':
    root = tk.Tk()
    app = SimuladorApp(root)
    root.mainloop()
