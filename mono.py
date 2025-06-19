import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from playsound import playsound
import wave
import numpy as np
import ttkbootstrap as tb

def stereo_to_mono(input_file, output_file):
    with wave.open(input_file, 'rb') as wav_in:
        params = wav_in.getparams()
        if params.nchannels != 2:
            raise ValueError("El fitxer d'entrada no és estèreo.")

        frames = wav_in.readframes(params.nframes)
        audio_data = np.frombuffer(frames, dtype=np.int16)
        left = audio_data[0::2]
        right = audio_data[1::2]
        mono = ((left.astype(np.int32) + right.astype(np.int32)) // 2).astype(np.int16)

    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setnchannels(1)
        wav_out.setsampwidth(params.sampwidth)
        wav_out.setframerate(params.framerate)
        wav_out.writeframes(mono.tobytes())

def mono_to_stereo(input_file, output_file):
    with wave.open(input_file, 'rb') as wav_in:
        params = wav_in.getparams()
        if params.nchannels != 1:
            raise ValueError("El fitxer d'entrada no és mono.")

        frames = wav_in.readframes(params.nframes)
        mono = np.frombuffer(frames, dtype=np.int16)
        stereo = np.repeat(mono, 2)

    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setnchannels(2)
        wav_out.setsampwidth(params.sampwidth)
        wav_out.setframerate(params.framerate)
        wav_out.writeframes(stereo.tobytes())

def codifica_estereo(input_file1, input_file2, output_file):
    with wave.open(input_file1, 'rb') as wav1, wave.open(input_file2, 'rb') as wav2:
        params1 = wav1.getparams()
        params2 = wav2.getparams()
        if params1.nchannels != 1 or params2.nchannels != 1:
            raise ValueError("Els fitxers d'entrada han de ser mono.")
        if params1.framerate != params2.framerate:
            raise ValueError("Els dos fitxers han de tenir la mateixa freqüència de mostreig.")

        frames1 = wav1.readframes(params1.nframes)
        frames2 = wav2.readframes(params2.nframes)
        mono1 = np.frombuffer(frames1, dtype=np.int16)
        mono2 = np.frombuffer(frames2, dtype=np.int16)

        length = min(len(mono1), len(mono2))
        stereo = np.empty(2 * length, dtype=np.int16)
        stereo[0::2] = mono1[:length]
        stereo[1::2] = mono2[:length]

    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setnchannels(2)
        wav_out.setsampwidth(params1.sampwidth)
        wav_out.setframerate(params1.framerate)
        wav_out.writeframes(stereo.tobytes())

def descodifica_estereo(input_file, output_file1, output_file2):
    with wave.open(input_file, 'rb') as wav_in:
        params = wav_in.getparams()
        if params.nchannels != 2:
            raise ValueError("El fitxer d'entrada no és estèreo.")

        frames = wav_in.readframes(params.nframes)
        stereo = np.frombuffer(frames, dtype=np.int16)
        left = stereo[0::2]
        right = stereo[1::2]

    with wave.open(output_file1, 'wb') as wav_out1:
        wav_out1.setnchannels(1)
        wav_out1.setsampwidth(params.sampwidth)
        wav_out1.setframerate(params.framerate)
        wav_out1.writeframes(left.tobytes())

    with wave.open(output_file2, 'wb') as wav_out2:
        wav_out2.setnchannels(1)
        wav_out2.setsampwidth(params.sampwidth)
        wav_out2.setframerate(params.framerate)
        wav_out2.writeframes(right.tobytes())

# Interfície gràfica
app = tb.Window(themename="flatly")
app.title("Conversor d'àudio estèreo/mono")
app.geometry("640x480")

notebook = ttk.Notebook(app)
notebook.pack(fill="both", expand=True)

# Pestanya 1: Estèreo a Mono
frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Estèreo a Mono")

entrada_path = tk.StringVar()
sortida_path = tk.StringVar()

ttk.Label(frame1, text="Fitxer d'entrada (estèreo):").pack(pady=5)
ttk.Entry(frame1, textvariable=entrada_path, width=60).pack()
ttk.Button(frame1, text="Selecciona", command=lambda: entrada_path.set(filedialog.askopenfilename(filetypes=[("WAV", "*.wav")]))).pack()

ttk.Button(frame1, text="Escoltar entrada", command=lambda: playsound(entrada_path.get()), bootstyle="info").pack(pady=5)

ttk.Label(frame1, text="Fitxer de sortida (mono):").pack(pady=5)
ttk.Entry(frame1, textvariable=sortida_path, width=60).pack()
ttk.Button(frame1, text="Desa com...", command=lambda: sortida_path.set(filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")]))).pack()

ttk.Button(frame1, text="Convertir", command=lambda: stereo_to_mono(entrada_path.get(), sortida_path.get()), bootstyle="success").pack(pady=10)
ttk.Button(frame1, text="Escoltar sortida", command=lambda: playsound(sortida_path.get()), bootstyle="info").pack()

#Pestanya 2: Mono a Estèreo 
frame2 = ttk.Frame(notebook)
notebook.add(frame2, text="Mono a Estèreo")

mono_path = tk.StringVar()
estereo_out_path = tk.StringVar()

ttk.Label(frame2, text="Fitxer d'entrada (mono):").pack(pady=5)
ttk.Entry(frame2, textvariable=mono_path, width=60).pack()
ttk.Button(frame2, text="Selecciona", command=lambda: mono_path.set(filedialog.askopenfilename(filetypes=[("WAV", "*.wav")]))).pack()
ttk.Button(frame2, text="Escoltar entrada", command=lambda: playsound(mono_path.get()), bootstyle="info").pack(pady=5)

ttk.Label(frame2, text="Fitxer de sortida (estèreo):").pack(pady=5)
ttk.Entry(frame2, textvariable=estereo_out_path, width=60).pack()
ttk.Button(frame2, text="Desa com...", command=lambda: estereo_out_path.set(filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")]))).pack()

ttk.Button(frame2, text="Convertir", command=lambda: mono_to_stereo(mono_path.get(), estereo_out_path.get()), bootstyle="success").pack(pady=10)
ttk.Button(frame2, text="Escoltar sortida", command=lambda: playsound(estereo_out_path.get()), bootstyle="info").pack()

#Pestanya 3: Codifica Estèreo 
frame3 = ttk.Frame(notebook)
notebook.add(frame3, text="Codifica Estèreo")

mono1_path = tk.StringVar()
mono2_path = tk.StringVar()
estereo_path = tk.StringVar()

ttk.Label(frame3, text="Fitxer mono esquerra:").pack(pady=5)
ttk.Entry(frame3, textvariable=mono1_path, width=60).pack()
ttk.Button(frame3, text="Selecciona", command=lambda: mono1_path.set(filedialog.askopenfilename(filetypes=[("WAV", "*.wav")]))).pack()
ttk.Button(frame3, text="Escoltar", command=lambda: playsound(mono1_path.get()), bootstyle="info").pack(pady=2)

ttk.Label(frame3, text="Fitxer mono dreta:").pack(pady=5)
ttk.Entry(frame3, textvariable=mono2_path, width=60).pack()
ttk.Button(frame3, text="Selecciona", command=lambda: mono2_path.set(filedialog.askopenfilename(filetypes=[("WAV", "*.wav")]))).pack()
ttk.Button(frame3, text="Escoltar", command=lambda: playsound(mono2_path.get()), bootstyle="info").pack(pady=2)

ttk.Label(frame3, text="Fitxer de sortida estèreo:").pack(pady=5)
ttk.Entry(frame3, textvariable=estereo_path, width=60).pack()
ttk.Button(frame3, text="Desa com...", command=lambda: estereo_path.set(filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")]))).pack()

ttk.Button(frame3, text="Codificar", command=lambda: codifica_estereo(mono1_path.get(), mono2_path.get(), estereo_path.get()), bootstyle="success").pack(pady=10)
ttk.Button(frame3, text="Escoltar sortida", command=lambda: playsound(estereo_path.get()), bootstyle="info").pack()

#Pestanya 4: Descodifica Estèreo 
frame4 = ttk.Frame(notebook)
notebook.add(frame4, text="Descodifica Estèreo")

entrada_estereo = tk.StringVar()
sortida_esq = tk.StringVar()
sortida_dret = tk.StringVar()

ttk.Label(frame4, text="Fitxer d'entrada estèreo:").pack(pady=5)
ttk.Entry(frame4, textvariable=entrada_estereo, width=60).pack()
ttk.Button(frame4, text="Selecciona", command=lambda: entrada_estereo.set(filedialog.askopenfilename(filetypes=[("WAV", "*.wav")]))).pack()
ttk.Button(frame4, text="Escoltar", command=lambda: playsound(entrada_estereo.get()), bootstyle="info").pack(pady=5)

ttk.Label(frame4, text="Fitxer sortida esquerra:").pack(pady=5)
ttk.Entry(frame4, textvariable=sortida_esq, width=60).pack()
ttk.Button(frame4, text="Desa com...", command=lambda: sortida_esq.set(filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")]))).pack()

ttk.Label(frame4, text="Fitxer sortida dreta:").pack(pady=5)
ttk.Entry(frame4, textvariable=sortida_dret, width=60).pack()
ttk.Button(frame4, text="Desa com...", command=lambda: sortida_dret.set(filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")]))).pack()

ttk.Button(frame4, text="Descodificar", command=lambda: descodifica_estereo(entrada_estereo.get(), sortida_esq.get(), sortida_dret.get()), bootstyle="success").pack(pady=10)
ttk.Button(frame4, text="Escoltar esquerra", command=lambda: playsound(sortida_esq.get()), bootstyle="info").pack()
ttk.Button(frame4, text="Escoltar dreta", command=lambda: playsound(sortida_dret.get()), bootstyle="info").pack()

# Executar la finestra
app.mainloop()
