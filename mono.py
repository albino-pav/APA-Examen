import struct as st
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import ttkbootstrap as tb

def estereo2mono(ficEste, ficMono, canal=2):
    """
    La funció llegeix el fitxer ficEste, que ha de contenir un senyal estèreo, i escriu el fitxer 
    ficMono, amb un senyal monofònic. El tipus concret de senyal que s'emmagatzemarà a ficMono
    depèn de l'argument canal:

    - canal=0: S'emmagatzema el canal esquerre (L).
    - canal=1: S'emmagatzema el canal dret (R).
    - canal=2: S'emmagatzema la semisuma (L + R) / 2.
    - canal=3: S'emmagatzema la semidiferència (L - R) / 2.

    """

    with open(ficEste, "rb") as fpEste:

        # Capçalera inicial (RIFF)
        formato = "<4sI4s"
        datos = fpEste.read(st.calcsize(formato))
        chunkID, chunkSize, format = st.unpack(formato, datos)

        if chunkID != b"RIFF" or format != b"WAVE":
            raise Exception(f"El fitxer {ficEste} no té un format WAVE vàlid.")

        # Subchunk1 'fmt ' (offset 12)
        fpEste.seek(12, 0)
        formato = "<4sIHHIIHH"
        datos = fpEste.read(st.calcsize(formato))
        subChunk1ID, subChunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample = st.unpack(formato, datos)

        if subChunk1ID != b"fmt " or audioFormat != 1 or numChannels != 2 or bitsPerSample != 16:
            raise Exception("El fitxer ha de ser PCM, estèreo i de 16 bits.")

        # Subchunk2 'data' (offset 36)
        fpEste.seek(36, 0)
        formato = "<4sI"
        datos = fpEste.read(st.calcsize(formato))
        subChunk2ID, subChunk2Size = st.unpack(formato, datos)

        if subChunk2ID != b"data":
            raise Exception("No s'ha trobat el subchunk 'data' on esperat (offset 36).")
        
        # Llegim les mostres stereo
        numMostres = subChunk2Size // 2  # nombre total de valors de 2 bytes
        formato = f"<{numMostres}h"
        dades = fpEste.read(st.calcsize(formato))
        mostres = st.unpack(formato, dades)

    # Passem de stereo a mono
    mostStereo = list(zip(mostres[::2], mostres[1::2]))
    if canal == 0:
        senyalMono = [L for L, R in mostStereo]
    elif canal == 1:
        senyalMono = [R for L, R in mostStereo]
    elif canal == 2:
        senyalMono = [(L + R) // 2 for L, R in mostStereo]
    elif canal == 3:
        senyalMono = [(L - R) // 2 for L, R in mostStereo]
    else:
        raise ValueError("El canal ha de ser 0, 1, 2 o 3")
    
    # Calcular mides per la capçalera mono
    subChunk2SizeMono = len(senyalMono) * 2
    chunkSizeMono = 36 + subChunk2SizeMono

    # Escriure el nou fitxer 
    with open(ficMono, "wb") as fpMono:
        # Capçalera inicial (RIFF)
        formato = "<4sI4s"
        fpMono.write(st.pack(formato, b"RIFF", chunkSizeMono, b"WAVE"))

        # Subchunk1 (fmt)
        formato = "<4sIHHIIHH"
        fpMono.write(st.pack(formato, b"fmt ", 16, 1, 1,
                             sampleRate, sampleRate * 2, 2, 16))

        # Subchunk2 (data)
        formato = "<4sI"
        fpMono.write(st.pack(formato, b"data", subChunk2SizeMono))

        # Dades mono
        formato = f"<{len(senyalMono)}h"
        fpMono.write(st.pack(formato, *senyalMono))
    


def mono2stereo(ficIzq, ficDer, ficEste):
    """
    Llegeix els fitxers ficIzq i ficDer, que contenen els senyals monofònics corresponents als
    canals esquerre i dret, respectivament, i construeix amb ells un senyal estèreo que s'emmagatzema 
    al fitxer ficEste.

    """

    # Llegir el fitxer del canal L
    with open(ficIzq, "rb") as fpIzq:

        # Capçalera inicial (RIFF)
        formato = "<4sI4s"
        datos = fpIzq.read(st.calcsize(formato))
        chunkID, chunkSize, format = st.unpack(formato, datos)

        if chunkID != b"RIFF" or format != b"WAVE":
            raise Exception(f"El fitxer {ficEste} no té un format WAVE vàlid.")

        # Subchunk1 'fmt ' (offset 12)
        fpIzq.seek(12, 0)
        formato = "<4sIHHIIHH"
        datos = fpIzq.read(st.calcsize(formato))
        subChunk1ID, subChunk1Size, audioFormat, numChannels, sampleRateL, byteRate, blockAlign, bitsPerSample = st.unpack(formato, datos)

        if subChunk1ID != b"fmt " or audioFormat != 1 or numChannels != 1 or bitsPerSample != 16:
            raise Exception("El fitxer ha de ser PCM, mono i de 16 bits.")

        # Subchunk2 'data' (offset 36)
        fpIzq.seek(36, 0)
        formato = "<4sI"
        datos = fpIzq.read(st.calcsize(formato))
        subChunk2ID, subChunk2Size = st.unpack(formato, datos)

        if subChunk2ID != b"data":
            raise Exception("No s'ha trobat el subchunk 'data' on esperat (offset 36).")
        
        # Llegim les mostres stereo
        numMostres = subChunk2Size // 2  # Nombre total de valors de 2 bytes
        formato = f"<{numMostres}h"
        dades = fpIzq.read(st.calcsize(formato))
        mostresL = st.unpack(formato, dades)

    # Llegir el fitxer del canal R
    with open(ficDer, "rb") as fpDer:

        # Capçalera inicial (RIFF)
        formato = "<4sI4s"
        datos = fpDer.read(st.calcsize(formato))
        chunkID, chunkSize, format = st.unpack(formato, datos)

        if chunkID != b"RIFF" or format != b"WAVE":
            raise Exception(f"El fitxer {ficEste} no té un format WAVE vàlid.")

        # Subchunk1 'fmt ' (offset 12)
        fpDer.seek(12, 0)
        formato = "<4sIHHIIHH"
        datos = fpDer.read(st.calcsize(formato))
        subChunk1ID, subChunk1Size, audioFormat, numChannels, sampleRateR, byteRate, blockAlign, bitsPerSample = st.unpack(formato, datos)

        if subChunk1ID != b"fmt " or audioFormat != 1 or numChannels != 1 or bitsPerSample != 16:
            raise Exception("El fitxer ha de ser PCM, mono i de 16 bits.")

        # Subchunk2 'data' (offset 36)
        fpDer.seek(36, 0)
        formato = "<4sI"
        datos = fpDer.read(st.calcsize(formato))
        subChunk2ID, subChunk2Size = st.unpack(formato, datos)

        if subChunk2ID != b"data":
            raise Exception("No s'ha trobat el subchunk 'data' on esperat (offset 36).")
        
        # Llegim les mostres mono
        numMostres = subChunk2Size // 2  # Nombre total de valors de 2 bytes
        formato = f"<{numMostres}h"
        dades = fpDer.read(st.calcsize(formato))
        mostresR = st.unpack(formato, dades)

    # Comvinem les mostres en una sola senyal de 2 canals
    mostresStereo = []
    for L, R in zip(mostresL, mostresR):
        mostresStereo.append(L)
        mostresStereo.append(R)

    # Calcular mides per la capçalera stereo
    subChunk2SizeStereo = len(mostresStereo) * 2
    chunkSizeStereo = 36 + subChunk2SizeStereo

    # Escriure el nou fitxer 
    with open(ficEste, "wb") as fpEste:
        # Capçalera RIFF
        formato = "<4sI4s"
        fpEste.write(st.pack(formato, b"RIFF", chunkSizeStereo, b"WAVE"))

        # Subchunk1 'fmt ' (estèreo, 2 canals, 16 bits)
        formato = "<4sIHHIIHH"
        fpEste.write(st.pack(formato, b"fmt ", 16, 1, 2, sampleRateL, sampleRateL * 4, 4, 16))

        # Subchunk2 'data'
        formato = "<4sI"
        fpEste.write(st.pack(formato, b"data", subChunk2SizeStereo))

        # Mostres
        formato = f"<{len(mostresStereo)}h"
        fpEste.write(st.pack(formato, *mostresStereo))



def codEstereo(ficEste, ficCod):
    """
    Llegeix un fitxer WAVE estèreo de 16 bits i genera un fitxer mono de 32 bits on:
    - Els 16 bits alts contenen la semisuma (L+R)//2
    - Els 16 bits baixos contenen la semidiferència (L-R)//2
    """
    with open(ficEste, "rb") as fpEste:
        # Capçalera inicial (RIFF)
        formato = "<4sI4s"
        datos = fpEste.read(st.calcsize(formato))
        chunkID, chunkSize, format = st.unpack(formato, datos)

        if chunkID != b"RIFF" or format != b"WAVE":
            raise Exception(f"El fitxer {ficEste} no té un format WAVE vàlid.")

        # Subchunk1 'fmt ' (offset 12)
        fpEste.seek(12, 0)
        formato = "<4sIHHIIHH"
        datos = fpEste.read(st.calcsize(formato))
        subChunk1ID, subChunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample = st.unpack(formato, datos)

        if subChunk1ID != b"fmt " or audioFormat != 1 or numChannels != 2 or bitsPerSample != 16:
            raise Exception("El fitxer ha de ser PCM, estèreo i de 16 bits.")

        # Subchunk2 'data' (offset 36)
        fpEste.seek(36, 0)
        formato = "<4sI"
        datos = fpEste.read(st.calcsize(formato))
        subChunk2ID, subChunk2Size = st.unpack(formato, datos)

        if subChunk2ID != b"data":
            raise Exception("No s'ha trobat el subchunk 'data' on esperat (offset 36).")
        
        # Llegim les mostres stereo
        numMostres = subChunk2Size // 2  # nombre total de valors de 2 bytes
        formato = f"<{numMostres}h"
        dades = fpEste.read(st.calcsize(formato))
        mostres = st.unpack(formato, dades)

    # Codifiquem les mostres L, R en 32 bits
    codificats = []
    for R, L in zip(mostres[::2], mostres[1::2]):
        semisuma = (L + R) // 2
        semidiferencia = (L - R) // 2
        valor32bits = st.unpack("<I", st.pack("<hh", semisuma, semidiferencia))[0]
        codificats.append(valor32bits) 
    
    subChunk2Size = len(codificats) * 4  # 4 bytes per mostra
    chunkSize = 36 + subChunk2Size

    with open(ficCod, "wb") as fpCod:
        # Capçalera RIFF
        formato = "<4sI4s"
        fpCod.write(st.pack(formato, b"RIFF", chunkSize, b"WAVE"))

        # Subchunk1 'fmt ' (PCM 32 bits mono)
        formato = "<4sIHHIIHH"
        fpCod.write(st.pack(formato, b"fmt ", 16, 1, 1,
                            sampleRate, sampleRate * 4, 4, 32))

        # Subchunk2 'data'
        formato = "<4sI"
        fpCod.write(st.pack(formato, b"data", subChunk2Size))

        # Dades codificades (32 bits unsigned int)
        formato = f"<{len(codificats)}I"
        fpCod.write(st.pack(formato, *codificats))
        


def decEstereo(ficCod, ficEste):
    """
    Llegeix un fitxer WAVE mono de 32 bits amb semisuma i semidiferència codificades,
    i reconstrueix un fitxer estèreo de 16 bits amb els canals esquerre i dret originals.
    """
    with open(ficCod, "rb") as fpCod:
        # Capçalera RIFF
        formato = "<4sI4s"
        dades = fpCod.read(st.calcsize(formato))
        chunkID, chunkSize, format = st.unpack(formato, dades)

        if chunkID != b"RIFF" or format != b"WAVE":
            raise Exception(f"{ficCod} no és un fitxer WAVE vàlid.")

        # Subchunk1 'fmt '
        fpCod.seek(12)
        formato = "<4sIHHIIHH"
        dades = fpCod.read(st.calcsize(formato))
        subChunk1ID, subChunk1Size, audioFormat, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample = st.unpack(formato, dades)

        if subChunk1ID != b"fmt " or audioFormat != 1 or numChannels != 1 or bitsPerSample != 32:
            raise Exception("El fitxer ha de ser mono, PCM i de 32 bits.")

        # Subchunk2 'data'
        fpCod.seek(36)
        formato = "<4sI"
        dades = fpCod.read(st.calcsize(formato))
        subChunk2ID, subChunk2Size = st.unpack(formato, dades)

        if subChunk2ID != b"data":
            raise Exception("No s'ha trobat el subchunk 'data' on esperat (offset 36).")

        # Llegim les mostres codificades (32 bits cada una)
        numMostres = subChunk2Size // 4
        formato = f"<{numMostres}I"
        dades = fpCod.read(st.calcsize(formato))
        codificats = st.unpack(formato, dades)

    # Reconstruïm L i R
    mostresStereo = []
    for cod in codificats:
        bytes32 = st.pack("<I", cod)
        semisuma, semidiferencia = st.unpack("<hh", bytes32)
        L = semisuma + semidiferencia
        R = semisuma - semidiferencia
        mostresStereo.extend([R, L])  

    # Capçaleres del fitxer estèreo (16 bits, 2 canals)
    subChunk2SizeStereo = len(mostresStereo) * 2
    chunkSizeStereo = 36 + subChunk2SizeStereo

    with open(ficEste, "wb") as fpEste:
        # Capçalera RIFF
        formato = "<4sI4s"
        fpEste.write(st.pack(formato, b"RIFF", chunkSizeStereo, b"WAVE"))

        # Subchunk1 'fmt '
        formato = "<4sIHHIIHH"
        fpEste.write(st.pack(formato, b"fmt ", 16, 1, 2,
                             sampleRate, sampleRate * 4, 4, 16))

        # Subchunk2 'data'
        formato = "<4sI"
        fpEste.write(st.pack(formato, b"data", subChunk2SizeStereo))

        # Dades L-R de 16 bits
        formato = f"<{len(mostresStereo)}h"
        fpEste.write(st.pack(formato, *mostresStereo))


#Tkinter
def mono():
    win = tb.Window(themename="darkly")
    win.title("Tractament d'Àudio Estèreo")
    win.geometry("800x500")
    win.resizable(False, False)

    ttk.Label(win, text="Tractament de Senyals Estèreo", font=("Segoe UI", 20, "bold")).pack(pady=10)

    notebook = ttk.Notebook(win)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)

    # === PESTANYA 1: Estèreo a Mono ===
    pest1 = ttk.Frame(notebook)
    notebook.add(pest1, text="Estèreo a Mono")

    entrada_path = tk.StringVar()
    sortida_path = tk.StringVar()
    canal_sel = tk.IntVar(value=2)
    missatge = tk.StringVar()

    frame1 = ttk.Frame(pest1, padding=20)
    frame1.pack(fill='both', expand=True)

    def seleccionar_entrada():
        fitxer = fd.askopenfilename(filetypes=[("Fitxers WAVE", "*.wav")])
        entrada_path.set(fitxer)

    def seleccionar_sortida():
        fitxer = fd.asksaveasfilename(defaultextension=".wav", filetypes=[("Fitxers WAVE", "*.wav")])
        sortida_path.set(fitxer)

    def convertir():
        if entrada_path.get() and sortida_path.get():
            try:
                estereo2mono(entrada_path.get(), sortida_path.get(), canal_sel.get())
                missatge.set("Conversió realitzada correctament.")
            except Exception as e:
                missatge.set(f"Error: {e}")
        else:
            missatge.set("Cal seleccionar els fitxers.")

    # Widgets
    ttk.Button(frame1, text="Fitxer estèreo d'entrada", command=seleccionar_entrada).pack(fill='x')
    ttk.Label(frame1, textvariable=entrada_path, foreground="blue").pack(fill='x')

    ttk.Label(frame1, text="Selecciona canal:").pack(pady=(10, 0))
    canals = [("Esquerre (L)", 0), ("Dret (R)", 1), ("Semisuma (L+R)/2", 2), ("Semidiferència (L-R)/2", 3)]
    for text, val in canals:
        ttk.Radiobutton(frame1, text=text, variable=canal_sel, value=val).pack(anchor='w')

    ttk.Button(frame1, text="Fitxer mono de sortida", command=seleccionar_sortida).pack(fill='x', pady=(10, 0))
    ttk.Label(frame1, textvariable=sortida_path, foreground="blue").pack(fill='x')

    ttk.Button(frame1, text="Convertir a Mono", command=convertir, bootstyle="success").pack(pady=15)
    ttk.Label(frame1, textvariable=missatge, foreground="green").pack()

    
    
        # === PESTANYA 2: Mono a Estèreo ===
    pest2 = ttk.Frame(notebook)
    notebook.add(pest2, text="Mono a Estèreo")

    frame2 = ttk.Frame(pest2, padding=20)
    frame2.pack(fill='both', expand=True)

    entradaL_path = tk.StringVar()
    entradaR_path = tk.StringVar()
    sortidaStereo_path = tk.StringVar()
    missatge2 = tk.StringVar()

    def seleccionar_entradaL():
        fitxer = fd.askopenfilename(filetypes=[("Fitxers WAVE", "*.wav")])
        entradaL_path.set(fitxer)

    def seleccionar_entradaR():
        fitxer = fd.askopenfilename(filetypes=[("Fitxers WAVE", "*.wav")])
        entradaR_path.set(fitxer)

    def seleccionar_sortida_stereo():
        fitxer = fd.asksaveasfilename(defaultextension=".wav", filetypes=[("Fitxers WAVE", "*.wav")])
        sortidaStereo_path.set(fitxer)

    def combinar():
        if entradaL_path.get() and entradaR_path.get() and sortidaStereo_path.get():
            try:
                mono2stereo(entradaL_path.get(), entradaR_path.get(), sortidaStereo_path.get())
                missatge2.set("Conversió feta correctament.")
            except Exception as e:
                missatge2.set(f"Error: {e}")
        else:
            missatge2.set("Cal seleccionar tots els fitxers.")

    # Widgets pestanya 2
    ttk.Button(frame2, text="Canal esquerre (L)", command=seleccionar_entradaL).pack(fill='x')
    ttk.Label(frame2, textvariable=entradaL_path, foreground="blue").pack(fill='x')

    ttk.Button(frame2, text="Canal dret (R)", command=seleccionar_entradaR).pack(fill='x', pady=(5, 0))
    ttk.Label(frame2, textvariable=entradaR_path, foreground="blue").pack(fill='x')

    ttk.Button(frame2, text="Fitxer estèreo de sortida", command=seleccionar_sortida_stereo).pack(fill='x', pady=(10, 0))
    ttk.Label(frame2, textvariable=sortidaStereo_path, foreground="blue").pack(fill='x')

    ttk.Button(frame2, text="Combinar a Estèreo", command=combinar, bootstyle="success").pack(pady=15)
    ttk.Label(frame2, textvariable=missatge2, foreground="green").pack()

    
        # === PESTANYA 3: Codifica Estèreo ===
    pest3 = ttk.Frame(notebook)
    notebook.add(pest3, text="Codifica Estèreo")

    frame3 = ttk.Frame(pest3, padding=20)
    frame3.pack(fill='both', expand=True)

    entradaCod_path = tk.StringVar()
    sortidaCod_path = tk.StringVar()
    missatge3 = tk.StringVar()

    def seleccionar_entrada_cod():
        fitxer = fd.askopenfilename(filetypes=[("Fitxers WAVE", "*.wav")])
        entradaCod_path.set(fitxer)

    def seleccionar_sortida_cod():
        fitxer = fd.asksaveasfilename(defaultextension=".wav", filetypes=[("Fitxers WAVE", "*.wav")])
        sortidaCod_path.set(fitxer)

    def codificar():
        if entradaCod_path.get() and sortidaCod_path.get():
            try:
                codEstereo(entradaCod_path.get(), sortidaCod_path.get())
                missatge3.set("Codificació realitzada correctament.")
            except Exception as e:
                missatge3.set(f"Error: {e}")
        else:
            missatge3.set("Cal seleccionar els fitxers.")

    ttk.Button(frame3, text="Fitxer estèreo d'entrada", command=seleccionar_entrada_cod).pack(fill='x')
    ttk.Label(frame3, textvariable=entradaCod_path, foreground="blue").pack(fill='x')

    ttk.Button(frame3, text="Fitxer codificat de sortida", command=seleccionar_sortida_cod).pack(fill='x', pady=(10, 0))
    ttk.Label(frame3, textvariable=sortidaCod_path, foreground="blue").pack(fill='x')

    ttk.Button(frame3, text="Codificar", command=codificar, bootstyle="success").pack(pady=15)
    ttk.Label(frame3, textvariable=missatge3, foreground="green").pack()


        # === PESTANYA 4: Descodifica Estèreo ===
    pest4 = ttk.Frame(notebook)
    notebook.add(pest4, text="Descodifica Estèreo")

    frame4 = ttk.Frame(pest4, padding=20)
    frame4.pack(fill='both', expand=True)

    entradaDec_path = tk.StringVar()
    sortidaDec_path = tk.StringVar()
    missatge4 = tk.StringVar()

    def seleccionar_entrada_dec():
        fitxer = fd.askopenfilename(filetypes=[("Fitxers WAVE", "*.wav")])
        entradaDec_path.set(fitxer)

    def seleccionar_sortida_dec():
        fitxer = fd.asksaveasfilename(defaultextension=".wav", filetypes=[("Fitxers WAVE", "*.wav")])
        sortidaDec_path.set(fitxer)

    def descodificar():
        if entradaDec_path.get() and sortidaDec_path.get():
            try:
                decEstereo(entradaDec_path.get(), sortidaDec_path.get())
                missatge4.set("Descodificació realitzada correctament.")
            except Exception as e:
                missatge4.set(f"Error: {e}")
        else:
            missatge4.set("Cal seleccionar els fitxers.")

    ttk.Button(frame4, text="Fitxer codificat (32 bits)", command=seleccionar_entrada_dec).pack(fill='x')
    ttk.Label(frame4, textvariable=entradaDec_path, foreground="blue").pack(fill='x')

    ttk.Button(frame4, text="Fitxer estèreo de sortida", command=seleccionar_sortida_dec).pack(fill='x', pady=(10, 0))
    ttk.Label(frame4, textvariable=sortidaDec_path, foreground="blue").pack(fill='x')

    ttk.Button(frame4, text="Descodificar", command=descodificar, bootstyle="success").pack(pady=15)
    ttk.Label(frame4, textvariable=missatge4, foreground="green").pack()



    win.mainloop()

if __name__ == "__main__":
    mono() 