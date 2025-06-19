# Ejercicio 1: Programa de Normalización de Expresiones Horarias (20%)
# ----------------------------------------------------------------------

# - Construya el programa `normaliza.py`que permita leer un fichero de texto, normalice
#   las expresiones horarias en él contenidas según las instrucciones de la tarea APA-T6
#   y escriba el resultado en otro fichero de texto.

# - El fichero de entrada y el nombre del fichero de salida tendrán la extensión `.txt` y
#   se escogerán usando las funciones gráficas de `TkInter.filedialog`.

# - No se evaluará la calidad de la normalización (ese aspecto se evalúa en APA-T6).

import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def normalizaHoras(ficText, ficNorm):
    """
    Lee un fichero de texto, analiza las expresiones horarias y escribe un nuevo fichero
    con las expresiones normalizadas en formato HH:MM.

    Las expresiones incorrectas se dejan tal cual.
    """
    patrones = [
        (re.compile(r'(\d{1,2}):(\d{1,2})'), lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'),
        (re.compile(r'(\d{1,2})h(\d{1,2})m'), lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'),
        (re.compile(r'(\d{1,2})h'), lambda m: f'{int(m.group(1)):02}:00'),
        (re.compile(r'(\d{1,2}) y media de la tarde'), lambda m: f'{int(m.group(1)) + 12}:30' if 1 <= int(m.group(1)) <= 11 else m.group(0)),
        (re.compile(r'(\d{1,2}) y cuarto de la tarde'), lambda m: f'{int(m.group(1)) + 12}:15' if 1 <= int(m.group(1)) <= 11 else m.group(0)),
        (re.compile(r'(\d{1,2}) menos cuarto de la tarde'), lambda m: f'{int(m.group(1)) + 11}:45' if 1 <= int(m.group(1)) <= 12 else m.group(0)),
        (re.compile(r'(\d{1,2})h de la mañana'), lambda m: f'{int(m.group(1)):02}:00' if 1 <= int(m.group(1)) <= 12 else m.group(0)),
        (re.compile(r'12 de la noche'), lambda m: '00:00'),
        (re.compile(r'(\d{1,2}) de la tarde'), lambda m: f'{int(m.group(1)) + 12}:00' if 1 <= int(m.group(1)) <= 11 else f'{int(m.group(1)):02}:00'),
    ]

    with open(ficText, 'r', encoding='utf-8') as entrada, open(ficNorm, 'w', encoding='utf-8') as salida:
        for linea in entrada:
            original = linea
            for patron, reemplazo in patrones:
                linea = patron.sub(reemplazo, linea)
            salida.write(linea)

def main():
    Tk().withdraw()

    ficText = askopenfilename(title="Selecciona el fichero de entrada", filetypes=[("Ficheros de texto", "*.txt")])
    if not ficText:
        print("No se seleccionó ningún fichero de entrada.")
        return
    ficNorm = asksaveasfilename(title="Selecciona el fichero de salida", filetypes=[("Ficheros de texto", "*.txt")], defaultextension=".txt")
    if not ficNorm:
        print("No se seleccionó ningún fichero de salida.")
        return

    normalizaHoras(ficText, ficNorm)
    print(f"Normalización completada. Resultado guardado en: {ficNorm}")

if __name__ == "__main__":
    main()
