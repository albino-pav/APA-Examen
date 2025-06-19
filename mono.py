import numpy as np
import struct as st
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os



def reproducir_wav(ruta_archivo):
    if not os.path.isfile(ruta_archivo):
        messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta_archivo}")
        return

    def hilo_reproduccion():
        try:
            import soundfile as sf
            import sounddevice as sd
            audio, tasa = sf.read(ruta_archivo, dtype='float32')
            sd.play(audio, tasa)
            sd.wait()
        except Exception as err:
            messagebox.showerror("Error al reproducir", str(err))

    threading.Thread(target=hilo_reproduccion, daemon=True).start()

def buscar_archivo(variable_destino):
    ruta = filedialog.askopenfilename(title="Seleccionar archivo WAV", filetypes=[("Archivos de audio", "*.wav")])
    if ruta:
        variable_destino.set(ruta)

def buscar_dos_archivos(var1, var2):
    rutas = filedialog.askopenfilenames(title="Seleccionar archivos MONO L y R", filetypes=[("Archivos WAV", "*.wav")])
    if rutas and len(rutas) >= 2:
        var1.set(rutas[0])
        var2.set(rutas[1])



def E2M(archivo_estereo, salida_mono, modo=2):
    with open(archivo_estereo, 'rb') as entrada:
        cabecera = entrada.read(12)
        riff, tam, formato = st.unpack('<4sI4s', cabecera)
        if riff != b'RIFF' or formato != b'WAVE':
            raise Exception("Archivo WAV no válido.")

        fmt_ok, data_ok = False, False

        while not fmt_ok:
            chunk_id, chunk_tam = st.unpack('<4sI', entrada.read(8))
            if chunk_id == b'fmt ':
                datos_fmt = entrada.read(chunk_tam)
                fmt_ok = True
            else:
                entrada.seek(chunk_tam, 1)

        audio_fmt, canales, fs, byte_rate, align, bps = st.unpack('<HHIIHH', datos_fmt[:16])
        if canales != 2 or bps != 16:
            raise Exception("Se requiere WAV estéreo PCM de 16 bits.")

        while not data_ok:
            cid, tam_c = st.unpack('<4sI', entrada.read(8))
            if cid == b'data':
                data_ok = True
                datos = entrada.read(tam_c)
            else:
                entrada.seek(tam_c, 1)

    mono = []
    for i in range(0, len(datos), 4):
        l, r = st.unpack('<hh', datos[i:i+4])
        if modo == 0:
            m = l
        elif modo == 1:
            m = r
        elif modo == 2:
            m = (l + r) // 2
        elif modo == 3:
            m = (l - r) // 2
        else:
            raise ValueError("Modo no válido.")
        mono.append(m)

    muestras = b''.join([st.pack('<h', x) for x in mono])
    chunk_total = 36 + len(muestras)

    with open(salida_mono, 'wb') as out:
        out.write(st.pack('<4sI4s', b'RIFF', chunk_total, b'WAVE'))
        out.write(st.pack('<4sIHHIIHH', b'fmt ', 16, 1, 1, fs, fs*2, 2, 16))
        out.write(st.pack('<4sI', b'data', len(muestras)))
        out.write(muestras)

def M2E(mono_L, mono_R, salida_estereo):
    def leer_mono(path):
        with open(path, 'rb') as f:
            if st.unpack('<4sI4s', f.read(12))[2] != b'WAVE':
                raise Exception("Formato incorrecto.")

            while True:
                cid, tam = st.unpack('<4sI', f.read(8))
                if cid == b'fmt ':
                    fmt = f.read(tam)
                    break
                else:
                    f.seek(tam, 1)

            audio_fmt, n_chan, fs, *_ = st.unpack('<HHIIHH', fmt[:16])
            if n_chan != 1:
                raise Exception("No es archivo mono válido.")

            while True:
                cid, tam = st.unpack('<4sI', f.read(8))
                if cid == b'data':
                    data = f.read(tam)
                    break
                else:
                    f.seek(tam, 1)

        return fs, np.frombuffer(data, dtype='<i2')

    fs1, L = leer_mono(mono_L)
    fs2, R = leer_mono(mono_R)

    if fs1 != fs2 or len(L) != len(R):
        raise Exception("Los archivos no coinciden.")

    intercalado = np.empty(len(L)*2, dtype='<i2')
    intercalado[0::2], intercalado[1::2] = L, R

    datos = intercalado.tobytes()
    total = 36 + len(datos)

    with open(salida_estereo, 'wb') as f:
        f.write(st.pack('<4sI4s', b'RIFF', total, b'WAVE'))
        f.write(st.pack('<4sIHHIIHH', b'fmt ', 16, 1, 2, fs1, fs1*4, 4, 16))
        f.write(st.pack('<4sI', b'data', len(datos)))
        f.write(datos)

