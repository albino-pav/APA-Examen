import re
import tkinter as tk
from tkinter import filedialog

def normalizaHoras(ficText, ficNorm):
    estructura = [
        (re.compile(r'(\d{1,2}):(\d{1,2})'), lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'),
        (re.compile(r'(\d{1,2})h(\d{1,2})m'), lambda m: f'{int(m.group(1)):02}:{int(m.group(2)):02}'),
        (re.compile(r'(\d{1,2})(?:h| de la (mañana|tarde))'),
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else (0 if m.group(1) == "12" and m.group(2) == "mañana" else int(m.group(1))):02}:00'),
        (re.compile(r'(\d{1,2}) y cuarto(?: de la (mañana|tarde))?'),
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)):02}:15'),
        (re.compile(r'(\d{1,2}) y media(?: de la (mañana|tarde))?'),
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)):02}:30'),
        (re.compile(r'(\d{1,2}) menos cuarto(?: de la (mañana|tarde))?'),
         lambda m: f'{(int(m.group(1)) - 1 + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)) - 1:02}:45'),
        (re.compile(r'(\d{1,2}) en punto(?: de la (mañana|tarde))?'),
         lambda m: f'{(int(m.group(1)) + 12) if m.group(2) == "tarde" and int(m.group(1)) < 12 else int(m.group(1)):02}:00'),
        (re.compile(r'12 de la noche'), lambda m: '00:00'),
    ]

    with open(ficText, 'r', encoding='utf-8') as input, open(ficNorm, 'w', encoding='utf-8') as output:
        for line in input:
            for patron, reemplazo in estructura:
                line = patron.sub(reemplazo, line)
            output.write(line)

def executa_normalitzador():
    root = tk.Tk()
    root.withdraw()  # Amaga la finestra principal

    print("Selecciona el fitxer d'entrada...")
    fitxer_entrada = filedialog.askopenfilename(filetypes=[("Fitxers de text", "*.txt")])

    print("Selecciona el fitxer de sortida...")
    fitxer_sortida = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Fitxers de text", "*.txt")])

    if fitxer_entrada and fitxer_sortida:
        normalizaHoras(fitxer_entrada, fitxer_sortida)
        print(f"Normalització completada. Resultat guardat a: {fitxer_sortida}")
    else:
        print("Procés cancel·lat.")

if __name__ == '__main__':
    executa_normalitzador()
