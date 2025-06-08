"""
normaliza.py

Guillem Perez Sanchez
QP 2025
"""
import re
import tkinter as tk
from tkinter import filedialog

def normaliza(ent,out):
    """
    Lee un fichero de texto y normaliza las expresiones horarias 
    en él (según la normalización de APA-T6), escribe el resultado
    en otro fichero de texto.
    """
    # Expresiones horarias correctas comunes
    patrones = [
        #18h45m
        (re.compile(r'\b(\d{1,2})h(\d{1,2})m\b'), 
         lambda h, m: f"{int(h):02d}:{int(m):02d}" if int(h) < 24 and int(m) < 60 else f"{h}h{m}m"),
        
        #7h
        (re.compile(r'\b(\d{1,2})h\b'), 
         lambda h: f"{int(h):02d}:00" if int(h) < 24 else f"{h}h"),
        
        #8:05
        (re.compile(r'\b(\d{1,2}):(\d{2})\b'), 
         lambda h, m: f"{int(h):02d}:{int(m):02d}" if int(h) < 24 and int(m) < 60 else f"{h}:{m}"),

        #... en punto
        (re.compile(r'\b(\d{1,2}) en punto\b'),
         lambda h: f"{int(h):02d}:00" if int(h)<24 else f"{h} en punto"),

        #... y media
        (re.compile(r'\b(\d{1,2}) y media\b'),
         lambda h: f"{int(h):02d}:30" if int(h)<24 else f"{h} y media"),

        #... y cuarto
        (re.compile(r'\b(\d{1,2}) y cuarto\b'),
         lambda h: f"{int(h):02d}:15" if int(h)<24 else f"{h} y cuarto"),
        
        #... y tres cuartos
        (re.compile(r'\b(\d{1,2}) y tres cuartos\b'),
         lambda h: f"{int(h):02d}:45" if int(h)<24 else f"{h} y tres cuartos"),

        #... de la mañana
        (re.compile(r'\b(\d{1,2}) de la mañana\b'),
         lambda h: f"{int(h):02d}:00" if 4<=int(h)<=12 else f"{h} de la mañana"),

        #... del mediodía
        (re.compile(r'\b(\d{1,2}) del mediodía\b'),
         lambda h: f"{int(h+12):02d}:00" if 1<=int(h)<=3 else
                   "00:00" if int(h)==12 else f"{h} del mediodía"),

        #... de la tarde
        (re.compile(r'\b(\d{1,2}) de la tarde\b'),
         lambda h: f"{int(h+12):02d}:00" if 3<=int(h)<=8 else f"{h} de la tarde"),

        #... de la noche
        (re.compile(r'\b(\d{1,2}) de la noche\b'),
         lambda h: f"{int(h+12):02d}:00" if 8<=int(h)<=11 else
                   f"{int(h):02d}:00" if 1<=int(h)<=4 else
                   "00:00" if int(h)==12 else f"{h} de la noche"),

        #... de la madrugada
        (re.compile(r'\b(\d{1,2}) de la madrugada\b'),
         lambda h: f"{int(h):02d}:00" if 1<=int(h)<=6 else f"{h} de la madrugada")
    ]

    with open(ficText, encoding="utf-8") as fin, open(ficNorm, "w", encoding="utf-8") as fout:
        for linea in fin:
            nueva = linea
            for patron, reemplazo in patrones:
                nueva = patron.sub(lambda m: reemplazo(*m.groups()), nueva)
            fout.write(nueva)

if __name__ == "__main__":
    import os

    # Iniciar tkinter en modo oculto
    root = tk.Tk()
    root.withdraw()

    print("Selecciona el archivo de entrada...")
    ficText = filedialog.askopenfilename(
        title="Selecciona el archivo de texto de entrada",
        filetypes=[("Archivos de texto", "*.txt")],
    )

    if not ficText:
        print("Operación cancelada.")
        exit()

    print("Selecciona el archivo de salida...")
    ficNorm = filedialog.asksaveasfilename(
        title="Selecciona el archivo de texto de salida",
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt")],
    )

    if not ficNorm:
        print("Operación cancelada.")
        exit()

    # Ejecutar la función
    normaliza(ficText, ficNorm)
    print(f"Normalización completada. Resultado guardado en:\n{ficNorm}")