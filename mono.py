import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import pygame
import soundfile as sf

# Asegura que el módulo estereo.py esté en el path
sys.path.append(os.path.dirname(__file__))

try:
    from estereo import estereo2mono, mono2estereo, codEstereo, decEstereo
except ImportError:
    messagebox.showerror("Error de Importación", "No se pudo importar 'estereo.py'. Asegúrese de que está en la misma carpeta que este script.")
    sys.exit(1)


class EstereoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Señales Estéreo")

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        self.pestana1 = ttk.Frame(notebook)
        self.pestana2 = ttk.Frame(notebook)
        self.pestana3 = ttk.Frame(notebook)
        self.pestana4 = ttk.Frame(notebook)

        notebook.add(self.pestana1, text='Estéreo a Mono')
        notebook.add(self.pestana2, text='Mono a Estéreo')
        notebook.add(self.pestana3, text='Codifica Estéreo')
        notebook.add(self.pestana4, text='Descodifica Estéreo')

        self.playing = False
        pygame.mixer.init()

        self.estereo_a_mono()
        self.mono_a_estereo()
        self.codifica_estereo()
        self.descodifica_estereo()

    def reproducir(self, ruta):
        try:
            if self.playing:
                self.detener_reproduccion()

            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play()
            self.playing = True

            self.playing_window = tk.Toplevel(self.root)
            self.playing_window.title("Reproduciendo")

            label = tk.Label(self.playing_window, text=f"Reproduciendo:\n{os.path.basename(ruta)}")
            label.pack(padx=10, pady=10)

            btn_terminar = tk.Button(self.playing_window, text="Terminar", command=self.detener_reproduccion)
            btn_terminar.pack(pady=(0, 10))

            self.playing_window.protocol("WM_DELETE_WINDOW", self.detener_reproduccion)

            self.root.update_idletasks()
            self.playing_window.update_idletasks()

            main_w = self.root.winfo_width()
            main_h = self.root.winfo_height()
            main_x = self.root.winfo_rootx()
            main_y = self.root.winfo_rooty()

            popup_w = self.playing_window.winfo_width()
            popup_h = self.playing_window.winfo_height()

            pos_x = main_x + (main_w // 2) - (popup_w // 2)
            pos_y = main_y + (main_h // 2) - (popup_h // 2)

            self.playing_window.geometry(f"+{pos_x}+{pos_y}")

        except Exception as e:
            messagebox.showerror("Error al reproducir", f"No se pudo reproducir el archivo:\n{e}")

    def detener_reproduccion(self):
        pygame.mixer.music.stop()
        self.playing = False
        if hasattr(self, 'playing_window') and self.playing_window.winfo_exists():
            self.playing_window.destroy()

    def estereo_a_mono(self):
        frame = self.pestana1
        tk.Button(frame, text="Seleccionar Estéreo", command=self.cargar_estereo_mono).pack(pady=5)

        self.opcion_mono = tk.IntVar(value=2)
        opciones = [
            ("Izquierdo", 0),
            ("Derecho", 1),
            ("Semisuma", 2),
            ("Semidiferencia", 3)
        ]
        for texto, val in opciones:
            tk.Radiobutton(frame, text=texto, variable=self.opcion_mono, value=val).pack(anchor='w')

        tk.Button(frame, text="Guardar como...", command=self.guardar_estereo_mono).pack(pady=5)

    def cargar_estereo_mono(self):
        self.fic_estereo = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if self.fic_estereo:
            self.reproducir(self.fic_estereo)

    def guardar_estereo_mono(self):
        if not hasattr(self, 'fic_estereo'):
            return messagebox.showerror("Error", "No se ha seleccionado archivo")
        salida = filedialog.asksaveasfilename(defaultextension=".wav")
        if salida:
            try:
                estereo2mono(self.fic_estereo, salida, self.opcion_mono.get())
                messagebox.showinfo("Hecho", "Archivo convertido correctamente")
                self.reproducir(salida)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def mono_a_estereo(self):
        frame = self.pestana2
        tk.Button(frame, text="Seleccionar Canal Izquierdo", command=self.cargar_izq).pack(pady=5)
        tk.Button(frame, text="Seleccionar Canal Derecho", command=self.cargar_der).pack(pady=5)
        tk.Button(frame, text="Guardar como...", command=self.guardar_estereo).pack(pady=5)

    def cargar_izq(self):
        self.fic_izq = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if self.fic_izq:
            self.reproducir(self.fic_izq)

    def cargar_der(self):
        self.fic_der = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if self.fic_der:
            self.reproducir(self.fic_der)

    def guardar_estereo(self):
        if not hasattr(self, 'fic_izq') or not hasattr(self, 'fic_der'):
            return messagebox.showerror("Error", "Faltan archivos")
        salida = filedialog.asksaveasfilename(defaultextension=".wav")
        if salida:
            try:
                mono2estereo(self.fic_izq, self.fic_der, salida)
                messagebox.showinfo("Hecho", "Archivo estéreo creado")
                self.reproducir(salida)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def codifica_estereo(self):
        frame = self.pestana3
        tk.Button(frame, text="Seleccionar Estéreo", command=self.cargar_est_cod).pack(pady=5)
        tk.Button(frame, text="Guardar como...", command=self.guardar_cod).pack(pady=5)

    def cargar_est_cod(self):
        self.fic_est_cod = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if self.fic_est_cod:
            self.reproducir(self.fic_est_cod)

    def guardar_cod(self):
        if not hasattr(self, 'fic_est_cod'):
            return messagebox.showerror("Error", "No se ha seleccionado archivo")
        salida = filedialog.asksaveasfilename(defaultextension=".wav")
        if salida:
            try:
                codEstereo(self.fic_est_cod, salida)
                messagebox.showinfo("Hecho", "Archivo codificado")
                self.reproducir(salida)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def descodifica_estereo(self):
        frame = self.pestana4
        tk.Button(frame, text="Seleccionar Codificado", command=self.cargar_cod_dec).pack(pady=5)
        tk.Button(frame, text="Guardar como...", command=self.guardar_dec).pack(pady=5)

    def cargar_cod_dec(self):
        self.fic_cod = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if self.fic_cod:
            self.reproducir(self.fic_cod)

    def guardar_dec(self):
        if not hasattr(self, 'fic_cod'):
            return messagebox.showerror("Error", "No se ha seleccionado archivo")
        salida = filedialog.asksaveasfilename(defaultextension=".wav")
        if salida:
            try:
                decEstereo(self.fic_cod, salida)
                messagebox.showinfo("Hecho", "Archivo decodificado")
                self.reproducir(salida)
            except Exception as e:
                messagebox.showerror("Error", str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = EstereoApp(root)
    root.mainloop()



