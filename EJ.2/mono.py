import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from estereo import estereo2mono, mono2estereo, codEstereo, decEstereo

class EstereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de audio estéreo/mono")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.crear_pestana_estereo_a_mono()
        self.crear_pestana_mono_a_estereo()
        self.crear_pestana_codifica()
        self.crear_pestana_decodifica()

    def crear_pestana_estereo_a_mono(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estéreo a Mono")
        self.add_file_selector(frame, "Entrada WAV estéreo:", "Guardar como:", self.convertir_estereo_a_mono, canal=True)

    def crear_pestana_mono_a_estereo(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mono a Estéreo")
        self.label_L = ttk.Label(frame, text="Archivo canal izquierdo:")
        self.label_L.pack(pady=5)
        self.entry_L = ttk.Entry(frame, width=50)
        self.entry_L.pack(pady=5)
        self.btn_L = ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.entry_L))
        self.btn_L.pack(pady=5)

        self.label_R = ttk.Label(frame, text="Archivo canal derecho:")
        self.label_R.pack(pady=5)
        self.entry_R = ttk.Entry(frame, width=50)
        self.entry_R.pack(pady=5)
        self.btn_R = ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.entry_R))
        self.btn_R.pack(pady=5)

        self.label_out = ttk.Label(frame, text="Guardar estéreo como:")
        self.label_out.pack(pady=5)
        self.entry_out = ttk.Entry(frame, width=50)
        self.entry_out.pack(pady=5)
        self.btn_out = ttk.Button(frame, text="Guardar como", command=lambda: self.seleccionar_archivo_salida(self.entry_out))
        self.btn_out.pack(pady=5)

        self.btn_convertir = ttk.Button(frame, text="Convertir", command=self.convertir_mono_a_estereo)
        self.btn_convertir.pack(pady=10)

    def crear_pestana_codifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Codifica Estéreo")
        self.add_file_selector(frame, "Entrada WAV estéreo:", "Guardar codificado como:", self.codificar_audio)

    def crear_pestana_decodifica(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Descodifica Estéreo")
        self.add_file_selector(frame, "Entrada codificada:", "Guardar descodificado como:", self.decodificar_audio)

    def add_file_selector(self, frame, label_in_text, label_out_text, callback, canal=False):
        self.label_in = ttk.Label(frame, text=label_in_text)
        self.label_in.pack(pady=5)
        self.entry_in = ttk.Entry(frame, width=50)
        self.entry_in.pack(pady=5)
        self.btn_in = ttk.Button(frame, text="Seleccionar", command=lambda: self.seleccionar_archivo(self.entry_in))
        self.btn_in.pack(pady=5)

        self.label_out = ttk.Label(frame, text=label_out_text)
        self.label_out.pack(pady=5)
        self.entry_out = ttk.Entry(frame, width=50)
        self.entry_out.pack(pady=5)
        self.btn_out = ttk.Button(frame, text="Guardar como", command=lambda: self.seleccionar_archivo_salida(self.entry_out))
        self.btn_out.pack(pady=5)

        if canal:
            self.label_canal = ttk.Label(frame, text="Canal (0: Izq, 1: Der, 2: Medio, 3: Diferencia):")
            self.label_canal.pack(pady=5)
            self.spin_canal = ttk.Spinbox(frame, from_=0, to=3, width=5)
            self.spin_canal.set(2)
            self.spin_canal.pack(pady=5)

        self.btn_convertir = ttk.Button(frame, text="Procesar", command=callback)
        self.btn_convertir.pack(pady=10)

    def seleccionar_archivo(self, entry):
        ruta = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if ruta:
            entry.delete(0, tk.END)
            entry.insert(0, ruta)

    def seleccionar_archivo_salida(self, entry):
        ruta = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if ruta:
            entry.delete(0, tk.END)
            entry.insert(0, ruta)

    def convertir_estereo_a_mono(self):
        try:
            estereo2mono(self.entry_in.get(), self.entry_out.get(), int(self.spin_canal.get()))
            messagebox.showinfo("Éxito", "Conversión realizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def convertir_mono_a_estereo(self):
        try:
            mono2estereo(self.entry_L.get(), self.entry_R.get(), self.entry_out.get())
            messagebox.showinfo("Éxito", "Conversión realizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def codificar_audio(self):
        try:
            codEstereo(self.entry_in.get(), self.entry_out.get())
            messagebox.showinfo("Éxito", "Codificación completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decodificar_audio(self):
        try:
            decEstereo(self.entry_in.get(), self.entry_out.get())
            messagebox.showinfo("Éxito", "Decodificación completada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = EstereoApp(root)
    root.mainloop()

