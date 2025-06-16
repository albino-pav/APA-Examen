"""
mono.py - Interfaz gráfica para manipulación de ficheros WAV (APA T5)

Este programa permite:
- Convertir audio estéreo a mono (con opción de canal)
- Convertir dos ficheros mono a uno estéreo
- Codificar estéreo (suma/resta)
- Decodificar audio codificado

Usa estero.py como módulo base.

Autor: Joan Gallardo
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import simpleaudio as sa
import estereo  

def reproducir_wav(path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
    except Exception as e:
        messagebox.showerror("Error de reproducción", str(e))

class AppAPA:
    def __init__(self, root):
        self.root = root
        self.root.title("APA - Tarea T5: Manipulación de audio WAV")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.crear_pestana_estereo_a_mono()
        self.crear_pestana_mono_a_estereo()
        self.crear_pestana_codificar()
        self.crear_pestana_decodificar()

    def crear_pestana_estereo_a_mono(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estéreo a Mono")

        self.archivo_estereo = tk.StringVar()
        self.archivo_salida_mono = tk.StringVar()
        self.canal = tk.IntVar(value=2)

        ttk.Label(frame, text="Fichero estéreo:").pack()
        ttk.Entry(frame, textvariable=self.archivo_estereo, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=self.seleccionar_estereo).pack()

        ttk.Label(frame, text="Canal: 0=Izq, 1=Der, 2=Promedio, 3=Diferencia").pack()
        ttk.Spinbox(frame, from_=0, to=3, textvariable=self.canal).pack()

        ttk.Label(frame, text="Fichero mono de salida:").pack()
        ttk.Entry(frame, textvariable=self.archivo_salida_mono, width=50).pack()
        ttk.Button(frame, text="Guardar como", command=self.guardar_salida_mono).pack()

        ttk.Button(frame, text="Convertir", command=self.ejecutar_estereo_a_mono).pack(pady=5)

        ttk.Button(frame, text="Escuchar entrada", command=lambda: reproducir_wav(self.archivo_estereo.get())).pack()
        ttk.Button(frame, text="Escuchar salida", command=lambda: reproducir_wav(self.archivo_salida_mono.get())).pack()

    def crear_pestana_mono_a_estereo(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mono a Estéreo")

        self.archivo_izq = tk.StringVar()
        self.archivo_der = tk.StringVar()
        self.archivo_salida_estereo = tk.StringVar()

        ttk.Label(frame, text="Fichero mono izquierdo:").pack()
        ttk.Entry(frame, textvariable=self.archivo_izq, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.archivo_izq)).pack()

        ttk.Label(frame, text="Fichero mono derecho:").pack()
        ttk.Entry(frame, textvariable=self.archivo_der, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.archivo_der)).pack()

        ttk.Label(frame, text="Fichero estéreo de salida:").pack()
        ttk.Entry(frame, textvariable=self.archivo_salida_estereo, width=50).pack()
        ttk.Button(frame, text="Guardar como", command=lambda: self.guardar_archivo(self.archivo_salida_estereo)).pack()

        ttk.Button(frame, text="Convertir", command=self.ejecutar_mono_a_estereo).pack(pady=5)

        ttk.Button(frame, text="Escuchar izq", command=lambda: reproducir_wav(self.archivo_izq.get())).pack()
        ttk.Button(frame, text="Escuchar der", command=lambda: reproducir_wav(self.archivo_der.get())).pack()
        ttk.Button(frame, text="Escuchar salida", command=lambda: reproducir_wav(self.archivo_salida_estereo.get())).pack()

    def crear_pestana_codificar(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Codifica Estéreo")

        self.archivo_entrada_cod = tk.StringVar()
        self.archivo_salida_cod = tk.StringVar()

        ttk.Label(frame, text="Fichero estéreo:").pack()
        ttk.Entry(frame, textvariable=self.archivo_entrada_cod, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.archivo_entrada_cod)).pack()

        ttk.Label(frame, text="Fichero codificado de salida:").pack()
        ttk.Entry(frame, textvariable=self.archivo_salida_cod, width=50).pack()
        ttk.Button(frame, text="Guardar como", command=lambda: self.guardar_archivo(self.archivo_salida_cod)).pack()

        ttk.Button(frame, text="Codificar", command=self.ejecutar_codificar).pack(pady=5)

        ttk.Button(frame, text="Escuchar entrada", command=lambda: reproducir_wav(self.archivo_entrada_cod.get())).pack()
        ttk.Button(frame, text="Escuchar salida", command=lambda: reproducir_wav(self.archivo_salida_cod.get())).pack()

    def crear_pestana_decodificar(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Decodifica Estéreo")

        self.archivo_entrada_dec = tk.StringVar()
        self.archivo_salida_dec = tk.StringVar()

        ttk.Label(frame, text="Fichero codificado:").pack()
        ttk.Entry(frame, textvariable=self.archivo_entrada_dec, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.archivo_entrada_dec)).pack()

        ttk.Label(frame, text="Fichero estéreo de salida:").pack()
        ttk.Entry(frame, textvariable=self.archivo_salida_dec, width=50).pack()
        ttk.Button(frame, text="Guardar como", command=lambda: self.guardar_archivo(self.archivo_salida_dec)).pack()

        ttk.Button(frame, text="Decodificar", command=self.ejecutar_decodificar).pack(pady=5)

        ttk.Button(frame, text="Escuchar entrada", command=lambda: reproducir_wav(self.archivo_entrada_dec.get())).pack()
        ttk.Button(frame, text="Escuchar salida", command=lambda: reproducir_wav(self.archivo_salida_dec.get())).pack()

    def seleccionar_estereo(self):
        ruta = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if ruta:
            self.archivo_estereo.set(ruta)

    def guardar_salida_mono(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if ruta:
            self.archivo_salida_mono.set(ruta)

    def seleccionar_archivo(self, variable):
        ruta = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if ruta:
            variable.set(ruta)

    def guardar_archivo(self, variable):
        ruta = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if ruta:
            variable.set(ruta)

    def ejecutar_estereo_a_mono(self):
        try:
            estereo.estereo2mono(self.archivo_estereo.get(), self.archivo_salida_mono.get(), self.canal.get())
            messagebox.showinfo("Conversión realizada", "Estéreo a mono completado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_mono_a_estereo(self):
        try:
            estereo.mono2estereo(self.archivo_izq.get(), self.archivo_der.get(), self.archivo_salida_estereo.get())
            messagebox.showinfo("Conversión realizada", "Mono a estéreo completado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_codificar(self):
        try:
            estereo.codEstereo(self.archivo_entrada_cod.get(), self.archivo_salida_cod.get())
            messagebox.showinfo("Codificación realizada", "Codificación completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_decodificar(self):
        try:
            estereo.decEstereo(self.archivo_entrada_dec.get(), self.archivo_salida_dec.get())
            messagebox.showinfo("Decodificación realizada", "Decodificación completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppAPA(root)
    root.mainloop()
