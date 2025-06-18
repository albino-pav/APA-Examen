import tkinter as tk
from tkinter import Toplevel, colorchooser, messagebox, filedialog
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import csv
import random
import os
import ctypes

# ─────────────────────────────────────────────────────────────────────────────
# Classe Cos (amb posició i velocitat inicials guardades)
# ─────────────────────────────────────────────────────────────────────────────
class Cos:
    def __init__(self, forma: str, mida: float, trail: int, massa: float,
                 color: str, posicio, velocitat):
        self.forma  = forma
        self.mida   = mida
        self.massa  = massa
        self.color  = color
        self.pos    = np.array(posicio,   dtype=float)
        self.vel    = np.array(velocitat, dtype=float)
        
        # ▼▼▼ CLAU: Guardem l'estat inicial per a la funció de reiniciar ▼▼▼
        self.pos_inicial = self.pos.copy()
        self.vel_inicial = self.vel.copy()
        
        self.acel   = np.zeros(2,         dtype=float)
        self.hist   = deque(maxlen=trail)

    def actualitza_aceleracio(self, altres, G=9.81, soft=1e-2):
        a = np.zeros(2)
        for b in altres:
            if b is self: continue
            delta = b.pos - self.pos
            dist2 = np.dot(delta, delta) + soft**2
            a += G * b.massa * delta / dist2**1.5
        self.acel = a

    def integra(self, dt):
        self.vel += self.acel * dt
        self.pos += self.vel * dt
        self.hist.append(self.pos.copy())

# ─────────────────────────────────────────────────────────────────────────────
# Paràmetres globals i funcions de creació
# ─────────────────────────────────────────────────────────────────────────────
G_default, dt_default, fps_default = 0.93, 0.0023, 17
G, dt = G_default, dt_default
trail_len, softening, N_planetes = 400, 1e-2, 5

is_running = False # Variable per controlar l'estat de l'animació
cosos, patches, trail_lines = [], [], []
marker_map = {"cercle": 'o', "*": '*', "+": '+', "X": 'x', ".": '.'}

def crea_artistes_matplotlib():
    global patches, trail_lines
    for p in patches: p.remove()
    for t in trail_lines: t.remove()
    patches.clear()
    trail_lines.clear()
    for c in cosos:
        marker = marker_map.get(c.forma, 'o')
        circ = ax.plot([], [], marker, color=c.color, markersize=c.mida * 100)[0]
        line, = ax.plot([], [], color=c.color, lw=1, alpha=0.7)
        patches.append(circ)
        trail_lines.append(line)

def crea_cossos_inicials():
    cosos.clear()
    # Nota per al bernat futur: aixi es creen els inicials
    #cosos.append(Cos(forma="cercle", mida=0.03, trail=trail_len, massa=10.0, color="#ffaa00", posicio=[0.0, 0.0], #velocitat=[0.0, 0.0]))
    #angles = np.linspace(0, 2 * np.pi, N_planetes + 1, endpoint=False)[1:]
    #radii = np.linspace(0.25, 0.6, N_planetes)
    #for ang, r in zip(angles, radii):
    #    x, y = r * np.cos(ang), r * np.sin(ang)
    #    v = np.sqrt(G * cosos[0].massa / r)
    #    vx, vy = -v * np.sin(ang), v * np.cos(ang)
    #    cosos.append(Cos(forma="cercle", mida=0.015, trail=trail_len, massa=0.1, color="#0077ff", posicio=[x, y], #velocitat=[vx, vy]))

def crea_cossos_predefinits():
    cosos.clear()
    cosos.append(Cos(forma="cercle", mida=0.03, trail=trail_len, massa=10.0, color="#ffaa00", posicio=[0.0, 0.0], velocitat=[0.0, 0.0]))
    angles = np.linspace(0, 2 * np.pi, N_planetes + 1, endpoint=False)[1:]
    radii = np.linspace(0.25, 0.6, N_planetes)
    for ang, r in zip(angles, radii):
        x, y = r * np.cos(ang), r * np.sin(ang)
        v = np.sqrt(G * cosos[0].massa / r)
        vx, vy = -v * np.sin(ang), v * np.cos(ang)
        cosos.append(Cos(forma="cercle", mida=0.015, trail=trail_len, massa=0.1, color="#0077ff", posicio=[x, y], velocitat=[vx, vy]))
    
