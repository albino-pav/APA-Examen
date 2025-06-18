''' 
        Examen Final APA 

        Autores:
        Sebastián Pérez Capitano
        Àlex Segura Medina 

        Ejercicio 2: Programa de Manejo de Señales Estéreo (35%)

'''


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import wave
import struct

# Utilizamos las funciones extraídas de la tarea APA-T5 para manejar archivos de audio estéreo y mono.
def estereo2mono(ficEste, ficMono, canal):
    with wave.open(ficEste, 'rb') as w:
        if w.getnchannels() != 2 or w.getsampwidth() != 2:
            raise ValueError("El archivo no es estéreo o no es PCM 16-bit")
        params = w.getparams()
        frames = w.readframes(params.nframes)
        datos = struct.unpack('<' + 'h' * params.nframes * 2, frames)

    if canal == 0:  # izquierdo
        nuevo = datos[::2]
    elif canal == 1:  # derecho
        nuevo = datos[1::2]
    elif canal == 2:  # semisuma
        nuevo = [(datos[i] + datos[i + 1]) // 2 for i in range(0, len(datos), 2)]
    elif canal == 3:  # semidiferencia
        nuevo = [(datos[i] - datos[i + 1]) // 2 for i in range(0, len(datos), 2)]
    else:
        raise ValueError("Canal no válido")

    with wave.open(ficMono, 'wb') as w:
        w.setparams((1, 2, params.framerate, 0, 'NONE', 'not compressed'))
        w.writeframes(struct.pack('<' + 'h' * len(nuevo), *nuevo))


def mono2estereo(ficIzq, ficDer, ficEste):
    with wave.open(ficIzq, 'rb') as wi, wave.open(ficDer, 'rb') as wd:
        if wi.getnchannels() != 1 or wi.getsampwidth() != 2 or wd.getnchannels() != 1 or wd.getsampwidth() != 2:
            raise ValueError("Ambos archivos deben ser mono PCM 16-bit")
        if wi.getframerate() != wd.getframerate():
            raise ValueError("Las frecuencias de muestreo no coinciden")
        frames_i = struct.unpack('<' + 'h' * wi.getnframes(), wi.readframes(wi.getnframes()))
        frames_d = struct.unpack('<' + 'h' * wd.getnframes(), wd.readframes(wd.getnframes()))

    minimo = min(len(frames_i), len(frames_d))
    entrelazado = [val for pair in zip(frames_i[:minimo], frames_d[:minimo]) for val in pair]

    with wave.open(ficEste, 'wb') as w:
        w.setparams((2, 2, wi.getframerate(), 0, 'NONE', 'not compressed'))
        w.writeframes(struct.pack('<' + 'h' * len(entrelazado), *entrelazado))


def codEstereo(ficEste, ficCod):
    with wave.open(ficEste, 'rb') as w:
        if w.getnchannels() != 2 or w.getsampwidth() != 2:
            raise ValueError("Debe ser un archivo estéreo PCM 16-bit")
        params = w.getparams()
        datos = struct.unpack('<' + 'h' * params.nframes * 2, w.readframes(params.nframes))

    semisuma = [(datos[i] + datos[i + 1]) for i in range(0, len(datos), 2)]
    semidif = [(datos[i] - datos[i + 1]) for i in range(0, len(datos), 2)]
    codificado = [val for par in zip(semisuma, semidif) for val in par]

    with wave.open(ficCod, 'wb') as w:
        w.setparams((1, 4, params.framerate, 0, 'NONE', 'not compressed'))
        w.writeframes(struct.pack('<' + 'i' * len(codificado), *codificado))


def decEstereo(ficCod, ficEste):
    with wave.open(ficCod, 'rb') as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 4:
            raise ValueError("Archivo codificado debe ser mono de 32 bits por muestra")
        params = w.getparams()
        datos = struct.unpack('<' + 'i' * w.getnframes(), w.readframes(w.getnframes()))

    if len(datos) % 2 != 0:
        raise ValueError("Número impar de muestras: faltan datos")

    izq = [(datos[i] + datos[i + 1]) // 2 for i in range(0, len(datos), 2)]
    der = [(datos[i] - datos[i + 1]) // 2 for i in range(0, len(datos), 2)]
    combinado = [val for par in zip(izq, der) for val in par]

    with wave.open(ficEste, 'wb') as w:
        w.setparams((2, 2, params.framerate, 0, 'NONE', 'not compressed'))
        w.writeframes(struct.pack('<' + 'h' * len(combinado), *combinado))



# INTERFAZ GRÁFICA: Uso de tkinter para crear una aplicación que permita al usuario seleccionar archivos y realizar conversiones.
class AplicacionMono:
    def __init__(self, root):
        self.root = root
        root.title("Procesado Estéreo/Mono")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        self.crea_pestana_estereo2mono()
        self.crea_pestana_mono2estereo()
        self.crea_pestana_codifica()
        self.crea_pestana_descodifica()

    def crea_pestana_estereo2mono(self):
        marco = ttk.Frame(self.notebook)
        self.notebook.add(marco, text="Estéreo a Mono")
        ttk.Label(marco, text="Archivo estéreo:").grid(row=0, column=0, padx=5, pady=5)
        self.entrada_estereo = ttk.Entry(marco, width=50)
        self.entrada_estereo.grid(row=0, column=1)
        ttk.Button(marco, text="Buscar", command=self.selecciona_estereo).grid(row=0, column=2)
        ttk.Label(marco, text="Canal (0-3):").grid(row=1, column=0, padx=5, pady=5)
        self.canal_var = tk.IntVar(value=2)
        ttk.Spinbox(marco, from_=0, to=3, textvariable=self.canal_var, width=5).grid(row=1, column=1, sticky='w')
        ttk.Button(marco, text="Convertir a Mono", command=self.convertir_a_mono).grid(row=2, column=0, columnspan=3, pady=10)

    def selecciona_estereo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos WAVE", "*.wav")])
        if archivo:
            self.entrada_estereo.delete(0, tk.END)
            self.entrada_estereo.insert(0, archivo)

    def convertir_a_mono(self):
        entrada = self.entrada_estereo.get()
        if not entrada:
            return messagebox.showwarning("Atención", "Debes seleccionar un archivo estéreo")
        salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAVE", "*.wav")])
        if not salida:
            return
        try:
            estereo2mono(entrada, salida, self.canal_var.get())
            messagebox.showinfo("Éxito", "Conversión completada")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crea_pestana_mono2estereo(self):
        marco = ttk.Frame(self.notebook)
        self.notebook.add(marco, text="Mono a Estéreo")
        ttk.Label(marco, text="Canal Izquierdo:").grid(row=0, column=0)
        self.entrada_izq = ttk.Entry(marco, width=50)
        self.entrada_izq.grid(row=0, column=1)
        ttk.Button(marco, text="Buscar", command=lambda: self.selecciona_mono(self.entrada_izq)).grid(row=0, column=2)
        ttk.Label(marco, text="Canal Derecho:").grid(row=1, column=0)
        self.entrada_der = ttk.Entry(marco, width=50)
        self.entrada_der.grid(row=1, column=1)
        ttk.Button(marco, text="Buscar", command=lambda: self.selecciona_mono(self.entrada_der)).grid(row=1, column=2)
        ttk.Button(marco, text="Fusionar", command=self.fusionar_mono).grid(row=2, column=0, columnspan=3, pady=10)

    def selecciona_mono(self, campo):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos WAVE", "*.wav")])
        if archivo:
            campo.delete(0, tk.END)
            campo.insert(0, archivo)

    def fusionar_mono(self):
        izq = self.entrada_izq.get()
        der = self.entrada_der.get()
        if not izq or not der:
            return messagebox.showwarning("Atención", "Debes seleccionar ambos canales")
        salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAVE", "*.wav")])
        if not salida:
            return
        try:
            mono2estereo(izq, der, salida)
            messagebox.showinfo("Éxito", "Archivo estéreo generado")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crea_pestana_codifica(self):
        marco = ttk.Frame(self.notebook)
        self.notebook.add(marco, text="Codifica Estéreo")
        ttk.Label(marco, text="Archivo estéreo:").grid(row=0, column=0)
        self.entrada_cod = ttk.Entry(marco, width=50)
        self.entrada_cod.grid(row=0, column=1)
        ttk.Button(marco, text="Buscar", command=lambda: self.selecciona_mono(self.entrada_cod)).grid(row=0, column=2)
        ttk.Button(marco, text="Codificar", command=self.codificar_estereo).grid(row=1, column=0, columnspan=3, pady=10)

    def codificar_estereo(self):
        entrada = self.entrada_cod.get()
        if not entrada:
            return messagebox.showwarning("Atención", "Selecciona un archivo estéreo")
        salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAVE", "*.wav")])
        if not salida:
            return
        try:
            codEstereo(entrada, salida)
            messagebox.showinfo("Éxito", "Archivo codificado")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crea_pestana_descodifica(self):
        marco = ttk.Frame(self.notebook)
        self.notebook.add(marco, text="Descodifica Estéreo")
        ttk.Label(marco, text="Archivo codificado:").grid(row=0, column=0)
        self.entrada_dec = ttk.Entry(marco, width=50)
        self.entrada_dec.grid(row=0, column=1)
        ttk.Button(marco, text="Buscar", command=lambda: self.selecciona_mono(self.entrada_dec)).grid(row=0, column=2)
        ttk.Button(marco, text="Descodificar", command=self.descodificar_estereo).grid(row=1, column=0, columnspan=3, pady=10)

    def descodificar_estereo(self):
        entrada = self.entrada_dec.get()
        if not entrada:
            return messagebox.showwarning("Atención", "Selecciona un archivo codificado")
        salida = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Archivos WAVE", "*.wav")])
        if not salida:
            return
        try:
            decEstereo(entrada, salida)
            messagebox.showinfo("Éxito", "Archivo descodificado")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# Ejecución (desde el terminal usamos: python3 mono.py)
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionMono(root)
    root.mainloop()

