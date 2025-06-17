
''' 
        Examen Final APA 

        Autores:
        Sebastián Pérez Capitano
        Àlex Segura Medina 

        Ejercicio 1: Programa de Normalización de Expresiones Horarias (20%)
        · Construya el programa normaliza.pyque permita leer un fichero de texto, normalice las expresiones horarias en él contenidas según las instrucciones de la tarea APA-T6 y escriba el resultado en otro fichero de texto.
        · El fichero de entrada y el nombre del fichero de salida tendrán la extensión .txt y se escogerán usando las funciones gráficas de TkInter.filedialog.
        · No se evaluará la calidad de la normalización (ese aspecto se evalúa en APA-T6).

'''


import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os
from datetime import datetime

# Usamos la función extraída de la tarea APA-T6 para normalizar las horas.
def normalizaHoras(ficText, ficNorm):
    def reemplaza(match):
        if match.group('hora_std'):
            h = int(match.group('hora_std'))
            m = int(match.group('min_std'))
            return f'{h:02}:{m:02}'

        elif match.group('hora_h'):
            h = int(match.group('hora_h'))
            m = match.group('min_h')
            m = int(m) if m else 0
            if 0 <= h <= 23 and 0 <= m <= 59:
                return f'{h:02}:{m:02}'
            return match.group(0)

        elif match.group('hora_nat'):
            h = int(match.group('hora_nat'))
            tipo = match.group('tipo') or ''
            periodo = match.group('periodo') or ''
            m = 0
            if tipo.strip() == 'y cuarto':
                m = 15
            elif tipo.strip() == 'y media':
                m = 30
            elif tipo.strip() == 'menos cuarto':
                h = (h - 1) if h > 1 else 12
                m = 45
            elif tipo.strip() == 'en punto' or tipo.strip() == '':
                m = 0
            else:
                return match.group(0)

            if 'mañana' in periodo:
                if h == 12:
                    h = 0
            elif 'mediodía' in periodo:
                if 1 <= h <= 3:
                    h += 12
                else:
                    return match.group(0)
            elif 'tarde' in periodo:
                if 1 <= h <= 8:
                    h += 12
                else:
                    return match.group(0)
            elif 'noche' in periodo:
                if 8 <= h <= 11:
                    h += 12
                elif h == 12:
                    h = 0
                elif 1 <= h <= 4:
                    h += 12
                else:
                    return match.group(0)
            elif 'madrugada' in periodo:
                if not (1 <= h <= 6):
                    return match.group(0)

            return f'{h:02}:{m:02}'
        return match.group(0)

    patron = re.compile(r'''
        (?P<hora_std>\d{1,2}):(?P<min_std>\d{2})                          | 
        (?P<hora_h>\d{1,2})h(?:\s*(?P<min_h>\d{1,2})m)?                  | 
        (?P<hora_nat>\d{1,2})\s*
        (?P<tipo>en\s+punto|y\s+cuarto|y\s+media|menos\s+cuarto)?\s*
        (de\s+la\s+(?P<periodo>mañana|tarde|noche|madrugada)|del\s+mediodía)?
    ''', re.IGNORECASE | re.VERBOSE)

    with open(ficText, encoding='utf-8') as f_in, open(ficNorm, 'w', encoding='utf-8') as f_out:
        for linea in f_in:
            nueva = patron.sub(reemplaza, linea)
            f_out.write(nueva)

def seleccionar_y_normalizar():
    fic_entrada = filedialog.askopenfilename(
        title="Selecciona el fichero de entrada",
        filetypes=[("Ficheros de texto", "*.txt")]
    )
    if not fic_entrada:
        return

    try:
        # Crear nombre del fichero de salida automáticamente
        base = os.path.basename(fic_entrada)
        nombre, _ = os.path.splitext(base)
        timestamp = datetime.now().strftime("%%Ym%d_%H%M%S") # Añade el tiempo exacto en el que se crea el fichero
        fic_salida = os.path.join(
            os.path.dirname(fic_entrada),
            f"{nombre}_normalizado_{timestamp}.txt"
        )

        normalizaHoras(fic_entrada, fic_salida)
        messagebox.showinfo("Hecho", f"Fichero guardado como:\n{fic_salida}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# Ejecución
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    seleccionar_y_normalizar()