# ─────────────────────────────────────────────────────────────────────────────
# Funcions per al menú i pantalla de benvinguda
# ─────────────────────────────────────────────────────────────────────────────
def mostra_credits():
    credits_window = Toplevel(root)
    credits_window.title("Crèdits")
    credits_window.geometry("400x250")
    ttk.Label(credits_window, text="Simulació Gravetat", font=('Helvetica', 14, 'bold')).pack(pady=10)
    ttk.Label(credits_window, text="Creat per: Bernat Rubiol i Àfrica Abad").pack(pady=5)
    ttk.Label(credits_window, text="Versió: 2.3").pack(pady=5)
    ttk.Label(credits_window, text="Llibreries utilitzades:").pack(pady=5)
    ttk.Label(credits_window, text="tkinter, matplotlib, numpy, ttkbootstrap, deque").pack(pady=5)
    ttk.Button(credits_window, text="Tanca", command=credits_window.destroy).pack(pady=10)

def exporta_csv():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return
    try:
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['forma', 'mida', 'massa', 'color', 'pos_x', 'pos_y', 'vel_x', 'vel_y'])
            for cos in cosos:
                writer.writerow([
                    cos.forma, cos.mida, cos.massa, cos.color,
                    cos.pos_inicial[0], cos.pos_inicial[1],
                    cos.vel_inicial[0], cos.vel_inicial[1]
                ])
        messagebox.showinfo("Èxit", "Dades exportades correctament!")
    except Exception as e:
        messagebox.showerror("Error", f"No s'ha pogut exportar: {str(e)}")

def importa_csv():
    global is_running
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return
    
    try:
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar capçalera
            nous_cossos = []
            for row in reader:
                try:
                    forma, mida, massa, color = row[0], float(row[1]), float(row[2]), row[3]
                    pos = [float(row[4]), float(row[5])]
                    vel = [float(row[6]), float(row[7])]
                    nous_cossos.append(Cos(forma, mida, trail_len, massa, color, pos, vel))
                except (IndexError, ValueError) as e:
                    messagebox.showwarning("Advertència", f"Error en llegir fila: {row}")
                    continue
            
            if nous_cossos:
                was_running = is_running
                if was_running: ani.pause()
                
                # Netegem la simulació actual
                for p in patches: p.remove()
                for t in trail_lines: t.remove()
                cosos.clear()
                patches.clear()
                trail_lines.clear()
                
                # Afegim els nous cossos
                for nou_cos in nous_cossos:
                    cosos.append(nou_cos)
                    marker = marker_map.get(nou_cos.forma, 'o')
                    patches.append(ax.plot([], [], marker, color=nou_cos.color, markersize=nou_cos.mida * 100)[0])
                    trail_lines.append(ax.plot([], [], color=nou_cos.color, lw=1, alpha=0.7)[0])
                
                ani._blit_cache.clear()
                canvas.draw_idle()
                if was_running: ani.resume()
                messagebox.showinfo("Èxit", f"S'han importat {len(nous_cossos)} cossos correctament!")
            else:
                messagebox.showwarning("Advertència", "No s'han trobat dades vàlides per importar.")
    except Exception as e:
        messagebox.showerror("Error", f"No s'ha pogut importar: {str(e)}")