def CodE(entrada_stereo, archivo_codificado):
    with open(entrada_stereo, 'rb') as f:
        header = f.read(44)
        campos = list(st.unpack('<4sI4s4sIHHIIHH4sI', header))
        canales = campos[6]
        bps = campos[10]
        tam = campos[12]

        if canales != 2 or bps != 16:
            raise Exception("Solo PCM estéreo 16 bits.")

        datos_raw = f.read(tam)
        datos = np.frombuffer(datos_raw, dtype='<i2')
        L, R = datos[::2], datos[1::2]
        combinados = ((L.astype(np.uint32) & 0xFFFF) << 16) | (R.astype(np.uint32) & 0xFFFF)

    with open(archivo_codificado, 'wb') as out:
        out.write(st.pack('<' + 'I' * len(combinados), *combinados))

    return campos[7]  

def DecodE(fichero_codificado, salida_stereo, tasa=44100):
    with open(fichero_codificado, 'rb') as f:
        datos = f.read()
        combinados = np.frombuffer(datos, dtype='<u4')

    L = ((combinados >> 16) & 0xFFFF).astype('<i2')
    R = (combinados & 0xFFFF).astype('<i2')

    intercalado = np.empty(len(L)*2, dtype='<i2')
    intercalado[0::2], intercalado[1::2] = L, R

    audio_bytes = intercalado.tobytes()
    total = 36 + len(audio_bytes)
    byte_rate = tasa * 4

    with open(salida_stereo, 'wb') as f:
        f.write(st.pack('<4sI4s', b'RIFF', total, b'WAVE'))
        f.write(st.pack('<4sIHHIIHH', b'fmt ', 16, 1, 2, tasa, byte_rate, 4, 16))
        f.write(st.pack('<4sI', b'data', len(audio_bytes)))
        f.write(audio_bytes)



def ventana_un_archivo(padre, funcion):
    ruta = tk.StringVar()

    def guardar():
        if not ruta.get():
            messagebox.showerror("Error", "Selecciona un archivo.")
            return
        destino = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if destino:
            funcion(ruta.get(), destino)
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{destino}")

    tk.Label(padre, text="Archivo de entrada:", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Entry(padre, textvariable=ruta, width=70).pack(pady=5)
    tk.Button(padre, text="Buscar", command=lambda: buscar_archivo(ruta)).pack(pady=5)
    tk.Button(padre, text="Guardar", command=guardar, bg="#669BBC", fg="#003049").pack(pady=10)

def ventana_dos_archivos(padre, funcion):
    izq = tk.StringVar()
    der = tk.StringVar()

    def guardar():
        if not izq.get() or not der.get():
            messagebox.showerror("Error", "Selecciona ambos archivos mono.")
            return
        destino = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if destino:
            funcion(izq.get(), der.get(), destino)
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{destino}")

    tk.Label(padre, text="Archivo MONO Izquierdo:", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Entry(padre, textvariable=izq, width=70).pack(pady=5)
    tk.Button(padre, text="Buscar Izq", command=lambda: buscar_archivo(izq)).pack(pady=5)

    tk.Label(padre, text="Archivo MONO Derecho:", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Entry(padre, textvariable=der, width=70).pack(pady=5)
    tk.Button(padre, text="Buscar Der", command=lambda: buscar_archivo(der)).pack(pady=5)

    tk.Button(padre, text="Guardar", command=guardar, bg="#669BBC", fg="#003049").pack(pady=10)



def iniciar_app():
    root = tk.Tk()
    root.title("Herramientas de Audio")
    root.geometry("750x350")
    root.configure(bg="#FDF0D5")

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, expand=True, fill='both')

    pestañas = [tk.Frame(notebook, bg="#FDF0D5") for _ in range(4)]
    nombres = ["E2M", "M2E", "CodE", "DecodE"]
    funciones = [E2M, M2E, CodE, DecodE]

    for i, tab in enumerate(pestañas):
        notebook.add(tab, text=nombres[i])
        if nombres[i] == "M2E":
            ventana_dos_archivos(tab, funciones[i])
        else:
            ventana_un_archivo(tab, funciones[i])

    root.mainloop()

if __name__ == '__main__':
    iniciar_app()
