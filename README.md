Algorismia i Programació Audiovisual
====================================

Examen Final - Primavera de 2025
Nom: Mark Bonete Ventura
--------------------------------

Ejercicio 1: Programa de Normalización de Expresiones Horarias (20%)
----------------------------------------------------------------------

- Construya el programa `normaliza.py`que permita leer un fichero de texto, normalice
  las expresiones horarias en él contenidas según las instrucciones de la tarea APA-T6
  y escriba el resultado en otro fichero de texto.
- El fichero de entrada y el nombre del fichero de salida tendrán la extensión `.txt` y
  se escogerán usando las funciones gráficas de `TkInter.filedialog`.
- No se evaluará la calidad de la normalización (ese aspecto se evalúa en APA-T6).

```p
import tkinter as tk
from tkinter import filedialog
from horas import normalizaHoras

def main():
    # Crea una raíz de Tkinter oculta
    root = tk.Tk()
    root.withdraw()

    # Selección del fichero de entrada
    ficText = filedialog.askopenfilename(
        title="Seleccione el fichero de texto a normalizar",
        filetypes=[("Ficheros de texto", "*.txt")]
    )
    if not ficText:
        print("No se seleccionó ningún fichero de entrada.")
        return

    # Selección del fichero de salida
    ficNorm = filedialog.asksaveasfilename(
        title="Seleccione el fichero donde guardar el texto normalizado",
        defaultextension=".txt",
        filetypes=[("Ficheros de texto", "*.txt")]
    )
    if not ficNorm:
        print("No se seleccionó ningún fichero de salida.")
        return

    # Ejecutar la normalización
    normalizaHoras(ficText, ficNorm)
    print(f"Normalización completada.\nArchivo guardado en: {ficNorm}")

if __name__ == "__main__":
    main()
```

Ejercicio 2: Programa de Manejo de Señales Estéreo (35%)
--------------------------------------------------------

- Construya el programa `mono.py` que permita realizar las funciones de la tarea
  APA-T5 en un entorno gráfico usando TkInter.
- El programa contará con cuatro pestañas de `ttk.notebook`:

  - Pestaña `Estéreo a Mono`
  - Pestaña `Mono a Estéreo`
  - Pestaña `Codifica Estéreo`
  - Pestaña `Descodifica Estéreo`

  En cada una de estas pestañas se dispondrán de todos los artilugios necesarios para:
  
  - Seleccionar el o los ficheros de entrada.
  - Realizar la operación correspondiente.
  - Escuchar cada una de las señales involucradas, tanto de entrada como de salida.
  - Escribir la señal resultante en un fichero cuyo nombre se indicará al seleccionar la opción de `Guardar`.

- No se evaluará la corrección de las funciones desarrolladas en la tarea APA-T5, pero el programa deberá
  ser compatible con sus interfaces, de manera que, al susituir el
  `estereo.py` presentado por uno que funcione correctamente, el programa `mono.py` también lo hará.