def mostra_benvinguda():
    welcome_window = Toplevel(root)
    welcome_window.title("Benvingut/da")
    welcome_window.geometry("500x450")
    welcome_window.configure(bg='#f0f0f0')
    
    # Estil per a la finestra
    style = ttk.Style()
    style.configure('Welcome.TFrame', background='#f0f0f0')
    style.configure('Title.TLabel', background='#f0f0f0', foreground='#333333', 
                   font=('Helvetica', 16, 'bold'))
    style.configure('Subtitle.TLabel', background='#f0f0f0', foreground='#555555', 
                   font=('Helvetica', 10))
    style.configure('Section.TLabel', background='#f0f0f0', foreground='#444444', 
                   font=('Helvetica', 11, 'bold'))
    style.configure('Feature.TLabel', background='#f0f0f0', foreground='#333333', 
                   font=('Helvetica', 10))
    style.configure('Accent.TButton', background='#4a90e2', foreground='white')
    
    # Frame principal
    main_frame = ttk.Frame(welcome_window, style='Welcome.TFrame', padding=20)
    main_frame.pack(fill=BOTH, expand=True)
    
    # Títol
    ttk.Label(main_frame, text="Benvingut/da al Simulador de Gravetat 2D", 
              style='Title.TLabel').pack(pady=(0, 10))
    
    # Subtítol
    ttk.Label(main_frame, text="Exercici 3 de APA - Simulació de sistemes de partícules", 
              style='Subtitle.TLabel').pack(pady=(0, 30))
    
    # Secció d'autors
    authors_frame = ttk.Frame(main_frame, style='Welcome.TFrame')
    authors_frame.pack(fill=X, pady=(0, 20))
    
    ttk.Label(authors_frame, text="Creat per:", style='Section.TLabel').pack(anchor='w')
    ttk.Label(authors_frame, text="Bernat Rubiol i Àfrica Abad", 
              style='Feature.TLabel').pack(anchor='w', padx=20)
    
    # Secció de característiques
    features_frame = ttk.Frame(main_frame, style='Welcome.TFrame')
    features_frame.pack(fill=X, pady=(0, 30))
    
    ttk.Label(features_frame, text="Característiques principals:", 
              style='Section.TLabel').pack(anchor='w')
    
    features = [
        "• Simulació de gravetat en 2D amb física realista",
        "• Importació/Exportació de configuracions en format CSV",
        "• Afegir múltiples cossos amb paràmetres personalitzats",
        "• Control de paràmetres en temps real",
        "• Visualització de trajectòries (trails)",
        "• Mode DISCO amb efectes visuals especials!"
    ]
    
    for feature in features:
        ttk.Label(features_frame, text=feature, style='Feature.TLabel').pack(anchor='w', padx=20)
    
    # Botó per tancar
    ttk.Button(main_frame, text="Començar l'experiència", command=welcome_window.destroy,
               style='Accent.TButton').pack(pady=10)
    
    # Centrar la finestra
    welcome_window.update_idletasks()
    width = welcome_window.winfo_width()
    height = welcome_window.winfo_height()
    x = (welcome_window.winfo_screenwidth() // 2) - (width // 2)
    y = (welcome_window.winfo_screenheight() // 2) - (height // 2)
    welcome_window.geometry(f'{width}x{height}+{x}+{y}')
    
def obrir_finestra_afegir_cos():
    finestra_nou = Toplevel(root)
    finestra_nou.title("Afegir Nou Cos")
    finestra_nou.geometry("400x650")  # Mida ajustada per als nous controls
    finestra_nou.configure(bg='#1a1a1a')
    
    style = ttk.Style()
    style.configure('Dark.TFrame', background='#1a1a1a')
    style.configure('Dark.TLabel', background='#1a1a1a', foreground='white')
    style.configure('Dark.TLabelframe.Label', background='#1a1a1a', foreground='white')
    style.configure('Dark.TLabelframe', background='#2d2d2d')
    style.configure('Dark.TEntry', fieldbackground='#333333', foreground='white')
    style.configure('Dark.TCombobox', fieldbackground='#333333', foreground='white')
    style.configure('Color.TButton', background='#ff0000')
    style.configure('Horizontal.TScale', background='#1a1a1a')
    
    frame = ttk.Frame(finestra_nou, padding=15, style='Dark.TFrame')
    frame.pack(fill=BOTH, expand=True)
    
    # Variables
    forma_var = tk.StringVar(value="cercle")
    mida_var = tk.DoubleVar(value=0.03)
    massa_var = tk.DoubleVar(value=0.1)
    color_var = tk.StringVar(value="#ff0000")
    quantitat_var = tk.IntVar(value=1)
    trail_var = tk.IntVar(value=20)  # Longitud del trail
    
    # Variables per a posició i velocitat amb valors aleatoris inicials
    pos_x_var = tk.DoubleVar(value=round(np.random.uniform(-1, 1), 2))
    pos_y_var = tk.DoubleVar(value=round(np.random.uniform(-1, 1), 2))
    vel_x_var = tk.DoubleVar(value=round(np.random.uniform(-0.5, 0.5), 2))
    vel_y_var = tk.DoubleVar(value=round(np.random.uniform(-0.5, 0.5), 2))
    random_pos_var = tk.BooleanVar(value=True)
    random_vel_var = tk.BooleanVar(value=True)
    
    def triar_color_nou_cos():
        color = colorchooser.askcolor(title="Tria un color", initialcolor=color_var.get())[1]
        if color:
            color_var.set(color)
            color_btn.configure(style='Color.TButton')
            style.configure('Color.TButton', background=color) 
            actualitza_mostra()
    
    def actualitza_mostra():
        forma = forma_var.get()
        if forma == "cercle":
            text_muestra = "●"  # Cercle sòlid
        elif forma == "*":
            text_muestra = "✱"  # Estrella
        elif forma == "+":
            text_muestra = "+"  # Creu
        elif forma == "X":
            text_muestra = "✖"  # X
        elif forma == ".":
            text_muestra = "•"  # Punt
        else:
            text_muestra = "●"  # Per defecte
        
        muestra_label.config(text=text_muestra, foreground=color_var.get())
        mida_text = int(10 + mida_var.get()/5)
        muestra_label.config(font=('Helvetica', mida_text, 'bold'))
    
    # Widgets amb estil fosc
    ttk.Label(frame, text="Forma:", style='Dark.TLabel').grid(row=0, column=0, sticky=W, pady=3)
    forma_cb = ttk.Combobox(frame, textvariable=forma_var, values=["cercle", "*", "+", "X", "."], 
                state="readonly", style='Dark.TCombobox')
    forma_cb.grid(row=0, column=1, sticky=EW)
    forma_cb.bind('<<ComboboxSelected>>', lambda e: actualitza_mostra())
    
    # Slider per a mida
    ttk.Label(frame, text="Mida (0.01-0.1):", style='Dark.TLabel').grid(row=1, column=0, sticky=W, pady=3)
    mida_slider = ttk.Scale(frame, from_=0.01, to=0.1, variable=mida_var, 
                           command=lambda v: actualitza_mostra(), style='Horizontal.TScale')
    mida_slider.grid(row=1, column=1, sticky=EW)
    ttk.Label(frame, textvariable=mida_var, style='Dark.TLabel').grid(row=1, column=2, padx=5)
    
    # Slider per a trail
    ttk.Label(frame, text="Longitud Trail:", style='Dark.TLabel').grid(row=2, column=0, sticky=W, pady=3)
    trail_slider = ttk.Scale(frame, from_=0, to=100, variable=trail_var, style='Horizontal.TScale')
    trail_slider.grid(row=2, column=1, sticky=EW)
    ttk.Label(frame, textvariable=trail_var, style='Dark.TLabel').grid(row=2, column=2, padx=5)
    
    ttk.Label(frame, text="Massa:", style='Dark.TLabel').grid(row=3, column=0, sticky=W, pady=3)
    ttk.Entry(frame, textvariable=massa_var, style='Dark.TEntry').grid(row=3, column=1, sticky=EW)
    
    ttk.Label(frame, text="Color:", style='Dark.TLabel').grid(row=4, column=0, sticky=W, pady=3)
    color_btn = ttk.Button(frame, text="Tria Color", style='Color.TButton', command=triar_color_nou_cos, 
              bootstyle="outline-secondary")
    color_btn.grid(row=4, column=1, sticky=EW)
    
    # Mostra de la forma
    muestra_frame = ttk.Frame(frame, style='Dark.TFrame')
    muestra_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky='ew')
    ttk.Label(muestra_frame, text="Mostra:", style='Dark.TLabel').pack(side=LEFT)
    muestra_label = ttk.Label(muestra_frame, text="●", 
                            style='Muestra.TLabel', foreground=color_var.get())
    muestra_label.pack(side=LEFT, padx=10)
    
    # Frame per a Posició
    pos_frame = ttk.LabelFrame(frame, text="Posició Inicial", style='Dark.TLabelframe')
    pos_frame.grid(row=6, columnspan=3, sticky=EW, pady=5)
    
    def actualitza_posicio_random():
        if random_pos_var.get():
            pos_x_var.set(round(np.random.uniform(-1, 1), 2))
            pos_y_var.set(round(np.random.uniform(-1, 1), 2))
    
    ttk.Checkbutton(pos_frame, text="Aleatòria", variable=random_pos_var, 
                   command=actualitza_posicio_random, style='Dark.TCheckbutton').pack(anchor=W, pady=2)
    
    pos_manual_frame = ttk.Frame(pos_frame, style='Dark.TFrame')
    pos_manual_frame.pack(fill=X, pady=3)
    
    ttk.Label(pos_manual_frame, text="X:", style='Dark.TLabel').pack(side=LEFT, padx=5)
    ttk.Entry(pos_manual_frame, textvariable=pos_x_var, width=8, style='Dark.TEntry').pack(side=LEFT, padx=5)
    ttk.Label(pos_manual_frame, text="Y:", style='Dark.TLabel').pack(side=LEFT, padx=5)
    ttk.Entry(pos_manual_frame, textvariable=pos_y_var, width=8, style='Dark.TEntry').pack(side=LEFT, padx=5)
    
    # Frame per a Velocitat
    vel_frame = ttk.LabelFrame(frame, text="Velocitat Inicial", style='Dark.TLabelframe')
    vel_frame.grid(row=7, columnspan=3, sticky=EW, pady=5)
    
    def actualitza_velocitat_random():
        if random_vel_var.get():
            vel_x_var.set(round(np.random.uniform(-0.5, 0.5), 2))
            vel_y_var.set(round(np.random.uniform(-0.5, 0.5), 2))
    
    ttk.Checkbutton(vel_frame, text="Aleatòria", variable=random_vel_var, 
                   command=actualitza_velocitat_random, style='Dark.TCheckbutton').pack(anchor=W, pady=2)
    
    vel_manual_frame = ttk.Frame(vel_frame, style='Dark.TFrame')
    vel_manual_frame.pack(fill=X, pady=3)
    
    ttk.Label(vel_manual_frame, text="Vx:", style='Dark.TLabel').pack(side=LEFT, padx=5)
    ttk.Entry(vel_manual_frame, textvariable=vel_x_var, width=8, style='Dark.TEntry').pack(side=LEFT, padx=5)
    ttk.Label(vel_manual_frame, text="Vy:", style='Dark.TLabel').pack(side=LEFT, padx=5)
    ttk.Entry(vel_manual_frame, textvariable=vel_y_var, width=8, style='Dark.TEntry').pack(side=LEFT, padx=5)
    
    # Quantitat
    ttk.Label(frame, text="Quantitat a crear:", style='Dark.TLabel').grid(row=8, column=0, sticky=W, pady=3)
    ttk.Entry(frame, textvariable=quantitat_var, style='Dark.TEntry').grid(row=8, column=1, sticky=EW, pady=3)
    
    def mostra_temporalment():
        btn_muestra.config(state=DISABLED)
        try:
            was_running = is_running
            if was_running:
                ani.pause()
                toggle_btn.config(text="Inicia", bootstyle=SUCCESS)
            
            # Crear cossos temporals
            temps_cossos = []
            quantitat = quantitat_var.get()
            if quantitat < 1:
                quantitat = 1
            
            for _ in range(quantitat):
                if random_pos_var.get():
                    pos = [np.random.uniform(-1, 1), np.random.uniform(-1, 1)]
                else:
                    pos = [pos_x_var.get(), pos_y_var.get()]
                
                if random_vel_var.get():
                    vel = [np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5)]
                else:
                    vel = [vel_x_var.get(), vel_y_var.get()]
                
                temps_cossos.append(Cos(
                    forma=forma_var.get(), 
                    mida=mida_var.get(), 
                    trail=trail_var.get(), 
                    massa=massa_var.get(), 
                    color=color_var.get(), 
                    posicio=pos, 
                    velocitat=vel
                ))
            
            # Afegir els cossos a la simulació temporalment
            temps_patches = []
            temps_trails = []
            
            for c in temps_cossos:
                marker = marker_map.get(c.forma, 'o')
                temps_patches.append(ax.plot([], [], marker, color=c.color, 
                                           markersize=c.mida * 100)[0])
                temps_trails.append(ax.plot([], [], color=c.color, lw=1, alpha=0.7)[0])
            
            # Actualitzar posicions
            for i, c in enumerate(temps_cossos):
                temps_patches[i].set_data([c.pos[0]], [c.pos[1]])
            
            canvas.draw()
            
            # Eliminar després de 2 segons
            def eliminar_temporal():
                for p in temps_patches:
                    p.remove()
                for t in temps_trails:
                    t.remove()
                canvas.draw()
                btn_muestra.config(state=NORMAL)
                if was_running:
                    ani.resume()
                    toggle_btn.config(text="Pausa", bootstyle=DANGER)
            
            finestra_nou.after(2000, eliminar_temporal)
            
        except tk.TclError:
            messagebox.showerror("Error", "Valors numèrics invàlids")
            btn_muestra.config(state=NORMAL)
    
    btn_muestra = ttk.Button(frame, text="Mostra Temporalment", command=mostra_temporalment, 
                           bootstyle="outline-info")
    btn_muestra.grid(row=9, columnspan=2, pady=10, sticky=EW)
    
    def crear_nous_cossos():
        try:
            nous_cossos_llista = []
            quantitat = quantitat_var.get()
            if quantitat < 1:
                quantitat = 1
            
            for _ in range(quantitat):
                # Determinar posició i velocitat segons les opcions
                if random_pos_var.get():
                    pos = [np.random.uniform(-1, 1), np.random.uniform(-1, 1)]
                else:
                    pos = [pos_x_var.get(), pos_y_var.get()]
                
                if random_vel_var.get():
                    vel = [np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5)]
                else:
                    vel = [vel_x_var.get(), vel_y_var.get()]
                
                nous_cossos_llista.append(Cos(
                    forma=forma_var.get(), 
                    mida=mida_var.get(), 
                    trail=trail_var.get(), 
                    massa=massa_var.get(), 
                    color=color_var.get(), 
                    posicio=pos, 
                    velocitat=vel
                ))
            
            afegir_cossos_a_simulacio(nous_cossos_llista)
            finestra_nou.destroy()
        except tk.TclError:
            messagebox.showerror("Error", "Valors numèrics invàlids.")

    ttk.Button(frame, text="Afegir a la Simulació", command=crear_nous_cossos, 
              bootstyle="success").grid(row=10, columnspan=2, pady=10, sticky=EW)
    
    # Actualitzar mostra inicial
    actualitza_mostra()
     
