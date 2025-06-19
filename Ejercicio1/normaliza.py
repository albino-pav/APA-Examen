# normaliza.py
# Este programa lee un archivo de texto con frases que contienen horas
# y las transforma a un formato claro tipo HH:MM (por ejemplo "ocho y media" → "08:30")
# Se usan ventanas para elegir el archivo de entrada y el de salida

import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Esta función aplica varios cambios a las horas que aparecen en una línea de texto
def transformar_linea(linea):
    patrones = [
        # Formato tipo 13:45 o 7:05
        (r'\b(\d{1,2}):(\d{2})\b', lambda h, m: f'{int(h):02}:{int(m):02}' 
         if 0 <= int(h) < 24 and 0 <= int(m) < 60 else f'{h}:{m}'),

        # Ejemplo: 9h15m → 09:15
        (r'\b(\d{1,2})h(\d{1,2})m\b', lambda h, m: f'{int(h):02}:{int(m):02}'),

        # 8h → 08:00
        (r'\b(\d{1,2})h\b', lambda h: f'{int(h):02}:00'),

        # Horas que dicen "de la tarde"
        (r'\b(\d{1,2}) y media de la tarde\b', lambda h: f'{(int(h) + 12) % 24:02}:30'),
        (r'\b(\d{1,2}) y cuarto de la tarde\b', lambda h: f'{(int(h) + 12) % 24:02}:15'),
        (r'\b(\d{1,2}) menos cuarto de la tarde\b', lambda h: f'{(int(h) + 11) % 24:02}:45'),

        # Por la mañana (tipo 7h de la mañana → 07:00)
        (r'\b(\d{1,2})h de la mañana\b', lambda h: f'{int(h) % 12:02}:00'),

        # Medianoche
        (r'\b12 de la noche\b', lambda: '00:00'),

        # Casos verbales más generales (en punto, y media, menos cuarto, etc.)
        (r'\b(\d{1,2}) en punto\b', lambda h: f'{int(h) % 12 or 12:02}:00'),
        (r'\b(\d{1,2}) y media\b', lambda h: f'{int(h) % 12 or 12:02}:30'),
        (r'\b(\d{1,2}) y cuarto\b', lambda h: f'{int(h) % 12 or 12:02}:15'),
        (r'\b(\d{1,2}) menos cuarto\b', lambda h: f'{(int(h) - 1) % 12 or 12:02}:45'),
    ]

    for patron, funcion in patrones:
        def reemplazo(m):
            try:
                return funcion(*m.groups())
            except TypeError:
                return funcion()
        linea = re.sub(patron, reemplazo, linea)
    return linea

# Esta parte es la que lanza las ventanas para elegir archivos y hace todo el proceso
def normalizaHoras():
    # Ocultamos la ventana principal de Tkinter porque solo usaremos las ventanas emergentes
    Tk().withdraw()

    # Abrimos el explorador para elegir el archivo original (el que tiene las frases con horas)
    fichero_entrada = askopenfilename(
        title="Selecciona el archivo que quieres procesar",
        filetypes=[("Archivos de texto", "*.txt")]
    )

    if not fichero_entrada:
        print("No se eligió archivo de entrada.")
        return

    # Ahora pedimos dónde queremos guardar el archivo con las horas ya cambiadas
    fichero_salida = asksaveasfilename(
        title="¿Dónde quieres guardar el archivo transformado?",
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt")]
    )

    if not fichero_salida:
        print("No se eligió archivo de salida.")
        return

    # Leemos el archivo línea por línea y aplicamos las transformaciones
    with open(fichero_entrada, 'r', encoding='utf-8') as entrada, open(fichero_salida, 'w', encoding='utf-8') as salida:
        for linea in entrada:
            linea_cambiada = transformar_linea(linea)
            salida.write(linea_cambiada)

    print("Proceso terminado. Archivo guardado en:", fichero_salida)

# Esta línea hace que el programa se ejecute solo si se lanza directamente (no si se importa)
if __name__ == "__main__":
    normalizaHoras()