```p
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sounddevice as sd
import soundfile as sf
import os
from estereo import estereo2mono, mono2estereo, codEstereo, decEstereo

class MonoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Audio Estéreo/Mono")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')

        self.fichero_entrada = None
        self.fichero_salida = None

        self._crear_pestana_estereo2mono()
        self._crear_pestana_mono2estereo()
        self._crear_pestana_codifica()
        self._crear_pestana_descodifica()

    def _crear_pestana_estereo2mono(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estéreo a Mono")

        self.entrada_1 = tk.StringVar()
        self.canal = tk.IntVar(value=2)

        ttk.Label(frame, text="Fichero Estéreo:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_1, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self._abrir_fichero_estereo).pack()

        ttk.Label(frame, text="Canal: 0=Izq, 1=Der, 2=Semisuma, 3=Semidif").pack()
        ttk.Entry(frame, textvariable=self.canal).pack()

        ttk.Button(frame, text="Reproducir Estéreo", command=lambda: self._reproducir(self.entrada_1.get())).pack()
        ttk.Button(frame, text="Convertir y Guardar", command=self._convertir_estereo_a_mono).pack()

    def _crear_pestana_mono2estereo(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mono a Estéreo")

        self.entrada_izq = tk.StringVar()
        self.entrada_der = tk.StringVar()
        self.salida_estereo = tk.StringVar()

        ttk.Label(frame, text="Fichero Izquierdo:").pack()
        ttk.Entry(frame, textvariable=self.entrada_izq, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.entrada_izq)).pack()

        ttk.Label(frame, text="Fichero Derecho:").pack()
        ttk.Entry(frame, textvariable=self.entrada_der, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.entrada_der)).pack()

        ttk.Label(frame, text="Guardar como:").pack()
        ttk.Entry(frame, textvariable=self.salida_estereo, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._guardar_fichero(self.salida_estereo)).pack()

        ttk.Button(frame, text="Convertir a Estéreo", command=self._convertir_mono_a_estereo).pack()

    def _crear_pestana_codifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Codifica Estéreo")

        self.fic_cod_in = tk.StringVar()
        self.fic_cod_out = tk.StringVar()

        ttk.Label(frame, text="Fichero Estéreo (16b):").pack()
        ttk.Entry(frame, textvariable=self.fic_cod_in, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.fic_cod_in)).pack()

        ttk.Label(frame, text="Guardar codificado (32b):").pack()
        ttk.Entry(frame, textvariable=self.fic_cod_out, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._guardar_fichero(self.fic_cod_out)).pack()

        ttk.Button(frame, text="Codificar", command=self._codificar_estereo).pack()

    def _crear_pestana_descodifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Descodifica Estéreo")

        self.fic_dec_in = tk.StringVar()
        self.fic_dec_out = tk.StringVar()

        ttk.Label(frame, text="Fichero Codificado (32b):").pack()
        ttk.Entry(frame, textvariable=self.fic_dec_in, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.fic_dec_in)).pack()

        ttk.Label(frame, text="Guardar como Estéreo (16b):").pack()
        ttk.Entry(frame, textvariable=self.fic_dec_out, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._guardar_fichero(self.fic_dec_out)).pack()

        ttk.Button(frame, text="Descodificar", command=self._descodificar_estereo).pack()

    # Funciones auxiliares

    def _abrir_fichero_estereo(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            self.entrada_1.set(path)

    def _seleccionar_fichero(self, var):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            var.set(path)

    def _guardar_fichero(self, var):
        path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if path:
            var.set(path)

    def _reproducir(self, filename):
        try:
            data, fs = sf.read(filename)
            sd.play(data, fs)
        except Exception as e:
            messagebox.showerror("Error al reproducir", str(e))

    def _convertir_estereo_a_mono(self):
        entrada = self.entrada_1.get()
        canal = self.canal.get()
        salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if not entrada or not salida:
            return
        try:
            estereo2mono(entrada, salida, canal)
            messagebox.showinfo("Conversión completada", f"Fichero guardado: {salida}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _convertir_mono_a_estereo(self):
        ficIzq = self.entrada_izq.get()
        ficDer = self.entrada_der.get()
        ficEste = self.salida_estereo.get()
        try:
            mono2estereo(ficIzq, ficDer, ficEste)
            messagebox.showinfo("Conversión completada", f"Estéreo guardado en: {ficEste}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _codificar_estereo(self):
        fic_in = self.fic_cod_in.get()
        fic_out = self.fic_cod_out.get()
        try:
            codEstereo(fic_in, fic_out)
            messagebox.showinfo("Codificación completada", f"Fichero guardado: {fic_out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _descodificar_estereo(self):
        fic_in = self.fic_dec_in.get()
        fic_out = self.fic_dec_out.get()
        try:
            decEstereo(fic_in, fic_out)
            messagebox.showinfo("Descodificación completada", f"Fichero guardado: {fic_out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MonoGUI(root)
    root.mainloop()
```

Ejercicio 3: Programa de Visualización de Cuerpos Sometidos a Atracción Gravitatoria (45%)
---------------------------------------------------------------------------------------------

Realizar un programa de simulación de cuerpos celestes sometidos a la Ley de Gravitación Universal
de Newton. Como mínimo debe tener las mismas funcionalidades del programa `gravedad.exe` subido a Atenea
y hacerlo igual o mejor que éste.

```p
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
```

Entrega
-------

Los tres programas deberán estar preparados para ser ejecutados desde la línea de comandos o desde
una sesión `ipython` usando el comando `%run`.
