import re
import tkinter as tk
from tkinter import filedialog

def normalitza(FitxerEntrada, FitxerSortida):
    """
    A partir d'un fitxer on les hores son escrites amb llenguatge col·loquial,
    fem un programa on es veuran les oraciones escrites amb les hores en el format correcte (Hh:Mm). 
    """
    Normhm = r"(?P<hh>\d\d?)[hH]((?P<mm>\d\d?)[mM])?"
    Normhh_en_punto = r'(?P<hh_en_punto>\d\d?) en punto'
    Normhh_y_media = r'(?P<hh_y_media>\d\d?) y media'
    Normhh_menos_cuarto = r'(?P<hh_menos_cuarto>\d\d?) menos cuarto'
    Normhh_y_cuarto = r'(?P<hh_y_cuarto>\d\d?) y cuarto'
    Normhh_12 = r'(?P<hh_12>\d\d?) de la noche'
    Normnum = r'(?P<num>\d)\s+(?P<texto>[a-zA-ZàÀéÉèÈóÓòÒíÍúÚçÇñ\s]+)'

    with open(FitxerEntrada, "r", encoding='utf-8') as Entrada, \
         open(FitxerSortida, "w", encoding='utf-8') as Sortida:
        
        for linea in Entrada:
            while (match := re.search(Normhm, linea)):
                Sortida.write(linea[:match.start()])
                hora = int(match["hh"])
                min = int(match["mm"]) if match["mm"] else 0
                if min > 60:
                    hora += 1
                    min -= 60
                Sortida.write(f'{hora:02d}:{min:02d}')
                linea = linea[match.end():]

            while (match := re.search(Normhh_en_punto, linea)):
                Sortida.write(linea[:match.start()])
                hora = int(match["hh_en_punto"])
                Sortida.write(f'{hora:02d}:00')
                linea = linea[match.end():]

            while (match := re.search(Normhh_y_media, linea)):
                Sortida.write(linea[:match.start()])
                hora = int(match["hh_y_media"])
                Sortida.write(f'{hora:02d}:30')
                linea = linea[match.end():]

            while (match := re.search(Normhh_menos_cuarto, linea)):
                Sortida.write(linea[:match.start()])
                hora = int(match["hh_menos_cuarto"]) - 1
                Sortida.write(f'{hora:02d}:45')
                linea = linea[match.end():]

            while (match := re.search(Normhh_y_cuarto, linea)):
                Sortida.write(linea[:match.start()])
                hora = int(match["hh_y_cuarto"])
                Sortida.write(f'{hora:02d}:15')
                linea = linea[match.end():]

            while (match := re.search(Normhh_12, linea)):
                Sortida.write(linea[:match.start()])
                hora = int(match["hh_12"]) - 12
                Sortida.write(f'{hora:02d}:00')
                linea = linea[match.end():]

            while (match := re.search(Normnum, linea)):
                Sortida.write(linea[:match.start()])
                num = int(match["num"])
                texto = match["texto"]
                if num == 7:
                    num = "siete"
                Sortida.write(f'{num} {texto}')
                linea = linea[match.end():]

            Sortida.write(linea)

def tria_fitxers():
    root = tk.Tk()
    root.withdraw()
    
    entrada = filedialog.askopenfilename(
        title="Seleccionar fitxer d'entrada",
        filetypes=[("Fitxers de text", "*.txt")]
    )
    
    sortida = filedialog.asksaveasfilename(
        title="Guardar fitxer de sortida", 
        defaultextension=".txt",
        filetypes=[("Fitxers de text", "*.txt")]
    )

    if entrada and sortida:
        normalitza(entrada, sortida)
        print(f"Fitxer normalitzat guardat a: {sortida}")
    else:
        print("Operació cancel·lada")

if __name__ == "__main__":
    tria_fitxers()