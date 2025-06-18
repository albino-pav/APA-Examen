import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import filedialog
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random
import math
import os
import tempfile
import subprocess

# =============== Variables Globals ===============
cossos = []
simulant = False
pausat = False
G = 1.0  # Constant gravitatòria
velocitat_temps = 1.0  # Valor inicial (1x)
finestres_obertes = []  # Llista per controlar finestres secundàries
color_fons = "#000033"
fitxer_temporal_editable = None  # Ruta del fitxer temporal per editar cossos

# =============== Classe del cos ===============
class CosCeleste:
    def __init__(self, forma, mida, massa, color, pos_x, pos_y, vel_x, vel_y):
        self.forma = forma
        self.mida = mida
        self.massa = massa
        self.color = color
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.traj = [(pos_x, pos_y)]

# =============== Funcions gestio de fitxers ===============
def guardar_posicions():
    fitxer = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if fitxer:
        with open(fitxer, 'w') as f:
            for cos in cossos:
                f.write(f"{cos.forma},{cos.mida},{cos.massa},{cos.color},{cos.pos_x},{cos.pos_y},{cos.vel_x},{cos.vel_y}\n")

def carregar_posicions(ax, canvas):
    global cossos
    fitxer = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if fitxer:
        cossos = []
        with open(fitxer, 'r') as f:
            for linia in f:
                parts = linia.strip().split(',')
                if len(parts) == 8:
                    forma, mida, massa, color, pos_x, pos_y, vel_x, vel_y = parts
                    cos = CosCeleste(
                        forma, float(mida), float(massa), color,
                        float(pos_x), float(pos_y), float(vel_x), float(vel_y)
                    )
                    cossos.append(cos)
        dibuixa_tots_els_cossos(ax, canvas)

# =============== Finestra avaluació ===============
def mostra_missatge_avaluacio():
    finestra = tk.Toplevel()
    finestra.title("Nota de la Version RB1.0")
    finestra.geometry("300x100")
    ttk.Label(finestra, text="Ens pots posar un 10 ;)!", font=("Segoe UI", 12)).pack(expand=True, pady=20)
    ttk.Button(finestra, text="Tancar", command=finestra.destroy).pack(pady=5)

# =============== Funció per editar cossos ===============
def obrir_editor_de_cossos():
    global fitxer_temporal_editable

    if not cossos:
        return

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".csv") as fitxer:
        fitxer.write("forma,mida,massa,color,pos_x,pos_y,vel_x,vel_y\n")
        for cos in cossos:
            fitxer.write(f"{cos.forma},{cos.mida},{cos.massa},{cos.color},{cos.pos_x},{cos.pos_y},{cos.vel_x},{cos.vel_y}\n")
        fitxer_temporal_editable = fitxer.name

    subprocess.call(['code', fitxer_temporal_editable])

def recarregar_cossos_editats(ax, canvas):
    global cossos, fitxer_temporal_editable
    if not fitxer_temporal_editable:
        return

    try:
        with open(fitxer_temporal_editable, 'r') as f:
            linies = f.readlines()[1:]  # Salta la capçalera
            cossos = []
            for linia in linies:
                parts = linia.strip().split(',')
                if len(parts) == 8:
                    forma, mida, massa, color, pos_x, pos_y, vel_x, vel_y = parts
                    cos = CosCeleste(
                        forma, float(mida), float(massa), color,
                        float(pos_x), float(pos_y), float(vel_x), float(vel_y)
                    )
                    cossos.append(cos)
        dibuixa_tots_els_cossos(ax, canvas)
    except Exception as e:
        print("Error recarregant fitxer:", e)

# =============== Finestra mostrar ajuda ===============

