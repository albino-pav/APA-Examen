import pygame
import customtkinter as ctk
import random
import tkinter.colorchooser as colorchooser
import tkinter as tk
import math
import os

# Configuración inicial
ANCHO, ALTO = 1000, 780
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class CuerpoCeleste:
    def __init__(self, forma, tamano, color, masa, posicion, velocidad, cola):
        self.forma = forma
        self.tamano = tamano
        self.color = color
        self.masa = masa
        self.posicion = list(posicion)
        self.velocidad = list(velocidad)
        self.cola = cola
        self.historial = []
        self.posicion_inicial = list(posicion)
        self.velocidad_inicial = list(velocidad)

    def actualizar_posicion(self, delta_t):
        self.posicion[0] += self.velocidad[0] * delta_t
        self.posicion[1] += self.velocidad[1] * delta_t
        self.historial.append(tuple(self.posicion))
        if len(self.historial) > self.cola:
            self.historial.pop(0)

    def dibujar(self, surface):
        for punto in self.historial:
            pygame.draw.circle(surface, self.color, (int(punto[0]), int(punto[1])), 2)

        x, y = int(self.posicion[0]), int(self.posicion[1])
        r = self.tamano
        if self.forma == "círculo":
            pygame.draw.circle(surface, self.color, (x, y), r)
        elif self.forma == "estrella":
            pygame.draw.polygon(surface, self.color, [(x, y - r), (x + r // 2, y + r), (x - r, y - r // 3), (x + r, y - r // 3), (x - r // 2, y + r)])
        elif self.forma == "+":
            pygame.draw.line(surface, self.color, (x - r, y), (x + r, y), 2)
            pygame.draw.line(surface, self.color, (x, y - r), (x, y + r), 2)
        elif self.forma == "x":
            pygame.draw.line(surface, self.color, (x - r, y - r), (x + r, y + r), 2)
            pygame.draw.line(surface, self.color, (x - r, y + r), (x + r, y - r), 2)
        elif self.forma == "punto":
            pygame.draw.circle(surface, self.color, (x, y), 1)

class Simulador:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Simulador de Gravedad")
        self.cossos = []
        self.simulando = False
        self.surface = None
        self.reloj = pygame.time.Clock()
        self.delta_t = 1
        self.fps = 30
        self.G = 1.0
        self.color_fondo = (0, 0, 0)
        self.crear_widgets()
        self.iniciar_pygame()
        self.root.after(1000 // self.fps, self.bucle)
        self.root.protocol("WM_DELETE_WINDOW", self.terminar_programa)
        self.root.mainloop()

    def crear_widgets(self):
        marco_botones = ctk.CTkFrame(self.root)
        marco_botones.pack(side="left", padx=10, pady=10, fill="y")

        ctk.CTkButton(marco_botones, text="CREAR CUERPO", command=self.abrir_finestra_cos).pack(pady=5)
        ctk.CTkButton(marco_botones, text="CAMBIAR COLOR FONDO", command=self.cambiar_color_fondo).pack(pady=5)
        ctk.CTkButton(marco_botones, text="INICIAR", command=self.iniciar_simulacion).pack(pady=5)
        ctk.CTkButton(marco_botones, text="REINICIAR", command=self.reiniciar_simulacion).pack(pady=5)
        ctk.CTkButton(marco_botones, text="RESET", command=self.resetear).pack(pady=5)
        ctk.CTkButton(marco_botones, text="TERMINAR", command=self.terminar_programa).pack(pady=5)

        ctk.CTkLabel(marco_botones, text="Constante G:").pack(pady=2)
        self.slider_G = ctk.CTkSlider(marco_botones, from_=0.01, to=10.0, number_of_steps=100, command=self.actualizar_G)
        self.slider_G.set(self.G)
        self.slider_G.pack(pady=2)

        ctk.CTkLabel(marco_botones, text="FPS:").pack(pady=2)
        self.slider_fps = ctk.CTkSlider(marco_botones, from_=1, to=120, number_of_steps=119, command=self.actualizar_fps)
        self.slider_fps.set(self.fps)
        self.slider_fps.pack(pady=2)

        ctk.CTkLabel(marco_botones, text="Incremento temporal:").pack(pady=2)
        self.slider_dt = ctk.CTkSlider(marco_botones, from_=0.01, to=5.0, number_of_steps=100, command=self.actualizar_dt)
        self.slider_dt.set(self.delta_t)
        self.slider_dt.pack(pady=2)

    def actualizar_G(self, valor):
        self.G = float(valor)

    def actualizar_fps(self, valor):
        self.fps = int(float(valor))

    def actualizar_dt(self, valor):
        self.delta_t = float(valor)

    def cambiar_color_fondo(self):
        color = colorchooser.askcolor()[0]
        if color:
            self.color_fondo = tuple(map(int, color))

    def iniciar_pygame(self):
        os.environ["SDL_VIDEODRIVER"] = "x11"
        pygame.display.init()
        self.surface = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Simulación")

    def bucle(self):
        if self.simulando:
            self.actualizar_simulacion()
        self.dibujar_cossos()
        self.root.after(1000 // self.fps, self.bucle)

    def actualizar_simulacion(self):
        for i, cuerpo1 in enumerate(self.cossos):
            for j, cuerpo2 in enumerate(self.cossos):
                if i != j:
                    dx = cuerpo2.posicion[0] - cuerpo1.posicion[0]
                    dy = cuerpo2.posicion[1] - cuerpo1.posicion[1]
                    distancia = math.sqrt(dx**2 + dy**2) + 1e-5
                    if distancia < (cuerpo1.tamano + cuerpo2.tamano):
                        distancia = cuerpo1.tamano + cuerpo2.tamano

                    fuerza = self.G * cuerpo1.masa * cuerpo2.masa / (distancia ** 2)
                    direccion = [dx / distancia, dy / distancia]
                    aceleracion = [fuerza * direccion[0] / cuerpo1.masa, fuerza * direccion[1] / cuerpo1.masa]

                    max_acc = 10
                    aceleracion[0] = max(-max_acc, min(max_acc, aceleracion[0]))
                    aceleracion[1] = max(-max_acc, min(max_acc, aceleracion[1]))

                    cuerpo1.velocidad[0] += aceleracion[0] * self.delta_t
                    cuerpo1.velocidad[1] += aceleracion[1] * self.delta_t

        for cuerpo in self.cossos:
            cuerpo.actualizar_posicion(self.delta_t)

    def dibujar_cossos(self):
        if not self.surface:
            return
        self.surface.fill(self.color_fondo)
        for cuerpo in self.cossos:
            cuerpo.dibujar(self.surface)
        pygame.display.flip()

    def iniciar_simulacion(self):
        self.simulando = True

    def reiniciar_simulacion(self):
        for cuerpo in self.cossos:
            cuerpo.historial.clear()
            cuerpo.posicion = list(cuerpo.posicion_inicial)
            cuerpo.velocidad = list(cuerpo.velocidad_inicial)
        self.simulando = True

    def resetear(self):
        self.simulando = False
        self.cossos.clear()

    def terminar_programa(self):
        pygame.quit()
        self.root.destroy()

    def abrir_finestra_cos(self):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Crear Cuerpo")
        ventana.geometry("400x700")

        formas = ["círculo", "estrella", "+", "x", "punto"]
        tamanos = list(range(2, 20, 2))
        masas = list(range(1, 21))
        colas = list(range(10, 110, 10))

        ctk.CTkLabel(ventana, text="Forma:").pack(pady=2)
        combo_forma = ctk.CTkComboBox(ventana, values=formas)
        combo_forma.set("círculo")
        combo_forma.pack(pady=2)

        ctk.CTkLabel(ventana, text="Color:").pack(pady=2)
        color_cuerpo = [255, 255, 255]

        def elegir_color():
            color = colorchooser.askcolor()[0]
            if color:
                color_cuerpo[0:3] = map(int, color)

        ctk.CTkButton(ventana, text="Elegir color del cuerpo", command=elegir_color).pack(pady=2)

        ctk.CTkLabel(ventana, text="Tamaño:").pack(pady=2)
        combo_tamano = ctk.CTkComboBox(ventana, values=[str(i) for i in tamanos])
        combo_tamano.set("8")
        combo_tamano.pack(pady=2)

        ctk.CTkLabel(ventana, text="Masa:").pack(pady=2)
        combo_masa = ctk.CTkComboBox(ventana, values=[str(i) for i in masas])
        combo_masa.set("5")
        combo_masa.pack(pady=2)

        ctk.CTkLabel(ventana, text="Cola (historial):").pack(pady=2)
        combo_cola = ctk.CTkComboBox(ventana, values=[str(i) for i in colas])
        combo_cola.set("30")
        combo_cola.pack(pady=2)

        ctk.CTkLabel(ventana, text="Posición inicial (x y):").pack(pady=2)
        entrada_posx = ctk.CTkEntry(ventana, placeholder_text="X")
        entrada_posx.pack(pady=1)
        entrada_posy = ctk.CTkEntry(ventana, placeholder_text="Y")
        entrada_posy.pack(pady=1)

        ctk.CTkLabel(ventana, text="Velocidad inicial (vx vy):").pack(pady=2)
        entrada_velx = ctk.CTkEntry(ventana, placeholder_text="Vx")
        entrada_velx.pack(pady=1)
        entrada_vely = ctk.CTkEntry(ventana, placeholder_text="Vy")
        entrada_vely.pack(pady=1)

        def agregar_manual():
            forma = combo_forma.get()
            tamano = int(combo_tamano.get())
            masa = int(combo_masa.get())
            cola = int(combo_cola.get())
            try:
                pos = [float(entrada_posx.get()), float(entrada_posy.get())]
                vel = [float(entrada_velx.get()), float(entrada_vely.get())]
            except:
                pos = [random.randint(200, 800), random.randint(200, 600)]
                vel = [random.uniform(-1, 1), random.uniform(-1, 1)]
            nuevo = CuerpoCeleste(forma, tamano, tuple(color_cuerpo), masa, pos, vel, cola)
            self.cossos.append(nuevo)

        ctk.CTkButton(ventana, text="Añadir cuerpo", command=agregar_manual).pack(pady=10)

        ctk.CTkLabel(ventana, text="Nº cuerpos aleatorios:").pack(pady=2)
        entrada_num = ctk.CTkEntry(ventana, placeholder_text="Número")
        entrada_num.pack(pady=2)

        def crear_aleatorios():
            try:
                n = int(entrada_num.get())
            except:
                return
            for _ in range(n):
                forma = random.choice(formas)
                color = tuple(random.randint(0, 255) for _ in range(3))
                tamano = random.choice(tamanos)
                masa = random.choice(masas)
                cola = random.choice(colas)
                pos = [random.randint(100, 900), random.randint(100, 700)]
                vel = [random.uniform(-1, 1), random.uniform(-1, 1)]
                cuerpo = CuerpoCeleste(forma, tamano, color, masa, pos, vel, cola)
                self.cossos.append(cuerpo)

        ctk.CTkButton(ventana, text="Crear aleatorios", command=crear_aleatorios).pack(pady=5)

if __name__ == '__main__':
    Simulador()
