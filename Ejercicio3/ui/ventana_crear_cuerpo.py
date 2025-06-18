import tkinter as tk
from tkinter import ttk, colorchooser
import random
from logic.cuerpo import Cuerpo

def abrir_ventana_crear_cuerpo(root, visualizador, simulacion):
    ventana_cuerpo = tk.Toplevel(root)
    ventana_cuerpo.title("Crear Cuerpo")
    ventana_cuerpo.geometry("400x600")

    # Función para dibujar un cuerpo en el Canvas
    def dibujar_cuerpo(forma, tamano, color, posicion):
        x, y = posicion
        r = int(tamano)  # Radio del cuerpo
        if forma == "*":  # Dibujar un círculo como ejemplo
            visualizador.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
        elif forma == "+":  # Dibujar una cruz
            visualizador.create_line(x - r, y, x + r, y, fill=color, width=2)
            visualizador.create_line(x, y - r, x, y + r, fill=color, width=2)
        elif forma == "X":  # Dibujar una X
            visualizador.create_line(x - r, y - r, x + r, y + r, fill=color, width=2)
            visualizador.create_line(x - r, y + r, x + r, y - r, fill=color, width=2)
        elif forma == "O":  # Dibujar un círculo
            visualizador.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
        elif forma == ".":  # Dibujar un punto
            visualizador.create_oval(x - 1, y - 1, x + 1, y + 1, fill=color, outline="")

    # Función para manejar el botón "Crear cuerpos aleatorios"
    def crear_cuerpos_aleatorios():
        for _ in range(aleatorio_var.get()):
            forma = random.choice(["*", "+", "X", "O", "."])
            tamano = random.choice(["1", "2", "4", "6", "8", "10", "12", "14", "16"])
            color = f"#{random.randint(0, 0xFFFFFF):06x}"  # Color aleatorio
            posicion = (random.uniform(100, 400), random.uniform(100, 400))  # Dentro de un rango limitado
            velocidad = (random.uniform(-2, 2), random.uniform(-2, 2))  # Velocidades iniciales limitadas
            cola = random.choice(["0", "10", "100", "1000", "10000", "100000", "1000000"])  # Cola aleatoria
            masa = random.uniform(3.0, 9.0)  # Limitar las masas a un rango razonable

            # Crear un nuevo cuerpo
            nuevo_cuerpo = Cuerpo(forma, tamano, cola, masa, color, posicion, velocidad)

            # Añadir el cuerpo a la simulación
            simulacion.agregar_cuerpo(nuevo_cuerpo)

            # Dibujar el cuerpo en el visualizador
            dibujar_cuerpo(forma, tamano, color, posicion)

    # Función para manejar el botón "Aceptar"
    def aceptar_cuerpo():
        # Obtener valores de los parámetros
        forma = forma_var.get()
        tamano = tamano_var.get()
        cola = cola_var.get()
        masa = masa_var.get()
        color = color_var.get()
        posicion = (pos_x_var.get(), pos_y_var.get())
        velocidad = (vel_x_var.get(), vel_y_var.get())

        # Crear un nuevo cuerpo y agregarlo a la simulación
        nuevo_cuerpo = Cuerpo(forma, tamano, cola, masa, color, posicion, velocidad)
        simulacion.agregar_cuerpo(nuevo_cuerpo)

        # Dibujar el cuerpo en el visualizador
        x, y = posicion
        r = int(tamano)
        visualizador.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

        # Randomizar posición y velocidad después de crear el cuerpo
        pos_x_var.set(round(random.uniform(0, 800), 2))
        pos_y_var.set(round(random.uniform(0, 700), 2))
        vel_x_var.set(round(random.uniform(-5, 5), 2))
        vel_y_var.set(round(random.uniform(-5, 5), 2))      

    # Parámetro: Forma
    forma_frame = tk.Frame(ventana_cuerpo)
    forma_frame.pack(fill=tk.X, pady=5, padx=10)

    forma_label = tk.Label(forma_frame, text="Forma:")
    forma_label.pack(side=tk.LEFT, padx=5)

    forma_var = tk.StringVar(value="*")
    forma_menu = ttk.Combobox(forma_frame, textvariable=forma_var, values=["*", "+", "X", "O", "."])
    forma_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Parámetro: Tamaño
    tamano_frame = tk.Frame(ventana_cuerpo)
    tamano_frame.pack(fill=tk.X, pady=5, padx=10)

    tamano_label = tk.Label(tamano_frame, text="Tamaño:")
    tamano_label.pack(side=tk.LEFT, padx=5)

    tamano_var = tk.StringVar(value="8")
    tamano_menu = ttk.Combobox(tamano_frame, textvariable=tamano_var, values=["1", "2", "4", "6", "8", "10", "12", "14", "16"])
    tamano_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Parámetro: Cola
    cola_frame = tk.Frame(ventana_cuerpo)
    cola_frame.pack(fill=tk.X, pady=5, padx=10)

    cola_label = tk.Label(cola_frame, text="Cola:")
    cola_label.pack(side=tk.LEFT, padx=5)

    cola_var = tk.StringVar(value="100")
    cola_menu = ttk.Combobox(cola_frame, textvariable=cola_var, values=["0", "10", "100", "1000", "10e4", "10e5", "10e6"])
    cola_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Parámetro: Masa
    masa_frame = tk.Frame(ventana_cuerpo)
    masa_frame.pack(fill=tk.X, pady=5, padx=10)

    masa_label = tk.Label(masa_frame, text="Masa:")
    masa_label.pack(side=tk.LEFT, padx=5)

    masa_var = tk.DoubleVar(value=1.0)
    masa_entry = tk.Entry(masa_frame, textvariable=masa_var)
    masa_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Parámetro: Color
    color_frame = tk.Frame(ventana_cuerpo)
    color_frame.pack(fill=tk.X, pady=5, padx=10)

    color_label = tk.Label(color_frame, text="Color:")
    color_label.pack(side=tk.LEFT, padx=5)

    color_var = tk.StringVar(value="#FFFF00")
    def seleccionar_color():
        color = colorchooser.askcolor(title="Selecciona un color")[1]
        if color:
            color_var.set(color)

    color_button = tk.Button(color_frame, text="Seleccionar", command=seleccionar_color)
    color_button.pack(side=tk.LEFT, padx=5)

    # Parámetro: Posición
    posicion_frame = tk.LabelFrame(ventana_cuerpo, text="Posición")
    posicion_frame.pack(fill=tk.X, pady=10, padx=10)

    pos_x_label = tk.Label(posicion_frame, text="Coordenada X:")
    pos_x_label.grid(row=0, column=0, padx=5, pady=5)

    pos_x_var = tk.DoubleVar(value=100)
    pos_x_entry = tk.Entry(posicion_frame, textvariable=pos_x_var)
    pos_x_entry.grid(row=0, column=1, padx=5, pady=5)

    pos_y_label = tk.Label(posicion_frame, text="Coordenada Y:")
    pos_y_label.grid(row=1, column=0, padx=5, pady=5)

    pos_y_var = tk.DoubleVar(value=100)
    pos_y_entry = tk.Entry(posicion_frame, textvariable=pos_y_var)
    pos_y_entry.grid(row=1, column=1, padx=5, pady=5)

    pos_reset_button = tk.Button(posicion_frame, text="Reset", command=lambda: (pos_x_var.set(0.0), pos_y_var.set(0.0)))
    pos_reset_button.grid(row=2, column=0, columnspan=2, pady=5)

    # Parámetro: Velocidad
    velocidad_frame = tk.LabelFrame(ventana_cuerpo, text="Velocidad")
    velocidad_frame.pack(fill=tk.X, pady=10, padx=10)

    vel_x_label = tk.Label(velocidad_frame, text="Coordenada X:")
    vel_x_label.grid(row=0, column=0, padx=5, pady=5)

    vel_x_var = tk.DoubleVar(value=-2.08)
    vel_x_entry = tk.Entry(velocidad_frame, textvariable=vel_x_var)
    vel_x_entry.grid(row=0, column=1, padx=5, pady=5)

    vel_y_label = tk.Label(velocidad_frame, text="Coordenada Y:")
    vel_y_label.grid(row=1, column=0, padx=5, pady=5)

    vel_y_var = tk.DoubleVar(value=1.19)
    vel_y_entry = tk.Entry(velocidad_frame, textvariable=vel_y_var)
    vel_y_entry.grid(row=1, column=1, padx=5, pady=5)

    vel_reset_button = tk.Button(velocidad_frame, text="Reset", command=lambda: (vel_x_var.set(0.0), vel_y_var.set(0.0)))
    vel_reset_button.grid(row=2, column=0, columnspan=2, pady=5)

    # Crear cuerpos aleatorios
    aleatorio_frame = tk.Frame(ventana_cuerpo)
    aleatorio_frame.pack(fill=tk.X, pady=10, padx=10)

    aleatorio_button = tk.Button(aleatorio_frame, text="Crear", command=crear_cuerpos_aleatorios)
    aleatorio_button.pack(side=tk.LEFT, padx=5)

    aleatorio_var = tk.IntVar(value=4)
    aleatorio_entry = tk.Entry(aleatorio_frame, textvariable=aleatorio_var, width=5)
    aleatorio_entry.pack(side=tk.LEFT, padx=5)

    aleatorio_text = tk.Label(aleatorio_frame, text="cuerpos aleatorios")
    aleatorio_text.pack(side=tk.LEFT, padx=5)

    # Botones inferiores
    botones_frame = tk.Frame(ventana_cuerpo)
    botones_frame.pack(fill=tk.X, pady=10, padx=10)

    mostrar_button = tk.Button(botones_frame, text="Mostrar")
    mostrar_button.pack(side=tk.LEFT, padx=5)

    aceptar_button = tk.Button(botones_frame, text="Aceptar", command=aceptar_cuerpo)
    aceptar_button.pack(side=tk.LEFT, padx=5)

    salir_button = tk.Button(botones_frame, text="Salir", command=ventana_cuerpo.destroy)
    salir_button.pack(side=tk.LEFT, padx=5)

    # Función para crear una estrella
    def crear_estrella():
        forma = "O"  # Forma de la estrella
        tamano = 24  # Tamaño grande
        cola = 0  # Sin cola
        masa = 1000.0  # Masa muy grande
        color = "#FFFF00"  # Amarillo
        posicion = (300, 300)  # Centro del Canvas
        velocidad = (0, 0)  # Sin velocidad inicial

        # Crear un nuevo cuerpo
        estrella = Cuerpo(forma, tamano, cola, masa, color, posicion, velocidad)

        # Añadir la estrella a la simulación
        simulacion.agregar_cuerpo(estrella)

        # Dibujar la estrella en el visualizador
        dibujar_cuerpo(forma, tamano, color, posicion)

    # Botón para crear una estrella
    btn_crear_estrella = tk.Button(ventana_cuerpo, text="Crear Estrella", command=crear_estrella)
    btn_crear_estrella.pack(side=tk.TOP, pady=10)