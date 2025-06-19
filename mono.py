"""
mono.py

Guillem Perez Sanchez
QP 2025

Versión corregida y mejorada con análisis de chunks robusto y
corrección de la lógica de codificación/decodificación.
"""
import struct
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox

# --- Funciones de Utilidad para WAV ---

def leer_wav(nombre_archivo):
    """
    Lee un archivo WAV de forma robusta, parseando los chunks.
    Devuelve los parámetros de formato, la posición del bloque 'data' y el manejador del archivo.
    """
    f = open(nombre_archivo, 'rb')
    riff, tam_riff, wave = struct.unpack('<4sI4s', f.read(12))
    if riff != b'RIFF' or wave != b'WAVE':
        f.close()
        raise ValueError("El archivo no es un WAVE válido.")

    params = {'canales': None, 'frec_muestreo': None, 'bits_muestra': None, 'tam_datos': None, 'data_offset': None}
    
    while True:
        chunk_id, chunk_size = struct.unpack('<4sI', f.read(8))
        if chunk_id == b'fmt ':
            formato, canales, frec, byte_rate, align, bits = struct.unpack('<HHIIHH', f.read(16))
            params.update({'canales': canales, 'frec_muestreo': frec, 'bits_muestra': bits})
            if chunk_size > 16: f.seek(chunk_size - 16, 1) # Saltar el resto del chunk si existe
        elif chunk_id == b'data':
            params['tam_datos'] = chunk_size
            params['data_offset'] = f.tell()
            f.seek(chunk_size, 1) # Dejamos el cursor al final de los datos para la siguiente lectura
        else:
            if chunk_size % 2 != 0: chunk_size += 1 # Asegurar alineación
            f.seek(chunk_size, 1)
        
        if f.tell() >= tam_riff + 8:
            break
            
    if not all(params.values()):
        f.close()
        raise ValueError("Archivo WAVE incompleto o con formato no reconocido.")
    
    return f, params

def escribir_wav(nombre_archivo, datos_muestras, canales, frec, bits):
    """Escribe los datos de muestra en un nuevo archivo WAV."""
    with open(nombre_archivo, 'wb') as f:
        tam_datos = len(datos_muestras)
        bytes_por_muestra = bits // 8
        block_align = canales * bytes_por_muestra
        byte_rate = frec * block_align
        
        # Cabecera RIFF y fmt
        f.write(struct.pack('<4sI4s', b'RIFF', 36 + tam_datos, b'WAVE'))
        f.write(struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, canales, frec, byte_rate, block_align, bits))
        
        # Cabecera data y datos
        f.write(struct.pack('<4sI', b'data', tam_datos))
        f.write(datos_muestras)

# --- Lógica de Procesamiento de Audio ---

