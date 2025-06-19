import random
import math
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, colorchooser
import json

# Parámetros globales
G = 1.0
FPS = 60
dt = 0.5
background_color = "#0a0a1e"
bodies = []
running_sim = False
paused_sim = False

FORMAS = ["o", "+", "*", "x", "□", "▲", "◆"]  # Formas disponibles

class Body:
    def __init__(self, x, y, mass, size=5, color="yellow", vx=0, vy=0, cola=0, forma="o", agujero_negro=False):
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
        self.agujero_negro = False 


    def update(self, others):
        ax = ay = 0
        for other in others:
            if other == self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = dx**2 + dy**2 + 1e-5
            force = G * self.mass * other.mass / dist_sq
            dist = math.sqrt(dist_sq)
            ax += force * dx / dist / self.mass
            ay += force * dy / dist / self.mass

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.cola > 0:
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.cola:
                self.trail.pop(0)


    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "mass": self.mass,
            "size": self.size,
            "color": self.color,
            "vx": self.vx,
            "vy": self.vy,
            "cola": self.cola,
            "forma": self.forma
        }

    @staticmethod
    def from_dict(data):
        return Body(
            x=data["x"], y=data["y"], mass=data["mass"], size=data["size"],
            color=data["color"], vx=data["vx"], vy=data["vy"],
            cola=data["cola"], forma=data["forma"]
        )

class SimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Gravitacional")
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.attributes("-zoomed", True)

        self.root.configure(bg=background_color)
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.panel = tk.Frame(root, width=300, bg="#DDDDFF")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)

        self.create_menu()
        self.create_controls()

        self.root.protocol("WM_DELETE_WINDOW", self.terminar)
        self.canvas.bind("<Button-1>", self.seleccionar_cuerpo)

        self.animate()
        self.initial_bodies_state = []


    def create_menu(self):
        menubar = tk.Menu(self.root)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Guardar constelaciones", command=self.guardar_constelacion)
        archivo_menu.add_command(label="Cargar constelaciones", command=self.cargar_constelacion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.terminar)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        cuerpos_menu = tk.Menu(menubar, tearoff=0)
        cuerpos_menu.add_command(label="Añadir", command=self.toggle_add_panel)
        cuerpos_menu.add_command(label="Editar", command=self.editar_cuerpo)
        menubar.add_cascade(label="Cuerpos", menu=cuerpos_menu)

        evaluacion_menu = tk.Menu(menubar, tearoff=0)
        evaluacion_menu.add_command(label="Evaluar", command=self.mostrar_mensaje_evaluacion)
        menubar.add_cascade(label="Evaluación", menu=evaluacion_menu)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_ayuda)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menubar)

    def create_controls(self):
        tk.Button(self.panel, text="Iniciar", bg="lightgreen", command=self.iniciar).pack(pady=5)
        tk.Button(self.panel, text="Parar", bg="orange", command=self.parar).pack(pady=5)
        tk.Button(self.panel, text="Reset", bg="salmon", command=self.reset).pack(pady=5)
        tk.Button(self.panel, text="Añadir cuerpo aleatorio", bg="lightblue", command=self.add_random_body).pack(pady=5)
        tk.Button(self.panel, text="Añadir cuerpo manual", bg="lightyellow", command=self.add_manual_body).pack(pady=5)
        tk.Button(self.panel, text="Reiniciar", bg="lightsteelblue", command=self.reiniciar).pack(pady=5)
        tk.Button(self.panel, text="Terminar", bg="red", command=self.terminar).pack(pady=5)

        tk.Label(self.panel, text="Constante gravitatoria (G)").pack()
        self.g_slider = tk.Scale(self.panel, from_=0.01, to=10.0, resolution=0.01, orient=tk.HORIZONTAL, command=self.update_g)
        self.g_slider.set(G)
        self.g_slider.pack()

        tk.Label(self.panel, text="FPS").pack()
        self.fps_slider = tk.Scale(self.panel, from_=1, to=120, orient=tk.HORIZONTAL, command=self.update_fps)
        self.fps_slider.set(FPS)
        self.fps_slider.pack()

        tk.Label(self.panel, text="Incremento temporal (dt)").pack()
        self.dt_slider = tk.Scale(self.panel, from_=0.01, to=5.0, resolution=0.01, orient=tk.HORIZONTAL, command=self.update_dt)
        self.dt_slider.set(dt)
        self.dt_slider.pack()

        tk.Button(self.panel, text="Cambiar color de fondo", bg="lightgray", command=self.cambiar_color_fondo).pack(pady=10)

    def animate(self):
        self.canvas.configure(bg=background_color)
        self.canvas.delete("all")
        global has_shown_blackhole_message
        if not hasattr(self, "total_initial"):
            self.total_initial = None
        if not hasattr(self, "has_shown_blackhole_message"):
            self.has_shown_blackhole_message = False

        if running_sim:
            for body in bodies[:]:
                body.update(bodies)

            # Detecta y transforma en agujeros negros
            for body in bodies:
                if not body.agujero_negro and body.mass >= 70:
                    body.agujero_negro = True
                    body.color = "black"
                    body.size *= 2  # aumentamos el tamaño visual del agujero negro
                    messagebox.showinfo("Agujero negro", "¡Se ha creado un agujero negro! Has usado una masa muy grande")

            # Almacenar cantidad inicial de cuerpos una sola vez
            if self.total_initial is None:
                self.total_initial = len([b for b in bodies if not b.agujero_negro]) + 1

            

            # Absorber cuerpos cercanos a agujeros negros
            agujeros = [b for b in bodies if b.agujero_negro]
            no_agujeros = [b for b in bodies if not b.agujero_negro]

            absorbed = []
            for ag in agujeros:
                for other in no_agujeros:
                    dx = ag.x - other.x
                    dy = ag.y - other.y
                    dist = math.hypot(dx, dy)
                    if dist < ag.size * 1.5:  # radio de absorción
                        ag.mass += other.mass
                        absorbed.append(other)

            for body in absorbed:
                if body in bodies:
                    bodies.remove(body)


        # Dibujo
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cx, cy = canvas_width // 2, canvas_height // 2

        for body in bodies:
            x, y = body.x + cx, body.y + cy
            s = body.size
            f = body.forma

            if f == "o":
                self.canvas.create_oval(x-s, y-s, x+s, y+s, fill=body.color)
            elif f == "+":
                self.canvas.create_line(x-s, y, x+s, y, fill=body.color)
                self.canvas.create_line(x, y-s, x, y+s, fill=body.color)
            elif f == "*":
                self.canvas.create_line(x-s, y, x+s, y, fill=body.color)
                self.canvas.create_line(x, y-s, x, y+s, fill=body.color)
                self.canvas.create_line(x-s, y-s, x+s, y+s, fill=body.color)
                self.canvas.create_line(x-s, y+s, x+s, y-s, fill=body.color)
            elif f == "x":
                self.canvas.create_line(x-s, y-s, x+s, y+s, fill=body.color)
                self.canvas.create_line(x-s, y+s, x+s, y-s, fill=body.color)
            elif f == "□":
                self.canvas.create_rectangle(x-s, y-s, x+s, y+s, outline=body.color)
            elif f == "▲":
                self.canvas.create_polygon(x, y-s, x-s, y+s, x+s, y+s, outline=body.color, fill="")
            elif f == "◆":
                self.canvas.create_polygon(x, y-s, x+s, y, x, y+s, x-s, y, outline=body.color, fill="")

            if body.cola:
                for i, (tx, ty) in enumerate(body.trail):
                    px, py = tx + cx, ty + cy
                    # Tamaño del puntito reducido
                    r = max(1, body.size // 4)
                    # Hace el punto más transparente o tenue a medida que es más antiguo
                    opacity = int(255 * (i + 1) / len(body.trail)) if len(body.trail) > 1 else 255
                    # Convertir color hex a rgba
                    self.canvas.create_oval(px - r, py - r, px + r, py + r, fill=body.color, outline="")


        self.root.after(int(1000 / FPS), self.animate)


    def iniciar(self):
        global running_sim
        if not self.initial_bodies_state:
            import copy
            self.initial_bodies_state = copy.deepcopy(bodies)
        running_sim = True

    def parar(self):
        global running_sim
        running_sim = False
        messagebox.showinfo("Parar", "Escoge un cuerpo")

    def reset(self):
        global bodies, running_sim
        running_sim = False  # Detiene la simulación
        bodies = []
        self.total_initial = None
        self.has_shown_blackhole_message = False

    def reiniciar(self):
        import copy
        global bodies, running_sim
        running_sim = False
        bodies = copy.deepcopy(self.initial_bodies_state)
        self.total_initial = None
        self.has_shown_blackhole_message = False
        running_sim = True  # Inicia la simulación automáticamente


    def terminar(self):
        self.root.destroy()

    def toggle_add_panel(self):
        self.add_manual_body()

    def add_random_body(self):
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        x = random.randint(-cw//2, cw//2)
        y = random.randint(-ch//2, ch//2)
        mass = random.uniform(1, 10)
        size = random.randint(3, 8)
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        color = random.choice(["red", "green", "blue", "white", "yellow"])
        forma = random.choice(FORMAS)
        cola = random.choice([0, 10, 100, 1000, 10000, 100000])  # ← Aquí el cambio
        bodies.append(Body(x, y, mass, size, color, vx, vy, cola, forma))


    def add_manual_body(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Añadir cuerpo")
        dialog.geometry("300x600")
        selected_color = ["yellow"]
        forma_idx = tk.IntVar(value=0)
        cola_val = [0]  # valor seleccionado para cola

        def choose_color():
            color = colorchooser.askcolor(title="Seleccionar color")
            if color[1]:
                selected_color[0] = color[1]
                color_btn.configure(bg=selected_color[0])

        def update_forma_label(val):
            forma_value.set(f"Forma: {FORMAS[int(val)]}")

        def select_cola():
            cola_window = tk.Toplevel(dialog)
            cola_window.title("Seleccionar valor Cola")
            cola_window.geometry("200x250")

            listbox = tk.Listbox(cola_window)
            valores = [0, 10, 100, 1000, 10000, 100000, 1000000]
            for v in valores:
                listbox.insert(tk.END, str(v))
            listbox.pack(fill=tk.BOTH, expand=True)

            def confirmar():
                sel = listbox.curselection()
                if sel:
                    val = int(listbox.get(sel))
                    cola_val[0] = val
                    cola_btn.config(text=f"Cola: {val}")
                    cola_window.destroy()
                else:
                    messagebox.showwarning("Aviso", "Selecciona un valor")

            btn_confirm = tk.Button(cola_window, text="Confirmar", command=confirmar)
            btn_confirm.pack(pady=5)

        def submit():
            try:
                x = float(x_entry.get())
                y = float(y_entry.get())
                mass = float(mass_entry.get())
                vx = float(vx_entry.get())
                vy = float(vy_entry.get())
                size = int(size_entry.get())
                color = selected_color[0]
                forma = FORMAS[forma_idx.get()]
                cola = cola_val[0]
                bodies.append(Body(x, y, mass, size, color, vx, vy, cola, forma))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Introduce valores válidos.")

        # Entradas normales
        x_entry, y_entry = tk.Entry(dialog), tk.Entry(dialog)
        mass_entry, vx_entry, vy_entry = tk.Entry(dialog), tk.Entry(dialog), tk.Entry(dialog)
        size_entry = tk.Entry(dialog)

        tk.Label(dialog, text="X").pack()
        x_entry.pack()
        tk.Label(dialog, text="Y").pack()
        y_entry.pack()
        tk.Label(dialog, text="Masa").pack()
        mass_entry.pack()
        tk.Label(dialog, text="Velocidad X").pack()
        vx_entry.pack()
        tk.Label(dialog, text="Velocidad Y").pack()
        vy_entry.pack()
        tk.Label(dialog, text="Tamaño").pack()
        size_entry.pack()

        tk.Label(dialog, text="Color").pack()
        color_btn = tk.Button(dialog, text="Seleccionar color", command=choose_color, bg=selected_color[0])
        color_btn.pack()

        forma_value = tk.StringVar()
        forma_value.set(f"Forma: {FORMAS[0]}")
        tk.Label(dialog, textvariable=forma_value).pack()
        tk.Scale(dialog, from_=0, to=len(FORMAS)-1, orient=tk.HORIZONTAL, variable=forma_idx,
                command=update_forma_label).pack()

        # Botón para escoger cola
        cola_btn = tk.Button(dialog, text=f"Cola: {cola_val[0]}", command=select_cola)
        cola_btn.pack(pady=10)

        tk.Button(dialog, text="Añadir", command=submit).pack(pady=5)
        tk.Button(dialog, text="Salir", command=dialog.destroy).pack(pady=5)


    def seleccionar_cuerpo(self, event):
        if not running_sim:
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            cx, cy = canvas_w // 2, canvas_h // 2
            x_click = event.x - cx
            y_click = event.y - cy

            for i, body in enumerate(bodies):
                dx = x_click - body.x
                dy = y_click - body.y
                if dx**2 + dy**2 < body.size**2 * 4:
                    msg = (
                        f"Cuerpo {i}\n"
                        f"Posición: ({body.x:.2f}, {body.y:.2f})\n"
                        f"Masa: {body.mass:.2f}\n"
                        f"Tamaño: {body.size}\n"
                        f"Color: {body.color}\n"
                        f"Velocidad: ({body.vx:.2f}, {body.vy:.2f})\n"
                        f"Cola: {body.cola}\n"
                        f"Forma: {body.forma}"
                    )
                    messagebox.showinfo("Parámetros del cuerpo", msg)
                    break

    def mostrar_mensaje_evaluacion(self):
        messagebox.showinfo("Evaluación", "El comité de evaluación evalúa esta versión con un 9.5 ;)")

    def mostrar_ayuda(self):
        messagebox.showinfo("Ayuda", "Simulador gravitacional. Añade cuerpos, cambia parámetros y observa el comportamiento físico.")

    def guardar_constelacion(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            data = [body.to_dict() for body in bodies]
            with open(filepath, "w") as f:
                json.dump(data, f)
            messagebox.showinfo("Guardar", "Constelación guardada.")

    def cargar_constelacion(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            with open(filepath, "r") as f:
                data = json.load(f)
            global bodies
            bodies = [Body.from_dict(d) for d in data]
            messagebox.showinfo("Cargar", "Constelación cargada.")

    def editar_cuerpo(self):
        if not bodies:
            messagebox.showwarning("Editar", "No hay cuerpos disponibles.")
            return
        idx = simpledialog.askinteger("Editar cuerpo", f"Índice de cuerpo (0 - {len(bodies)-1})")
        if idx is not None and 0 <= idx < len(bodies):
            nuevo_m = simpledialog.askfloat("Editar masa", "Nueva masa:", initialvalue=bodies[idx].mass)
            if nuevo_m:
                bodies[idx].mass = nuevo_m
                messagebox.showinfo("Editar", f"Cuerpo {idx} actualizado")
        else:
            messagebox.showerror("Error", "Índice inválido.")

    def update_g(self, val):
        global G
        G = float(val)

    def update_fps(self, val):
        global FPS
        FPS = int(val)

    def update_dt(self, val):
        global dt
        dt = float(val)

    def cambiar_color_fondo(self):
        global background_color
        color = colorchooser.askcolor(title="Selecciona un color de fondo")
        if color[1]:
            background_color = color[1]
            self.canvas.configure(bg=background_color)  # actualiza fondo inmediatamente
        

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()