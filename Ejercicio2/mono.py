# Autor: Tomàs Lloret
# Fecha: 16/06/2025
# Ejercicio 2: Programa de Manejo de Señales Estéreo

import tkinter as tk
import os
from tkinter import filedialog, ttk
from pathlib import Path
import estereo
import tempfile
import threading
import sounddevice as sd #simpleaudio me provocava errores de segmentacion
import scipy.io.wavfile

def seleccionar_salida():

    archivo_salida = filedialog.asksaveasfilename(
        initialdir = str(Path.home()),
        title="Selecciona dónde guardar el fichero de audio",
        defaultextension=".wav",
        filetypes=[("Archivos de audio", "*.wav")]
    )
    return archivo_salida

def crear_entry_busqueda_audio(parent, modo, label_text="Archivo de audio (.wav):"):
    frame = tk.Frame(parent, bg="black")
    label = tk.Label(frame, text=label_text, font=("Calibri", 12), fg="white", bg="black")
    label.pack(side=tk.LEFT, padx=5)

    entry = tk.Entry(frame, width=50)
    entry.pack(side=tk.LEFT, padx=5)

    def buscar_archivo():
        archivo = filedialog.askopenfilename(
            initialdir=str(Path.home()),
            title="Selecciona el fichero de audio",
            filetypes=[("Archivos de audio", "*.wav")]
        )
        if archivo:
            entry.delete(0, tk.END)
            entry.insert(0, archivo)

    def guardar_archivo():
        archivo = filedialog.asksaveasfilename(
            initialdir=str(Path.home()),
            title="Selecciona dónde guardar el fichero de audio",
            defaultextension=".wav",
            filetypes=[("Archivos de audio", "*.wav")]
        )
        if archivo:
            entry.delete(0, tk.END)
            entry.insert(0, archivo)

    # que chulo lo de los modos lastima que al final no me sirva de nada en esta funcion
    if modo == "busca":
        boton = tk.Button(frame, text="Buscar", command=buscar_archivo)
    elif modo == "guarda":
        boton = tk.Button(frame, text="Guardar como", command=guardar_archivo)
    else:
        tk.messagebox.showerror("Error", "Selecciona un modo de crear_entry_busqueda_audio valido (o 'busca' o 'guarda').")
        return
    boton.pack(side=tk.LEFT, padx=5)

    frame.pack(pady=10)
    return entry

def reproducir_audio(audio):
    def _thread():
        archivo = audio.get()
        if not archivo or not os.path.isfile(archivo):
            tk.messagebox.showerror("Error", "Selecciona un archivo de audio válido.")
            return
        try:
            rate, data = scipy.io.wavfile.read(archivo)
            # Normaliza si es necesario
            if data.dtype != 'int16':
                data = data.astype('int16')
            sd.play(data, rate)
            sd.wait()
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo reproducir el audio:\n{e}")
    threading.Thread(target=_thread, daemon=True).start()

def preview_audio_procesado(archivo_entrada, modo, archivo_entrada_derecho=None):
    def _thread(): # adeu segmentacion
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            archivo_temp = temp.name
        try:
            if modo == "estereo2mono":
                estereo.estereo2mono(archivo_entrada, archivo_temp)
            elif modo == "mono2estereo":
                if not archivo_entrada_derecho or not os.path.isfile(archivo_entrada_derecho):
                    tk.messagebox.showerror("Error", "Selecciona un archivo mono derecho válido.")
                    return
                estereo.mono2estereo(archivo_entrada, archivo_entrada_derecho, archivo_temp)
            elif modo == "codEstereo":
                estereo.codEstereo(archivo_entrada, archivo_temp)
            elif modo == "decEstereo":
                estereo.decEstereo(archivo_entrada, archivo_temp)
            else:
                tk.messagebox.showerror("Error", "Modo de procesamiento no válido.")
                return

            rate, data = scipy.io.wavfile.read(archivo_temp)
            if data.dtype != 'int16':
                data = data.astype('int16')
            sd.play(data, rate)
            sd.wait()
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo reproducir el audio procesado:\n{e}")
        finally:
            os.remove(archivo_temp)
    threading.Thread(target=_thread, daemon=True).start()