# ─────────────────────────────────────────────────────────────────────────────
# GUI amb ttkbootstrap
# ─────────────────────────────────────────────────────────────────────────────
root = ttk.Window(themename="cosmo")
root.title("Simulació N-body 2D")
root.geometry("1200x800")

# Ruta de la icona (PNG o ICO)
icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'solar-system.png')

try:
    if os.path.exists(icon_path):
        # 1. Icona per a la finestra (amb .ico)
        temp_ico = os.path.join(os.path.dirname(__file__), 'temp_icon.ico')
        img = Image.open(icon_path)
        
        # Convertir a .ico (necessari per a la barra de tasques)
        img.save(temp_ico, format='ICO', sizes=[(32, 32), (48, 48), (64, 64), (128, 128)])
        
        # Assignar a la finestra
        root.iconbitmap(temp_ico)  # Això funciona per a la finestra
        
        # 2. Icona per a la barra de tasques (Windows específic)
        if os.name == 'nt':  # Només en Windows
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("simulacio.nbody.2d")  # Identificador únic
            root.iconbitmap(temp_ico)  # Força la icona a la barra de tasques
        
        # 3. Icona per a la finestra (alternativa amb PhotoImage)
        icon_img = ImageTk.PhotoImage(img)
        root.iconphoto(True, icon_img)  # Això ajuda en alguns entorns
        
        # Neteja (opcional): esborra el fitxer temporal .ico després
        # import time; time.sleep(1); os.remove(temp_ico)
        
    else:
        print(f"⚠️ No s'ha trobat la icona: {icon_path}")
