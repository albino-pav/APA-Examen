import re
import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as msg

def normalizaHoras(ficText, ficNorm):
    """
    Lee el fichero ficText, y normaliza las expresiones horarias como por ejemplo:

    - 8h30m -> 08:30
    - 7h -> 07:00
    - 08:05 -> 08:05
    - 5 menos cuarto -> 04:45
    - 6 y media -> 06:30
    - 8 en punto -> 08:00
    """

    patrones = [
        # hh:mm exacto
        (re.compile(r'\b(\d{1,2}):([0-5]\d)\b'), lambda h, m: f'{int(h):02d}:{int(m):02d}'),

        # HHhMMm como 7h o 7h30m
        (re.compile(r'\b(\d{1,2})h(?:(\d{1,2})m)?\b'), lambda h, m=None: f'{int(h):02d}:{int(m):02d}' if m is not None and int(m) < 60 else (f'{int(h):02d}:00' if m is None else f'{h}h{m}m')),

        # habladas: "x en punto"
        (re.compile(r'\b(\d{1,2})\s+en punto\b'), lambda h: f'{int(h):02d}:00' if 1 <= int(h) <= 12 else f'{h} en punto'),

        # habladas: "x y media"
        (re.compile(r'\b(\d{1,2})\s+y media\b'), lambda h: f'{int(h):02d}:30' if 1 <= int(h) <= 12 else f'{h} y media'),

        # habladas: "x y cuarto"
        (re.compile(r'\b(\d{1,2})\s+y cuarto\b'), lambda h: f'{int(h):02d}:15' if 1 <= int(h) <= 12 else f'{h} y cuarto'),

        # habladas: "x menos cuarto"
        (re.compile(r'\b(\d{1,2})\s+menos cuarto\b'), lambda h: f'{(int(h)-1)%12:02d}:45' if 1 <= int(h) <= 12 else f'{h} menos cuarto'),

        # con referencias de momento del día
        (re.compile(r'\b(1[0-2]|[1-9])\s+de la mañana\b'), lambda h: f'{int(h):02d}:00'),
        (re.compile(r'\b(1[0-2]|[1-9])\s+del mediodía\b'), lambda h: f'{(12 if int(h) == 12 else int(h)):02d}:00'),
        (re.compile(r'\b(1[0-2]|[1-9])\s+de la tarde\b'), lambda h: f'{(int(h)+12)%24:02d}:00' if int(h) < 12 else f'{h} de la tarde'),
        (re.compile(r'\b(1[0-2]|[1-9])\s+de la noche\b'), lambda h: f'{(int(h)+12)%24:02d}:00' if int(h) != 12 else '00:00'),
        (re.compile(r'\b(1[0-2]|[1-9])\s+de la madrugada\b'), lambda h: f'{int(h)%12:02d}:00'),
    ]

    with open(ficText, 'rt', encoding='utf-8') as fin, open(ficNorm, 'wt', encoding='utf-8') as fout:
        for linea in fin:
            original = linea
            for patron, formato in patrones:
                def reemplazo(match):
                    try:
                        return formato(*match.groups())
                    except:
                        return match.group(0)
                linea = patron.sub(reemplazo, linea)
            fout.write(linea)

def seleccionar_archivo_entrada():
    archivo = fd.askopenfilename(title="Selecciona un archivo de entrada", initialdir='ficheros', filetypes=[("Archivos de texto", "*.txt")])
    entrada_var.set(archivo)

def normalizar():
    ficText = entrada_var.get()
    nombre_salida = salida_var.get()

    if ficText and nombre_salida:
        carpeta_salida = 'ficheros'
        # Crear carpeta si no existe
        os.makedirs(carpeta_salida, exist_ok=True)
        ficNorm = os.path.join(carpeta_salida, f"{nombre_salida}.txt")  # Agregar ruta completa con carpeta y extensión .txt
        normalizaHoras(ficText, ficNorm)
        msg.showinfo("Éxito", f"Las horas han sido normalizadas y guardadas en:\n{ficNorm}")
    else:
        msg.showwarning("Advertencia", "Por favor, seleccione el archivo de entrada y escriba el nombre del archivo de salida.")

# Interfaz gráfica
root = tk.Tk()
root.title("Normalizador de Horas")

entrada_var = tk.StringVar()
salida_var = tk.StringVar()

tk.Label(root, text="Archivo de entrada:").pack(pady=5)
tk.Entry(root, textvariable=entrada_var, width=50).pack(pady=5)
tk.Button(root, text="Seleccionar", command=seleccionar_archivo_entrada).pack(pady=5)

tk.Label(root, text="Nombre del archivo de salida (sin extensión):").pack(pady=5)
tk.Entry(root, textvariable=salida_var, width=50).pack(pady=5)

tk.Button(root, text="Normalizar", command=normalizar).pack(pady=20)

root.mainloop()

