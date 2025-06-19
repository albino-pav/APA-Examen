"""
Biel Bernal Pratdesaba
"""
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import ttkbootstrap as tb

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import re

def normaliza():
    win = tb.Window(themename="flatly")
    win.title("Normalització d'hores")
    win.geometry('800x400')
    win.resizable(False, False)

    ttk.Style(win).configure('.', font=('Segoe UI', 12), padding=8)

    # Títol gran
    ttk.Label(win, text="Normalitzador d'Expressions Horàries", font=("Segoe UI", 18, "bold")).pack(pady=10)

    # Frame principal
    frame = ttk.Frame(win)
    frame.pack(pady=10, fill='x', padx=20)

    entrada_path = tk.StringVar()
    sortida_path = tk.StringVar()
    missatge_resultat = tk.StringVar()

    def seleccionar_entrada():
        fitxer = fd.askopenfilename(
            title="Selecciona fitxer d'entrada",
            filetypes=[("Fitxers de text", "*.txt")]
        )
        entrada_path.set(fitxer)

    def seleccionar_sortida():
        fitxer = fd.asksaveasfilename(
            title="Selecciona fitxer de sortida",
            defaultextension=".txt",
            filetypes=[("Fitxers de text", "*.txt")]
        )
        sortida_path.set(fitxer)

    def executar_normalitzacio():
        entrada = entrada_path.get()
        sortida = sortida_path.get()
        if entrada and sortida:
            normalizaHoras(entrada, sortida)
            missatge_resultat.set("Fitxer normalitzat correctament.")
        else:
            missatge_resultat.set("Cal seleccionar els dos fitxers.")

    # Grup de selecció de fitxers
    grup_fitxers = ttk.LabelFrame(frame, text="Fitxers", padding=12)
    grup_fitxers.pack(fill='x', padx=10, pady=10)

    ttk.Button(grup_fitxers, text="Fitxer d'entrada", command=seleccionar_entrada).pack(fill='x', pady=5)
    ttk.Label(grup_fitxers, textvariable=entrada_path, foreground="blue").pack(fill='x')

    ttk.Button(grup_fitxers, text="Fitxer de sortida", command=seleccionar_sortida).pack(fill='x', pady=5)
    ttk.Label(grup_fitxers, textvariable=sortida_path, foreground="blue").pack(fill='x')

    # Botó d'acció
    ttk.Button(frame, text="Normalitza hores", command=executar_normalitzacio, bootstyle="success").pack(pady=15)

    # Missatge de resultat
    ttk.Label(frame, textvariable=missatge_resultat, font=("Segoe UI", 11, "italic"), foreground="green").pack()

    win.mainloop()



def normalizaHoras(ficText, ficNorm):
    """
    Llegeix un fitxer de text, detecta expressions horàries vàlides i les substitueix pel format HH:MM.
    """

    # Patrons
    patron_hm_periodo = re.compile(
        r'\b(\d{1,2})h(?:\s+de la\s+(mañana|tarde|noche|madrugada))\b',
        re.IGNORECASE
    )
    patron_hm = re.compile(r'\b(\d{1,2})h(?:(\d{1,2})m)?\b')
    patron_colon = re.compile(r'\b(\d{1,2}):(\d{2})\b')
    patron_oral = re.compile(
        r'\b(\d{1,2})\s*(en punto|y cuarto|y media|menos cuarto)'
        r'(?:\s+de la\s+(mañana|tarde|noche|madrugada))?',
        re.IGNORECASE
    )
    patron_periodo = re.compile(
        r'\b(\d{1,2})\s*de la (mañana|tarde|noche|madrugada)\b|\b(\d{1,2})\s*del mediodía\b',
        re.IGNORECASE
    )

    with open(ficText, 'rt', encoding='utf-8') as f_in, open(ficNorm, 'wt', encoding='utf-8') as f_out:
        for linia in f_in:

            def substituir_hm_periodo(match):
                h = int(match.group(1))
                periode = match.group(2).lower()

                if not (1 <= h <= 12):
                    return match.group(0)

                if periode == 'mañana':
                    return f'{h % 12:02}:00'
                elif periode == 'tarde':
                    if 1 <= h <= 8:
                        return f'{(h + 12):02}:00'
                elif periode == 'noche':
                    if 8 <= h <= 11:
                        return f'{(h + 12):02}:00'
                    elif h == 12:
                        return '00:00'
                elif periode == 'madrugada':
                    if 1 <= h <= 6:
                        return f'{h:02}:00'

                return match.group(0)

            def substituir_hm(match):
                h, m = match.groups()
                h = int(h)
                m = int(m) if m is not None else 0
                return f'{h:02}:{m:02}' if 0 <= h <= 23 and 0 <= m <= 59 else match.group(0)

            def substituir_colon(match):
                h, m = int(match.group(1)), int(match.group(2))
                return f'{h:02}:{m:02}' if 0 <= h <= 23 and 0 <= m <= 59 else match.group(0)

            def substituir_oral(match):
                h = int(match.group(1))
                frase = match.group(2).lower()
                periode = match.group(3).lower() if match.group(3) else None

                if not (1 <= h <= 12):
                    return match.group(0)

                if frase == 'en punto':
                    m = 0
                elif frase == 'y cuarto':
                    m = 15
                elif frase == 'y media':
                    m = 30
                elif frase == 'menos cuarto':
                    h = (h - 1) if h > 1 else 12
                    m = 45
                else:
                    return match.group(0)

                if periode == 'tarde':
                    if 1 <= h <= 8:
                        h += 12
                elif periode == 'noche':
                    if 8 <= h <= 11:
                        h += 12
                    elif h == 12:
                        h = 0
                elif periode == 'mañana':
                    h = h % 12
                elif periode == 'madrugada':
                    if not (1 <= h <= 6):
                        return match.group(0)

                return f'{h:02}:{m:02}'

            def substituir_periodo(match):
                h1 = match.group(1)
                periode = match.group(2)
                h2 = match.group(3)

                if h2:  # del mediodía
                    h = int(h2)
                    if 1 <= h <= 2:
                        return f'{12 + (h % 12):02}:00'
                    return match.group(0)

                if not h1 or not periode:
                    return match.group(0)

                h = int(h1)
                periode = periode.lower()

                if not (1 <= h <= 12):
                    return match.group(0)

                if periode == 'mañana':
                    return f'{h % 12:02}:00'
                elif periode == 'tarde':
                    if 1 <= h <= 8:
                        return f'{(h + 12):02}:00'
                elif periode == 'noche':
                    if 8 <= h <= 11:
                        return f'{(h + 12):02}:00'
                    elif h == 12:
                        return '00:00'
                elif periode == 'madrugada':
                    if 1 <= h <= 6:
                        return f'{h:02}:00'

                return match.group(0)

            # Ordre de substitució
            linia = patron_hm_periodo.sub(substituir_hm_periodo, linia)
            linia = patron_hm.sub(substituir_hm, linia)
            linia = patron_colon.sub(substituir_colon, linia)
            linia = patron_oral.sub(substituir_oral, linia)
            linia = patron_periodo.sub(substituir_periodo, linia)

            f_out.write(linia)


if __name__ == "__main__":
    normaliza()