except Exception as e:
    print(f"❌ Error en carregar la icona: {str(e)}")
    
# Crear menú superior
menubar = tk.Menu(root)
root.config(menu=menubar)

# Menú File
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exportar CSV...", command=exporta_csv)
file_menu.add_command(label="Importar CSV...", command=importa_csv)
file_menu.add_separator()
file_menu.add_command(label="Sortir", command=root.quit)

cosos_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Cossos", menu=cosos_menu)
cosos_menu.add_command(label="Crear", command=obrir_finestra_afegir_cos)

# Menú About
help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="About", menu=help_menu)
help_menu.add_command(label="Crèdits", command=mostra_credits)

main_frame = ttk.Frame(root)
main_frame.pack(fill=BOTH, expand=True)

left_frame = ttk.Frame(main_frame)
left_frame.pack(side=LEFT, fill=BOTH, expand=True)

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_aspect('auto')
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

canvas = FigureCanvasTkAgg(fig, master=left_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=BOTH, expand=True)

bg_color = "#00001a"
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)
canvas.draw()

crea_cossos_inicials()
crea_artistes_matplotlib()

def update(_):
    for i, c in enumerate(cosos):
        c.actualitza_aceleracio(cosos, G, softening)
    for c in cosos:
        c.integra(dt)
    for i, c in enumerate(cosos):
        patches[i].set_data([c.pos[0]], [c.pos[1]])
        trail = np.array(c.hist)
        if len(trail) > 1:
            trail_lines[i].set_data(trail[:, 0], trail[:, 1])
    return patches + trail_lines

