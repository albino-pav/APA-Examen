import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
import soundfile as sf
import sounddevice as sd
import numpy as np
import wave
import struct

def write_encoded_wav(filename, data, samplerate):
    # data: numpy int32 array
    byte_data = struct.pack('<' + 'i' * len(data), *data)
    with open(filename, 'wb') as out:
        out.write(struct.pack('<4sI4s', b'RIFF', 36 + len(byte_data), b'WAVE'))
        # Format chunk: PCM(1), mono(1), 32 bits/sample
        out.write(struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, 1, samplerate,
                              samplerate * 4, 4, 32))
        out.write(struct.pack('<4sI', b'data', len(byte_data)))
        out.write(byte_data)

def read_encoded_wav(filename):
    with open(filename, 'rb') as f:
        # Read header chunks (simplified)
        riff = f.read(12)
        fmt = f.read(24)
        data_header = f.read(8)
        # Extract sample rate and data size
        samplerate = struct.unpack('<I', fmt[12:16])[0]
        datasize = struct.unpack('<I', data_header[4:8])[0]
        data = f.read(datasize)
        samples = struct.unpack('<' + 'i' * (datasize // 4), data)
        return np.array(samples, dtype=np.int32), samplerate
    
class Audio:
    def __init__(self):
        self.audio = None  # numpy array
        self.fm = None     # sample rate
        self.params = None # wave params (if loaded with wave module)
        self.nchannels = None

    def cargar(self, ruta):
        with wave.open(ruta, 'rb') as wf:
            self.params = wf.getparams()
            self.nchannels = self.params.nchannels
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            if self.nchannels == 2:
                audio = audio.reshape(-1, 2)  # convert to 2D array: (num_samples, 2)
            self.audio = audio
            self.fm = wf.getframerate()

    def set(self, audio, fm):
        self.audio = audio
        self.fm = fm
        self.params = None
        self.nchannels = None

    def get(self):
        return self.audio, self.fm

def botonSeleccionarArchivoCodificado(parent, varCodificado):
    varMensaje = tk.StringVar(parent, 'Selecciona una señal de audio')

    def seleccionarArchivoCodificado():
        ruta = askopenfilename(filetypes=[("Archivo codificado", "*.bin")])
        if ruta:
            with open(ruta, 'rb') as f:
                varMensaje.set(ruta)
                contenido = f.read()
                varCodificado.set(contenido.hex())

    ttk.Button(
        parent,
        textvariable=varMensaje,
        command=seleccionarArchivoCodificado
    ).pack()


def selecAudio(raiz, varAudio):
    varMensaje = tk.StringVar(raiz, 'Selecciona una señal de audio')

    def abrirArchivo():
        fichero = askopenfilename(
            title='Selecciona un fichero de audio',
            filetypes=(('Fichero de audio', '.mp3 .wav'), ('Todos los archivos', '*.*'))
        )
        if fichero:
            varMensaje.set(fichero)
            senyal, fm = sf.read(fichero)
            varAudio.set(senyal, fm)
            varAudio.cargar(fichero)

    boton = ttk.Button(raiz, textvariable=varMensaje, command=abrirArchivo)
    boton.pack()

def reproduce(varAudio, varVolumen):
    audio, fm = varAudio.get()
    if audio is not None:
        sd.play(audio * varVolumen.get(), fm, blocking=False)

def reproduceParaSal(raiz, varAudio, varVolumen):
    marco = ttk.Frame(raiz)
    marco.pack(side=tk.BOTTOM)

    ttk.Button(marco, text='Play', command=lambda: reproduce(varAudio, varVolumen)).pack(side=tk.LEFT)
    ttk.Button(marco, text='Stop', command=sd.stop).pack(side=tk.LEFT)
    ttk.Button(marco, text='Quit', command=raiz.quit).pack(side=tk.LEFT)

def volumen(raiz, varVolumen):
    marco = ttk.LabelFrame(raiz, text='Volumen')
    marco.pack()
    ttk.Scale(marco, from_=0, to=1, length=200, variable=varVolumen).pack()

def EstereoMono(varAudio, varOutput, canal=2):

    audio, fm = varAudio.get()
    if audio is None:
        return  # No input audio

    # Confirm it's stereo
    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("La señal de entrada no es estéreo.")

    L = audio[:, 0]
    R = audio[:, 1]

    if canal == 0:
        mono = L
    elif canal == 1:
        mono = R
    elif canal == 2:
        mono = (L + R) / 2
    elif canal == 3:
        mono = (L - R) / 2
    else:
        raise ValueError("Canal debe ser 0, 1, 2 o 3.")

    # Save mono as 2D array for sounddevice compatibility
    mono = mono.reshape(-1, 1)
    varOutput.set(mono, fm)
    messagebox.showinfo("Cambio", "Archivo Modificado correctamente.")

def MonoEstereo(varAudio, varOutput):

    audio, fm = varAudio.get()
    if audio is None:
        return  # No input audio

    # If already stereo, just pass through or raise error
    if audio.ndim == 2 and audio.shape[1] == 2:
        raise ValueError("La señal ya es estéreo.")

    # Make sure audio is 1D for mono
    if audio.ndim == 2 and audio.shape[1] == 1:
        audio = audio[:, 0]

    # Duplicate mono to stereo by stacking channels
    stereo = np.column_stack((audio, audio))

    varOutput.set(stereo, fm)
    messagebox.showinfo("Cambio", "Archivo Modificado correctamente.")

def CodEstereo(varAudio, varCodificado):
    if varAudio is None or varAudio.audio is None or varAudio.params is None:
        messagebox.showerror("Error", "No audio cargado.")
        return

    if varAudio.params.nchannels != 2:
        messagebox.showerror("Error", "El archivo debe ser estéreo (2 canales).")
        return

    # varAudio.audio is expected to be a 1D or 2D numpy array
    # If 1D interleaved stereo, reshape it to Nx2 for easier processing
    audio = varAudio.audio
    if audio.ndim == 1 and varAudio.nchannels == 2:
        audio = audio.reshape(-1, 2)

    codificats = []
    for l, r in audio:
        sum_lr = int((l + r).item())
        diff_lr = int((l - r).item())

        # Saturate sum_lr to 16-bit signed integer range
        sum_lr = max(min(sum_lr, 32767), -32768)

        # Saturate diff_lr to 16-bit signed integer range as well
        diff_lr = max(min(diff_lr, 32767), -32768)

        # Combine into a 32-bit word: sum_lr in high 16 bits, diff_lr in low 16 bits
        combined = (sum_lr << 16) | (diff_lr & 0xFFFF)
        codificats.append(combined)

    # Pack into bytes (little endian, 32-bit signed integers)
    byte_data = struct.pack('<' + 'i' * len(codificats), *codificats)
    varCodificado.set(byte_data.hex())
    messagebox.showinfo("Codificación", "Codificación completada correctamente.")

def DescoEstereo(varCodificado, varOutput):
    coded_str = varCodificado.get()
    print("Decode called. Encoded data length:", len(coded_str))
    if not coded_str:
        messagebox.showwarning("Advertencia", "No hay datos codificados cargados.")
        return
    
    try:
        byte_data = bytes.fromhex(coded_str)
        print("Byte data length:", len(byte_data))
        codificats = struct.unpack('<' + 'i' * (len(byte_data) // 4), byte_data)
        print("Number of integers unpacked:", len(codificats))

        L = []
        R = []

        for x in codificats:
            # Extract sum and diff from 32-bit packed integer
            sum_lr = (x >> 16) & 0xFFFF
            diff_lr = x & 0xFFFF

            # Convert both to signed 16-bit integers
            if sum_lr >= 0x8000:
                sum_lr -= 0x10000
            if diff_lr >= 0x8000:
                diff_lr -= 0x10000

            # Recover original L and R
            l = (sum_lr + diff_lr) // 2
            r = (sum_lr - diff_lr) // 2

            # Saturate back to int16 just in case
            l = max(min(l, 32767), -32768)
            r = max(min(r, 32767), -32768)

            L.append(l)
            R.append(r)

        # Interleave
        intercalado = np.empty(len(L) + len(R), dtype=np.int16)
        intercalado[::2] = L
        intercalado[1::2] = R

        varOutput.audio = intercalado
        varOutput.sample_rate = 44100
        varOutput.nchannels = 2
        print("Decoding completed, audio length:", len(varOutput.audio))
        messagebox.showinfo("Decodificación", "Decodificación completada correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Error en la decodificación: {e}")
        print("Exception in decode:", e)

def botonExtra1(raiz, varAudio, varOutput, varCodificado2, num):
    def repartir(varAudio, varOutput, varCodificado2, num):
        if num in (1, 2, 3):  # operations that require audio input
            if varAudio is None or varAudio.audio is None:
                messagebox.showerror("Error", "No hay audio cargado.")
                return
            if num == 1:
                EstereoMono(varAudio, varOutput)
            elif num == 2:
                MonoEstereo(varAudio, varOutput)
            elif num == 3:
                CodEstereo(varAudio, varCodificado2)
        elif num == 4:
            DescoEstereo(varCodificado2, varOutput)
        else:
            messagebox.showerror("Error", "Operación desconocida.")



    titulos = {
        1: 'Modificació',
        2: 'Modificació',
        3: 'Codificar',
        4: 'Descodificar'
    }
    texto_boton = titulos[num]

    ttk.Button(
        raiz,
        text=texto_boton,
        command=lambda: repartir(varAudio, varOutput, varCodificado2, num)
    ).pack(side=tk.LEFT, padx=10)

def botonGuardarArchivoCodificado(parent, varCodificado):
    def guardar():
        if not varCodificado.get():
            messagebox.showwarning("Advertencia", "No hay datos codificados para guardar.")
            return
        
        ruta = asksaveasfilename(defaultextension=".bin", filetypes=[("Archivo codificado", "*.bin")])
        if ruta:
            with open(ruta, 'wb') as f:
                f.write(bytes.fromhex(varCodificado.get()))
            messagebox.showinfo("Guardado", "Archivo codificado guardado correctamente.")

    ttk.Button(parent, text="Guardar Archivo Codificado", command=guardar).pack(side=tk.LEFT)



def botonExtra2(raiz, varOutput):
    def guardarAudio():
        audio, fm = varOutput.get()
        if audio is not None:
            archivo = asksaveasfilename(
                title='Guardar archivo de audio',
                defaultextension='.wav',
                filetypes=(('Archivo WAV', '*.wav'), ('Todos los archivos', '*.*'))
            )
            if archivo:
                sf.write(archivo, audio, fm)
                print(f'Audio guardado en: {archivo}')
                messagebox.showinfo("Guardado", f"Audio guardado en: {archivo}")
        else:
            print("No hay audio para guardar.")
            messagebox.showinfo("Guardado", "No hay audio para guardar.")

    ttk.Button(raiz, text='Guardar Audio', command=guardarAudio).pack(side=tk.LEFT)

# === Audio player layout per tab ===
def crearTabContenido(tab, num):
    if num == 1:
        varAudio0 = Audio()
        varOutput0 = Audio()
        varVolumen0 = tk.DoubleVar(tab, 0.6)
        varCodificado0 = None

        selecAudio(tab, varAudio0)
        marcoBotonesExtra = ttk.Frame(tab)
        marcoBotonesExtra.pack(pady=10)
        botonExtra1(marcoBotonesExtra, varAudio0, varOutput0, varCodificado0, num)
        botonExtra2(marcoBotonesExtra, varOutput0)
        volumen(tab, varVolumen0)
        reproduceParaSal(tab, varAudio0, varVolumen0)

    elif num == 2:
        varAudio1 = Audio()
        varOutput1 = Audio()
        varVolumen1 = tk.DoubleVar(tab, 0.6)
        varCodificado1 = None

        selecAudio(tab, varAudio1)
        marcoBotonesExtra = ttk.Frame(tab)
        marcoBotonesExtra.pack(pady=10)
        botonExtra1(marcoBotonesExtra, varAudio1, varOutput1, varCodificado1, num)
        botonExtra2(marcoBotonesExtra, varOutput1)
        volumen(tab, varVolumen1)
        reproduceParaSal(tab, varAudio1, varVolumen1)

    elif num == 3:
        varAudio2 = Audio()
        varCodificado2 = tk.StringVar()
        varVolumen2 = tk.DoubleVar(tab, 0.6)
        varOutput2 = None

        selecAudio(tab, varAudio2)
        marcoBotonesExtra = ttk.Frame(tab)
        marcoBotonesExtra.pack(pady=10)
        botonExtra1(marcoBotonesExtra, varAudio2, varOutput2, varCodificado2, num)
        botonGuardarArchivoCodificado(marcoBotonesExtra, varCodificado2)
        volumen(tab, varVolumen2)
        reproduceParaSal(tab, varAudio2, varVolumen2)

    elif num == 4:
        varAudio3 = None
        varCodificado3 = tk.StringVar()
        varOutput3 = Audio()
        varVolumen3 = tk.DoubleVar(tab, 0.6)

        botonSeleccionarArchivoCodificado(tab, varCodificado3)
        marcoBotonesExtra = ttk.Frame(tab)
        marcoBotonesExtra.pack(pady=10)
        botonExtra1(marcoBotonesExtra, varAudio3, varOutput3, varCodificado3, num)
        botonExtra2(marcoBotonesExtra, varOutput3)
        volumen(tab, varVolumen3)
        reproduceParaSal(tab, varOutput3, varVolumen3)

# === Main app ===
def main():
    root = tk.Tk()
    root.title("Notebook con Reproductores de Audio")
    root.geometry("600x300")
    root.configure(background='Lavender Blush')
    ttk.Style().configure('.', font=("Arial", 14), background='Lavender Blush', padding=8)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    tab_tittle = {
        1: 'Estéreo a Mono',
        2: 'Mono a Estéreo',
        3: 'Codifica Estéreo',
        4: 'Descodifica Estéreo'
    }

    for i in range(4):
        tab = ttk.Frame(notebook)
        text_tab = tab_tittle[i+1]
        notebook.add(tab, text=text_tab)
        crearTabContenido(tab, num=i + 1)  # Pass tab number

    root.mainloop()

if __name__ == '__main__':
    main()