def mostrar_instruccions():
    ajuda = tk.Toplevel()
    ajuda.title("Instruccions")
    ajuda.geometry("600x500")
    ajuda.configure(bg='black')

    text = tk.Text(ajuda, wrap='word', bg='black', fg='white', font=('Segoe UI', 11))
    text.pack(expand=True, fill='both', padx=10, pady=10)

    instruccions = """
SIMULADOR GRAVITACIONAL – Instruccions d'ús 

Creació de cossos:
- Fes clic a 'Crear cuerpo' (menú o botó) per definir un nou cos.
- Pots indicar forma, mida, massa, color, posició i velocitat inicial.
- També pots crear 10 cossos aleatoris amb un sol clic.

Edició de cossos:
- Ves al menú 'Cuerpos' > 'Editar cuerpo'.
- Es generarà un fitxer temporal que pots modificar amb VS Code.
- Després, guarda'l i usa 'Recarregar cossos editats' per aplicar els canvis.

Control de la simulació:
- 'Inicia': comença la simulació.
- 'Pausa': pausa/continua la simulació.
- 'Reset': elimina tots els cossos.
- 'Termina': surt del programa.

Paràmetres:
- Pots controlar la velocitat temporal i la constant gravitatòria amb sliders o entrada manual.
- També pots canviar el color del fons galàctic.

Guarda i carrega:
- Al menú 'Archivo' pots guardar les posicions actuals o carregar-ne de prèviament desades.

Versió:
- Consulta la pestanya 'Evaluacion' per a la nota actual de la versió.

"""
    text.insert('1.0', instruccions)
    text.config(state='disabled')

# =============== Dibuix ===============
def dibuixa_tots_els_cossos(ax, canvas):
    ax.clear()
    ax.set_facecolor(color_fons)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])

    for cos in cossos:
        if len(cos.traj) > 1:
            xs, ys = zip(*cos.traj)
            ax.plot(xs, ys, color=cos.color, linewidth=1, alpha=0.5)
        ax.plot(cos.pos_x, cos.pos_y, marker=cos.forma, markersize=cos.mida, color=cos.color, linestyle='None')

    canvas.draw()

# =============== Simulació ===============
def actualitza_simulacio(ax, canvas, win):
    global simulant, pausat
    if not simulant or pausat:
        return

    dt = 0.05 * velocitat_temps
    for i, c1 in enumerate(cossos):
        fx, fy = 0, 0
        for j, c2 in enumerate(cossos):
            if i == j:
                continue
            dx = c2.pos_x - c1.pos_x
            dy = c2.pos_y - c1.pos_y
            dist_sq = dx**2 + dy**2 + 0.01
            dist = math.sqrt(dist_sq)
            f = G * c1.massa * c2.massa / dist_sq
            fx += f * dx / dist
            fy += f * dy / dist
        c1.vel_x += fx / c1.massa * dt
        c1.vel_y += fy / c1.massa * dt

    for c in cossos:
        c.pos_x += c.vel_x * dt
        c.pos_y += c.vel_y * dt
        c.traj.append((c.pos_x, c.pos_y))
        if len(c.traj) > 300:
            c.traj.pop(0)

    if cossos:
        xs = [cos.pos_x for cos in cossos]
        ys = [cos.pos_y for cos in cossos]
        marge = 2
        min_x, max_x = min(xs) - marge, max(xs) + marge
        min_y, max_y = min(ys) - marge, max(ys) + marge
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)

    dibuixa_tots_els_cossos(ax, canvas)
    win.after(33, lambda: actualitza_simulacio(ax, canvas, win))

# =============== Tancar tot ===============
def tancar_totes_les_finstres_i_sortir(win):
    for f in finestres_obertes:
        try:
            f.destroy()
        except:
            pass
    win.quit()

