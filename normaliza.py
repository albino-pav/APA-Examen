## importem les llibreies necessaries per al programa
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import os
import re

## funció per a la lectura de fitxers txt
def leer_archivo(root, inputText, state):
    ## variable per enmagatzemar el nom del fitxer i mostrar-lo per l'article boto
    varMessage = tk.StringVar(root, 'Selecciona un archiu de text')
    
    ## funció de crida del fotcher amd askopenfilename i emmagatzemar dades a traces de al variable  input
    def seltext():
        fichero = fd.askopenfilename(
            title="Selecciona un archiu de text",
            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
        )
        if fichero:
            varMessage.set(f"Archiu seleccionat: {fichero}")
            with open(fichero, 'r', encoding='utf-8') as file:
                content = file.read()
                inputText.set(content)
                state["filename"] = fichero  # Store the original filename

    ## Article per a tigerejar la funció de selecció
    button = ttk.Button(root, textvariable=varMessage, command=seltext)
    button.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

## funció per a mostrar el contigut importat i el modificat en un tk.Text
def View_dual_content(root, inputText, outputText):
    frame = tk.Frame(root, bg='lightcyan')
    frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

    # Input Text Frame
    frame_left = tk.Frame(frame)
    frame_left.grid(row=0, column=0, sticky='nsew', padx=5)
    text_in = tk.Text(frame_left, wrap="word", font=('Arial', 12), state='disabled')
    scrollbar_in = tk.Scrollbar(frame_left, command=text_in.yview)
    text_in.config(yscrollcommand=scrollbar_in.set)
    text_in.grid(row=0, column=0, sticky='nsew')
    scrollbar_in.grid(row=0, column=1, sticky='ns')
    frame_left.grid_rowconfigure(0, weight=1)
    frame_left.grid_columnconfigure(0, weight=1)

    # Output Text Frame
    frame_right = tk.Frame(frame)
    frame_right.grid(row=0, column=1, sticky='nsew', padx=5)
    text_out = tk.Text(frame_right, wrap="word", font=('Arial', 12), state='disabled')
    scrollbar_out = tk.Scrollbar(frame_right, command=text_out.yview)
    text_out.config(yscrollcommand=scrollbar_out.set)
    text_out.grid(row=0, column=0, sticky='nsew')
    scrollbar_out.grid(row=0, column=1, sticky='ns')
    frame_right.grid_rowconfigure(0, weight=1)
    frame_right.grid_columnconfigure(0, weight=1)

    # Bind carregar constantment el text per mostrar
    def bind_text_widget(var, widget):
        def update_text(*_):
            widget.config(state='normal')
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, var.get())
            widget.config(state='disabled')
        var.trace_add("write", update_text)

    bind_text_widget(inputText, text_in)
    bind_text_widget(outputText, text_out)

    # expandeix de forma proporcional els dos frames per al finestra
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
 
