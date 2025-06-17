''' 
        Examen Final APA 

        Autores:
        Sebastián Pérez Capitano
        Àlex Segura Medina 

        Ejercicio 2: Programa de Manejo de Señales Estéreo (35%)
        · Construya el programa mono.py que permita realizar las funciones de la tarea APA-T5 en un entorno gráfico usando TkInter.

'''


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import struct

# Asegúrate de que estas funciones están en este archivo o importadas correctamente
# from tu_modulo import estereo2mono, mono2estereo

def estereo2mono(ficEste, ficMono, canal = 2):

    """
    
    Convierte un archivo WAVE estéreo a mono en función del canal indicado:
    0 = izquierdo, 1 = derecho, 2 = semisuma, 3 = semidiferencia.

    """
    with open(ficEste, 'rb') as fe:
        cabecera = fe.read(44)
        if cabecera[0:4] != b'RIFF' or cabecera[8:12] != b'WAVE':
            raise ValueError("El fichero de entrada no es un WAVE válido")

        fmt_tag, n_channels, sample_rate, byte_rate, block_align, bps = struct.unpack('<HHIIHH', cabecera[20:36])
        if n_channels != 2 or fmt_tag != 1 or bps != 16:
            raise ValueError("El fichero no es estéreo o no usa PCM lineal de 16 bits")

        data_size = struct.unpack('<I', cabecera[40:44])[0]
        num_frames = data_size // 4  # 4 bytes por muestra estéreo (2 bytes por canal)
        datos = fe.read()

    muestras = struct.unpack('<' + 'hh'*num_frames, datos)
    if canal == 0:
        canal_mono = [muestras[i] for i in range(0, len(muestras), 2)]
    elif canal == 1:
        canal_mono = [muestras[i] for i in range(1, len(muestras), 2)]
    elif canal == 2:
        canal_mono = [(muestras[i] + muestras[i+1]) // 2 for i in range(0, len(muestras), 2)]
    elif canal == 3:
        canal_mono = [(muestras[i] - muestras[i+1]) // 2 for i in range(0, len(muestras), 2)]
    else:
        raise ValueError("Parámetro 'canal' no válido. Usa 0, 1, 2 o 3.")

    nuevo_data_size = len(canal_mono) * 2  # 2 bytes por muestra
    nuevo_byte_rate = sample_rate * 2
    nuevo_block_align = 2
    with open(ficMono, 'wb') as fm:
        fm.write(b'RIFF')
        fm.write(struct.pack('<I', 36 + nuevo_data_size))
        fm.write(b'WAVE')
        fm.write(b'fmt ')
        fm.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate,
                             nuevo_byte_rate, nuevo_block_align, 16))
        fm.write(b'data')
        fm.write(struct.pack('<I', nuevo_data_size))
        fm.write(struct.pack('<' + 'h'*len(canal_mono), *canal_mono))



def mono2estereo(ficIzq, ficDer, ficEste):
    """

    Genera un archivo WAVE estéreo combinando dos archivos WAVE mono.

    """
    with open(ficIzq, 'rb') as fz:
        header_izq = fz.read(44)
        if header_izq[0:4] != b'RIFF' or header_izq[8:12] != b'WAVE':
            raise ValueError("ficIzq no es un fichero WAVE válido")
        fmt_tag, nchannels, sample_rate, _, _, bps = struct.unpack('<HHIIHH', header_izq[20:36])
        if nchannels != 1 or fmt_tag != 1 or bps != 16:
            raise ValueError("ficIzq no es un fichero mono PCM 16-bit válido")
        data_izq = fz.read()

    with open(ficDer, 'rb') as fd:
        header_der = fd.read(44)
        if header_der[0:4] != b'RIFF' or header_der[8:12] != b'WAVE':
            raise ValueError("ficDer no es un fichero WAVE válido")
        fmt_tag_d, nchannels_d, sample_rate_d, _, _, bps_d = struct.unpack('<HHIIHH', header_der[20:36])
        if nchannels_d != 1 or fmt_tag_d != 1 or bps_d != 16:
            raise ValueError("ficDer no es un fichero mono PCM 16-bit válido")
        if sample_rate_d != sample_rate or bps_d != bps:
            raise ValueError("Los ficheros mono no tienen la misma configuración")
        data_der = fd.read()

    muestras_izq = struct.unpack('<' + 'h' * (len(data_izq) // 2), data_izq)
    muestras_der = struct.unpack('<' + 'h' * (len(data_der) // 2), data_der)
    if len(muestras_izq) != len(muestras_der):
        raise ValueError("Los ficheros mono no tienen el mismo número de muestras")

    intercaladas = [val for pair in zip(muestras_izq, muestras_der) for val in pair]
    data_size = len(intercaladas) * 2  # 2 bytes por muestra
    byte_rate = sample_rate * 4        # 2 canales x 2 bytes
    block_align = 4                    # 2 canales x 2 bytes

    with open(ficEste, 'wb') as fe:
        fe.write(b'RIFF')
        fe.write(struct.pack('<I', 36 + data_size))
        fe.write(b'WAVE')
        fe.write(b'fmt ')
        fe.write(struct.pack('<IHHIIHH', 16, 1, 2, sample_rate,
                             byte_rate, block_align, 16))
        fe.write(b'data')
        fe.write(struct.pack('<I', data_size))
        fe.write(struct.pack('<' + 'h' * len(intercaladas), *intercaladas))




class AplicacionMono:
    def __init__(self, root):
        self.root = root
        root.title("APA-T5: Procesado Estéreo/Mono")

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
        ttk.Label(marco, text="(A implementar)").pack(pady=20)

    def crea_pestana_descodifica(self):
        marco = ttk.Frame(self.notebook)
        self.notebook.add(marco, text="Descodifica Estéreo")
        ttk.Label(marco, text="(A implementar)").pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionMono(root)
    root.mainloop()