ani = FuncAnimation(fig, update, interval=int(1000/fps_default), blit=True, cache_frame_data=True)
ani.pause()  # La simulació comença pausada

# ─────────────────────────────────────────────────────────────────────────────
# Frame dreta amb controls
# ─────────────────────────────────────────────────────────────────────────────
right_frame = ttk.Frame(main_frame, padding=10, width=280, style='Dark.TFrame')
right_frame.pack(side=RIGHT, fill=Y)
right_frame.pack_propagate(False)

# Assegura't que el style existeix i té el color fosc
style = ttk.Style()
style.configure('Dark.TFrame', background='#1a1a1a')

def afegir_cossos_a_simulacio(nous_cossos_llista):
    was_running = is_running
    if was_running:
        ani.pause()
    
    for nou_cos in nous_cossos_llista:
        cosos.append(nou_cos)
        marker = marker_map.get(nou_cos.forma, 'o')
        patches.append(ax.plot([], [], marker, color=nou_cos.color, markersize=nou_cos.mida * 100)[0])
        trail_lines.append(ax.plot([], [], color=nou_cos.color, lw=1, alpha=0.7)[0])
    
    ani._blit_cache.clear()
    canvas.draw_idle()
    if was_running:
        ani.resume()

ttk.Button(right_frame, text="Afegir cos", command=obrir_finestra_afegir_cos).pack(fill=X, pady=10)