## funció clau per normalizar les dades dins del text
def normalizaHoras_text(texto):
    ## nomralitzar paraules en hores del dia
    def a24h(hora, periodo):
        if hora == 12:
            hora = 0
        if periodo == "mañana":
            return hora
        elif periodo == "mediodía":
            return hora + 12 if hora < 12 else 12
        elif periodo == "tarde":
            return hora + 12 if 1 <= hora <= 7 else -1
        elif periodo == "noche":
            return hora + 12 if 8 <= hora <= 11 else 0 if hora == 12 else -1
        elif periodo == "madrugada":
            return hora if 1 <= hora <= 6 else -1
        return -1

    ## funció que retorna les frases insertades ja normalitzades per l'anterior funció
    def normalitzar(match):
        if match.group("formato1"):
            h, m = match.group("h1"), match.group("m1")
            if len(m) == 1:
                return match.group(0)
            return f"{int(h):02}:{int(m):02}"

        if match.group("formato2"):
            h = int(match.group("h2"))
            m = match.group("m2")
            if m:
                m = int(m)
                if m > 59:
                    return match.group(0)
            else:
                m = 0
            if h > 23:
                return match.group(0)
            return f"{h:02}:{m:02}"

        if match.group("formato3"):
            h = int(match.group("h3"))
            if h > 23:
                return match.group(0)
            return f"{h:02}:00"

        if match.group("formato4"):
            h = int(match.group("h4"))
            if "cuarto" in match.group(0):
                m = 15
            elif "media" in match.group(0):
                m = 30
            elif "menos cuarto" in match.group(0):
                h = h - 1 if h > 1 else 12
                m = 45
            else:
                return match.group(0)
            return f"{h % 12:02}:{m:02}"

        if match.group("formato5"):
            h = int(match.group("h5"))
            periodo = match.group("p5").strip()
            pmap = {
                "mañana": "mañana",
                "mediodía": "mediodía",
                "tarde": "tarde",
                "noche": "noche",
                "madrugada": "madrugada"
            }
            p = pmap.get(periodo, "")
            h24 = a24h(h, p)
            if h24 == -1:
                return match.group(0)
            return f"{h24:02}:00"

        return match.group(0)

    ## patro per tal de distinguir quin format d'escriutura es trobar el text per tal de distribuir-lo
    patron = re.compile(r"""
        (?P<formato1>(?P<h1>\d{1,2}):(?P<m1>\d{2}))                         | # 18:30
        (?P<formato2>(?P<h2>\d{1,2})h(?P<m2>\d{1,2})?m?)                    | # 8h, 10h30m
        (?P<formato3>(?P<h3>\d{1,2})\s+en\s+punto)                          | # 7 en punto
        (?P<formato4>(?P<h4>\d{1,2})\s+(y\s+(cuarto|media)|menos\s+cuarto))| # 4 y media
        (?P<formato5>(?P<h5>\d{1,2})\s+de\s+la\s+(?P<p5>mañana|tarde|noche|mediodía|madrugada)) # 7 de la mañana
    """, re.VERBOSE | re.IGNORECASE)


    return patron.sub(normalitzar, texto)

## funció que executa la normalització del text entrant i l'escritura de la variable de sortida
def add_modifier_button(root, inputText, outputText):
    def modifier(in_var, out_var):
        text = in_var.get()
        normalized = normalizaHoras_text(text)
        out_var.set(normalized)

    ## boto que trigereja la funció modifier
    btn_modify = ttk.Button(root, text="Apply Modifications", command=lambda: modifier(inputText, outputText))
    btn_modify.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

## funció final que utlitizar un boto per tal de tigerejar al funció asksaveasfilename per tal de guardar el contingut de la variable normalitzada de forma manual a un fitxer
def add_save_button(root, outputText, state):
    def save_output():
        if not state.get("filename"):
            return

        base, ext = os.path.splitext(state["filename"])
        suggested_name = f"{os.path.basename(base)}_Normalized{ext}"

        filepath = fd.asksaveasfilename(
            title="Guardar archivo modificado",
            defaultextension=ext,
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=suggested_name
        )

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(outputText.get())

    btn_save = ttk.Button(root, text="Save Output", command=save_output)
    btn_save.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

## funció rpincipal
def main():
    ## delcara la finestra del programa i la seva configuració
    win = tk.Tk()
    win.title("Normalitzar Expressions Horàries")
    win.geometry("800x600")
    win.configure(bg='lightcyan')
    ttk.Style().configure('TButton', font=('Arial', 12), padding=10)

    ## declara les variables que interactuen entre les diverses funcions.
    inputText = tk.StringVar(win)
    outputText = tk.StringVar(win)
    state = {"filename": None}  # To store the original file name

    ## activa totes les funcions
    leer_archivo(win, inputText, state)
    add_modifier_button(win, inputText, outputText)
    add_save_button(win, outputText, state)
    View_dual_content(win, inputText, outputText)

    ## mostra el contigut GUI de forma perpetua fins que s'acabi
    win.mainloop()

## Declara com la funció main, la principal del programa
if __name__ == '__main__':
    main()
