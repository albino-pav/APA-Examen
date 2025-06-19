
"""
Maria Freixas Solé
normalitza.py

"""

import re
import tkinter as tk
from tkinter import filedialog

def normalizar_horas(fic_entrada, fic_salida):
    """
    Lee un fichero de texto y normaliza las expresiones horarias en él contenidas
    según las especificaciones de APA-T6. Escribe el resultado en otro fichero de texto.
    """
    # Lista de patrones y funciones de normalización
    patrones = [
        # 18h45m
        (re.compile(r'\b(\d{1,2})h(\d{1,2})m\b'),
         lambda h, m: f"{int(h):02d}:{int(m):02d}" if int(h) < 24 and int(m) < 60 else f"{h}h{m}m"),

        # 7h
        (re.compile(r'\b(\d{1,2})h\b'),
         lambda h: f"{int(h):02d}:00" if int(h) < 24 else f"{h}h"),

        # 8:05 o 08:27
        (re.compile(r'\b(\d{1,2}):(\d{1,2})\b'),
         lambda h, m: f"{int(h):02d}:{int(m):02d}" if int(h) < 24 and int(m) < 60 else f"{h}:{m}"),

        # 8 en punto
        (re.compile(r'\b(\d{1,2}) en punto\b'),
         lambda h: f"{int(h):02d}:00" if 1 <= int(h) <= 12 else f"{h} en punto"),

        # 8 y tres cuartos
        (re.compile(r'\b(\d{1,2}) y tres cuartos\b'),
        lambda h: f"{int(h):02d}:45" if int(h) < 24 else f"{h} y tres cuartos"),

        # 8 y media
        (re.compile(r'\b(\d{1,2}) y media\b'),
         lambda h: f"{int(h):02d}:30" if 1 <= int(h) <= 12 else f"{h} y media"),

        # 8 y cuarto
        (re.compile(r'\b(\d{1,2}) y cuarto\b'),
         lambda h: f"{int(h):02d}:15" if 1 <= int(h) <= 12 else f"{h} y cuarto"),

        # 8 menos cuarto
        (re.compile(r'\b(\d{1,2}) menos cuarto\b'),
         lambda h: f"{(int(h) - 1)%12 or 12:02d}:45" if 1 <= int(h) <= 12 else f"{h} menos cuarto"),

        # 8 menos (\d{1,2})
        (re.compile(r'\b(\d{1,2}) menos (\d{1,2})\b'),
         lambda h, m: f"{(int(h) - 1)%12 or 12:02d}:{60 - int(m):02d}" 
         if 1 <= int(h) <= 12 and 0 < int(m) < 60 else f"{h} menos {m}"),

        # 8 de la mañana
        (re.compile(r'\b(\d{1,2}) de la mañana\b'),
         lambda h: f"{int(h):02d}:00" if 4 <= int(h) <= 12 else f"{h} de la mañana"),

        # 12 del mediodía
        (re.compile(r'\b(\d{1,2}) del mediodía\b'),
         lambda h: f"12:00" if int(h) == 12 else f"{(int(h) + 12)%24:02d}:00" if 1 <= int(h) <= 3 else f"{h} del mediodía"),

        # 4 de la tarde
        (re.compile(r'\b(\d{1,2}) de la tarde\b'),
         lambda h: f"{int(h) + 12:02d}:00" if 1 <= int(h) <= 8 else f"{h} de la tarde"),

        # 10 de la noche
        (re.compile(r'\b(\d{1,2}) de la noche\b'),
         lambda h: f"{int(h) + 12:02d}:00" if 8 <= int(h) <= 11 else
                   f"00:00" if int(h) == 12 else
                   f"{int(h):02d}:00" if 1 <= int(h) <= 4 else f"{h} de la noche"),

        # 3 de la madrugada
        (re.compile(r'\b(\d{1,2}) de la madrugada\b'),
         lambda h: f"{int(h):02d}:00" if 1 <= int(h) <= 6 else f"{h} de la madrugada")
    ]

    with open(fic_entrada, encoding="utf-8") as entrada, open(fic_salida, "w", encoding="utf-8") as salida:
        for linea in entrada:
            nueva_linea = linea
            for patron, reemplazo in patrones:
                nueva_linea = patron.sub(lambda m: reemplazo(*m.groups()), nueva_linea)
            salida.write(nueva_linea)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    print("Selecciona el archivo de entrada (.txt)...")
    archivo_entrada = filedialog.askopenfilename(
        title="Archivo de entrada",
        filetypes=[("Archivos de texto", "*.txt")],
    )

    if not archivo_entrada:
        print("Operación cancelada.")
        exit()

    print("Selecciona el archivo de salida (.txt)...")
    archivo_salida = filedialog.asksaveasfilename(
        title="Archivo de salida",
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt")],
    )

    if not archivo_salida:
        print("Operación cancelada.")
        exit()

    normalizar_horas(archivo_entrada, archivo_salida)
    print(f"Normalización completada. Resultado guardado en: {archivo_salida}")