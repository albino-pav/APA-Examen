import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sounddevice as sd
import numpy as np
from scipy.io import wavfile

from estereo import estereo2mono, mono2estereo, codEstereo, decEstereo

class Libreta:
    def __init__(self, root):
        root.title("Procesador de Señales Estéreo")
        self.notebook = ttk.Notebook(root)

        self.frames = {}
        self.paths = {}
        self.fs_cache = {}
        self.data_cache = {}

        tabs = [
            ("Estéreo → Mono", self.init_est2mono),
            ("Mono → Estéreo", self.init_mono2est),
            ("Codifica Estéreo", self.init_codifica),
            ("Descodifica Estéreo", self.init_descodifica)
        ]

        for name, init_func in tabs:
            frame = ttk.Frame(self.notebook)
            self.frames[name] = frame
            self.notebook.add(frame, text=name)
            init_func(frame)

        self.notebook.pack(expand=True, fill="both")

    def reproducir(self, path):
        if path:
            try:
                if path not in self.data_cache:
                    fs, data = wavfile.read(path)
                    self.fs_cache[path] = fs
                    self.data_cache[path] = data
                else:
                    fs = self.fs_cache[path]
                    data = self.data_cache[path]
                sd.play(data, fs)
                sd.wait()
            except Exception as e:
                messagebox.showerror("Error de reproducción", str(e))

    def init_est2mono(self, frame):
        canal = tk.IntVar(value=2)
        paths = {}

        def cargar():
            paths['in'] = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])

        def guardar():
            paths['out'] = filedialog.asksaveasfilename(defaultextension=".wav")

        def ejecutar():
            if 'in' in paths and 'out' in paths:
                estereo2mono(paths['in'], paths['out'], canal.get())
                messagebox.showinfo("OK", "Conversión realizada")

        ttk.Button(frame, text="Seleccionar Estéreo", command=cargar).pack(pady=2)
        ttk.Button(frame, text="Guardar Mono Como...", command=guardar).pack(pady=2)

        for i, txt in enumerate(["Izquierdo", "Derecho", "Media", "Diferencia"]):
            ttk.Radiobutton(frame, text=txt, variable=canal, value=i).pack(anchor="w")

        ttk.Button(frame, text="Ejecutar Conversión", command=ejecutar).pack(pady=2)
        ttk.Button(frame, text="Escuchar Entrada", command=lambda: self.reproducir(paths.get('in'))).pack()
        ttk.Button(frame, text="Escuchar Salida", command=lambda: self.reproducir(paths.get('out'))).pack()

    def init_mono2est(self, frame):
        paths = {}

        def cargar_L():
            paths['L'] = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])

        def cargar_R():
            paths['R'] = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])

        def guardar():
            paths['out'] = filedialog.asksaveasfilename(defaultextension=".wav")

        def ejecutar():
            if all(k in paths for k in ['L', 'R', 'out']):
                mono2estereo(paths['L'], paths['R'], paths['out'])
                messagebox.showinfo("OK", "Estéreo generado")

        ttk.Button(frame, text="Seleccionar Canal Izquierdo", command=cargar_L).pack(pady=2)
        ttk.Button(frame, text="Seleccionar Canal Derecho", command=cargar_R).pack(pady=2)
        ttk.Button(frame, text="Guardar Estéreo Como...", command=guardar).pack(pady=2)
        ttk.Button(frame, text="Ejecutar", command=ejecutar).pack(pady=2)
        ttk.Button(frame, text="Escuchar L", command=lambda: self.reproducir(paths.get('L'))).pack()
        ttk.Button(frame, text="Escuchar R", command=lambda: self.reproducir(paths.get('R'))).pack()
        ttk.Button(frame, text="Escuchar Estéreo", command=lambda: self.reproducir(paths.get('out'))).pack()

    def init_codifica(self, frame):
        paths = {}

        def cargar():
            paths['in'] = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])

        def guardar():
            paths['out'] = filedialog.asksaveasfilename(defaultextension=".wav")

        def ejecutar():
            if 'in' in paths and 'out' in paths:
                codEstereo(paths['in'], paths['out'])
                messagebox.showinfo("OK", "Codificación realizada")

        ttk.Button(frame, text="Seleccionar Estéreo", command=cargar).pack(pady=2)
        ttk.Button(frame, text="Guardar Codificado Como...", command=guardar).pack(pady=2)
        ttk.Button(frame, text="Ejecutar", command=ejecutar).pack(pady=2)
        ttk.Button(frame, text="Escuchar Entrada", command=lambda: self.reproducir(paths.get('in'))).pack()
        ttk.Button(frame, text="Escuchar Salida", command=lambda: self.reproducir(paths.get('out'))).pack()

    def init_descodifica(self, frame):
        paths = {}

        def cargar():
            paths['in'] = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])

        def guardar():
            paths['out'] = filedialog.asksaveasfilename(defaultextension=".wav")

        def ejecutar():
            if 'in' in paths and 'out' in paths:
                decEstereo(paths['in'], paths['out'])
                messagebox.showinfo("OK", "Decodificación realizada")

        ttk.Button(frame, text="Seleccionar Codificado", command=cargar).pack(pady=2)
        ttk.Button(frame, text="Guardar Estéreo Como...", command=guardar).pack(pady=2)
        ttk.Button(frame, text="Ejecutar", command=ejecutar).pack(pady=2)
        ttk.Button(frame, text="Escuchar Entrada", command=lambda: self.reproducir(paths.get('in'))).pack()
        ttk.Button(frame, text="Escuchar Salida", command=lambda: self.reproducir(paths.get('out'))).pack()

if __name__ == '__main__':
    root = tk.Tk()
    app = Libreta(root)
    root.mainloop()
