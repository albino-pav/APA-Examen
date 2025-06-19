# Ejercicio 2: Programa de Manejo de Señales Estéreo (35%)
# --------------------------------------------------------

# - Construya el programa `mono.py` que permita realizar las funciones de la tarea
#   APA-T5 en un entorno gráfico usando TkInter.
# - El programa contará con cuatro pestañas de `ttk.notebook`:

#   - Pestaña `Estéreo a Mono`
#   - Pestaña `Mono a Estéreo`
#   - Pestaña `Codifica Estéreo`
#   - Pestaña `Descodifica Estéreo`

#   En cada una de estas pestañas se dispondrán de todos los artilugios necesarios para:
  
#   - Seleccionar el o los ficheros de entrada.
#   - Realizar la operación correspondiente.
#   - Escuchar cada una de las señales involucradas, tanto de entrada como de salida.
#   - Escribir la señal resultante en un fichero cuyo nombre se indicará al seleccionar la opción de `Guardar`.

# - No se evaluará la corrección de las funciones desarrolladas en la tarea APA-T5, pero el programa deberá
#   ser compatible con sus interfaces, de manera que, al susituir el
#   `estereo.py` presentado por uno que funcione correctamente, el programa `mono.py` también lo hará.

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
import subprocess
import estereo 

def seleccionar_fichero():
    """Abre un cuadro de diálogo para seleccionar un fichero."""
    return askopenfilename(title="Selecciona un fichero", filetypes=[("Ficheros WAV", "*.wav")])

def reproducir_audio(fichero):
    """Reproduce un fichero de audio usando el reproductor predeterminado."""
    if os.path.exists(fichero):
        subprocess.run(["start", fichero], shell=True)

def generar_nombre_salida(ficEntrada, sufijo):
    """Genera automáticamente el nombre del fichero de salida."""
    base, ext = os.path.splitext(ficEntrada)
    return f"{base}_{sufijo}{ext}"

def estereo_a_mono():
    """Función para la pestaña 'Estéreo a Mono'."""
    ficEste = seleccionar_fichero()
    if not ficEste:
        return
    canal = int(canal_var.get())
    ficMono = generar_nombre_salida(ficEste, f"mono_canal{canal}")
    estereo.estereo2mono(ficEste, ficMono, canal)
    tk.messagebox.showinfo("Operación completada", f"El fichero monofónico se ha guardado en: {ficMono}")

def mono_a_estereo():
    """Función para la pestaña 'Mono a Estéreo'."""
    ficIzq = seleccionar_fichero()
    if not ficIzq:
        return
    ficDer = seleccionar_fichero()
    if not ficDer:
        return
    ficEste = generar_nombre_salida(ficIzq, "estereo")
    estereo.mono2estereo(ficIzq, ficDer, ficEste)
    tk.messagebox.showinfo("Operación completada", f"El fichero estéreo se ha guardado en: {ficEste}")

def codificar_estereo():
    """Función para la pestaña 'Codifica Estéreo'."""
    ficEste = seleccionar_fichero()
    if not ficEste:
        return
    ficCod = generar_nombre_salida(ficEste, "codificado")
    estereo.codEstereo(ficEste, ficCod)
    tk.messagebox.showinfo("Operación completada", f"El fichero codificado se ha guardado en: {ficCod}")

def decodificar_estereo():
    """Función para la pestaña 'Descodifica Estéreo'."""
    ficCod = seleccionar_fichero()
    if not ficCod:
        return
    ficEste = generar_nombre_salida(ficCod, "descodificado")
    estereo.decEstereo(ficCod, ficEste)
    tk.messagebox.showinfo("Operación completada", f"El fichero estéreo se ha guardado en: {ficEste}")

root = tk.Tk()
root.title("Manejo de Señales Estéreo")

notebook = ttk.Notebook(root)

# Pestaña 'Estéreo a Mono'
frame_estereo_mono = ttk.Frame(notebook)
notebook.add(frame_estereo_mono, text="Estéreo a Mono")
canal_var = tk.StringVar(value="2")
ttk.Label(frame_estereo_mono, text="Selecciona el canal:").pack(pady=5)
ttk.Radiobutton(frame_estereo_mono, text="Izquierdo", variable=canal_var, value="0").pack(anchor="w")
ttk.Radiobutton(frame_estereo_mono, text="Derecho", variable=canal_var, value="1").pack(anchor="w")
ttk.Radiobutton(frame_estereo_mono, text="Semisuma", variable=canal_var, value="2").pack(anchor="w")
ttk.Radiobutton(frame_estereo_mono, text="Semidiferencia", variable=canal_var, value="3").pack(anchor="w")
ttk.Button(frame_estereo_mono, text="Convertir", command=estereo_a_mono).pack(pady=10)

# Pestaña 'Mono a Estéreo'
frame_mono_estereo = ttk.Frame(notebook)
notebook.add(frame_mono_estereo, text="Mono a Estéreo")
ttk.Button(frame_mono_estereo, text="Convertir", command=mono_a_estereo).pack(pady=10)

# Pestaña 'Codifica Estéreo'
frame_codificar = ttk.Frame(notebook)
notebook.add(frame_codificar, text="Codifica Estéreo")
ttk.Button(frame_codificar, text="Codificar", command=codificar_estereo).pack(pady=10)

# Pestaña 'Descodifica Estéreo'
frame_descodificar = ttk.Frame(notebook)
notebook.add(frame_descodificar, text="Descodifica Estéreo")
ttk.Button(frame_descodificar, text="Descodificar", command=decodificar_estereo).pack(pady=10)


notebook.pack(expand=True, fill="both")

root.mainloop()
