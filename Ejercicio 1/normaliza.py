"""
normaliza.py - Ejercicio 1: Normalización de Expresiones Horarias

Este programa permite leer un fichero de texto, detectar expresiones horarias 
en lenguaje natural y normalizarlas al formato HH:MM de 24 horas.

Expresiones soportadas:
- Formato HH:MM (ej. 7:05)
- Formato con sufijos h y m (ej. 8h27m, 7h)
- Expresiones en texto (ej. "8 en punto", "9 y cuarto", "10 menos cuarto")
- Expresiones con periodo (ej. "7 de la mañana", "4 de la tarde", "12 de la noche")

Las expresiones horarias incorrectas o no reconocidas se dejan sin modificar.

Al ejecutar el programa, se abre un diálogo gráfico para seleccionar:
1. El fichero de entrada (.txt) con el texto a procesar.
2. El fichero de salida (.txt) donde se guardará el texto con horas normalizadas.

Requiere:
- Módulo estándar `re` para expresiones regulares
- Módulo estándar `tkinter` para la interfaz gráfica

Autor: Joan Gallardo
Fecha: Junio 2025
"""


import re
from tkinter import Tk, filedialog

def normalizaHoras(ficText, ficNorm):
    def corrige_hora(match):
        h = int(match.group(1))
        m = int(match.group(2)) if match.group(2) else 0
        return f'{h:02}:{m:02}' if 0 <= h < 24 and 0 <= m < 60 else match.group(0)

    def corrige_hhmm(match):
        h = int(match.group(1))
        m = int(match.group(2))
        return f'{h:02}:{m:02}' if 0 <= h < 24 and 0 <= m < 60 else match.group(0)

    def corrige_en_punto(match):
        h = int(match.group(1))
        return f'{h % 12:02}:00' if 1 <= h <= 12 else match.group(0)

    def corrige_y_cuarto_media(match):
        h = int(match.group(1))
        sufijo = match.group(2)
        if 1 <= h <= 12:
            if "cuarto" in sufijo:
                return f'{h % 12:02}:15'
            elif "media" in sufijo:
                return f'{h % 12:02}:30'
        return match.group(0)

    def corrige_menos_cuarto(match):
        h = int(match.group(1))
        return f'{(h - 1) % 12:02}:45' if 2 <= h <= 12 else match.group(0)

    def corrige_con_periodo(match):
        h = int(match.group(1))
        m = 0
        periodo = match.group(2)
        if periodo == "de la mañana":
            if 4 <= h <= 12:
                return f'{h % 12:02}:{m:02}'
        elif periodo == "del mediodía":
            if 12 <= h <= 15:
                return f'{(h if h < 13 else h - 12) + 12:02}:{m:02}'
        elif periodo == "de la tarde":
            if 3 <= h <= 8:
                return f'{(h + 12) % 24:02}:{m:02}'
        elif periodo == "de la noche":
            if 8 <= h <= 11:
                return f'{h % 12:02}:{m:02}'
            elif h == 12:
                return f'00:{m:02}'
        elif periodo == "de la madrugada":
            if 1 <= h <= 6:
                return f'{h % 12:02}:{m:02}'
        return match.group(0)

    with open(ficText, encoding='utf-8') as fin, open(ficNorm, 'w', encoding='utf-8') as fout:
        for linea in fin:
            linea = re.sub(r'\b(\d{1,2}):(\d{2})\b', corrige_hora, linea)
            linea = re.sub(r'\b(\d{1,2})h(\d{1,2})m\b', corrige_hhmm, linea)
            linea = re.sub(r'\b(\d{1,2})h\b', lambda m: f'{int(m.group(1)):02}:00' if 0 <= int(m.group(1)) < 24 else m.group(0), linea)
            linea = re.sub(r'\b(\d{1,2}) en punto\b', corrige_en_punto, linea)
            linea = re.sub(r'\b(\d{1,2}) y (cuarto|media)\b', corrige_y_cuarto_media, linea)
            linea = re.sub(r'\b(\d{1,2}) menos cuarto\b', corrige_menos_cuarto, linea)
            linea = re.sub(r'\b(\d{1,2}) (de la mañana|de la noche|del mediodía|de la tarde|de la madrugada)\b',
                           corrige_con_periodo, linea)
            fout.write(linea)

if __name__ == '__main__':
    # Desactiva ventana principal de Tkinter
    root = Tk()
    root.withdraw()

    print("Selecciona el archivo de entrada (.txt)")
    fichero_entrada = filedialog.askopenfilename(filetypes=[("Ficheros de texto", "*.txt")])
    if not fichero_entrada:
        print("No se seleccionó ningún archivo de entrada.")
        exit()

    print("Selecciona dónde guardar el archivo de salida (.txt)")
    fichero_salida = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Ficheros de texto", "*.txt")])
    if not fichero_salida:
        print("No se seleccionó ningún archivo de salida.")
        exit()

    normalizaHoras(fichero_entrada, fichero_salida)
    print(f"Archivo normalizado guardado en: {fichero_salida}")

