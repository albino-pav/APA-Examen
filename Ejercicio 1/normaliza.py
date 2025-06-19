import tkinter as tk
from tkinter import filedialog
import re

def convertir_24h(hora, minuto):
    h = int(hora)
    m = int(minuto)
    if 0 <= h <= 23 and 0 <= m <= 59:
        return f"{h:02d}:{m:02d}"
    return f"{hora}h{minuto}m"  # Incorrecta, se deja igual

def convertir_pm(hora, minuto):
    h = int(hora)
    m = int(minuto)
    if 1 <= h <= 11:
        h += 12
    if 0 <= h <= 23 and 0 <= m <= 59:
        return f"{h:02d}:{m:02d}"
    return f"{hora} y media de la tarde"  # Incorrecta, se deja igual

def convertir_am(hora, minuto):
    h = int(hora)
    m = int(minuto)
    if 0 <= h <= 11 and 0 <= m <= 59:
        return f"{h:02d}:{m:02d}"
    return f"{hora}h de la mañana"  # Incorrecta, se deja igual

def convertir_menos_cuarto(hora):
    try:
        h = int(hora) - 1
        if h < 0:
            h = 23
        return f"{h:02d}:45"
    except:
        return f"{hora} menos cuarto"  # Incorrecta, se deja igual

def normalizaHoras(ficEntrada, ficSalida):
    with open(ficEntrada, 'r', encoding='utf-8') as fIn:
        lineas = fIn.readlines()

    lineas_normalizadas = []

    for linea in lineas:
        original = linea

        # 18h45m → 18:45
        linea = re.sub(r'\b(\d{1,2})h(\d{1,2})m\b', lambda m: convertir_24h(m.group(1), m.group(2)), linea)

        # 10h → 10:00
        linea = re.sub(r'\b(\d{1,2})h\b', lambda m: convertir_24h(m.group(1), '00'), linea)

        # 4 y media de la tarde → 16:30
        linea = re.sub(r'\b(\d{1,2}) y media de la tarde\b', lambda m: convertir_pm(m.group(1), '30'), linea)

        # 7h de la mañana → 07:00
        linea = re.sub(r'\b(\d{1,2})h de la mañana\b', lambda m: convertir_am(m.group(1), '00'), linea)

        # 5 menos cuarto → 04:45
        linea = re.sub(r'\b(\d{1,2}) menos cuarto\b', lambda m: convertir_menos_cuarto(m.group(1)), linea)

        # 12 de la noche → 00:00
        linea = re.sub(r'\b12 de la noche\b', '00:00', linea)

        lineas_normalizadas.append(linea)

    with open(ficSalida, 'w', encoding='utf-8') as fOut:
        fOut.writelines(lineas_normalizadas)

def main():
    root = tk.Tk()
    root.withdraw()

    ficText = filedialog.askopenfilename(title="Selecciona el fichero de entrada", filetypes=[("Text files", "*.txt")])
    if not ficText:
        print("No se seleccionó archivo de entrada.")
        return

    ficNorm = filedialog.asksaveasfilename(title="Selecciona el fichero de salida", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not ficNorm:
        print("No se seleccionó archivo de salida.")
        return

    normalizaHoras(ficText, ficNorm)
    print("Archivo normalizado guardado en:", ficNorm)

if __name__ == "__main__":
    main()