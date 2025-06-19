# normaliza.py
# MARK BONETE VENTURA

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
