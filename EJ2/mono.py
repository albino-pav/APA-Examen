import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame # libreria para reproducir archivos, ers necesaria instalarla en ipython
pygame.mixer.init()
import estereo

def seleccionar_archivo(entry_widget):
    archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if archivo:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, archivo)

def seleccionar_guardado(entry_widget):
    archivo = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if archivo:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, archivo)

def reproducir(archivo):
    try:
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.play()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo reproducir:\n{e}")

def detener_audio():
    pygame.mixer.music.stop()

def crear_pestana_estereo2mono(tab):
    tk.Label(tab, text="Archivo estéreo:").grid(row=0, column=0)
    entrada = tk.Entry(tab, width=50)
    entrada.grid(row=0, column=1)
    tk.Button(tab, text="Seleccionar", command=lambda: seleccionar_archivo(entrada)).grid(row=0, column=2)

    tk.Label(tab, text="Archivo mono de salida:").grid(row=1, column=0)
    salida = tk.Entry(tab, width=50)
    salida.grid(row=1, column=1)
    tk.Button(tab, text="Guardar como", command=lambda: seleccionar_guardado(salida)).grid(row=1, column=2)

    tk.Label(tab, text="Canal:").grid(row=2, column=0)
    canal = ttk.Combobox(tab, values=["Izquierdo (0)", "Derecho (1)", "Semisuma (2)", "Semidiferencia (3)"], state="readonly")
    canal.current(2)
    canal.grid(row=2, column=1)

    tk.Button(tab, text="▶ Reproducir entrada", command=lambda: reproducir(entrada.get())).grid(row=4, column=0, pady=5)
    tk.Button(tab, text="▶ Reproducir salida", command=lambda: reproducir(salida.get())).grid(row=4, column=2, pady=5)
    tk.Button(tab, text="Detener audio", command=detener_audio).grid(row=4, column=1)

    def ejecutar():
        try:
            c = canal.current()
            estereo.estereo2mono(entrada.get(), salida.get(), canal=c)
            messagebox.showinfo("Éxito", "Conversión completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(tab, text="Convertir", command=ejecutar).grid(row=3, column=1, pady=10)

def crear_pestana_mono2estereo(tab):
    tk.Label(tab, text="Canal izquierdo:").grid(row=0, column=0)
    izq = tk.Entry(tab, width=50)
    izq.grid(row=0, column=1)
    tk.Button(tab, text="Seleccionar", command=lambda: seleccionar_archivo(izq)).grid(row=0, column=2)

    tk.Label(tab, text="Canal derecho:").grid(row=1, column=0)
    der = tk.Entry(tab, width=50)
    der.grid(row=1, column=1)
    tk.Button(tab, text="Seleccionar", command=lambda: seleccionar_archivo(der)).grid(row=1, column=2)

    tk.Label(tab, text="Archivo estéreo de salida:").grid(row=2, column=0)
    salida = tk.Entry(tab, width=50)
    salida.grid(row=2, column=1)
    tk.Button(tab, text="Guardar como", command=lambda: seleccionar_guardado(salida)).grid(row=2, column=2)

    tk.Button(tab, text="▶ Reproducir entrada", command=lambda: reproducir(entrada.get())).grid(row=4, column=0, pady=5)
    tk.Button(tab, text="▶ Reproducir salida", command=lambda: reproducir(salida.get())).grid(row=4, column=2, pady=5)
    tk.Button(tab, text="Detener audio", command=detener_audio).grid(row=4, column=1)

    def ejecutar():
        try:
            estereo.mono2estereo(izq.get(), der.get(), salida.get())
            messagebox.showinfo("Éxito", "Conversión completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(tab, text="Unir canales", command=ejecutar).grid(row=3, column=1, pady=10)

def crear_pestana_codifica(tab):
    tk.Label(tab, text="Archivo estéreo:").grid(row=0, column=0)
    entrada = tk.Entry(tab, width=50)
    entrada.grid(row=0, column=1)
    tk.Button(tab, text="Seleccionar", command=lambda: seleccionar_archivo(entrada)).grid(row=0, column=2)

    tk.Label(tab, text="Archivo codificado (32 bits):").grid(row=1, column=0)
    salida = tk.Entry(tab, width=50)
    salida.grid(row=1, column=1)
    tk.Button(tab, text="Guardar como", command=lambda: seleccionar_guardado(salida)).grid(row=1, column=2)

    tk.Button(tab, text="▶ Reproducir entrada", command=lambda: reproducir(entrada.get())).grid(row=4, column=0, pady=5)
    tk.Button(tab, text="▶ Reproducir salida", command=lambda: reproducir(salida.get())).grid(row=4, column=2, pady=5)
    tk.Button(tab, text="Detener audio", command=detener_audio).grid(row=4, column=1)

    def ejecutar():
        try:
            estereo.codEstereo(entrada.get(), salida.get())
            messagebox.showinfo("Éxito", "Codificación completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(tab, text="Codificar", command=ejecutar).grid(row=2, column=1, pady=10)

def crear_pestana_descodifica(tab):
    tk.Label(tab, text="Archivo codificado (32 bits):").grid(row=0, column=0)
    entrada = tk.Entry(tab, width=50)
    entrada.grid(row=0, column=1)
    tk.Button(tab, text="Seleccionar", command=lambda: seleccionar_archivo(entrada)).grid(row=0, column=2)

    tk.Label(tab, text="Archivo estéreo de salida:").grid(row=1, column=0)
    salida = tk.Entry(tab, width=50)
    salida.grid(row=1, column=1)
    tk.Button(tab, text="Guardar como", command=lambda: seleccionar_guardado(salida)).grid(row=1, column=2)

    tk.Button(tab, text="▶ Reproducir entrada", command=lambda: reproducir(entrada.get())).grid(row=4, column=0, pady=5)
    tk.Button(tab, text="▶ Reproducir salida", command=lambda: reproducir(salida.get())).grid(row=4, column=2, pady=5)
    tk.Button(tab, text="Detener audio", command=detener_audio).grid(row=4, column=1)

    def ejecutar():
        try:
            estereo.decEstereo(entrada.get(), salida.get())
            messagebox.showinfo("Éxito", "Decodificación completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(tab, text="Decodificar", command=ejecutar).grid(row=2, column=1, pady=10)

def main():
    root = tk.Tk()
    root.title("Conversor de Audio Estéreo/Mono")
    root.geometry("800x320")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill="both")

    tabs = []
    for nombre in ["Estéreo a Mono", "Mono a Estéreo", "Codifica Estéreo", "Descodifica Estéreo"]:
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=nombre)
        tabs.append(tab)

    crear_pestana_estereo2mono(tabs[0])
    crear_pestana_mono2estereo(tabs[1])
    crear_pestana_codifica(tabs[2])
    crear_pestana_descodifica(tabs[3])

    root.mainloop()

if __name__ == "__main__":
    main()