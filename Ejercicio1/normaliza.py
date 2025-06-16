# Autor: Tomàs Lloret
# Fecha: 15/06/2025
# Ejercicio 1: Programa de Normalización de Expresiones Horarias

import tkinter as tk
from horas import normalizaHoras
from tkinter import filedialog #Para abrir y cerrar dialogos
from pathlib import Path # Para initialdir (quiero que empieze para todos en la misma carpeta)
# Las pestañas de filedialog tristemente no se pueden editar gráficamente porque dependen del OS :(

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    archivo = filedialog.askopenfilename(
        initialdir = str(Path.home()), # Inicia la carpeta en el home de usuario independientemented del OS
        title="Selecciona el fichero de texto a normalizar",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    root.destroy()
    return archivo

def seleccionar_salida():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    archivo_salida = filedialog.asksaveasfilename(
        initialdir = str(Path.home()), # Inicia la carpeta en el home de usuario independientemented del OS
        title="Selecciona dónde guardar el texto normalizado",
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    root.destroy()
    return archivo_salida

def main():
    archivo = seleccionar_archivo()
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        salida = seleccionar_salida()
        
        if salida:
            print(f"Archivo de salida: {salida}")
            try:
                normalizaHoras(archivo, salida)
                print("Normalización realizada correctamente.")
            except Exception as error:
                print(f"Ha ocurrido el siguiente error:\n{error}")

        else:
            print("No se creó ningún archivo.")
            
    else:
        print("No se seleccionó ningún archivo.")

if __name__ == "__main__":
    main()