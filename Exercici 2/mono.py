import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pyaudio
import numpy as np 
import wave
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import stereo

class ReproductorAudio:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.reproduciendo = False

    def reproducir(self, archivo, actualizar_grafico=None):
        if self.reproduciendo:
            self.detener()

        def hilo_reproduccion():
            try:
                with wave.open(archivo, 'rb') as wav:
                    self.stream = self.pa.open(
                        format=self.pa.get_format_from_width(wav.getsampwidth()),
                        channels=wav.getnchannels(),
                        rate=wav.getframerate(),
                        output=True
                    )
                    self.reproduciendo = True
                    datos = wav.readframes(1024)
                    while datos and self.reproduciendo:
                        self.stream.write(datos)
                        if actualizar_grafico:
                            actualizar_grafico(datos)
                        datos = wav.readframes(1024)
                    self.detener()
            except Exception as e:
                messagebox.showerror("Error", f"Error al reproducir: {str(e)}")
                self.detener()

        threading.Thread(target=hilo_reproduccion, daemon=True).start()

    def detener(self):
        self.reproduciendo = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

class GraficoOnda:
    def __init__(self, padre, titulo):
        self.frame = ttk.Frame(padre)
        self.figura = Figure(figsize=(5, 2), dpi=80)
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        ttk.Label(self.frame, text=titulo).pack()
        self.limpiar()

    def limpiar(self):
        self.ax.clear()
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def actualizar(self, datos):
        self.ax.clear()
        if datos:
            audio = np.frombuffer(datos, dtype=np.int16)
            self.ax.plot(audio)
        self.canvas.draw()

class ConversorAudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor Audio")
        self.player = ReproductorAudio()
        self.archivo_actual = None
        self.datos_entrada = None
        self.datos_salida = None
        
        self.configurar_interfaz()
        
    def configurar_interfaz(self):
        self.notebook = ttk.Notebook(self.root)
        
        tab1 = ttk.Frame(self.notebook)
        self.crear_pestana_conversion(tab1, "Estéreo", "Mono", self.estereo_a_mono)
        
        tab2 = ttk.Frame(self.notebook)
        self.crear_pestana_conversion(tab2, "Mono", "Estéreo", self.mono_a_estereo)
        
        self.notebook.add(tab1, text="Estéreo → Mono")
        self.notebook.add(tab2, text="Mono → Estéreo")
        self.notebook.pack(expand=True, fill='both')

    def crear_pestana_conversion(self, tab, entrada, salida, funcion_conversion):
        frame_graficos = ttk.Frame(tab)
        frame_graficos.pack(fill='both', expand=True)
        
        self.grafico_entrada = GraficoOnda(frame_graficos, f"Entrada {entrada}")
        self.grafico_entrada.frame.pack(side='left', fill='both', expand=True)
        
        self.grafico_salida = GraficoOnda(frame_graficos, f"Salida {salida}")
        self.grafico_salida.frame.pack(side='left', fill='both', expand=True)
        
        frame_controles = ttk.Frame(tab)
        frame_controles.pack(fill='x')
        
        ttk.Button(frame_controles, text=f"Abrir {entrada}", 
                 command=lambda: self.cargar_archivo(entrada)).pack(side='left')
        
        ttk.Button(frame_controles, text="Reproducir entrada",
                 command=self.reproducir_entrada).pack(side='left')
        
        ttk.Button(frame_controles, text=f"Convertir a {salida}",
                 command=funcion_conversion).pack(side='left')
        
        ttk.Button(frame_controles, text="Reproducir salida",
                 command=self.reproducir_salida).pack(side='left')
        
        ttk.Button(frame_controles, text="Guardar salida",
                 command=self.guardar_salida).pack(side='left')

    def cargar_archivo(self, tipo):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos WAV", "*.wav")])
        if archivo:
            self.archivo_actual = archivo
            try:
                with wave.open(archivo, 'rb') as wav:
                    if (tipo == "Estéreo" and wav.getnchannels() != 2) or (tipo == "Mono" and wav.getnchannels() != 1):
                        messagebox.showerror("Error", f"El archivo no es {tipo}")
                        return
                    self.datos_entrada = wav.readframes(wav.getnframes())
                    self.grafico_entrada.actualizar(self.datos_entrada)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar: {str(e)}")

    def reproducir_entrada(self):
        if self.archivo_actual:
            self.player.reproducir(self.archivo_actual, self.grafico_entrada.actualizar)

    def reproducir_salida(self):
        if self.datos_salida is None:
            messagebox.showerror("Error", "No hay datos de salida")
            return
            
        temp_file = "temp.wav"
        try:
            with wave.open(temp_file, 'wb') as wav:
                wav.setnchannels(1 if "Mono" in self.grafico_salida.frame.winfo_children()[1].cget("text") else 2)
                wav.setsampwidth(2)
                wav.setframerate(44100)
                wav.writeframes(self.datos_salida)
            self.player.reproducir(temp_file, self.grafico_salida.actualizar)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def guardar_salida(self):
        if self.datos_salida is None:
            messagebox.showerror("Error", "No hay datos para guardar")
            return
            
        archivo = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if archivo:
            try:
                with wave.open(archivo, 'wb') as wav:
                    wav.setnchannels(1 if "Mono" in self.grafico_salida.frame.winfo_children()[1].cget("text") else 2)
                    wav.setsampwidth(2)
                    wav.setframerate(44100)
                    wav.writeframes(self.datos_salida)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def estereo_a_mono(self):
        if not self.archivo_actual:
            messagebox.showerror("Error", "No hay archivo cargado")
            return
            
        try:
            audio = np.frombuffer(self.datos_entrada, dtype=np.int16)
            estereo = audio.reshape(-1, 2)
            mono = stereo.ster2mono(estereo[:, 0], estereo[:, 1], 'center')
            self.datos_salida = mono.astype(np.int16).tobytes()
            self.grafico_salida.actualizar(self.datos_salida)
        except Exception as e:
            messagebox.showerror("Error", f"Error en conversión: {str(e)}")

    def mono_a_estereo(self):
        if not self.archivo_actual:
            messagebox.showerror("Error", "No hay archivo cargado")
            return
            
        try:
            mono = np.frombuffer(self.datos_entrada, dtype=np.int16)
            izq, der = stereo.mono2stereo(mono, 1.0, 1.0)
            estereo = np.column_stack((izq, der)).flatten()
            self.datos_salida = estereo.astype(np.int16).tobytes()
            self.grafico_salida.actualizar(self.datos_salida)
        except Exception as e:
            messagebox.showerror("Error", f"Error en conversión: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x500")
    app = ConversorAudio(root)
    root.mainloop()