def estereo2mono(ficEste, ficMono, canal=2):
    fe, params = leer_wav(ficEste)
    if params['canales'] != 2 or params['bits_muestra'] != 16:
        fe.close()
        raise ValueError("El fichero de entrada no es estéreo de 16 bits.")

    fe.seek(params['data_offset'])
    datos = fe.read(params['tam_datos'])
    num_muestras_par = params['tam_datos'] // 4
    muestras = struct.unpack(f'<{num_muestras_par}hh', datos)
    fe.close()

    if canal == 0:    # Canal Izquierdo
        mono = [muestras[i] for i in range(0, len(muestras), 2)]
    elif canal == 1:  # Canal Derecho
        mono = [muestras[i] for i in range(1, len(muestras), 2)]
    elif canal == 2:  # Media (Mid)
        mono = [(muestras[i] + muestras[i+1]) // 2 for i in range(0, len(muestras), 2)]
    elif canal == 3:  # Diferencia (Side)
        mono = [(muestras[i] - muestras[i+1]) // 2 for i in range(0, len(muestras), 2)]
    else:
        raise ValueError("Parámetro 'canal' no válido (0, 1, 2 o 3).")

    datos_mono = struct.pack(f'<{len(mono)}h', *mono)
    escribir_wav(ficMono, datos_mono, 1, params['frec_muestreo'], 16)


def mono2estereo(ficIzq, ficDer, ficEste):
    fz, params_izq = leer_wav(ficIzq)
    fd, params_der = leer_wav(ficDer)
    
    if not (params_izq['canales'] == 1 and params_der['canales'] == 1 and params_izq['bits_muestra'] == 16 and params_der['bits_muestra'] == 16):
        fz.close(); fd.close()
        raise ValueError("Ambos ficheros deben ser monofónicos de 16 bits.")
    if params_izq['tam_datos'] != params_der['tam_datos']:
        fz.close(); fd.close()
        raise ValueError("Los ficheros deben tener el mismo número de muestras.")
    
    fz.seek(params_izq['data_offset']); datos_izq = fz.read()
    fd.seek(params_der['data_offset']); datos_der = fd.read()
    fz.close(); fd.close()

    num_muestras = len(datos_izq) // 2
    izq = struct.unpack(f'<{num_muestras}h', datos_izq)
    der = struct.unpack(f'<{num_muestras}h', datos_der)

    estereo_intercalado = [val for par in zip(izq, der) for val in par]
    datos_estereo = struct.pack(f'<{len(estereo_intercalado)}h', *estereo_intercalado)
    escribir_wav(ficEste, datos_estereo, 2, params_izq['frec_muestreo'], 16)

def codEstereo(ficEste, ficCod):
    fe, params = leer_wav(ficEste)
    if params['canales'] != 2 or params['bits_muestra'] != 16:
        fe.close()
        raise ValueError("El archivo de entrada no es estéreo de 16 bits.")
    
    fe.seek(params['data_offset'])
    datos = fe.read(params['tam_datos'])
    muestras = struct.unpack(f'<{params["tam_datos"] // 2}h', datos)
    fe.close()
    
    codificadas = [
        (((l + r) // 2) << 16) | (((l - r) // 2) & 0xFFFF)
        for l, r in zip(muestras[::2], muestras[1::2])
    ]
    
    datos_cod = struct.pack(f'<{len(codificadas)}i', *codificadas) # 'i' para entero con signo de 32 bits
    escribir_wav(ficCod, datos_cod, 1, params['frec_muestreo'], 32)


def decEstereo(ficCod, ficEste):
    fc, params = leer_wav(ficCod)
    if params['canales'] != 1 or params['bits_muestra'] != 32:
        fc.close()
        raise ValueError("El archivo de entrada no es mono de 32 bits.")
        
    fc.seek(params['data_offset'])
    datos_cod = fc.read(params['tam_datos'])
    codificados = struct.unpack(f'<{params["tam_datos"] // 4}i', datos_cod)
    fc.close()

    muestras_dec = []
    for cod in codificados:
        mid = cod >> 16
        side = struct.unpack('<h', struct.pack('<h', cod & 0xFFFF))[0] # Recupera el signo de 'side'
        
        l = mid + side
        r = mid - side
        muestras_dec.extend([l, r])

    datos_est = struct.pack(f'<{len(muestras_dec)}h', *muestras_dec)
    escribir_wav(ficEste, datos_est, 2, params['frec_muestreo'], 16)

# --- Interfaz Gráfica ---

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Audio WAV")
        self.root.geometry("600x250")

        notebook = tb.Notebook(root)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.crear_pestana_estereo_a_mono(notebook)
        self.crear_pestana_mono_a_estereo(notebook)
        self.crear_pestana_codifica_estereo(notebook)
        self.crear_pestana_decodifica_estereo(notebook)

    def _crear_fila_archivo(self, parent, etiqueta_texto, es_guardar=False):
        frame = tb.Frame(parent)
        tb.Label(frame, text=etiqueta_texto, width=25).pack(side="left", padx=5)
        entry = tb.Entry(frame, width=40)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        
        def seleccionar():
            if es_guardar:
                path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
            else:
                path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
            if path:
                entry.delete(0, "end")
                entry.insert(0, path)

        btn_text = "Guardar como..." if es_guardar else "Seleccionar"
        tb.Button(frame, text=btn_text, command=seleccionar, bootstyle="outline").pack(side="left", padx=5)
        frame.pack(fill="x", pady=5)
        return entry
    
    def _ejecutar_conversion(self, funcion, *args):
        try:
            # Validar que las rutas no estén vacías
            for arg in args:
                if not arg:
                    Messagebox.show_warning("Por favor, especifique todas las rutas de archivo.", "Ruta Faltante")
                    return
            
            funcion(*args)
            Messagebox.show_info("Conversión completada con éxito.", "Éxito")
        except Exception as e:
            Messagebox.show_error(f"Se produjo un error:\n{e}", "Error")

    def crear_pestana_estereo_a_mono(self, notebook):
        frame = tb.Frame(notebook, padding=10)
        notebook.add(frame, text="Estéreo a Mono")
        
        self.entrada_este = self._crear_fila_archivo(frame, "Archivo estéreo de entrada:")
        self.salida_mono = self._crear_fila_archivo(frame, "Archivo mono de salida:", es_guardar=True)

        # Selector de canal
        combo_frame = tb.Frame(frame)
        tb.Label(combo_frame, text="Canal a extraer:", width=25).pack(side="left", padx=5)
        self.canal = tb.Combobox(combo_frame, values=["0: Izquierdo", "1: Derecho", "2: Medio (L+R)/2", "3: Diferencia (L-R)/2"], state="readonly")
        self.canal.current(2)
        self.canal.pack(side="left", padx=5, fill="x", expand=True)
        combo_frame.pack(fill="x", pady=5)
        
        tb.Button(frame, text="Convertir", bootstyle="success", command=lambda: 
            self._ejecutar_conversion(estereo2mono, self.entrada_este.get(), self.salida_mono.get(), int(self.canal.get().split(':')[0]))
        ).pack(pady=15)

    def crear_pestana_mono_a_estereo(self, notebook):
        frame = tb.Frame(notebook, padding=10)
        notebook.add(frame, text="Mono a Estéreo")
        
        self.entrada_izq = self._crear_fila_archivo(frame, "Archivo canal izquierdo (L):")
        self.entrada_der = self._crear_fila_archivo(frame, "Archivo canal derecho (R):")
        self.salida_estereo = self._crear_fila_archivo(frame, "Archivo estéreo de salida:", es_guardar=True)
        
        tb.Button(frame, text="Convertir", bootstyle="success", command=lambda: 
            self._ejecutar_conversion(mono2estereo, self.entrada_izq.get(), self.entrada_der.get(), self.salida_estereo.get())
        ).pack(pady=15)

    def crear_pestana_codifica_estereo(self, notebook):
        frame = tb.Frame(notebook, padding=10)
        notebook.add(frame, text="Codificar Estéreo (M/S)")
        
        self.entrada_cod = self._crear_fila_archivo(frame, "Archivo estéreo de entrada:")
        self.salida_cod = self._crear_fila_archivo(frame, "Archivo codificado de salida:", es_guardar=True)
        
        tb.Button(frame, text="Codificar", bootstyle="success", command=lambda: 
            self._ejecutar_conversion(codEstereo, self.entrada_cod.get(), self.salida_cod.get())
        ).pack(pady=15)

    def crear_pestana_decodifica_estereo(self, notebook):
        frame = tb.Frame(notebook, padding=10)
        notebook.add(frame, text="Decodificar Estéreo (M/S)")

        self.entrada_dec = self._crear_fila_archivo(frame, "Archivo codificado de entrada:")
        self.salida_dec = self._crear_fila_archivo(frame, "Archivo estéreo de salida:", es_guardar=True)
        
        tb.Button(frame, text="Decodificar", bootstyle="success", command=lambda: 
            self._ejecutar_conversion(decEstereo, self.entrada_dec.get(), self.salida_dec.get())
        ).pack(pady=15)

if __name__ == "__main__":
    app_root = tb.Window(themename="minty")
    Aplicacion(app_root)
    app_root.mainloop()
