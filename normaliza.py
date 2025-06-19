import re

def normalizaHoras(ficText, ficNorm):
    estructura = [
        # Formato dos puntos 
        (re.compile(r'(\d{1,2}):(\d{1,2})'), lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'),

        # Formato h y m 
        (re.compile(r'(\d{1,2})h(\d{1,2})m'), lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'),

    	# Formato h 
        (re.compile(r'(\d{1,2})(?:h| de la (mañana|tarde))'), 
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else (0 if m.group(1) == "12" and m.group(2) == "mañana" else int(m.group(1))):02}:00'),

        # Formato y cuarto (opcional de la mañana/tarde)
        (re.compile(r'(\d{1,2}) y cuarto(?: de la (mañana|tarde))?'), 
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)):02}:15'),

        # Formato y media (opcional de la mañana/tarde)
        (re.compile(r'(\d{1,2}) y media(?: de la (mañana|tarde))?'), 
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)):02}:30'),

        # Formato menos cuarto (opcional de la mañana/tarde)
        (re.compile(r'(\d{1,2}) menos cuarto(?: de la (mañana|tarde))?'), 
         lambda m: f'{(int(m.group(1)) - 1 + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)) - 1:02}:45'),

        # Formato en punto (opcional de la mañana/tarde)
        (re.compile(r'(\d{1,2}) en punto(?: de la (mañana|tarde))?'),
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)):02}:00'),

        # 12 de la noche → 00:00
        (re.compile(r'12 de la noche'), lambda m: '00:00'),
    ]

    with open(ficText, 'r') as input, open(ficNorm, 'w') as output:
        for line in input: 
            for x, reemplece in estructura:
                line = x.sub(reemplece, line)
            output.write(line)


import tkinter as tk
from tkinter import filedialog, messagebox

def seleccionar_archivo(entrada_var):
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo .txt",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if ruta:
        entrada_var.set(ruta)


def main():
    # Crear la ventana
    ventana = tk.Tk()
    ventana.title("Normalizador de Horas")
    ventana.geometry("400x150")
    
    entrada_var = tk.StringVar()
    ventana.configure(bg="#FDF0D5") 

    # Etiqueta
    etiqueta = tk.Label(ventana, text="Selecciona un archivo TXT para normalizar:", 
                        font=("Arial", 12, "bold"), bg="#FDF0D5", fg="#003049")
    etiqueta.pack(pady=10)

    # Caja de texto
    entrada = tk.Entry(ventana, textvariable=entrada_var, width=60, 
                       font=("Arial", 10), bg="#ffffff", fg="#003049", relief="sunken", bd=2)
    entrada.pack(pady=5)

    # Botón Buscar
    boton_buscar = tk.Button(ventana, text="Buscar", width=15, bg="#669BBC", fg="#003049",
                             font=("Arial", 10, "bold"),
                             command=lambda: seleccionar_archivo(entrada_var))
    boton_buscar.pack(pady=5)

    # Botón Normalizar
    boton_normalizar = tk.Button(ventana, text="Normalizar", width=15, bg="#669BBC", fg="#003049",
                                 font=("Arial", 10, "bold"),
                                 command=lambda: normalizaHoras(entrada_var.get(), "FicheroNormalizado.txt"))
    boton_normalizar.pack(pady=5)
    ventana.mainloop()

if __name__ == '__main__':
    main()