# =============== Interfície Principal ===============
def simulador_gravitacional_ui():
    global simulant, pausat, color_fons

    win = tb.Window(themename="darkly")
    win.title("Simulador Gravitacional")
    win.geometry("1200x700")
    win.configure(bg='black')
    win.protocol("WM_DELETE_WINDOW", lambda: tancar_totes_les_finstres_i_sortir(win))

    # Menú superior
    menu_bar = tk.Menu(win)
    win.config(menu=menu_bar)

    # Pestanya Archivo
    archivo_menu = tk.Menu(menu_bar, tearoff=0)
    archivo_menu.add_command(label="Guardar posicions", command=guardar_posicions)
    archivo_menu.add_command(label="Carregar posicions", command=lambda: carregar_posicions(ax, canvas))
    menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

    # Pestanya Evaluacion
    evaluacion_menu = tk.Menu(menu_bar, tearoff=0)
    evaluacion_menu.add_command(label="Nota de la Versió RB1.0", command=mostra_missatge_avaluacio)
    menu_bar.add_cascade(label="Evaluación", menu=evaluacion_menu)

    # Pestanya Cuerpos
    cuerpos_menu = tk.Menu(menu_bar, tearoff=0)
    cuerpos_menu.add_command(label="Crear cuerpo", command=lambda: finestra_crear_cos(win, ax, canvas))
    cuerpos_menu.add_command(label="Editar cuerpo", command=obrir_editor_de_cossos)
    cuerpos_menu.add_command(label="Recarregar cossos editats", command=lambda: recarregar_cossos_editats(ax, canvas))
    menu_bar.add_cascade(label="Cuerpos", menu=cuerpos_menu)

    # Pestanya Ayuda
    ayuda_menu = tk.Menu(menu_bar, tearoff=0)
    ayuda_menu.add_command(label="Instruccions", command=mostrar_instruccions)
    menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)


    frame_principal = ttk.Frame(win)
    frame_principal.pack(fill='both', expand=True)

    frame_canvas = tk.Frame(frame_principal, bg="black", bd=2, relief="solid")
    frame_canvas.pack(side='left', fill='both', expand=True)

    fig, ax = plt.subplots(facecolor=color_fons)
    ax.set_facecolor(color_fons)
    ax.set_title("Simulació", color="white")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='both', expand=True)

    frame_controls = ttk.Frame(frame_principal, padding=15)
    frame_controls.pack(side='right', fill='y')

    ttk.Button(frame_controls, text="Crear Cuerpo", command=lambda: finestra_crear_cos(win, ax, canvas)).pack(pady=10, fill='x')

    ttk.Label(frame_controls, text="Color del fondo galáctico:").pack(anchor='w', pady=(20, 5))
    btn_color_fons = tk.Button(frame_controls, bg=color_fons, width=3, command=lambda: canvia_color_fons(btn_color_fons, ax, canvas, fig, frame_canvas))
    btn_color_fons.pack(anchor='w')

    def canvia_color_fons(boto, ax, canvas, fig, frame_canvas):
        global color_fons
        nou_color = colorchooser.askcolor(initialcolor=color_fons)[1]
        if nou_color:
            color_fons = nou_color
            boto.config(bg=color_fons)
            ax.set_facecolor(color_fons)
            frame_canvas.config(bg=color_fons)
            dibuixa_tots_els_cossos(ax, canvas)

    # === Control de velocitat temporal ===
    ttk.Label(frame_controls, text="Velocidad temporal:").pack(anchor='w', pady=(20, 5))

    velocitat_frame = ttk.Frame(frame_controls)
    velocitat_frame.pack(anchor='w', pady=(0, 10))

    velocitat_var = tk.DoubleVar(value=1.0)

    def actualitza_velocitat_temps(val):
        global velocitat_temps
        try:
            velocitat_temps = float(val)
            velocitat_label.config(text=f"{velocitat_temps:.2f}x")
            if abs(velocitat_slider.get() - velocitat_temps) > 0.01:
                velocitat_slider.set(velocitat_temps)
        except ValueError:
            pass

    velocitat_slider = ttk.Scale(
        velocitat_frame, from_=0.1, to=10.0, orient='horizontal',
        length=120, variable=velocitat_var, command=actualitza_velocitat_temps
    )
    velocitat_slider.pack(side='left')

    velocitat_label = ttk.Label(velocitat_frame, text="1.00x", width=6)
    velocitat_label.pack(side='left', padx=5)

    velocitat_entry = ttk.Entry(velocitat_frame, width=5)
    velocitat_entry.insert(0, "1.0")
    velocitat_entry.pack(side='left')

    def entrada_manual(event=None):
        actualitza_velocitat_temps(velocitat_entry.get())

    velocitat_entry.bind("<Return>", entrada_manual)

    # === Control de constant gravitatòria G ===
    ttk.Label(frame_controls, text="Constante gravitatoria (G):").pack(anchor='w', pady=(20, 5))

    G_frame = ttk.Frame(frame_controls)
    G_frame.pack(anchor='w', pady=(0, 10))

    G_var = tk.DoubleVar(value=1.0)

    def actualitza_G(val):
        global G
        try:
            G = float(val)
            G_label.config(text=f"{G:.2f}")
            if abs(G_slider.get() - G) > 0.01:
                G_slider.set(G)
        except ValueError:
            pass

    G_slider = ttk.Scale(
        G_frame, from_=0.01, to=10.0, orient='horizontal',
        length=120, variable=G_var, command=actualitza_G
    )
    G_slider.pack(side='left')

    G_label = ttk.Label(G_frame, text="1.00", width=6)
    G_label.pack(side='left', padx=5)

    G_entry = ttk.Entry(G_frame, width=5)
    G_entry.insert(0, "1.0")
    G_entry.pack(side='left')

    def entrada_manual_G(event=None):
        actualitza_G(G_entry.get())

    G_entry.bind("<Return>", entrada_manual_G)

    # Botons inferiors
    frame_botons = ttk.Frame(frame_controls)
    frame_botons.pack(pady=20)

    ttk.Button(frame_botons, text="Inicia", bootstyle="success", command=lambda: iniciar_simulacio(ax, canvas, win)).pack(side='left', padx=5)
    ttk.Button(frame_botons, text="Pausa", bootstyle="warning", command=pausar_simulacio).pack(side='left', padx=5)
    ttk.Button(frame_botons, text="Reset", bootstyle="secondary", command=lambda: reiniciar_simulacio(ax, canvas)).pack(side='left', padx=5)
    ttk.Button(frame_botons, text="Termina", bootstyle="danger", command=lambda: tancar_totes_les_finstres_i_sortir(win)).pack(side='left', padx=5)

    win.mainloop()

