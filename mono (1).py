"""
mono.py

Guillem Perez Sanchez
QP 2025
"""
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb

# Funciones APA T5

def estereo2mono(ficEste, ficMono, canal=2):
    with open(ficEste, 'rb') as fe:
        cabecera = fe.read(44)
        if cabecera[22:24] != struct.pack('<H', 2):
            raise ValueError("El fichero de entrada no es estéreo (2 canales)")

        tam_muestras = struct.unpack('<I', cabecera[40:44])[0]
        num_muestras = tam_muestras // 4
        datos = fe.read(tam_muestras)
        muestras = struct.unpack('<' + 'hh'*num_muestras, datos)

        if canal == 0:
            mono = [muestras[i] for i in range(0, len(muestras), 2)]
        elif canal == 1:
            mono = [muestras[i] for i in range(1, len(muestras), 2)]
        elif canal == 2:
            mono = [(muestras[i] + muestras[i+1]) // 2 for i in range(0, len(muestras), 2)]
        elif canal == 3:
            mono = [(muestras[i] - muestras[i+1]) // 2 for i in range(0, len(muestras), 2)]
        else:
            raise ValueError("Parámetro 'canal' no válido (debe ser 0, 1, 2 o 3)")

    nuevo_tam_datos = len(mono) * 2
    nueva_cabecera = bytearray(cabecera)
    nueva_cabecera[22:24] = struct.pack('<H', 1)
    nueva_cabecera[32:34] = struct.pack('<H', 2)
    nueva_cabecera[34:36] = struct.pack('<H', 16)
    nueva_cabecera[40:44] = struct.pack('<I', nuevo_tam_datos)
    nueva_cabecera[4:8] = struct.pack('<I', 36 + nuevo_tam_datos)

    with open(ficMono, 'wb') as fm:
        fm.write(nueva_cabecera)
        fm.write(struct.pack('<' + 'h'*len(mono), *mono))

def mono2estereo(ficIzq, ficDer, ficEste):
    with open(ficIzq, 'rb') as fz, open(ficDer, 'rb') as fd:
        cab_izq = fz.read(44)
        cab_der = fd.read(44)

        if cab_izq[22:24] != struct.pack('<H', 1) or cab_der[22:24] != struct.pack('<H', 1):
            raise ValueError("Ambos ficheros deben ser monofónicos (1 canal)")

        datos_izq = fz.read()
        datos_der = fd.read()

        num_muestras_izq = len(datos_izq) // 2
        num_muestras_der = len(datos_der) // 2

        if num_muestras_izq != num_muestras_der:
            raise ValueError("Los ficheros deben tener el mismo número de muestras")

        izq = struct.unpack('<' + 'h'*num_muestras_izq, datos_izq)
        der = struct.unpack('<' + 'h'*num_muestras_der, datos_der)

    estereo = [val for par in zip(izq, der) for val in par]

    nuevo_tam_datos = len(estereo) * 2
    nueva_cabecera = bytearray(cab_izq)
    nueva_cabecera[22:24] = struct.pack('<H', 2)
    nueva_cabecera[32:34] = struct.pack('<H', 4)
    nueva_cabecera[34:36] = struct.pack('<H', 16)
    nueva_cabecera[40:44] = struct.pack('<I', nuevo_tam_datos)
    nueva_cabecera[4:8] = struct.pack('<I', 36 + nuevo_tam_datos)

    with open(ficEste, 'wb') as fe:
        fe.write(nueva_cabecera)
        fe.write(struct.pack('<' + 'h'*len(estereo), *estereo))

import struct

def codEstereo(ficEste, ficCod):
    with open(ficEste, 'rb') as fe:
        # Leer cabecera RIFF
        riff, tam, wave = struct.unpack('<4sI4s', fe.read(12))
        if riff != b'RIFF' or wave != b'WAVE':
            raise TypeError("Archivo no válido WAVE")

        canales = None
        frec_muestreo = None
        bits_muestra = None
        desplazamiento = None
        tam_datos = None

        while True:
            subchunk = fe.read(8)
            if len(subchunk) < 8:
                break
            ident, tam_subchunk = struct.unpack('<4sI', subchunk)
            if ident == b'fmt ':
                fmt = fe.read(tam_subchunk)
                formato, canales, frec_muestreo, _, _, bits_muestra = struct.unpack('<HHIIHH', fmt[:16])
            elif ident == b'data':
                desplazamiento = fe.tell()
                tam_datos = tam_subchunk
                fe.seek(tam_subchunk, 1)
            else:
                fe.seek(tam_subchunk, 1)

        if canales != 2 or bits_muestra != 16:
            raise ValueError("El archivo no es estéreo de 16 bits")

        # Leer datos
        fe.seek(desplazamiento)
        datos = fe.read(tam_datos)
        muestras = struct.unpack('<' + 'hh' * (tam_datos // 4), datos)

        codificadas = [((l + r) << 16) | ((l - r) & 0xFFFF)
                       for l, r in zip(muestras[::2], muestras[1::2])]
        
        datos_cod = struct.pack('<' + 'I' * len(codificadas), *codificadas)
        tam_cod = len(datos_cod)
        bloque = 4
        tasa = frec_muestreo * bloque

        # Crear cabecera mono 32 bits
        cabecera = (
            struct.pack('4sI4s', b'RIFF', 36 + tam_cod, b'WAVE') +
            struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, 1, frec_muestreo,
                        tasa, bloque, 32) +
            struct.pack('<4sI', b'data', tam_cod)
        )

    with open(ficCod, 'wb') as fc:
        fc.write(cabecera)
        fc.write(datos_cod)

def decEstereo(ficCod, ficEste):
    with open(ficCod, 'rb') as fc:
        # Leer cabecera RIFF
        riff, tam, wave = struct.unpack('<4sI4s', fc.read(12))
        if riff != b'RIFF' or wave != b'WAVE':
            raise TypeError("Archivo no válido WAVE")

        canales = None
        frec_muestreo = None
        bits_muestra = None
        desplazamiento = None
        tam_datos = None

        while True:
            subchunk = fc.read(8)
            if len(subchunk) < 8:
                break
            ident, tam_subchunk = struct.unpack('<4sI', subchunk)
            if ident == b'fmt ':
                fmt = fc.read(tam_subchunk)
                formato, canales, frec_muestreo, _, _, bits_muestra = struct.unpack('<HHIIHH', fmt[:16])
            elif ident == b'data':
                desplazamiento = fc.tell()
                tam_datos = tam_subchunk
                fc.seek(tam_subchunk, 1)
            else:
                fc.seek(tam_subchunk, 1)

        if canales != 1 or bits_muestra != 32:
            raise ValueError("El archivo no es mono de 32 bits")

        # Leer datos
        fc.seek(desplazamiento)
        datos = fc.read(tam_datos)
        codificados = struct.unpack('<' + 'I' * (tam_datos // 4), datos)

        muestras = []
        for cod in codificados:
            suma = (cod >> 16) & 0xFFFF
            dif = cod & 0xFFFF
            suma = struct.unpack('<h', struct.pack('<H', suma))[0]
            dif = struct.unpack('<h', struct.pack('<H', dif))[0]
            l = suma + dif
            r = suma - dif
            muestras.extend([l, r])

        datos_est = struct.pack('<' + 'h' * len(muestras), *muestras)
        tam_est = len(datos_est)
        bloque = 4
        tasa = frec_muestreo * bloque

        # Crear cabecera estéreo 16 bits
        cabecera = (
            struct.pack('4sI4s', b'RIFF', 36 + tam_est, b'WAVE') +
            struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, 2, frec_muestreo,
                        tasa, bloque, 16) +
            struct.pack('<4sI', b'data', tam_est)
        )

    with open(ficEste, 'wb') as fe:
        fe.write(cabecera)
        fe.write(datos_est)


# Diseño interfaz gráfica con TkInter

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Audio Estéreo/Mono")

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        self.crear_pestana_estereo_a_mono(notebook)
        self.crear_pestana_mono_a_estereo(notebook)
        self.crear_pestana_codifica_estereo(notebook)
        self.crear_pestana_decodifica_estereo(notebook)


# Diseño pestañas:
    
    # Pestaña Estereo a Mono
    def crear_pestana_estereo_a_mono(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Estéreo a Mono")

        ttk.Label(frame, text="Archivo estéreo:").grid(row=0, column=0, sticky='w')
        self.entrada_este = ttk.Entry(frame, width=50)
        self.entrada_este.grid(row=0, column=1)
        ttk.Button(frame, text="Seleccionar", command=self.sel_estereo).grid(row=0, column=2)

        ttk.Label(frame, text="Canal (0=Izq, 1=Der, 2=Med, 3=Dif):").grid(row=1, column=0, sticky='w')
        self.canal = ttk.Combobox(frame, values=["0", "1", "2", "3"])
        self.canal.current(2)
        self.canal.grid(row=1, column=1)

        ttk.Button(frame, text="Guardar como...", command=self.guardar_mono).grid(row=2, column=0)
        self.salida_mono = ttk.Entry(frame, width=50)
        self.salida_mono.grid(row=2, column=1)

        ttk.Button(frame, text="Convertir", command=self.convertir_estereo_a_mono).grid(row=3, column=1, pady=10)

    def sel_estereo(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_este.delete(0, tk.END)
            self.entrada_este.insert(0, archivo)

    def guardar_mono(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.salida_mono.delete(0, tk.END)
            self.salida_mono.insert(0, archivo)

    def convertir_estereo_a_mono(self):
        try:
            estereo2mono(
                self.entrada_este.get(),
                self.salida_mono.get(),
                int(self.canal.get())
            )
            messagebox.showinfo("Éxito", "Conversión completada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Pestaña Mono a Estéreo
    def crear_pestana_mono_a_estereo(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Mono a Estéreo")

        ttk.Label(frame, text="Archivo canal izquierdo:").grid(row=0, column=0, sticky='w')
        self.entrada_izq = ttk.Entry(frame, width=50)
        self.entrada_izq.grid(row=0, column=1)
        ttk.Button(frame, text="Seleccionar", command=self.sel_izq).grid(row=0, column=2)

        ttk.Label(frame, text="Archivo canal derecho:").grid(row=1, column=0, sticky='w')
        self.entrada_der = ttk.Entry(frame, width=50)
        self.entrada_der.grid(row=1, column=1)
        ttk.Button(frame, text="Seleccionar", command=self.sel_der).grid(row=1, column=2)

        ttk.Button(frame, text="Guardar como...", command=self.guardar_estereo).grid(row=2, column=0)
        self.salida_estereo = ttk.Entry(frame, width=50)
        self.salida_estereo.grid(row=2, column=1)

        ttk.Button(frame, text="Convertir", command=self.convertir_mono_a_estereo).grid(row=3, column=1, pady=10)

    def sel_izq(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_izq.delete(0, tk.END)
            self.entrada_izq.insert(0, archivo)

    def sel_der(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_der.delete(0, tk.END)
            self.entrada_der.insert(0, archivo)

    def guardar_estereo(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.salida_estereo.delete(0, tk.END)
            self.salida_estereo.insert(0, archivo)

    def convertir_mono_a_estereo(self):
        try:
            mono2estereo(
                self.entrada_izq.get(),
                self.entrada_der.get(),
                self.salida_estereo.get()
            )
            messagebox.showinfo("Éxito", "Conversión completada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Pestaña Codifica Estéreo
    def crear_pestana_codifica_estereo(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Codificar Estéreo")

        ttk.Label(frame, text="Archivo estéreo:").grid(row=0, column=0, sticky='w')
        self.entrada_cod = ttk.Entry(frame, width=50)
        self.entrada_cod.grid(row=0, column=1)
        ttk.Button(frame, text="Seleccionar", command=self.sel_cod_entrada).grid(row=0, column=2)

        ttk.Button(frame, text="Guardar como...", command=self.guardar_cod).grid(row=1, column=0)
        self.salida_cod = ttk.Entry(frame, width=50)
        self.salida_cod.grid(row=1, column=1)

        ttk.Button(frame, text="Codificar", command=self.codificar_estereo).grid(row=2, column=1, pady=10)

    def sel_cod_entrada(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_cod.delete(0, tk.END)
            self.entrada_cod.insert(0, archivo)
    
    def guardar_cod(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.salida_cod.delete(0, tk.END)
            self.salida_cod.insert(0, archivo)

    def codificar_estereo(self):
        try:
            codEstereo(self.entrada_cod.get(), self.salida_cod.get())
            messagebox.showinfo("Éxito", "Codificación completada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Pestaña Descodifica Estéreo
    def crear_pestana_decodifica_estereo(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Decodificar Estéreo")

        ttk.Label(frame, text="Archivo codificado:").grid(row=0, column=0, sticky='w')
        self.entrada_dec = ttk.Entry(frame, width=50)
        self.entrada_dec.grid(row=0, column=1)
        ttk.Button(frame, text="Seleccionar", command=self.sel_dec_entrada).grid(row=0, column=2)

        ttk.Button(frame, text="Guardar como...", command=self.guardar_dec).grid(row=1, column=0)
        self.salida_dec = ttk.Entry(frame, width=50)
        self.salida_dec.grid(row=1, column=1)

        ttk.Button(frame, text="Decodificar", command=self.decodificar_estereo).grid(row=2, column=1, pady=10)

    def sel_dec_entrada(self):
        archivo = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.entrada_dec.delete(0, tk.END)
            self.entrada_dec.insert(0, archivo)

    def guardar_dec(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if archivo:
            self.salida_dec.delete(0, tk.END)
            self.salida_dec.insert(0, archivo)

    def decodificar_estereo(self):
        try:
            decEstereo(self.entrada_dec.get(), self.salida_dec.get())
            messagebox.showinfo("Éxito", "Decodificación completada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = tb.Window(themename="minty")
    Aplicacion(app)
    app.mainloop()
