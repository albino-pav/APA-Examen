import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import soundfile as sf
import sounddevice as sd
import threading
import time
import estereo as stereo

class MonoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Programa de Maneig de Senyals Estèreo i Mono")
        self.style = ttk.Style(theme='cosmo')
        
        # Variables de control de audio
        self.playing = False
        self.should_stop = False
        self.current_stream = None
        self.current_playing = None
        
        # Variables de archivos
        self.input_file = ""
        self.output_file = ""
        self.input_data = None
        self.output_data = None
        self.fs = 44100
        
        # Variables de opciones
        self.canal_sel = tk.IntVar(value=2)  # 0:L, 1:R, 2:(L+R)/2, 3:(L-R)/2
        self.input_file_L = ""
        self.input_file_R = ""
        
        # Crear interfaz
        self.notebook = ttk.Notebook(root, bootstyle='info')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_estereo_mono_tab()
        self.create_mono_estereo_tab()
        self.create_codifica_tab()
        self.create_descodifica_tab()
        
        self.progress = ttk.Progressbar(root, mode='determinate', bootstyle='success striped')
        
        self.graph_frame = ttk.Frame(root)
        self.graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.create_global_waveform_frames()
        
    def create_global_waveform_frames(self):
        # Frame principal pels gràfics
        frame_graphs = ttk.Frame(self.graph_frame)
        frame_graphs.pack(fill='both', expand=True)
        
        # Gràfic d'entrada
        frame_input_graph = ttk.LabelFrame(frame_graphs, text="Senyal d'entrada", bootstyle='info')
        frame_input_graph.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.fig_input = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax_input = self.fig_input.add_subplot(111)
        self.ax_input.grid(True, linestyle='--', alpha=0.7)
        self.canvas_input = FigureCanvasTkAgg(self.fig_input, master=frame_input_graph)
        self.canvas_input.get_tk_widget().pack(fill='both', expand=True)
        
        btn_frame = ttk.Frame(frame_input_graph)
        btn_frame.pack(fill='x', pady=5)
        
        self.play_input_btn = ttk.Button(btn_frame, text="▶ Escoltar entrada", 
                                       command=lambda: self.play_audio('input'),
                                       bootstyle='success')
        self.play_input_btn.pack(side='left', padx=2, expand=True, fill='x')
        
        self.stop_input_btn = ttk.Button(btn_frame, text="⏹ Aturar", 
                                       command=self.stop_audio,
                                       bootstyle='danger')
        self.stop_input_btn.pack(side='left', padx=2, expand=True, fill='x')
        self.stop_input_btn.config(state='disabled')
        
        # Gràfic de sortida
        frame_output_graph = ttk.LabelFrame(frame_graphs, text="Senyal de sortida", bootstyle='info')
        frame_output_graph.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.fig_output = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax_output = self.fig_output.add_subplot(111)
        self.ax_output.grid(True, linestyle='--', alpha=0.7)
        self.canvas_output = FigureCanvasTkAgg(self.fig_output, master=frame_output_graph)
        self.canvas_output.get_tk_widget().pack(fill='both', expand=True)
        
        btn_frame_out = ttk.Frame(frame_output_graph)
        btn_frame_out.pack(fill='x', pady=5)
        
        self.play_output_btn = ttk.Button(btn_frame_out, text="▶ Escoltar sortida", 
                                        command=lambda: self.play_audio('output'),
                                        bootstyle='success')
        self.play_output_btn.pack(side='left', padx=2, expand=True, fill='x')
        
        self.stop_output_btn = ttk.Button(btn_frame_out, text="⏹ Aturar", 
                                        command=self.stop_audio,
                                        bootstyle='danger')
        self.stop_output_btn.pack(side='left', padx=2, expand=True, fill='x')
        self.stop_output_btn.config(state='disabled')
    
    def create_estereo_mono_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Estèreo a Mono")
        
        frame_input = ttk.LabelFrame(tab, text="Entrada", bootstyle='info')
        frame_input.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_input, text="Seleccionar arxiu estèreo", 
                 command=lambda: self.load_file('estereo'),
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
        
        self.input_info = ScrolledText(frame_input, height=4, state='disabled')
        self.input_info.pack(fill='x', padx=5, pady=5)
        
        frame_op = ttk.LabelFrame(tab, text="Operació", bootstyle='info')
        frame_op.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        # Opcions de canal
        ttk.Label(frame_op, text="Selecciona el canal:").pack(pady=(0, 5))
        
        frame_radios = ttk.Frame(frame_op)
        frame_radios.pack(fill='x')
        
        ttk.Radiobutton(frame_radios, text="Canal Esquerre (L)", variable=self.canal_sel, value=0).pack(side='left', padx=5)
        ttk.Radiobutton(frame_radios, text="Canal Dret (R)", variable=self.canal_sel, value=1).pack(side='left', padx=5)
        
        frame_radios2 = ttk.Frame(frame_op)
        frame_radios2.pack(fill='x')
        
        ttk.Radiobutton(frame_radios2, text="Semisuma (L+R)/2", variable=self.canal_sel, value=2).pack(side='left', padx=5)
        ttk.Radiobutton(frame_radios2, text="Semidiferència (L-R)/2", variable=self.canal_sel, value=3).pack(side='left', padx=5)
        
        ttk.Button(frame_op, text="Convertir a Mono", 
                 command=self.convertir_estereo_mono,
                 bootstyle='success').pack(pady=5, padx=5, fill='x')
        
        frame_output = ttk.LabelFrame(tab, text="Sortida", bootstyle='info')
        frame_output.pack(fill='both', expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_output, text="Guardar arxiu mono", 
                 command=self.save_file,
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
    
    def create_mono_estereo_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mono a Estèreo")
        
        frame_input = ttk.LabelFrame(tab, text="Entrada", bootstyle='info')
        frame_input.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        # Frame per als dos canals
        frame_canals = ttk.Frame(frame_input)
        frame_canals.pack(fill='x', pady=5)
        
        ttk.Button(frame_canals, text="Seleccionar canal esquerre (L)", 
                 command=lambda: self.select_mono_file('L'),
                 bootstyle='primary').pack(side='left', expand=True, fill='x', padx=2)
        
        ttk.Button(frame_canals, text="Seleccionar canal dret (R)", 
                 command=lambda: self.select_mono_file('R'),
                 bootstyle='primary').pack(side='left', expand=True, fill='x', padx=2)
        
        self.input_info_mono = ScrolledText(frame_input, height=4, state='disabled')
        self.input_info_mono.pack(fill='x', padx=5, pady=5)
        
        frame_op = ttk.LabelFrame(tab, text="Operació", bootstyle='info')
        frame_op.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_op, text="Convertir a Estèreo", 
                 command=self.convertir_mono_estereo,
                 bootstyle='success').pack(pady=5, padx=5, fill='x')
        
        frame_output = ttk.LabelFrame(tab, text="Sortida", bootstyle='info')
        frame_output.pack(fill='both', expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_output, text="Guardar arxiu estèreo", 
                 command=self.save_file,
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
    
    def create_codifica_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Codifica Estèreo")
        
        frame_input = ttk.LabelFrame(tab, text="Entrada", bootstyle='info')
        frame_input.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_input, text="Seleccionar arxiu estèreo", 
                 command=lambda: self.load_file('codifica'),
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
        
        self.input_info_cod = ScrolledText(frame_input, height=4, state='disabled')
        self.input_info_cod.pack(fill='x', padx=5, pady=5)
        
        frame_op = ttk.LabelFrame(tab, text="Operació", bootstyle='info')
        frame_op.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_op, text="Codificar senyal", 
                 command=self.codificar_estereo,
                 bootstyle='success').pack(pady=5, padx=5, fill='x')
        
        frame_output = ttk.LabelFrame(tab, text="Sortida", bootstyle='info')
        frame_output.pack(fill='both', expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_output, text="Guardar arxiu codificat", 
                 command=self.save_file,
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
    
    def create_descodifica_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Descodifica Estèreo")
        
        frame_input = ttk.LabelFrame(tab, text="Entrada", bootstyle='info')
        frame_input.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_input, text="Seleccionar arxiu codificat", 
                 command=lambda: self.load_file('descodifica'),
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
        
        self.input_info_descod = ScrolledText(frame_input, height=4, state='disabled')
        self.input_info_descod.pack(fill='x', padx=5, pady=5)
        
        frame_op = ttk.LabelFrame(tab, text="Operació", bootstyle='info')
        frame_op.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_op, text="Descodificar senyal", 
                 command=self.descodificar_estereo,
                 bootstyle='success').pack(pady=5, padx=5, fill='x')
        
        frame_output = ttk.LabelFrame(tab, text="Sortida", bootstyle='info')
        frame_output.pack(fill='both', expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Button(frame_output, text="Guardar arxiu descodificat", 
                 command=self.save_file,
                 bootstyle='primary').pack(pady=5, padx=5, fill='x')
    
    def select_mono_file(self, canal):
        file = filedialog.askopenfilename(filetypes=[("Arxius WAV", "*.wav"), ("Tots els arxius", "*.*")])
        if file:
            if canal == 'L':
                self.input_file_L = file
            else:
                self.input_file_R = file
            
            # Actualitzar la informació
            info_text = f"Canal {'Esquerre' if canal == 'L' else 'Dret'}: {file}\n"
            self.input_info_mono.config(state='normal')
            self.input_info_mono.insert(tk.END, info_text)
            self.input_info_mono.config(state='disabled')
    
    def load_file(self, tab_type):
        self.clear_waveforms()
        self.input_file = filedialog.askopenfilename(
            filetypes=[("Arxius WAV", "*.wav"), ("Tots els arxius", "*.*")])
        
        if self.input_file:
            # Mostrem la barra de progrés
            self.progress.pack(fill='x', padx=10, pady=5)
            self.progress['value'] = 0
            self.root.update()
            
            # Fem la càrrega en un fil separat per no bloquejar la interfície
            threading.Thread(target=self._load_file_thread, args=(tab_type,), daemon=True).start()

    def _load_file_thread(self, tab_type):
        try:
            # Simulem progrés (en una aplicació real, això seria el progrés real de càrrega)
            for i in range(0, 101, 10):
                time.sleep(0.1)  # Simulem temps de càrrega
                self.progress['value'] = i
                self.root.update()
            
            self.input_data, self.fs = sf.read(self.input_file)
            
            info_text = f"Arxiu: {self.input_file}\n"
            info_text += f"Freqüència de mostratge: {self.fs} Hz\n"
            info_text += f"Mostres: {len(self.input_data)}\n"
            info_text += f"Canals: {self.input_data.shape[1] if len(self.input_data.shape) > 1 else 1}"
            
            # Actualitzem la interfície des del fil principal
            self.root.after(0, self._update_ui_after_load, tab_type, info_text)
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"No s'ha pogut llegir l'arxiu:\n{e}")
        finally:
            self.root.after(0, self.progress.pack_forget)
    
    def _update_ui_after_load(self, tab_type, info_text):
        if tab_type == 'estereo':
            self.input_info.config(state='normal')
            self.input_info.delete(1.0, tk.END)
            self.input_info.insert(tk.END, info_text)
            self.input_info.config(state='disabled')
        elif tab_type == 'mono':
            self.input_info_mono.config(state='normal')
            self.input_info_mono.delete(1.0, tk.END)
            self.input_info_mono.insert(tk.END, info_text)
            self.input_info_mono.config(state='disabled')
        elif tab_type == 'codifica':
            self.input_info_cod.config(state='normal')
            self.input_info_cod.delete(1.0, tk.END)
            self.input_info_cod.insert(tk.END, info_text)
            self.input_info_cod.config(state='disabled')
        elif tab_type == 'descodifica':
            self.input_info_descod.config(state='normal')
            self.input_info_descod.delete(1.0, tk.END)
            self.input_info_descod.insert(tk.END, info_text)
            self.input_info_descod.config(state='disabled')
                    
        # Dibuixem el senyal d'entrada
        self.plot_waveform(self.ax_input, self.fig_input, self.canvas_input, self.input_data)
        
        # Actualitzem l'estat dels botons
        self.update_play_buttons()
    
    def clear_waveforms(self):
        self.ax_input.clear()
        self.ax_output.clear()
    
    def plot_waveform(self, ax, fig, canvas, data):
        ax.clear()
        if data is None:
            ax.text(0.5, 0.5, 'Sense dades', ha='center', va='center')
        elif len(data.shape) == 1:
            x = np.arange(0, len(data))
            ax.plot(x, data, color='#1f77b4', linewidth=1)
            ax.set_title("Senyal Mono", fontsize=10)
        else:
            x = np.arange(0, len(data))
            ax.plot(x, data[:, 0], color='#d62728', linewidth=1, label='Canal Esquerre')
            ax.plot(x, data[:, 1], color='#2ca02c', linewidth=1, label='Canal Dret')
            ax.set_title("Senyal Estèreo", fontsize=10)
            ax.legend(fontsize=8)

        ax.set_xlim(left=0, right=len(data))
        ax.set_xlabel("Mostres", fontsize=8)
        ax.set_ylabel("Amplitud", fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)
        fig.tight_layout()
        canvas.draw()

    def update_play_buttons(self):
        # Actualitza l'estat dels botons de reproducció segons les dades disponibles
        input_state = 'normal' if self.input_data is not None else 'disabled'
        output_state = 'normal' if self.output_data is not None else 'disabled'
        
        self.play_input_btn.config(state=input_state)
        self.play_output_btn.config(state=output_state)
        
        # Actualitza els botons d'aturada segons si s'està reproduint
        if self.playing:
            self.stop_input_btn.config(state='normal')
            self.stop_output_btn.config(state='normal')
            self.play_input_btn.config(state='disabled')
            self.play_output_btn.config(state='disabled')
        else:
            self.stop_input_btn.config(state='disabled')
            self.stop_output_btn.config(state='disabled')
    
    def play_audio(self, source):
        data = self.input_data if source == 'input' else self.output_data
        
        if data is None:
            messagebox.showwarning("Avís", "No hi ha dades per reproduir")
            return
        
        self.stop_audio()  # Aturar qualsevol reproducció prèvia
        
        # Actualitzem l'estat
        self.current_playing = source
        self.playing = True
        self.update_play_buttons()
        
        # Fem la reproducció en un fil separat
        threading.Thread(target=self._play_audio_thread, args=(data,), daemon=True).start()
    
    def _play_audio_thread(self, data):
        try:
            self.should_stop = False
            
            # Creem un stream que podrem aturar
            self.current_stream = sd.InputStream(
                samplerate=self.fs,
                channels=1 if len(data.shape) == 1 else 2,
                callback=lambda *args: None  # Callback buit
            )
            
            with self.current_stream:
                sd.play(data, self.fs)
                
                while self.playing and not self.should_stop and sd.get_stream().active:
                    time.sleep(0.1)  # Comprovem periòdicament si hem d'aturar
                
                sd.stop()
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"No s'ha pogut reproduir l'àudio:\n{e}")
        finally:
            self.playing = False
            self.current_stream = None
            self.root.after(0, self.update_play_buttons)
    
    def stop_audio(self):
        self.should_stop = True
        if self.playing and self.current_stream is not None:
            sd.stop()
    
    def convertir_estereo_mono(self):
        if self.input_file and self.input_data is not None:
            try:
                # Verificar que es estéreo
                if len(self.input_data.shape) != 2 or self.input_data.shape[1] != 2:
                    messagebox.showerror("Error", "El archivo debe ser estéreo (2 canales)")
                    return
                
                # Crear archivo temporal
                temp_file = "temp_mono.wav"
                
                # Usar función del módulo stereo
                stereo.estereo2mono(self.input_file, temp_file, self.canal_sel.get())
                
                # Leer resultado y asegurar que es mono
                self.output_data, self.fs = sf.read(temp_file)
                
                # Si el resultado es estéreo (puede pasar con algunos métodos), convertirlo a mono
                if len(self.output_data.shape) > 1:
                    self.output_data = np.mean(self.output_data, axis=1)
                
                # Eliminar temporal
                os.remove(temp_file)
                
                # Actualizar interfaz
                self.plot_waveform(self.ax_output, self.fig_output, self.canvas_output, self.output_data)
                messagebox.showinfo("Éxito", "Conversión a mono completada")
                self.update_play_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Error en la conversión:\n{str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un archivo de entrada primero")
        if self.input_file and self.input_data is not None:
            try:
                # Creem un fitxer temporal per a la conversió
                temp_file = "temp_mono.wav"
                
                # Utilitzem la funció del mòdul stereo
                stereo.estereo2mono(self.input_file, temp_file, self.canal_sel.get())
                
                # Llegim el resultat
                self.output_data, self.fs = sf.read(temp_file)
                
                # Eliminem el fitxer temporal
                os.remove(temp_file)
                
                self.plot_waveform(self.ax_output, self.fig_output, self.canvas_output, self.output_data)
                messagebox.showinfo("Èxit", "Conversió a mono completada")
                self.update_play_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Error en la conversió:\n{e}")
        else:
            messagebox.showwarning("Avís", "Seleccioneu un arxiu d'entrada primer")

    def convertir_mono_estereo(self):
        if self.input_file_L and self.input_file_R:
            try:
                # Leer ambos archivos mono
                data_L, fs_L = sf.read(self.input_file_L)
                data_R, fs_R = sf.read(self.input_file_R)
                
                # Verificar compatibilidad
                if fs_L != fs_R:
                    messagebox.showerror("Error", "Los archivos deben tener la misma frecuencia de muestreo")
                    return
                
                # Asegurar que son mono
                if len(data_L.shape) > 1:
                    data_L = data_L[:,0] if data_L.shape[1] >= 1 else data_L.flatten()
                if len(data_R.shape) > 1:
                    data_R = data_R[:,0] if data_R.shape[1] >= 1 else data_R.flatten()
                
                # Ajustar longitudes
                min_len = min(len(data_L), len(data_R))
                data_L = data_L[:min_len]
                data_R = data_R[:min_len]
                
                # Crear señal estéreo
                self.output_data = np.column_stack((data_L, data_R))
                self.fs = fs_L
                
                # Actualizar interfaz
                self.plot_waveform(self.ax_output, self.fig_output, self.canvas_output, self.output_data)
                messagebox.showinfo("Éxito", "Combinación a estéreo completada")
                self.update_play_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Error al combinar archivos:\n{str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione ambos archivos mono (L y R)")
            
    def codificar_estereo(self):
        if self.input_file and self.input_data is not None:
            try:
                # Verificar que es estéreo
                if len(self.input_data.shape) != 2 or self.input_data.shape[1] != 2:
                    messagebox.showerror("Error", "El archivo debe ser estéreo (2 canales)")
                    return
                
                # Crear archivo temporal
                temp_file = "temp_codificado.wav"
                
                # Codificar usando el módulo
                stereo.codEstereo(self.input_file, temp_file)
                
                # Leer resultado
                self.output_data, self.fs = sf.read(temp_file)
                
                # Eliminar temporal
                os.remove(temp_file)
                
                # Actualizar interfaz
                self.plot_waveform(self.ax_output, self.fig_output, self.canvas_output, self.output_data)
                messagebox.showinfo("Éxito", "Codificación completada")
                self.update_play_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Error en codificación:\n{str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un archivo de entrada primero")

    def descodificar_estereo(self):
        if self.input_file and self.input_data is not None:
            try:
                # Crear archivo temporal
                temp_file = "temp_descodificado.wav"
                
                # Descodicar usando el módulo
                stereo.decEstereo(self.input_file, temp_file)
                
                # Leer resultado
                self.output_data, self.fs = sf.read(temp_file)
                
                # Eliminar temporal
                os.remove(temp_file)
                
                # Actualizar interfaz
                self.plot_waveform(self.ax_output, self.fig_output, self.canvas_output, self.output_data)
                messagebox.showinfo("Éxito", "Descodificación completada")
                self.update_play_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Error en descodificación:\n{str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un archivo de entrada primero")

    def play_audio(self, source):
        data = self.input_data if source == 'input' else self.output_data
        
        if data is None:
            messagebox.showwarning("Advertencia", "No hay datos para reproducir")
            return
        
        self.stop_audio()
        self.current_playing = source
        self.playing = True
        self.update_play_buttons()
        
        # Asegurar que los datos mono se reproduzcan correctamente
        if len(data.shape) == 1:
            # Convertir mono a estéreo para reproducción (mismo audio en ambos canales)
            play_data = np.column_stack((data, data))
        else:
            play_data = data
        
        threading.Thread(target=self._play_audio_thread, args=(play_data,), daemon=True).start()
        
    def save_file(self):
        if self.output_data is not None:
            self.output_file = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("Arxius WAV", "*.wav")])
            
            if self.output_file:
                try:
                    sf.write(self.output_file, self.output_data, self.fs)
                    messagebox.showinfo("Èxit", "Arxiu guardat correctament")
                except Exception as e:
                    messagebox.showerror("Error", f"No s'ha pogut guardar l'arxiu:\n{e}")
        else:
            messagebox.showwarning("Avís", "No hi ha dades de sortida per guardar")

if __name__ == "__main__":
    root = ttk.Window(themename='cosmo')
    app = MonoApp(root)
    root.mainloop()