# =============== Controls ===============
def iniciar_simulacio(ax, canvas, win):
    global simulant, pausat
    simulant = True
    pausat = False
    actualitza_simulacio(ax, canvas, win)

def pausar_simulacio():
    global pausat
    pausat = not pausat

def reiniciar_simulacio(ax, canvas):
    global cossos, simulant
    simulant = False
    cossos = []
    dibuixa_tots_els_cossos(ax, canvas)

# =============== Finestra per crear cos ===============
def finestra_crear_cos(master, ax=None, canvas=None):
    finestra = tk.Toplevel(master)
    finestres_obertes.append(finestra)
    finestra.title("Crear Cuerpo")
    finestra.geometry("500x700")
    finestra.configure(bg='black')

    forma = tk.StringVar(value='*')
    mida = tk.DoubleVar(value=8)
    massa = tk.DoubleVar(value=1.0)
    color = tk.StringVar(value='#FFFF00')
    pos_x = tk.DoubleVar(value=0.0)
    pos_y = tk.DoubleVar(value=0.0)
    vel_x = tk.DoubleVar(value=0.0)
    vel_y = tk.DoubleVar(value=0.0)

    def seleccionar_color():
        nou_color = colorchooser.askcolor(parent=finestra, initialcolor=color.get())[1]
        if nou_color:
            color.set(nou_color)
            mostra_color.config(bg=nou_color)

    def acceptar():
        cos = CosCeleste(
            forma.get(), mida.get(), massa.get(), color.get(),
            pos_x.get(), pos_y.get(), vel_x.get(), vel_y.get()
        )
        cossos.append(cos)
        if ax and canvas:
            dibuixa_tots_els_cossos(ax, canvas)
        finestres_obertes.remove(finestra)
        finestra.destroy()

    def generar_valors_aleatoris():
        forma.set(random.choice(['*', 'o', '^', 's']))
        mida.set(round(random.uniform(5, 12), 1))
        massa.set(round(random.uniform(0.5, 5.0), 2))
        color.set("#{:06x}".format(random.randint(0, 0xFFFFFF)))
        pos_x.set(round(random.uniform(-9, 9), 2))
        pos_y.set(round(random.uniform(-9, 9), 2))
        vel_x.set(round(random.uniform(-1, 1), 2))
        vel_y.set(round(random.uniform(-1, 1), 2))
        actualitza_preview()

    def crear_i_afegir_cos_aleatori():
        generar_valors_aleatoris()
        acceptar()

    def crear_deu_cossos_aleatoris():
        for _ in range(10):
            generar_valors_aleatoris()
            cos = CosCeleste(
                forma.get(), mida.get(), massa.get(), color.get(),
                pos_x.get(), pos_y.get(), vel_x.get(), vel_y.get()
            )
            cossos.append(cos)
        if ax and canvas:
            dibuixa_tots_els_cossos(ax, canvas)
        finestra.destroy()

    def etiqueta(text):
        return ttk.Label(finestra, text=text, background='black', foreground='white')

    etiqueta("Forma:").pack(anchor='w', padx=10, pady=(10, 0))
    ttk.Combobox(finestra, textvariable=forma, values=['*', 'o', '^', 's']).pack(fill='x', padx=10)

    forma_preview = tk.Canvas(finestra, width=60, height=60, bg='black', highlightthickness=0)
    forma_preview.pack(pady=5)

    def actualitza_preview(*args):
        forma_preview.delete("all")
        f = forma.get()
        color_preview = color.get()
        if f == 'o':
            forma_preview.create_oval(20, 20, 40, 40, fill=color_preview, outline=color_preview)
        elif f == '^':
            forma_preview.create_polygon(30, 10, 50, 50, 10, 50, fill=color_preview, outline=color_preview)
        elif f == 's':
            forma_preview.create_rectangle(20, 20, 40, 40, fill=color_preview, outline=color_preview)
        else:
            forma_preview.create_text(30, 30, text=f, fill=color_preview, font=("Segoe UI", 18))

    forma.trace_add('write', actualitza_preview)
    color.trace_add('write', actualitza_preview)
    actualitza_preview()

    for text, var in [("Tamaño:", mida), ("Masa:", massa)]:
        etiqueta(text).pack(anchor='w', padx=10, pady=(10, 0))
        ttk.Entry(finestra, textvariable=var).pack(fill='x', padx=10)

    etiqueta("Color:").pack(anchor='w', padx=10, pady=(10, 0))
    color_frame = ttk.Frame(finestra)
    color_frame.pack(fill='x', padx=10)
    ttk.Entry(color_frame, textvariable=color, width=15).pack(side='left')
    mostra_color = tk.Label(color_frame, width=3, bg=color.get())
    mostra_color.pack(side='left', padx=5)
    ttk.Button(color_frame, text="...", width=3, command=seleccionar_color).pack(side='left')

    for nom, vx, vy in [("Posición", pos_x, pos_y), ("Velocidad", vel_x, vel_y)]:
        marc = ttk.LabelFrame(finestra, text=nom, padding=10)
        marc.pack(fill='x', padx=10, pady=10)
        ttk.Label(marc, text="X:").grid(row=0, column=0)
        ttk.Entry(marc, textvariable=vx).grid(row=0, column=1)
        ttk.Label(marc, text="Y:").grid(row=1, column=0)
        ttk.Entry(marc, textvariable=vy).grid(row=1, column=1)

    boto_frame = ttk.Frame(finestra)
    boto_frame.pack(pady=15)
    ttk.Button(boto_frame, text="Crear Aleatorio", bootstyle="info", command=crear_i_afegir_cos_aleatori).pack(side='left', padx=5)
    ttk.Button(boto_frame, text="Aceptar", bootstyle="success", command=acceptar).pack(side='left', padx=5)
    ttk.Button(boto_frame, text="Salir", bootstyle="danger", command=lambda: [finestres_obertes.remove(finestra), finestra.destroy()]).pack(side='left', padx=5)
    ttk.Button(boto_frame, text="Crear 10 aleatorios", bootstyle="info", command=crear_deu_cossos_aleatoris).pack(side='left', padx=5)


if __name__ == "__main__":
    simulador_gravitacional_ui()