slider_frame = ttk.LabelFrame(right_frame, text="Paràmetres Globals", style='Dark.TFrame')
slider_frame.pack(fill=X, pady=10)

g_var = tk.DoubleVar(value=G_default)
fps_var = tk.IntVar(value=fps_default)
dt_var = tk.DoubleVar(value=dt_default)
trail_var = tk.IntVar(value=trail_len)

def update_gravity(v):
    global G
    G = g_var.get()
    g_label.config(text=f"Gravetat (G): {G:.2f}")

def update_fps(v):
    fps = fps_var.get()
    ani.event_source.interval = int(1000/fps) if fps > 0 else 1000
    fps_label.config(text=f"FPS: {fps}")

def update_dt(v):
    global dt
    dt = dt_var.get()
    dt_label.config(text=f"Increment (dt): {dt:.4f}")

def update_trail(v):
    global trail_len
    trail_len = trail_var.get()
    for c in cosos:
        c.hist = deque(maxlen=trail_len)
    trail_label.config(text=f"Trail Length: {trail_len}")

g_label = ttk.Label(slider_frame, text=f"Gravetat (G): {g_var.get():.2f}")
g_label.pack(fill=X, padx=5, pady=(5,0))
ttk.Scale(slider_frame, from_=0.1, to=20.0, var=g_var, command=update_gravity).pack(fill=X, padx=5, pady=(0,10))

fps_label = ttk.Label(slider_frame, text=f"FPS: {fps_var.get()}")
fps_label.pack(fill=X, padx=5, pady=(5,0))
ttk.Scale(slider_frame, from_=10, to=120, var=fps_var, command=update_fps).pack(fill=X, padx=5, pady=(0,10))

dt_label = ttk.Label(slider_frame, text=f"Increment (dt): {dt_var.get():.4f}")
dt_label.pack(fill=X, padx=5, pady=(5,0))
ttk.Scale(slider_frame, from_=0.0005, to=0.02, var=dt_var, command=update_dt).pack(fill=X, padx=5, pady=(0,10))

# Slider per controlar la longitud del trail
trail_label = ttk.Label(slider_frame, text=f"Trail Length: {trail_var.get()}")
trail_label.pack(fill=X, padx=5, pady=(5,0))
ttk.Scale(slider_frame, from_=10, to=1000, var=trail_var, command=update_trail).pack(fill=X, padx=5, pady=(0,10))

def tria_color():
    global bg_color, ani
    was_running = is_running
    ani.pause()
    color = colorchooser.askcolor(title="Tria color", initialcolor=bg_color)[1]
    if color:
        bg_color = color
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        canvas_widget.configure(bg=bg_color)
        ani._blit_cache.clear()
        canvas.draw_idle()
    if was_running:
        ani.resume()

# Botó per canviar el color de fons, amb el color del botó igual al color seleccionat
def actualitza_boto_color():
    style.configure('BgColor.TButton', background=bg_color, foreground='white')
    boto_color.config(style='BgColor.TButton')

def tria_color():
    global bg_color, ani
    was_running = is_running
    ani.pause()
    color = colorchooser.askcolor(title="Tria color", initialcolor=bg_color)[1]
    if color:
        bg_color = color
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        canvas_widget.configure(bg=bg_color)
        ani._blit_cache.clear()
        canvas.draw_idle()
        actualitza_boto_color()
    if was_running:
        ani.resume()

boto_color = ttk.Button(right_frame, text="Canvia color de fons", command=tria_color)
boto_color.pack(fill=X, pady=10)
actualitza_boto_color()

