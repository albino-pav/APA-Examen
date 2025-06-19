import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import random
import json
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class CuerpoCeleste:
    def __init__(self, forma="★ Estrella", tamaño=10, masa=1.0, color="#FFFFFF",
                 posicion=(0, 0), velocidad=(0, 0), cola=False):
        self.forma = forma            # str: Círculo, Cuadrado, etc.
        self.tamaño = tamaño          # int: tamaño del cuerpo
        self.masa = masa              # float: masa para simulación
        self.color = color            # str: color hexadecimal
        self.x, self.y = posicion     # float: coordenadas X e Y
        self.vx, self.vy = velocidad  # float: velocidad en X e Y
        self.cola = cola              # bool: si tiene o no cola (trayectoria)
        self.trayectoria = []         # lista de posiciones pasadas si cola = True

        # Guardar posición y velocidad inicial para reset
        self.x_inicial = self.x
        self.y_inicial = self.y
        self.vx_inicial = self.vx
        self.vy_inicial = self.vy

    def actualizar_posicion(self, dt):
        """Actualiza la posición según la velocidad y el tiempo"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.cola:
            self.trayectoria.append((self.x, self.y))

    def __repr__(self):
        return f"<{self.forma} en ({self.x:.1f}, {self.y:.1f}) masa={self.masa}>"
    
    def resetear(self):
        """Restaura posición y velocidad inicial"""
        self.x = self.x_inicial
        self.y = self.y_inicial
        self.vx = self.vx_inicial
        self.vy = self.vy_inicial
        self.trayectoria.clear()




class SpaceSimApp(tb.Window):
    def __init__(self):
        super().__init__(themename="solar")
        self.title("Simulación de Cuerpos Celestes")
        self.geometry("1200x700")

        self.cuerpos = []

        self.G = 1.0      # Constante de gravitación universal
        self.dt = 0.1     # Incremento de tiempo
        self.fps = 30
        self.running = False  # Estado de simulación

        self.fondo = None

        self.create_menu()
        self.create_main_layout()
        self.create_control_buttons()
        

        self.right_frame = tk.Frame(self, width=400)
        self.right_frame.pack(side="right", fill="y")
        

        self.zoom = 1.0  # zoom inicial (1 = 100%)
        self.offset_x = 0
        self.offset_y = 0

        self.canvas.bind("<Double-Button-1>", self.ajustar_zoom)


    def create_menu(self):
        menubar = tk.Menu(self)
        
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Guardar", command=self.guardar_proyecto)
        archivo_menu.add_command(label="Restaurar", command=self.cargar_proyecto)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)


        cuerpos_menu = tk.Menu(menubar, tearoff=0)
        cuerpos_menu.add_command(label="Añadir Cuerpo", command=self.abrir_crear_cuerpo)
        cuerpos_menu.add_command(label="Editar Cuerpo", command=self.editar_cuerpo)
        cuerpos_menu.add_command(label="Añadir aleatorio", command=self.crear_cuerpo_aleatorio)
        menubar.add_cascade(label="Cuerpos", menu=cuerpos_menu)

        eval_menu = tk.Menu(menubar, tearoff=0)
        eval_menu.add_command(label="Ver Nota", command=self.mostrar_evaluacion)
        menubar.add_cascade(label="Evaluación", menu=eval_menu)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Preguntas Frecuentes", command=self.mostrar_ayuda)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.config(menu=menubar)


    def guardar_proyecto(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("Archivos JSON", "*.json")],
                                               title="Guardar proyecto")
        if archivo:
            datos_proyecto = {
                "fondo": self.fondo,  # esto funciona porque self.fondo existe
                "cuerpos": [
                    {
                        "forma": cuerpo.forma,
                        "tamaño": cuerpo.tamaño,
                        "masa": cuerpo.masa,
                        "color": cuerpo.color,
                        "posicion": [cuerpo.x, cuerpo.y],
                        "velocidad": [cuerpo.vx, cuerpo.vy],
                        "cola": cuerpo.cola
                    }
                    for cuerpo in self.cuerpos
                ]
            }

            with open(archivo, 'w') as f:
                json.dump(datos_proyecto, f, indent=4)
    

    def cargar_proyecto(self):
        archivo = filedialog.askopenfilename(defaultextension=".json",
                                            filetypes=[("Archivos JSON", "*.json")],
                                            title="Cargar proyecto")
        if archivo:
            with open(archivo, 'r') as f:
                datos_proyecto = json.load(f)

            # Restaurar fondo
            self.fondo = datos_proyecto.get("fondo", "default_background")
            self.canvas.config(bg=self.fondo)

            # Limpiar lista actual de cuerpos
            self.cuerpos.clear()

            # Restaurar cuerpos desde archivo
            for datos_cuerpo in datos_proyecto["cuerpos"]:
                cuerpo = CuerpoCeleste(
                    forma=datos_cuerpo.get("forma", "★ Estrella"),
                    tamaño=datos_cuerpo.get("tamaño", 10),
                    masa=datos_cuerpo.get("masa", 1.0),
                    color=datos_cuerpo.get("color", "#FFFFFF"),
                    posicion=tuple(datos_cuerpo.get("posicion", (0, 0))),
                    velocidad=tuple(datos_cuerpo.get("velocidad", (0, 0))),
                    cola=datos_cuerpo.get("cola", False)
                )
                self.cuerpos.append(cuerpo)

            # Redibujar cuerpos en el canvas
            self.dibujar_cuerpos()


    def calcular_poligono(self, x, y, r, lados):
        from math import sin, cos, pi
        return [
            (x + r * cos(2 * pi * i / lados), y + r * sin(2 * pi * i / lados))
            for i in range(lados)
        ]


    def dibujar_cuerpos(self):
        self.canvas.delete("all")  # Borra todo antes de redibujar

        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()

        for cuerpo in self.cuerpos:
            # Aplicar zoom y desplazamiento
            x = (cuerpo.x + self.offset_x) * self.zoom + ancho_canvas / 2
            y = (cuerpo.y + self.offset_y) * self.zoom + alto_canvas / 2
            r = cuerpo.tamaño * self.zoom
            color = cuerpo.color

            # Dibuja el cuerpo
            if cuerpo.forma == "Círculo":
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            elif cuerpo.forma == "Cuadrado":
                self.canvas.create_rectangle(x - r, y - r, x + r, y + r, fill=color, outline="")
            elif cuerpo.forma == "Triángulo":
                self.canvas.create_polygon(
                    x, y - r,
                    x - r, y + r,
                    x + r, y + r,
                    fill=color, outline=""
                )
            elif cuerpo.forma == "Estrella":
                self.canvas.create_text(x, y, text="★", font=("Arial", int(r * 2)), fill=color)
            elif cuerpo.forma == "Pentágono":
                self.canvas.create_polygon(self.calcular_poligono(x, y, r, 5), fill=color, outline="")
            elif cuerpo.forma == "Hexágono":
                self.canvas.create_polygon(self.calcular_poligono(x, y, r, 6), fill=color, outline="")

            self.canvas.create_text(x, y, text=f"{cuerpo.masa:.1f}", fill="white")

            # Dibuja la trayectoria si hay
            if cuerpo.cola and cuerpo.trayectoria:
                for tx, ty in cuerpo.trayectoria:
                    tx = (tx + self.offset_x) * self.zoom + ancho_canvas / 2
                    ty = (ty + self.offset_y) * self.zoom + alto_canvas / 2
                    self.canvas.create_oval(tx - 1, ty - 1, tx + 1, ty + 1, fill=color, outline="")



    def create_main_layout(self):
        self.left_frame = tk.Frame(self, bg="black", width=800, height=600)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = tk.Frame(self, width=400)
        self.right_frame.pack(side="right", fill="y")

        btn1 = tk.Button(self.right_frame, text="Crear cuerpo", command=self.abrir_crear_cuerpo)
        btn1.pack(pady=10)

        # Botón para añadir cuerpo aleatorio
        boton_aleatorio = tk.Button(self.right_frame, text="Crear Cuerpo Aleatorio", command=self.crear_cuerpo_aleatorio)
        boton_aleatorio.pack(pady=10)

        # Sliders en la pantalla principal (¡usa self.right_frame, no self.create_main_layout!)
        tk.Label(self.right_frame, text="Constante G:").pack()
        self.slider_G = tk.Scale(self.right_frame, from_=0.001, to=500, resolution=0.01, orient=tk.HORIZONTAL, command=self.actualizar_G)
        self.slider_G.set(self.G)
        self.slider_G.pack()

        tk.Label(self.right_frame, text="FPS:").pack()
        self.slider_fps = tk.Scale(self.right_frame, from_=1, to=120, orient=tk.HORIZONTAL, command=self.actualizar_fps)
        self.slider_fps.set(30)  # Establece un valor por defecto
        self.slider_fps.pack()

        tk.Label(self.right_frame, text="Δt:").pack()
        self.slider_dt = tk.Scale(self.right_frame, from_=0.001, to=5, resolution=0.01, orient=tk.HORIZONTAL, command=self.actualizar_dt)
        self.slider_dt.set(self.dt)
        self.slider_dt.pack()

        btn3 = tk.Button(self.right_frame, text="Color fondo", command=self.cambiar_color_fondo)
        btn3.pack(pady=10)

        self.canvas = tk.Canvas(self.left_frame, bg="black", width=800, height=600)
        self.canvas.pack(fill="both", expand=True)



    def create_control_buttons(self):
        bottom_frame = tk.Frame(self.right_frame)
        bottom_frame.pack(side="bottom", pady=20)

        colores = ["green", "red", "orange", "yellow"]
        nombres = ["Inicia", "Reinicia", "Reset", "Pausa"]
        comandos = [self.iniciar_sim, self.reiniciar_sim, self.reset_sim, self.pausar_sim]

        for nombre, color, cmd in zip(nombres, colores, comandos):
            btn = tk.Button(bottom_frame, text=nombre, bg=color, command=cmd, width=8)
            btn.pack(side="left", padx=5)

    def abrir_parametros(self):
        ventana = tk.Toplevel(self)

        # Constante gravitatoria
        tk.Label(ventana, text="Constante G:").pack()
        tk.Scale(ventana, from_=0.01, to=10, resolution=0.01, orient="horizontal").pack()

        # Reproducción (fps)
        tk.Label(ventana, text="FPS:").pack()
        tk.Scale(ventana, from_=1, to=60, orient="horizontal").pack()

        # Incremento temporal
        tk.Label(ventana, text="Δt:").pack()
        tk.Scale(ventana, from_=0.1, to=10, resolution=0.1, orient="horizontal").pack()

    def cambiar_color_fondo(self):
        color = colorchooser.askcolor(title="Selecciona un color de fondo")[1]
        if color:
            self.canvas.delete("all")  # Limpia el canvas antes de cambiar el fondo
            self.fondo = color
            self.canvas.config(bg=color)
            self.reset_sim()

    def mostrar_evaluacion(self):
        messagebox.showinfo("Evaluación", "Evaluado con la nota: 9")

    def mostrar_ayuda(self):
        ayuda = (
            "1. Usa 'Crear cuerpo' para añadir objetos.\n"
            "2. Modifica datos de un cuerpo en Cuerpos > Editar cuerpo\n"
            "3. Inicia, pausa o reinicia (borrar todo) o resetea (posiciones iniciales) la simulación con los botones de colores.\n"
            "4. Puedes guardar tu configuración desde Archivo > Guardar.\n"
            "5. Puedes restaurar un proyecto desde Archivo > Restaurar."
        )
        messagebox.showinfo("Ayuda", ayuda)

    def abrir_crear_cuerpo(self):
        ventana = tk.Toplevel(self)
        ventana.title("Crear nuevo cuerpo")

        formas_disponibles = [
            "● Círculo",
            "■ Cuadrado",
            "▲ Triángulo",
            "★ Estrella",
            "⬟ Pentágono",
            "⬢ Hexágono"
        ]

        # Vista previa
        preview_canvas = tk.Canvas(ventana, width=100, height=100, bg="black")
        preview_canvas.grid(row=0, column=2, rowspan=10, padx=10, pady=10)

        def actualizar_preview():
            preview_canvas.delete("all")
            forma_seleccionada = forma_cb.get().split(" ", 1)

            if len(forma_seleccionada) > 1:
                forma = forma_seleccionada[1]
            else:
                forma = forma_seleccionada[0]
            

            try:
                r = int(tamaño_entry.get())
            except:
                r = 10  # tamaño por defecto si error
            color = color_btn.color
            x, y = 50, 50  # centro de preview

            if forma == "Círculo":
                preview_canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            elif forma == "Cuadrado":
                preview_canvas.create_rectangle(x - r, y - r, x + r, y + r, fill=color, outline="")
            elif forma == "Triángulo":
                preview_canvas.create_polygon(
                    x, y - r,
                    x - r, y + r,
                    x + r, y + r,
                    fill=color, outline=""
                )
            elif forma == "Estrella":
                preview_canvas.create_text(x, y, text="★", font=("Arial", r), fill=color)
            elif forma == "Pentágono":
                coords = self.calcular_poligono(x, y, r, 5)
                preview_canvas.create_polygon(coords, fill=color, outline="")
            elif forma == "Hexágono":
                coords = self.calcular_poligono(x, y, r, 6)
                preview_canvas.create_polygon(coords, fill=color, outline="")

        # Forma
        tk.Label(ventana, text="Forma:").grid(row=0, column=0, sticky="w")
        forma_cb = ttk.Combobox(ventana, values=formas_disponibles)
        forma_cb.grid(row=0, column=1)
        forma_cb.set("★ Estrella")
        forma_cb.bind("<<ComboboxSelected>>", lambda e: actualizar_preview())

        # Tamaño
        tk.Label(ventana, text="Tamaño:").grid(row=1, column=0, sticky="w")
        tamaño_entry = tk.Entry(ventana)
        tamaño_entry.insert(0, "10")
        tamaño_entry.grid(row=1, column=1)
        tamaño_entry.bind("<KeyRelease>", lambda e: actualizar_preview())

        # Masa
        tk.Label(ventana, text="Masa:").grid(row=2, column=0, sticky="w")
        masa_entry = tk.Entry(ventana)
        masa_entry.insert(0, "1.0")
        masa_entry.grid(row=2, column=1)

        # Cola
        tk.Label(ventana, text="¿Mostrar cola?:").grid(row=3, column=0)
        cola_var = tk.BooleanVar()
        cola_cb = tk.Checkbutton(ventana, variable=cola_var)
        cola_cb.grid(row=3, column=1)

        # Color
        def elegir_color():
            color = colorchooser.askcolor()[1]
            if color:
                color_btn.config(bg=color)
                color_btn.color = color
                actualizar_preview()

        color_btn = tk.Button(ventana, text="Seleccionar color", command=elegir_color)
        color_btn.grid(row=4, column=1)
        color_btn.color = "#FFFFFF"

        # Posición
        tk.Label(ventana, text="Posición X:").grid(row=5, column=0)
        posx_entry = tk.Entry(ventana)
        posx_entry.insert(0, "0")
        posx_entry.grid(row=5, column=1)

        tk.Label(ventana, text="Posición Y:").grid(row=6, column=0)
        posy_entry = tk.Entry(ventana)
        posy_entry.insert(0, "0")
        posy_entry.grid(row=6, column=1)

        # Velocidad
        tk.Label(ventana, text="Velocidad X:").grid(row=7, column=0)
        velx_entry = tk.Entry(ventana)
        velx_entry.insert(0, "0")
        velx_entry.grid(row=7, column=1)

        tk.Label(ventana, text="Velocidad Y:").grid(row=8, column=0)
        vely_entry = tk.Entry(ventana)
        vely_entry.insert(0, "0")
        vely_entry.grid(row=8, column=1)

        # Número de cuerpos
        tk.Label(ventana, text="Número de cuerpos:").grid(row=9, column=0)
        num_entry = tk.Entry(ventana)
        num_entry.insert(0, "1")
        num_entry.grid(row=9, column=1)

        def randomizar_posicion_velocidad():
            x = random.uniform(0, 800)  # suponiendo canvas de 800x600
            y = random.uniform(0, 600)
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)

            posx_entry.delete(0, tk.END)
            posx_entry.insert(0, str(round(x, 2)))

            posy_entry.delete(0, tk.END)
            posy_entry.insert(0, str(round(y, 2)))

            velx_entry.delete(0, tk.END)
            velx_entry.insert(0, str(round(vx, 2)))

            vely_entry.delete(0, tk.END)
            vely_entry.insert(0, str(round(vy, 2)))


        btn_random_pos_vel = tk.Button(ventana, text="Randomizar Posición/Velocidad", command=randomizar_posicion_velocidad)
        btn_random_pos_vel.grid(row=10, column=0, columnspan=2, pady=5)  # Moverlo a la fila 10

        def aceptar():
            try:
                forma = forma_cb.get().split(" ", 1)[1]
                tamaño = int(tamaño_entry.get())
                masa = float(masa_entry.get())
                color = color_btn.color
                cola = cola_var.get()
                x = float(posx_entry.get())
                y = float(posy_entry.get())
                vx = float(velx_entry.get())
                vy = float(vely_entry.get())
                num = int(num_entry.get())

                if num < 1:
                    messagebox.showerror("Error", "Debes crear al menos 1 cuerpo.")
                    return

                for _ in range(num):
                    # Usar los mismos valores para todos si num > 1
                    x = float(posx_entry.get()) + random.uniform(-20, 20)
                    y = float(posy_entry.get()) + random.uniform(-20, 20)
                    vx = float(velx_entry.get())
                    vy = float(vely_entry.get())

                    cuerpo = CuerpoCeleste(
                        forma=forma,
                        tamaño=tamaño,
                        masa=masa,
                        color=color,
                        posicion=(x, y),
                        velocidad=(vx, vy),
                        cola=cola
                    )
                    self.cuerpos.append(cuerpo)

                self.dibujar_cuerpos()
                ventana.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {e}")

        btns = tk.Frame(ventana)
        btns.grid(row=11, column=0, columnspan=2, pady=10)  # Ahora en fila 11
        tk.Button(btns, text="Aceptar", command=aceptar).pack(side="left", padx=5)
        tk.Button(btns, text="Cancelar", command=ventana.destroy).pack(side="right", padx=5)

        # Actualiza preview inicialmente
        actualizar_preview()
    
    def crear_cuerpo_aleatorio(self):
        self.canvas.update_idletasks()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        formas = ["● Círculo", "■ Cuadrado", "★ Estrella", "▲ Triángulo"]
        forma = random.choice(formas)

        tamaño = random.randint(5, 20)
        masa = round(random.uniform(0.5, 5.0), 2)
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))

        x = random.uniform(-canvas_width/2, canvas_width/2)
        y = random.uniform(-canvas_height/2, canvas_height/2)

        vx = round(random.uniform(-2.0, 2.0), 2)
        vy = round(random.uniform(-2.0, 2.0), 2)

        cola = random.choice([True, False])

        nuevo_cuerpo = CuerpoCeleste(
            forma=forma,
            tamaño=tamaño,
            masa=masa,
            color=color,
            posicion=(x, y),
            velocidad=(vx, vy),
            cola=cola
        )

        # Añadir el cuerpo a la lista y dibujarlo
        self.cuerpos.append(nuevo_cuerpo)
        self.dibujar_cuerpos()  # asumiendo que tienes esta función
    
    def abrir_editar_cuerpo(self):
        if not self.cuerpos:
            messagebox.showinfo("Info", "No hay cuerpos para editar.")
            return

        ventana = tk.Toplevel(self)
        ventana.title("Editar cuerpo")

        # Lista de cuerpos
        tk.Label(ventana, text="Selecciona un cuerpo:").grid(row=0, column=0, sticky="w")
        lista_cb = ttk.Combobox(ventana, state="readonly")
        lista_cb.grid(row=0, column=1, sticky="ew", padx=5)

        lista_cb["values"] = [f"{i}: {c.masa}" for i, c in enumerate(self.cuerpos)]
        lista_cb.current(0)

        formas_disponibles = [
            "● Círculo",
            "■ Cuadrado",
            "▲ Triángulo",
            "★ Estrella",
            "⬟ Pentágono",
            "⬢ Hexágono"
        ]

        # Campos para editar
        campos = {
            "forma": tk.StringVar(),
            "tamaño": tk.StringVar(),
            "masa": tk.StringVar(),
            "pos_x": tk.StringVar(),
            "pos_y": tk.StringVar(),
            "vel_x": tk.StringVar(),
            "vel_y": tk.StringVar(),
            "cola": tk.BooleanVar(),
            "color": "#FFFFFF"
        }

        labels = [
            ("Forma:", "forma"),
            ("Tamaño:", "tamaño"),
            ("Masa:", "masa"),
            ("Posición X:", "pos_x"),
            ("Posición Y:", "pos_y"),
            ("Velocidad X:", "vel_x"),
            ("Velocidad Y:", "vel_y"),
        ]

        for i, (text, key) in enumerate(labels, start=1):
            tk.Label(ventana, text=text).grid(row=i, column=0, sticky="w")

            if key == "forma":
                forma_cb = ttk.Combobox(ventana, textvariable=campos["forma"], values=formas_disponibles, state="readonly")
                forma_cb.grid(row=i, column=1, padx=5, pady=2)
            else:
                entry = tk.Entry(ventana, textvariable=campos[key])
                entry.grid(row=i, column=1, padx=5, pady=2)

        tk.Checkbutton(ventana, text="Mostrar cola", variable=campos["cola"]).grid(row=8, column=1, sticky="w")



        def elegir_color():
            color = colorchooser.askcolor()[1]
            if color:
                color_btn.config(bg=color)
                campos["color"] = color

        color_btn = tk.Button(ventana, text="Color", bg=campos["color"], command=elegir_color)
        color_btn.grid(row=9, column=1, pady=5)

        def cargar_datos(event=None):
            index = lista_cb.current()
            cuerpo = self.cuerpos[index]

            campos["forma"].set(cuerpo.forma)
            campos["tamaño"].set(str(cuerpo.tamaño))
            campos["masa"].set(str(cuerpo.masa))
            campos["pos_x"].set(str(cuerpo.x))
            campos["pos_y"].set(str(cuerpo.y))
            campos["vel_x"].set(str(cuerpo.vx))
            campos["vel_y"].set(str(cuerpo.vy))
            campos["cola"].set(cuerpo.cola)
            campos["color"] = cuerpo.color
            color_btn.config(bg=cuerpo.color)


        def guardar():
            try:
                index = lista_cb.current()
                cuerpo = self.cuerpos[index]

                cuerpo.forma = campos["forma"].get()
                cuerpo.tamaño = int(campos["tamaño"].get())
                cuerpo.masa = float(campos["masa"].get())
                cuerpo.posicion = (float(campos["pos_x"].get()), float(campos["pos_y"].get()))
                cuerpo.velocidad = (float(campos["vel_x"].get()), float(campos["vel_y"].get()))
                cuerpo.cola = campos["cola"].get()
                cuerpo.color = campos["color"]

                self.dibujar_cuerpos()
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        # Botones
        btns = tk.Frame(ventana)
        btns.grid(row=10, columnspan=2, pady=10)
        tk.Button(btns, text="Guardar", command=guardar).pack(side="left", padx=5)
        tk.Button(btns, text="Cancelar", command=ventana.destroy).pack(side="right", padx=5)


    def ajustar_zoom(self, event=None):
        if not self.cuerpos:
            return

        min_x = min(c.x for c in self.cuerpos)
        max_x = max(c.x for c in self.cuerpos)
        min_y = min(c.y for c in self.cuerpos)
        max_y = max(c.y for c in self.cuerpos)

        # Aumentamos un margen
        margen = 50
        min_x -= margen
        max_x += margen
        min_y -= margen
        max_y += margen

        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()

        ancho_escena = max_x - min_x
        alto_escena = max_y - min_y

        if ancho_escena == 0 or alto_escena == 0:
            return

        zoom_x = ancho_canvas / ancho_escena
        zoom_y = alto_canvas / alto_escena

        self.zoom = min(zoom_x, zoom_y)

        # Centrar
        self.offset_x = - (min_x + max_x) / 2
        self.offset_y = - (min_y + max_y) / 2

        self.dibujar_cuerpos()  # o el método que redibuja todo


    def simular_fisica(self):
        if not self.running:
            return

        for i, cuerpo1 in enumerate(self.cuerpos):
            fx_total, fy_total = 0, 0

            for j, cuerpo2 in enumerate(self.cuerpos):
                if i == j:
                    continue

                dx = cuerpo2.x - cuerpo1.x
                dy = cuerpo2.y - cuerpo1.y
                distancia = (dx**2 + dy**2) ** 0.5 + 1e-5  # evitar división por cero

                fuerza = self.G * cuerpo1.masa * cuerpo2.masa / distancia**2

                # Descomponer en componentes
                fx = fuerza * dx / distancia
                fy = fuerza * dy / distancia

                fx_total += fx
                fy_total += fy

            # Aceleración
            ax = fx_total / cuerpo1.masa
            ay = fy_total / cuerpo1.masa

            # Actualizar velocidad
            cuerpo1.vx += ax * self.dt
            cuerpo1.vy += ay * self.dt

        # Ahora que todas las velocidades están actualizadas, mover cuerpos
        for cuerpo in self.cuerpos:
            cuerpo.actualizar_posicion(self.dt)

        self.dibujar_cuerpos()
        self.after_id = self.after(int(1000 / self.fps), self.simular_fisica)


    def editar_cuerpo(self):
        self.abrir_editar_cuerpo()

    # Controladores de simulación
    def iniciar_sim(self):
        self.running = True
        self.simular_fisica()
        print("Iniciar simulación")

    def pausar_sim(self):
        self.running = False
        print("Pausar simulación")

    def actualizar_G(self, valor):
        self.G = float(valor)

    def actualizar_fps(self, valor):
        self.fps = int(valor)

    def actualizar_dt(self, valor):
        self.dt = float(valor)

    def reset_sim(self):
        """Restaura posición y velocidad inicial de cada cuerpo"""
        for cuerpo in self.cuerpos:
            cuerpo.resetear()
        self.dibujar_cuerpos()
        print("Reset: Posiciones y velocidades restauradas.")

    def reiniciar_sim(self):
        """Borra todos los cuerpos y limpia la pantalla"""
        self.running = False  # detiene la simulación si está en marcha
        self.cuerpos.clear()
        self.canvas.delete("all")  # limpia el canvas
        print("Reinicia: Todos los cuerpos eliminados, pantalla limpia.")

if __name__ == "__main__":
    app = SpaceSimApp()
    app.mainloop()
