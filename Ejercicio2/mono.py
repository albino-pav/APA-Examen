import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pygame
import estereo

# Inicializamos pygame.mixer para reproducir sonidos
pygame.mixer.init()

def reproducir_wav(ruta):
    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.play()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo reproducir el archivo: {e}")

def seleccionar_archivo():
    return filedialog.askopenfilename(filetypes=[("Archivos WAV", "*.wav")])

def guardar_como():
    return filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAV", "*.wav")])

ventana = tk.Tk()
ventana.title("APA - Conversor Estéreo / Mono")
ventana.geometry("600x400")

notebook = ttk.Notebook(ventana)
notebook.pack(expand=True, fill="both")

# Estéreo a Mono
frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Estéreo a Mono")

entrada1 = tk.StringVar()
tk.Label(frame1, text="Archivo estéreo:").pack()
tk.Entry(frame1, textvariable=entrada1, width=50).pack()
tk.Button(frame1, text="Seleccionar", command=lambda: entrada1.set(seleccionar_archivo())).pack()

canal_var = tk.IntVar(value=2)
tk.Label(frame1, text="Canal a usar:").pack()
tk.Radiobutton(frame1, text="Izquierdo", variable=canal_var, value=0).pack()
tk.Radiobutton(frame1, text="Derecho", variable=canal_var, value=1).pack()
tk.Radiobutton(frame1, text="Media (L+R)/2", variable=canal_var, value=2).pack()
tk.Radiobutton(frame1, text="Izq - Der", variable=canal_var, value=3).pack()

def convertir_estereo_a_mono():
    fic_entrada = entrada1.get()
    if not fic_entrada:
        return
    fic_salida = guardar_como()
    if fic_salida:
        estereo.estereo2mono(fic_entrada, fic_salida, canal=canal_var.get())
        messagebox.showinfo("Hecho", f"Guardado en {fic_salida}")

tk.Button(frame1, text="Convertir", command=convertir_estereo_a_mono).pack(pady=5)
tk.Button(frame1, text="Escuchar", command=lambda: reproducir_wav(entrada1.get())).pack()

# Mono a Estéreo
frame2 = ttk.Frame(notebook)
notebook.add(frame2, text="Mono a Estéreo")

entradaL = tk.StringVar()
entradaR = tk.StringVar()
tk.Label(frame2, text="Canal Izquierdo:").pack()
tk.Entry(frame2, textvariable=entradaL, width=50).pack()
tk.Button(frame2, text="Seleccionar", command=lambda: entradaL.set(seleccionar_archivo())).pack()
tk.Label(frame2, text="Canal Derecho:").pack()
tk.Entry(frame2, textvariable=entradaR, width=50).pack()
tk.Button(frame2, text="Seleccionar", command=lambda: entradaR.set(seleccionar_archivo())).pack()

def convertir_mono_a_estereo():
    fic_izq = entradaL.get()
    fic_der = entradaR.get()
    if not fic_izq or not fic_der:
        return
    fic_salida = guardar_como()
    if fic_salida:
        estereo.mono2estereo(fic_izq, fic_der, fic_salida)
        messagebox.showinfo("Hecho", f"Guardado en {fic_salida}")

tk.Button(frame2, text="Combinar", command=convertir_mono_a_estereo).pack(pady=5)

# Codifica estéreo
frame3 = ttk.Frame(notebook)
notebook.add(frame3, text="Codifica Estéreo")

entrada3 = tk.StringVar()
tk.Label(frame3, text="Archivo estéreo a codificar:").pack()
tk.Entry(frame3, textvariable=entrada3, width=50).pack()
tk.Button(frame3, text="Seleccionar", command=lambda: entrada3.set(seleccionar_archivo())).pack()

def codificar():
    entrada = entrada3.get()
    if not entrada:
        return
    salida = guardar_como()
    if salida:
        estereo.codEstereo(entrada, salida)
        messagebox.showinfo("Codificado", f"Guardado en: {salida}")

tk.Button(frame3, text="Codificar", command=codificar).pack(pady=5)

# Decodifica estéreo
frame4 = ttk.Frame(notebook)
notebook.add(frame4, text="Decodifica Estéreo")

entrada4 = tk.StringVar()
tk.Label(frame4, text="Archivo codificado:").pack()
tk.Entry(frame4, textvariable=entrada4, width=50).pack()
tk.Button(frame4, text="Seleccionar", command=lambda: entrada4.set(seleccionar_archivo())).pack()

def decodificar():
    entrada = entrada4.get()
    if not entrada:
        return
    salida = guardar_como()
    if salida:
        estereo.decEstereo(entrada, salida)
        messagebox.showinfo("Decodificado", f"Guardado en: {salida}")

tk.Button(frame4, text="Decodificar", command=decodificar).pack(pady=5)

ventana.mainloop()
