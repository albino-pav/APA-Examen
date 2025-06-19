import struct as st
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd 
from tkinter import messagebox as msg
import ttkbootstrap as tb

# Funciones de APA-T5

def estereo2mono(ficEste, ficMono, canal=2):
    """
    Esta funcion lee el fichero 'ficEste', que contiene una señal estereo, y devuelve una
    señal monofonica en el fichero 'ficMono'. El tipo de señal monofonica depende del argumento
    'canal':
    canal = 0 ==> Se almacena en el canal izquierdo (L).
    canal = 1 ==> Se almacena en el canal derecho (R).
    canal = 2 ==> Se almacena la semisuma (L+R)/2. (Default)
    canal = 3 ==> Se almacena la semidiferencia (L-R)/2.
    """

    with open(ficEste, 'rb') as f:
        header = f.read(44)  # Leer cabecera WAV estándar (44 bytes)
        fmt = header[0:4]
        if fmt != b'RIFF':
            raise ValueError("No es un archivo WAV válido")

        num_channels = st.unpack('<H', header[22:24])[0]
        sample_rate = st.unpack('<I', header[24:28])[0]
        bits_per_sample = st.unpack('<H', header[34:36])[0]
        data_size = st.unpack('<I', header[40:44])[0]
        
        if num_channels != 2 or bits_per_sample != 16:
            raise ValueError("Solo se soportan archivos estéreo PCM de 16 bits")

        raw_data = f.read()
        num_samples = data_size // (bits_per_sample // 8) // 2  

        samples = st.unpack('<' + 'h' * num_samples * 2, raw_data)

        L = samples[::2]
        R = samples[1::2]

        # Generar canal mono
        if canal == 0:
            mono = L
        elif canal == 1:
            mono = R
        elif canal == 2:
            mono = [((l + r) // 2) for l, r in zip(L, R)]
        elif canal == 3:
            mono = [((l - r) // 2) for l, r in zip(L, R)]
        else:
            raise ValueError("Canal no válido. Debe ser 0, 1, 2 o 3")

        mono_bytes = st.pack('<' + 'h' * len(mono), *mono)

        new_data_size = len(mono) * 2
        new_file_size = 36 + new_data_size

        header = bytearray(header)
        header[22:24] = st.pack('<H', 1)  
        header[34:36] = st.pack('<H', 16)  
        header[40:44] = st.pack('<I', new_data_size)  
        header[4:8] = st.pack('<I', new_file_size) 

    with open(ficMono, 'wb') as f_out:
        f_out.write(header)
        f_out.write(mono_bytes)

def mono2estereo(ficIzq, ficDer, ficEste):
    with open(ficIzq, 'rb') as f_izq:
        header_izq = f_izq.read(44)
        fmt = header_izq[0:4]
        if fmt != b'RIFF':
            raise ValueError("ficIzq no es un archivo WAV válido")
        
        num_channels = st.unpack('<H', header_izq[22:24])[0]
        sample_rate = st.unpack('<I', header_izq[24:28])[0]
        bits_per_sample = st.unpack('<H', header_izq[34:36])[0]
        data_size = st.unpack('<I', header_izq[40:44])[0]

        if num_channels != 1 or bits_per_sample != 16:
            raise ValueError("ficIzq debe ser un archivo mono de 16 bits")

        raw_izq = f_izq.read()
        L = st.unpack('<' + 'h' * (len(raw_izq) // 2), raw_izq)

    with open(ficDer, 'rb') as f_der:
        header_der = f_der.read(44)
        num_channels_der = st.unpack('<H', header_der[22:24])[0]
        bits_per_sample_der = st.unpack('<H', header_der[34:36])[0]

        if num_channels_der != 1 or bits_per_sample_der != 16:
            raise ValueError("ficDer debe ser un archivo mono de 16 bits")

        raw_der = f_der.read()
        R = st.unpack('<' + 'h' * (len(raw_der) // 2), raw_der)

    if len(L) != len(R):
        raise ValueError("Los archivos izquierdo y derecho deben tener el mismo número de muestras")

    stereo = []
    for l, r in zip(L, R):
        stereo.append(l)
        stereo.append(r)

    stereo_bytes = st.pack('<' + 'h' * len(stereo), *stereo)

    new_data_size = len(stereo) * 2  # 2 bytes por muestra
    new_file_size = 36 + new_data_size

    header_estereo = bytearray(header_izq)  
    header_estereo[22:24] = st.pack('<H', 2)           
    header_estereo[28:32] = st.pack('<I', sample_rate) 
    byte_rate = sample_rate * 2 * (bits_per_sample // 8)
    block_align = 2 * (bits_per_sample // 8)
    header_estereo[32:34] = st.pack('<H', block_align)
    header_estereo[34:36] = st.pack('<H', bits_per_sample)
    header_estereo[40:44] = st.pack('<I', new_data_size)
    header_estereo[4:8] = st.pack('<I', new_file_size)

    with open(ficEste, 'wb') as f_out:
        f_out.write(header_estereo)
        f_out.write(stereo_bytes)

def codEstereo(ficEste, ficCod):
    """
    Esta funcion lee la señal estereo contenida en 'ficEste' codificada con PCM lineal de
    16 bits, y construye una señal codificada con 32 bits que permita su reproduccion tanto en 
    sistemas monofonicos cono en sistemas estero que lo permitan.
    """

    with open(ficEste, 'rb') as fpEste:
        header = fpEste.read(44)

        if header[0:4] != b'RIFF' or header[8:12] != b'WAVE':
            raise ValueError(f"El fichero {ficEste} no tiene formato WAVE válido")

        num_channels = st.unpack('<H', header[22:24])[0]
        bits_per_sample = st.unpack('<H', header[34:36])[0]
        data_size = st.unpack('<I', header[40:44])[0]

        if num_channels != 2 or bits_per_sample != 16:
            raise ValueError("Se requiere un archivo WAV estéreo de 16 bits")

        raw_data = fpEste.read()
        num_samples = len(raw_data) // 4 

        samples = st.unpack('<' + 'h' * num_samples * 2, raw_data)

        encoded = []

        for i in range(0, len(samples), 2):
            L = samples[i]
            R = samples[i + 1]

            semi_sum = (L + R) // 2
            semi_dif = (L - R) // 2
            semi_sum &= 0xFFFF
            semi_dif &= 0xFFFF
            encoded_sample = (semi_sum << 16) | semi_dif
            encoded.append(encoded_sample)

        new_data_size = len(encoded) * 4
        new_file_size = 36 + new_data_size
        header_c = bytearray(header)
        header_c[22:24] = st.pack('<H', 1)  
        header_c[34:36] = st.pack('<H', 32)  
        header_c[32:34] = st.pack('<H', 4)  
        header_c[28:32] = st.pack('<I', 4 * st.unpack('<I', header[24:28])[0])  # byte rate
        header_c[40:44] = st.pack('<I', new_data_size)
        header_c[4:8] = st.pack('<I', new_file_size)

    # Guardar archivo codificado
    with open(ficCod, 'wb') as fpCod:
        fpCod.write(header_c)
        fpCod.write(st.pack('<' + 'I' * len(encoded), *encoded))


def decEstereo(ficCod, ficEste):
    """
    Esta funcion lee la señal monofonnica de 32 bits contenida en 'ficCod' en la que los 
    16 MSB contienen la semisuma de los canales L y R, y los 16 LSB contienen la semidiferencia
    y escribe en 'ficEste' los dos canales por separado en formato WAVE estereo.
    """

    with open(ficCod, 'rb') as f:
        header = f.read(44)
        fmt = header[0:4]
        if fmt != b'RIFF':
            raise ValueError("ficCod no es un archivo WAV válido")

        num_channels = st.unpack('<H', header[22:24])[0]
        sample_rate = st.unpack('<I', header[24:28])[0]
        bits_per_sample = st.unpack('<H', header[34:36])[0]
        data_size = st.unpack('<I', header[40:44])[0]

        if num_channels != 1 or bits_per_sample != 32:
            raise ValueError("ficCod debe ser un archivo mono de 32 bits")

        raw_data = f.read()
        num_samples = len(raw_data) // 4
        samples_32bit = st.unpack('<' + 'I' * num_samples, raw_data)

        L = []
        R = []

        for sample in samples_32bit:
            # Extraer semisuma (MSB) y semidiferencia (LSB)
            semi_suma = st.unpack('<h', st.pack('<H', (sample >> 16) & 0xFFFF))[0]
            semi_dif  = st.unpack('<h', st.pack('<H', sample & 0xFFFF))[0]

            # Reconstruir L y R
            l = semi_suma + semi_dif
            r = semi_suma - semi_dif
            l = max(min(l, 32767), -32768)
            r = max(min(r, 32767), -32768)

            L.append(l)
            R.append(r)

        stereo = []
        for l, r in zip(L, R):
            stereo.append(l)
            stereo.append(r)
        stereo_bytes = st.pack('<' + 'h' * len(stereo), *stereo)
        new_data_size = len(stereo_bytes)
        new_file_size = 36 + new_data_size
        header_estereo = bytearray(header)
        header_estereo[22:24] = st.pack('<H', 2)  
        header_estereo[34:36] = st.pack('<H', 16) 
        header_estereo[32:34] = st.pack('<H', 2 * 2)  
        header_estereo[28:32] = st.pack('<I', sample_rate * 2 * 2) 
        header_estereo[40:44] = st.pack('<I', new_data_size)
        header_estereo[4:8] = st.pack('<I', new_file_size)

    with open(ficEste, 'wb') as f_out:
        f_out.write(header_estereo)
        f_out.write(stereo_bytes)


# Interfaz gráfica
class EstereoAMonoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.archivoSeleccionado = tk.StringVar()
        self.nombreSalida = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Archivo de entrada:").grid(row=0, column=0, padx=4, pady=(15, 5), sticky="w")
        self.entry_input = ttk.Entry(self, textvariable=self.archivoSeleccionado, width=50)
        self.entry_input.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        ttk.Button(self, text="Seleccionar", command=self.select_file).grid(row=0, column=2, padx=(4, 0))

        ttk.Label(self, text="Nombre del archivo de salida (sin extensión):").grid(row=1, column=0, padx=4, sticky="w")
        ttk.Entry(self, textvariable=self.nombreSalida).grid(row=1, column=1, padx=4, pady=(0, 10), sticky="ew")

        ttk.Button(self, text="Convertir a Mono", command=self.convert).grid(row=2, column=0, columnspan=3, pady=10)

    def select_file(self):
        file = fd.askopenfilename(title="Seleccionar archivo estéreo", initialdir="ficheros")
        if file:
            self.archivoSeleccionado.set(file)

    def convert(self):
        if not self.archivoSeleccionado.get():
            msg.showwarning("Advertencia", "Por favor seleccione un archivo de entrada.")
            return
        if not self.nombreSalida.get():
            msg.showwarning("Advertencia", "Por favor ingrese un nombre para el archivo de salida.")
            return
        try:
            # Establecer el directorio de salida como "ficheros"
            directorio_salida = "ficheros"
            salida = f"{directorio_salida}/{self.nombreSalida.get()}.wav"
            estereo2mono(self.archivoSeleccionado.get(), salida)
            msg.showinfo("Éxito", "Conversión a mono completada.")
        except Exception as e:
            msg.showerror("Error", f"No se pudo completar la conversión:\n{e}")

class MonoAEstereoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.archivoIzquierdo = tk.StringVar()
        self.archivoDerecho = tk.StringVar()
        self.nombreSalida = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Archivo izquierdo:").grid(row=0, column=0, padx=4, pady=(15, 5), sticky="w")
        self.entry_izquierdo = ttk.Entry(self, textvariable=self.archivoIzquierdo, width=50)
        self.entry_izquierdo.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        ttk.Button(self, text="Seleccionar", command=self.select_file_izq).grid(row=0, column=2, padx=(4, 0))

        ttk.Label(self, text="Archivo derecho:").grid(row=1, column=0, padx=4, pady=(5, 5), sticky="w")
        self.entry_derecho = ttk.Entry(self, textvariable=self.archivoDerecho, width=50)
        self.entry_derecho.grid(row=1, column=1, padx=(4, 0), sticky="ew")
        ttk.Button(self, text="Seleccionar", command=self.select_file_der).grid(row=1, column=2, padx=(4, 0))

        ttk.Label(self, text="Nombre del archivo de salida (sin extensión):").grid(row=2, column=0, padx=4, sticky="w")
        ttk.Entry(self, textvariable=self.nombreSalida).grid(row=2, column=1, padx=4, pady=(0, 10), sticky="ew")

        ttk.Button(self, text="Convertir a Estéreo", command=self.convert).grid(row=3, column=0, columnspan=3, pady=10)

    def select_file_izq(self):
        file = fd.askopenfilename(title="Seleccionar archivo mono izquierdo", initialdir="ficheros")
        if file:
            self.archivoIzquierdo.set(file)

    def select_file_der(self):
        file = fd.askopenfilename(title="Seleccionar archivo mono derecho")
        if file:
            self.archivoDerecho.set(file)

    def convert(self):
        if not self.archivoIzquierdo.get():
            msg.showwarning("Advertencia", "Por favor seleccione el archivo mono izquierdo.")
            return
        if not self.archivoDerecho.get():
            msg.showwarning("Advertencia", "Por favor seleccione el archivo mono derecho.")
            return
        if not self.nombreSalida.get():
            msg.showwarning("Advertencia", "Por favor ingrese un nombre para el archivo de salida.")
            return
        try:
            # Establecer el directorio de salida como "ficheros"
            directorio_salida = "ficheros"
            salida = f"{directorio_salida}/{self.nombreSalida.get()}.wav"
            mono2estereo(self.archivoIzquierdo.get(), self.archivoDerecho.get(), salida)
            msg.showinfo("Éxito", "Conversión a estéreo completada.")
        except Exception as e:
            msg.showerror("Error", f"No se pudo completar la conversión:\n{e}")

class CodificaEstereoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.archivoSeleccionado = tk.StringVar()
        self.nombreSalida = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Archivo de entrada:").grid(row=0, column=0, padx=4, pady=(15, 5), sticky="w")
        self.entry_input = ttk.Entry(self, textvariable=self.archivoSeleccionado, width=50)
        self.entry_input.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        ttk.Button(self, text="Seleccionar", command=self.select_file).grid(row=0, column=2, padx=(4, 0))

        ttk.Label(self, text="Nombre del archivo de salida (sin extensión):").grid(row=1, column=0, padx=4, sticky="w")
        ttk.Entry(self, textvariable=self.nombreSalida).grid(row=1, column=1, padx=4, pady=(0, 10), sticky="ew")

        ttk.Button(self, text="Codificar Estéreo", command=self.convert).grid(row=2, column=0, columnspan=3, pady=10)

    def select_file(self):
        file = fd.askopenfilename(title="Seleccionar archivo estéreo para codificar", initialdir="ficheros")
        if file:
            self.archivoSeleccionado.set(file)

    def convert(self):
        if not self.archivoSeleccionado.get():
            msg.showwarning("Advertencia", "Por favor seleccione un archivo de entrada.")
            return
        if not self.nombreSalida.get():
            msg.showwarning("Advertencia", "Por favor ingrese un nombre para el archivo de salida.")
            return
        try:
            # Establecer el directorio de salida como "ficheros"
            directorio_salida = "ficheros"
            salida = f"{directorio_salida}/{self.nombreSalida.get()}.wav"
            codEstereo(self.archivoSeleccionado.get(), salida)
            msg.showinfo("Éxito", "Codificación de estéreo completada.")
        except Exception as e:
            msg.showerror("Error", f"No se pudo completar la codificación:\n{e}")

class DescodificaEstereoTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.archivoSeleccionado = tk.StringVar()
        self.nombreSalida = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Archivo codificado:").grid(row=0, column=0, padx=4, pady=(15, 5), sticky="w")
        self.entry_input = ttk.Entry(self, textvariable=self.archivoSeleccionado, width=50)
        self.entry_input.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        ttk.Button(self, text="Seleccionar", command=self.select_file).grid(row=0, column=2, padx=(4, 0))

        ttk.Label(self, text="Nombre del archivo de salida (sin extensión):").grid(row=1, column=0, padx=4, sticky="w")
        ttk.Entry(self, textvariable=self.nombreSalida).grid(row=1, column=1, padx=4, pady=(0, 10), sticky="ew")

        ttk.Button(self, text="Descodificar Estéreo", command=self.convert).grid(row=2, column=0, columnspan=3, pady=10)

    def select_file(self):
        file = fd.askopenfilename(title="Seleccionar archivo codificado de entrada", initialdir="ficheros")
        if file:
            self.archivoSeleccionado.set(file)

    def convert(self):
        if not self.archivoSeleccionado.get():
            msg.showwarning("Advertencia", "Por favor seleccione un archivo codificado de entrada.")
            return
        if not self.nombreSalida.get():
            msg.showwarning("Advertencia", "Por favor ingrese un nombre para el archivo de salida.")
            return
        try:
            # Establecer el directorio de salida como "ficheros"
            directorio_salida = "ficheros"
            salida = f"{directorio_salida}/{self.nombreSalida.get()}.wav"
            decEstereo(self.archivoSeleccionado.get(), salida)
            msg.showinfo("Éxito", "Descodificación de estéreo completada.")
        except Exception as e:
            msg.showerror("Error", f"No se pudo completar la descodificación:\n{e}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Programa de Manejo de Señales Estéreo")
        self.root.geometry("1000x200")
        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.tab1 = EstereoAMonoTab(self.notebook)
        self.tab2 = MonoAEstereoTab(self.notebook)
        self.tab3 = CodificaEstereoTab(self.notebook)
        self.tab4 = DescodificaEstereoTab(self.notebook)

        self.notebook.add(self.tab1, text="Estéreo a Mono")
        self.notebook.add(self.tab2, text="Mono a Estéreo")
        self.notebook.add(self.tab3, text="Codifica Estéreo")
        self.notebook.add(self.tab4, text="Descodifica Estéreo")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