def procesar_audio(archivo_entrada, archivo_salida, modo, archivo_entrada_derecho=None):
    if modo == "mono2estereo":
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            tk.messagebox.showerror("Error", "Selecciona el archivo mono izquierdo válido.")
            return
        if not archivo_entrada_derecho or not os.path.isfile(archivo_entrada_derecho):
            tk.messagebox.showerror("Error", "Selecciona el archivo mono derecho válido.")
            return
    else:
        if not archivo_entrada or not os.path.isfile(archivo_entrada):
            tk.messagebox.showerror("Error", "Selecciona un archivo de audio válido.")
            return

    if not archivo_salida:
        tk.messagebox.showerror("Error", "Selecciona un archivo de salida válido.")
        return

    try:
        if modo == "estereo2mono":
            estereo.estereo2mono(archivo_entrada, archivo_salida)
        elif modo == "mono2estereo":
            estereo.mono2estereo(archivo_entrada, archivo_entrada_derecho, archivo_salida)
        elif modo == "codEstereo":
            estereo.codEstereo(archivo_entrada, archivo_salida)
        elif modo == "decEstereo":
            estereo.decEstereo(archivo_entrada, archivo_salida)
        else:
            tk.messagebox.showerror("Error", "Modo de procesamiento no válido.")
            return
        tk.messagebox.showinfo("Éxito", "Procesamiento completado correctamente.")
    except Exception as e:
        tk.messagebox.showerror("Error", f"No se pudo procesar el audio:\n{e}")

