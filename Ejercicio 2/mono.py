import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import estereo
import os

class AplicacionAudio:
    def __init__(self, root):
        root.title("APA - Examen Final")
        root.geometry("600x400")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.pestana_estereo2mono()
        self.pestana_mono2estereo()
        self.pestana_codifica()
        self.pestana_descodifica()

    def pestana_estereo2mono(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estéreo a Mono")

        self.entrada_estereo = tk.StringVar()
        self.salida_mono = tk.StringVar()
        self.canal = tk.IntVar(value=2)

        ttk.Label(frame, text="Archivo estéreo de entrada:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_estereo, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self.seleccionar_estereo).pack(pady=5)

        ttk.Label(frame, text="Canal:").pack(pady=5)
        for texto, val in [("Izquierdo (0)", 0), ("Derecho (1)", 1), ("Semisuma (2)", 2), ("Semidiferencia (3)", 3)]:
            ttk.Radiobutton(frame, text=texto, variable=self.canal, value=val).pack(anchor='w')

        ttk.Button(frame, text="Escuchar entrada", command=lambda: self.reproducir(self.entrada_estereo.get())).pack(pady=2)
        ttk.Button(frame, text="Escuchar salida", command=lambda: self.reproducir(self.salida_mono.get())).pack(pady=2)
        ttk.Button(frame, text="Guardar como...", command=self.guardar_mono).pack(pady=10)

    def pestana_mono2estereo(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mono a Estéreo")

        self.entrada_izq = tk.StringVar()
        self.entrada_der = tk.StringVar()
        self.salida_estereo = tk.StringVar()

        ttk.Label(frame, text="Canal izquierdo:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_izq, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self.seleccionar_izq).pack(pady=2)

        ttk.Label(frame, text="Canal derecho:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_der, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self.seleccionar_der).pack(pady=2)

        ttk.Button(frame, text="Escuchar izquierdo", command=lambda: self.reproducir(self.entrada_izq.get())).pack(pady=2)
        ttk.Button(frame, text="Escuchar derecho", command=lambda: self.reproducir(self.entrada_der.get())).pack(pady=2)
        ttk.Button(frame, text="Guardar como estéreo...", command=self.guardar_estereo).pack(pady=10)
        ttk.Button(frame, text="Escuchar salida estéreo", command=lambda: self.reproducir(self.salida_estereo.get())).pack(pady=2)

    def pestana_codifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Codifica Estéreo")

        self.entrada_cod = tk.StringVar()
        self.salida_cod = tk.StringVar()

        ttk.Label(frame, text="Archivo estéreo de entrada:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_cod, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self.seleccionar_cod_input).pack(pady=5)
        
        ttk.Button(frame, text="Escuchar entrada", command=lambda: self.reproducir(self.entrada_cod.get())).pack(pady=2)
        ttk.Button(frame, text="Guardar codificado como...", command=self.guardar_codificado).pack(pady=10)
        ttk.Button(frame, text="Escuchar codificado", command=lambda: self.reproducir(self.salida_cod.get())).pack(pady=2)

    def pestana_descodifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Descodifica Estéreo")

        self.entrada_dec = tk.StringVar()
        self.salida_dec = tk.StringVar()

        ttk.Label(frame, text="Archivo codificado de entrada:").pack(pady=5)
        ttk.Entry(frame, textvariable=self.entrada_dec, width=60).pack()
        ttk.Button(frame, text="Seleccionar", command=self.seleccionar_codificado).pack(pady=5)

        ttk.Button(frame, text="Escuchar entrada codificada", command=lambda: self.reproducir(self.entrada_dec.get())).pack(pady=2)
        ttk.Button(frame, text="Guardar como estéreo...", command=self.guardar_descodificado).pack(pady=10)
        ttk.Button(frame, text="Escuchar salida estéreo", command=lambda: self.reproducir(self.salida_dec.get())).pack(pady=2)

    def seleccionar_estereo(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_estereo.set(archivo)

    def guardar_mono(self):
        archivo_salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo_salida:
            estereo.estereo2mono(self.entrada_estereo.get(), archivo_salida, self.canal.get())
            self.salida_mono.set(archivo_salida)

    def seleccionar_izq(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_izq.set(archivo)

    def seleccionar_der(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_der.set(archivo)

    def guardar_estereo(self):
        archivo_salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo_salida:
            estereo.mono2estereo(self.entrada_izq.get(), self.entrada_der.get(), archivo_salida)
            self.salida_estereo.set(archivo_salida)

    def seleccionar_cod_input(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_cod.set(archivo)

    def guardar_codificado(self):
        archivo_salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo_salida:
            estereo.codEstereo(self.entrada_cod.get(), archivo_salida)
            self.salida_cod.set(archivo_salida)

    def seleccionar_codificado(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_dec.set(archivo)

    def guardar_descodificado(self):
        archivo_salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo_salida:
            estereo.decEstereo(self.entrada_dec.get(), archivo_salida)
            self.salida_dec.set(archivo_salida)

    def reproducir(self, archivo):
        if archivo:
            os.system(f'afplay "{archivo}"')  # Para mi mac

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = AplicacionAudio(root)
    root.mainloop()