bottom_frame = ttk.LabelFrame(right_frame, text="Controls Simulació")
bottom_frame.pack(fill=X, pady=10)

def toggle_simulation():
    global is_running
    if is_running:
        ani.pause()
        is_running = False
        toggle_btn.config(text="Inicia", bootstyle=SUCCESS)
    else:
        ani.resume()
        is_running = True
        toggle_btn.config(text="Pausa", bootstyle=WARNING)

def reinicia_posicions():
    global is_running
    ani.pause()
    is_running = False
    toggle_btn.config(text="Inicia", bootstyle=SUCCESS)
    for c in cosos:
        c.pos = c.pos_inicial.copy()
        c.vel = c.vel_inicial.copy()
        c.hist.clear()
    crea_artistes_matplotlib()
    ani._blit_cache.clear()
    canvas.draw_idle()

def reset_total():
    global is_running
    ani.pause()
    is_running = False
    toggle_btn.config(text="Inicia", bootstyle=SUCCESS)
    crea_cossos_inicials()
    crea_artistes_matplotlib()
    ani._blit_cache.clear()
    canvas.draw_idle()

def sortir():
    root.quit()
    root.destroy()

def inicia_predefinits():
    reset_total()
    crea_cossos_predefinits()
    crea_artistes_matplotlib()
    ani._blit_cache.clear()
    canvas.draw_idle()
    toggle_simulation()
    

def disco_color():
    # Guardar els colors originals
    original_colors = {
        'bg_color': fig.patch.get_facecolor(),
        'ax_color': ax.get_facecolor(),
        'canvas_color': canvas_widget.cget('bg'),
        'cosos': [(c.color, p.get_color(), t.get_color()) 
                 for c, p, t in zip(cosos, patches, trail_lines)]
    }
    
    # No pause/resume, just change colors while animation runs
    def canvi_color_iteracio(n):
        if n == 0:
            # Restaurar colors originals
            fig.patch.set_facecolor(original_colors['bg_color'])
            ax.set_facecolor(original_colors['ax_color'])
            canvas_widget.configure(bg=original_colors['canvas_color'])
            
            for (original_color, original_patch, original_trail), c, p, t in zip(
                original_colors['cosos'], cosos, patches, trail_lines):
                c.color = original_color
                p.set_color(original_patch)
                t.set_color(original_trail)
            
            ani._blit_cache.clear()
            canvas.draw_idle()
            return
            
        # Canvi de color dels cossos i trails
        for c, p, t in zip(cosos, patches, trail_lines):
            nou_color = "#%06x" % random.randint(0, 0xFFFFFF)
            c.color = nou_color
            p.set_color(nou_color)
            t.set_color(nou_color)
            
        # Canvi de color de fons
        nou_bg_color = "#%06x" % random.randint(0, 0xFFFFFF)
        global bg_color
        bg_color = nou_bg_color
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        canvas_widget.configure(bg=bg_color)
        ani._blit_cache.clear()
        canvas.draw_idle()
        
        # Programar la següent iteració
        root.after(200, lambda: canvi_color_iteracio(n - 1))

    # Iniciar l'efecte disco (10 iteracions)
    canvi_color_iteracio(15)

toggle_btn = ttk.Button(bottom_frame, text="Inicia", bootstyle=SUCCESS, command=toggle_simulation)
toggle_btn.pack(side=LEFT, expand=True, fill=X, padx=2, pady=5)
ttk.Button(bottom_frame, text="Reinicia", bootstyle="info", command=reinicia_posicions).pack(side=LEFT, expand=True, fill=X, padx=2, pady=5)
ttk.Button(bottom_frame, text="Eliminar tot", bootstyle="secondary", command=reset_total).pack(side=LEFT, expand=True, fill=X, padx=2, pady=5)

ttk.Button(right_frame, text="Inicia predefinits", bootstyle="primary", command=inicia_predefinits).pack(fill=X, pady=(0,10))
style = ttk.Style()
style.configure("Disco.TButton", foreground="#fff", background="#ff69b4", bordercolor="#ff69b4")
ttk.Button(right_frame, text="DISCO", bootstyle="danger outline", style="Disco.TButton", command=disco_color).pack(fill=X, pady=(0,10))
ttk.Button(right_frame, text="Surt", bootstyle="danger", command=sortir).pack(fill=X, pady=(20,10))

# Mostrar pantalla de benvinguda després d'iniciar l'aplicació
root.after(100, mostra_benvinguda)

root.mainloop()