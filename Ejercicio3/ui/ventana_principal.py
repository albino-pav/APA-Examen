import tkinter as tk
from tkinter import ttk, colorchooser
from ui.ventana_crear_cuerpo import abrir_ventana_crear_cuerpo
from logic.simulacion import Simulacion

def iniciar_aplicacion():
    root = tk.Tk()
    root.title("Simulador de Cuerpos Gravitatorios 2D")
    root.geometry("1080x720")

    # Visualizador (Canvas)
    visualizador = tk.Canvas(root, bg="black", width=500, height=600)
    visualizador.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Crear instancia de la simulación
    simulacion = Simulacion()

    # Función para redibujar los cuerpos en el visualizador
    def redibujar_cuerpos():
        visualizador.delete("all")  # Limpiar el Canvas
        for cuerpo in simulacion.cuerpos:
            x, y = cuerpo.posicion
            r = int(cuerpo.tamano)
            forma = cuerpo.forma
            color = cuerpo.color

            # Dibujar la cola
            if len(cuerpo.trayectoria) > 1:
                visualizador.create_line(
                    *[coord for pos in cuerpo.trayectoria for coord in pos],  # Descomponer las posiciones en coordenadas
                    fill=color,
                    width=1
                )

            # Dibujar según la forma del cuerpo
            if forma == "*":  # Dibujar un círculo
                visualizador.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            elif forma == "+":  # Dibujar una cruz
                visualizador.create_line(x - r, y, x + r, y, fill=color, width=2)
                visualizador.create_line(x, y - r, x, y + r, fill=color, width=2)
            elif forma == "X":  # Dibujar una X
                visualizador.create_line(x - r, y - r, x + r, y + r, fill=color, width=2)
                visualizador.create_line(x - r, y + r, x + r, y - r, fill=color, width=2)
            elif forma == "O":  # Dibujar un círculo con borde
                visualizador.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
            elif forma == ".":  # Dibujar un punto
                visualizador.create_oval(x - 1, y - 1, x + 1, y + 1, fill=color, outline="")

    # Función para actualizar la simulación
    def actualizar_simulacion():
        delta_t = slider_tiempo.get()  # Obtener el incremento temporal del slider
        simulacion.actualizar(delta_t)
        redibujar_cuerpos()
        if btn_inicia["text"] == "Pausa":  # Continuar solo si el botón está en "Pausa"
            root.after(33, actualizar_simulacion)  # Aproximadamente 30 FPS

    # Función para manejar el botón "Inicia/Pausa"
    def iniciar_pausar_simulacion():
        if btn_inicia["text"] == "Inicia":
            btn_inicia.config(text="Pausa")
            actualizar_simulacion()
        elif btn_inicia["text"] == "Pausa":
            btn_inicia.config(text="Continua")
        elif btn_inicia["text"] == "Continua":
            btn_inicia.config(text="Pausa")
            actualizar_simulacion()

    # Controles
    controles_frame = tk.Frame(root, bg="lightgray", width=300, height=600)
    controles_frame.pack(side=tk.RIGHT, fill=tk.Y)

    # Controles principales (botones inferiores)
    botones_frame = tk.Frame(controles_frame, bg="lightgray")
    botones_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    btn_inicia = tk.Button(botones_frame, text="Inicia", width=10, command=iniciar_pausar_simulacion)
    btn_inicia.pack(side=tk.LEFT, padx=5)

    btn_reinicia = tk.Button(botones_frame, text="Reinicia", width=10, command=lambda: reiniciar_simulacion())
    btn_reinicia.pack(side=tk.LEFT, padx=5)

    btn_reset = tk.Button(botones_frame, text="Reset", width=10, command=lambda: reset_simulacion())
    btn_reset.pack(side=tk.LEFT, padx=5)

    btn_termina = tk.Button(botones_frame, text="Termina", width=10, command=root.quit)
    btn_termina.pack(side=tk.LEFT, padx=5)

    # Botón para cambiar el color de fondo
    color_frame = tk.Frame(controles_frame, bg="lightgray")
    color_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    color_label = tk.Label(color_frame, text="Color del fondo galáctico:", bg="lightgray")
    color_label.pack(side=tk.LEFT, padx=5)

    def cambiar_color_fondo():
        color = colorchooser.askcolor(title="Selecciona un color")[1]
        if color:
            visualizador.config(bg=color)

    btn_color = tk.Button(color_frame, text="Cambiar color", command=cambiar_color_fondo)
    btn_color.pack(side=tk.LEFT, padx=5)

    # Parámetros Generales (sliders con nombres y valores)
    parametros_frame = tk.LabelFrame(controles_frame, text="Parámetros Generales", bg="lightgray")
    parametros_frame.pack(side=tk.TOP, fill=tk.X, pady=10, padx=5)

    # Slider para Constante Gravitatoria
    gravedad_frame = tk.Frame(parametros_frame, bg="lightgray")
    gravedad_frame.pack(fill=tk.X, pady=5)
    
    gravedad_label = tk.Label(gravedad_frame, text="Constante Gravitatoria:", bg="lightgray")
    gravedad_label.pack(side=tk.LEFT, padx=5)
    
    def actualizar_constante_gravitacional(value):
        simulacion.constante_gravitacional = float(value)
    
    slider_gravedad = ttk.Scale(gravedad_frame, from_=0.1, to=10, orient=tk.HORIZONTAL, command=actualizar_constante_gravitacional)
    slider_gravedad.set(7.0)  # Valor inicial medio alto (por ejemplo, 7.0)
    slider_gravedad.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)


    # Slider para Reproducción (con valor visible)
    fps_frame = tk.Frame(parametros_frame, bg="lightgray")
    fps_frame.pack(fill=tk.X, pady=5)

    fps_label = tk.Label(fps_frame, text="Reproducción (fps):", bg="lightgray")
    fps_label.pack(side=tk.LEFT, padx=5)

    fps_value = tk.StringVar(value="30 fps")  # Valor inicial
    slider_fps = ttk.Scale(fps_frame, from_=0.5, to=60, orient=tk.HORIZONTAL, command=lambda v: fps_value.set(f"{float(v):.1f} fps"))
    slider_fps.set(30)  # Valor inicial
    slider_fps.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

    fps_value_label = tk.Label(fps_frame, textvariable=fps_value, bg="lightgray")
    fps_value_label.pack(side=tk.LEFT, padx=5)

    # Slider para Incremento Temporal
    tiempo_frame = tk.Frame(parametros_frame, bg="lightgray")
    tiempo_frame.pack(fill=tk.X, pady=5)

    tiempo_label = tk.Label(tiempo_frame, text="Incremento Temporal:", bg="lightgray")
    tiempo_label.pack(side=tk.LEFT, padx=5)

    slider_tiempo = ttk.Scale(tiempo_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL)
    slider_tiempo.set(0.2)  # Valor inicial lento (por ejemplo, 0.1)
    slider_tiempo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
    # Botón para abrir la ventana de creación de cuerpos
    btn_crear_cuerpo = tk.Button(controles_frame, text="Crear Cuerpo", command=lambda: abrir_ventana_crear_cuerpo(root, visualizador, simulacion))
    btn_crear_cuerpo.pack(side=tk.TOP, pady=10)

    def reiniciar_simulacion():
        for cuerpo in simulacion.cuerpos:
            cuerpo.posicion = cuerpo.posicion_inicial  # Restaurar la posición inicial
            cuerpo.velocidad = cuerpo.velocidad_inicial  # Restaurar la velocidad inicial
            cuerpo.trayectoria.clear()  # Limpiar la trayectoria
        redibujar_cuerpos()  # Redibujar los cuerpos en el visualizador

    def reset_simulacion():
        simulacion.cuerpos.clear()  # Vaciar la lista de cuerpos en la simulación
        visualizador.delete("all")  # Limpiar el Canvas del visualizador

    root.mainloop()