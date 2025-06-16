# Autor: Tomàs Lloret
# Fecha: 16/06/2025
# Ejercicio 2: Programa de Manejo de Señales Estéreo

import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    archivo = filedialog.askopenfilename(
        initialdir = str(Path.home()), # Inicia la carpeta en el home de usuario independientemented del OS
        title="Selecciona el fichero de audio",
        filetypes=[("Archivos de àudio", "*.wav")]
    )
    root.destroy()
    return archivo

def seleccionar_salida():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    archivo_salida = filedialog.asksaveasfilename(
        initialdir = str(Path.home()), # Inicia la carpeta en el home de usuario independientemented del OS
        title="Selecciona dónde guardar el fichero de audio",
        defaultextension=".wav",
        filetypes=[("Archivos de audio", "*.wav")]
    )
    root.destroy()
    return archivo_salida

def main():
    root = tk.Tk()
    root.configure(bg="black")
    root.geometry("1080x1920")
    root.title("Ejercicio 2: Programa de Manejo de Señales")

    titulo = tk.Label(root, text="Test ejercicio 2", font=("Calibri", 20, "bold"), fg="blue")
    titulo.pack()

    subtitulo = tk.Label(root, text="Test subtitulo", font=("Calibri", 15, "bold"), fg="cyan")
    subtitulo.pack()

    root.mainloop()
    

if __name__ == "__main__":
    main()