def main():
    root = tk.Tk()
    root.configure(bg="gray10")
    root.geometry("1100x800")
    root.title("Ejercicio 2: Programa de Manejo de Señales")

    titulo = tk.Label(root, text="Ejercicio 2: Programa de Manejo de Señales", font=("Calibri", 20, "bold"), fg="white", bg="gray10", pady=10)
    titulo.pack()

    subtitulo = tk.Label(root, text="Tomàs Lloret", font=("Calibri", 15, "bold"), fg="grey", bg="gray10", pady=5)
    subtitulo.pack()

    notebook = ttk.Notebook(root)

    # Crear las pestañas
    tab_estereo_mono = ttk.Frame(notebook)
    tab_mono_estereo = ttk.Frame(notebook)
    tab_cod_estereo = ttk.Frame(notebook)
    tab_decod_estereo = ttk.Frame(notebook)

    # tab_estereo_mono
    pestanya1 = tk.Label(tab_estereo_mono, text="Convertidor estereo a mono", font=("Calibri", 12), fg="black")
    pestanya1.pack()
    entry_audio1 = crear_entry_busqueda_audio(tab_estereo_mono, "busca")
    entry_audio1.pack()
    boton_escuchar1 = tk.Button(tab_estereo_mono, text="Escuchar audio sin procesar", command=lambda:reproducir_audio(entry_audio1)) # la lambdda hace que se ejecute en clicar
    boton_escuchar1.pack(pady=5)
    boton_preview1 = tk.Button(tab_estereo_mono, text="Escuchar preview del audio procesado",
    command=lambda: preview_audio_procesado(entry_audio1.get(), "estereo2mono"))
    boton_preview1.pack(pady=5)    
    ''' no uso esto al final porque en el trabajo dice que escojamos ubicación en clicar boton y esto hacia como el search
    entry_salida1 = crear_entry_busqueda_audio(tab_estereo_mono, "guarda")
    entry_salida1.pack()
    boton_guardar1 = tk.Button(
        tab_estereo_mono,
        text="Guardar audio procesado",
        command=lambda: procesar_audio(entry_audio1.get(), entry_salida1.get(), "estereo2mono")
    )
    boton_guardar1.pack(pady=5)
    '''
    boton_guardar1 = tk.Button(
        tab_estereo_mono,
        text="Guardar audio procesado",
        command=lambda: procesar_audio(entry_audio1.get(), seleccionar_salida(), "estereo2mono")
    )
    boton_guardar1.pack(pady=5)

    # tab_mono_estereo
    pestanya2 = tk.Label(tab_mono_estereo, text="Convertidor mono a estereo", font=("Calibri", 12), fg="black")
    pestanya2.pack()
    entry_audio21 = crear_entry_busqueda_audio(tab_mono_estereo, "busca", "Archivo de audio izquierdo (.wav):")
    entry_audio21.pack()
    boton_escuchar21 = tk.Button(tab_mono_estereo, text="Escuchar audio izquierdo sin procesar", command=lambda: reproducir_audio(entry_audio21))
    boton_escuchar21.pack(pady=5)
    entry_audio22 = crear_entry_busqueda_audio(tab_mono_estereo, "busca", "Archivo de audio derecho (.wav):")
    entry_audio22.pack()
    boton_escuchar22 = tk.Button(tab_mono_estereo, text="Escuchar audio derecho sin procesar", command=lambda: reproducir_audio(entry_audio22))
    boton_escuchar22.pack(pady=5)
    boton_preview2 = tk.Button(tab_mono_estereo, text="Escuchar preview del audio procesado",
        command=lambda: preview_audio_procesado(entry_audio21.get(), "mono2estereo", entry_audio22.get()))
    boton_preview2.pack(pady=5)
    boton_guardar2 = tk.Button(
        tab_mono_estereo,
        text="Guardar audio procesado",
        command=lambda: procesar_audio(entry_audio21.get(), seleccionar_salida(), "mono2estereo", entry_audio22.get())
    )
    boton_guardar2.pack(pady=5)

    # tab_cod_estereo
    pestanya3 = tk.Label(tab_cod_estereo, text="Codificador estereo a mono", font=("Calibri", 12), fg="black")
    pestanya3.pack()
    entry_audio3 = crear_entry_busqueda_audio(tab_cod_estereo, "busca")
    entry_audio3.pack()
    boton_escuchar3 = tk.Button(tab_cod_estereo, text="Escuchar audio sin procesar", command=lambda: reproducir_audio(entry_audio3))
    boton_escuchar3.pack(pady=5)
    boton_preview3 = tk.Button(tab_cod_estereo, text="Escuchar preview del audio procesado",
        command=lambda: preview_audio_procesado(entry_audio3.get(), "codEstereo"))
    boton_preview3.pack(pady=5)
    boton_guardar3 = tk.Button(
        tab_cod_estereo,
        text="Guardar audio procesado",
        command=lambda: procesar_audio(entry_audio3.get(), seleccionar_salida(), "codEstereo")
    )
    boton_guardar3.pack(pady=5)

    # tab_decod_estereo
    pestanya4 = tk.Label(tab_decod_estereo, text="Decodificador mono a estereo", font=("Calibri", 12), fg="black")
    pestanya4.pack()
    entry_audio4 = crear_entry_busqueda_audio(tab_decod_estereo, "busca")
    entry_audio4.pack()
    boton_escuchar4 = tk.Button(tab_decod_estereo, text="Escuchar audio sin procesar", command=lambda: reproducir_audio(entry_audio4))
    boton_escuchar4.pack(pady=5)
    boton_preview4 = tk.Button(tab_decod_estereo, text="Escuchar preview del audio procesado",
        command=lambda: preview_audio_procesado(entry_audio4.get(), "decEstereo"))
    boton_preview4.pack(pady=5)
    boton_guardar4 = tk.Button(
        tab_decod_estereo,
        text="Guardar audio procesado",
        command=lambda: procesar_audio(entry_audio4.get(), seleccionar_salida(), "decEstereo")
    )
    boton_guardar4.pack(pady=5)

    # Agregamos las pestañas al notebook
    notebook.add(tab_estereo_mono, text="Convertidor estereo a mono")
    notebook.add(tab_mono_estereo, text="Convertidor mono a estereo")
    notebook.add(tab_cod_estereo, text="Codificador estereo a mono")
    notebook.add(tab_decod_estereo, text="Decodificador mono a estereo")
    notebook.pack()

    # imagenes :P
    filaimagenes = tk.Frame(root, bg="grey10")
    
    nota = tk.PhotoImage(file="img/100.png").subsample(3,3)
    etiq = tk.Label(filaimagenes, cursor='boat', borderwidth=20, relief=tk.RIDGE, image=nota)
    etiq.pack(side="left")
    
    terrassa = tk.PhotoImage(file="img/gifcorpolitecnic.gif").subsample(5,5)
    etiq2 = tk.Label(filaimagenes, cursor='heart', borderwidth=20, relief=tk.RIDGE, image=terrassa)
    etiq2.pack(side="left", padx=10, pady=10)

    filaimagenes.pack()

    root.mainloop()
    

if __name__ == "__main__":
    main()