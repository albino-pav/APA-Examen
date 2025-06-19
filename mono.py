# mono.py
# MARK BONETE VENTURA

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sounddevice as sd
import soundfile as sf
import os
from estereo import estereo2mono, mono2estereo, codEstereo, decEstereo

class MonoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Audio Estéreo/Mono")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')

        self.fichero_entrada = None
        self.fichero_salida = None

        self._crear_pestana_estereo2mono()
        self._crear_pestana_mono2estereo()
        self._crear_pestana_codifica()
        self._crear_pestana_descodifica()

    def _crear_pestana_estereo2mono(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estéreo a Mono")

        self.entrada_1 = tk.StringVar()
        self.canal = tk.IntVar(value=2)

        ttk.Label(frame, text="Fichero Estéreo:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_1, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self._abrir_fichero_estereo).pack()

        ttk.Label(frame, text="Canal: 0=Izq, 1=Der, 2=Semisuma, 3=Semidif").pack()
        ttk.Entry(frame, textvariable=self.canal).pack()

        ttk.Button(frame, text="Reproducir Estéreo", command=lambda: self._reproducir(self.entrada_1.get())).pack()
        ttk.Button(frame, text="Convertir y Guardar", command=self._convertir_estereo_a_mono).pack()

    def _crear_pestana_mono2estereo(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mono a Estéreo")

        self.entrada_izq = tk.StringVar()
        self.entrada_der = tk.StringVar()
        self.salida_estereo = tk.StringVar()

        ttk.Label(frame, text="Fichero Izquierdo:").pack()
        ttk.Entry(frame, textvariable=self.entrada_izq, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.entrada_izq)).pack()

        ttk.Label(frame, text="Fichero Derecho:").pack()
        ttk.Entry(frame, textvariable=self.entrada_der, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.entrada_der)).pack()

        ttk.Label(frame, text="Guardar como:").pack()
        ttk.Entry(frame, textvariable=self.salida_estereo, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._guardar_fichero(self.salida_estereo)).pack()

        ttk.Button(frame, text="Convertir a Estéreo", command=self._convertir_mono_a_estereo).pack()

    def _crear_pestana_codifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Codifica Estéreo")

        self.fic_cod_in = tk.StringVar()
        self.fic_cod_out = tk.StringVar()

        ttk.Label(frame, text="Fichero Estéreo (16b):").pack()
        ttk.Entry(frame, textvariable=self.fic_cod_in, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.fic_cod_in)).pack()

        ttk.Label(frame, text="Guardar codificado (32b):").pack()
        ttk.Entry(frame, textvariable=self.fic_cod_out, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._guardar_fichero(self.fic_cod_out)).pack()

        ttk.Button(frame, text="Codificar", command=self._codificar_estereo).pack()

    def _crear_pestana_descodifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Descodifica Estéreo")

        self.fic_dec_in = tk.StringVar()
        self.fic_dec_out = tk.StringVar()

        ttk.Label(frame, text="Fichero Codificado (32b):").pack()
        ttk.Entry(frame, textvariable=self.fic_dec_in, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._seleccionar_fichero(self.fic_dec_in)).pack()

        ttk.Label(frame, text="Guardar como Estéreo (16b):").pack()
        ttk.Entry(frame, textvariable=self.fic_dec_out, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=lambda: self._guardar_fichero(self.fic_dec_out)).pack()

        ttk.Button(frame, text="Descodificar", command=self._descodificar_estereo).pack()

    # Funciones auxiliares

    def _abrir_fichero_estereo(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            self.entrada_1.set(path)

    def _seleccionar_fichero(self, var):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            var.set(path)

    def _guardar_fichero(self, var):
        path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if path:
            var.set(path)

    def _reproducir(self, filename):
        try:
            data, fs = sf.read(filename)
            sd.play(data, fs)
        except Exception as e:
            messagebox.showerror("Error al reproducir", str(e))

    def _convertir_estereo_a_mono(self):
        entrada = self.entrada_1.get()
        canal = self.canal.get()
        salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if not entrada or not salida:
            return
        try:
            estereo2mono(entrada, salida, canal)
            messagebox.showinfo("Conversión completada", f"Fichero guardado: {salida}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _convertir_mono_a_estereo(self):
        ficIzq = self.entrada_izq.get()
        ficDer = self.entrada_der.get()
        ficEste = self.salida_estereo.get()
        try:
            mono2estereo(ficIzq, ficDer, ficEste)
            messagebox.showinfo("Conversión completada", f"Estéreo guardado en: {ficEste}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _codificar_estereo(self):
        fic_in = self.fic_cod_in.get()
        fic_out = self.fic_cod_out.get()
        try:
            codEstereo(fic_in, fic_out)
            messagebox.showinfo("Codificación completada", f"Fichero guardado: {fic_out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _descodificar_estereo(self):
        fic_in = self.fic_dec_in.get()
        fic_out = self.fic_dec_out.get()
        try:
            decEstereo(fic_in, fic_out)
            messagebox.showinfo("Descodificación completada", f"Fichero guardado: {fic_out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MonoGUI(root)
    root.mainloop()
