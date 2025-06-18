from Espacio import Espacio
from Cuerpo  import Cuerpo, CuerpoDialog

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from random   import uniform, choice, random, randint
import pygame

pygame.mixer.init()
pygame.mixer.music.load("Ejercicio_3/musica_ambiente/komm.wav")

W, H = 900, 600 
FORMAS = ['o', '*', '+', 'x', '-']

class Ventana(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Simulador de cuerpos sometidos a atracción Gravitatoria - Oriol Jiménez")
		self.configure(background="#000000")

		self.protocol("WM_DELETE_WINDOW", self.on_close)

		self.espacio = Espacio(g=1000.0, dt=0.08)
		self.anim_running = False
		self.after_id     = None
		self.fps          = 30

		self.columnconfigure(0, weight=1)
		self.rowconfigure   (0, weight=1)

		self.canvas = tk.Canvas(self, width=W, height=H, bg="#001044", highlightthickness=0)
		self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

		self.panel = ttk.Frame(self)
		self.panel.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

		ttk.Button(self.panel, text="Anyadir cuerpo (aleatorio)", command=self.crea_cuerpo_random).pack(fill="x", pady=5)

		ttk.Button(self.panel, text="Crear cuerpo…", command=self.open_manual_cuerpo).pack(fill="x", pady=(0,10))

		self.btn_toggle = tk.Button(self.panel, text="Iniciar", bg="green", fg="white", command=self.toggle_anim)
		self.btn_toggle.pack(fill="x", pady=5)

		ttk.Button(self.panel, text="Reiniciar", command=self.reset).pack(fill="x", pady=5)

		ttk.Separator(self.panel, orient="horizontal").pack(fill="x", pady=10)

		ttk.Label(self.panel, text="Constante gravitatoria").pack(anchor="w")
		self.var_G = tk.DoubleVar(value=1000.0)
		g_scale = tk.Scale(self.panel, from_=0, to=10000, orient="horizontal", variable=self.var_G, resolution=1, command=self.on_change_G)
		g_scale.pack(fill="x")

		ttk.Label(self.panel, text="∆t").pack(anchor="w", pady=(10,0))
		self.var_dt = tk.DoubleVar(value=0.02)
		sd = ttk.Scale(self.panel, from_=0.009, to=0.1, orient="horizontal", variable=self.var_dt, command=self.on_change_dt)
		sd.pack(fill="x")

		ttk.Label(self.panel, text="FPS").pack(anchor="w", pady=(10,0))
		self.var_fps = tk.IntVar(value=self.fps)
		sf = ttk.Scale(self.panel, from_=1, to=60, orient="horizontal", variable=self.var_fps, command=self.on_change_fps)
		sf.pack(fill="x")

		ttk.Label(self.panel, text="Color de fondo").pack(anchor="w", pady=(10,0))
		ttk.Button(self.panel, text="Escoge el color", command=self.pick_color).pack(fill="x")

		self.btn_exit = tk.Button(self.panel, text="Salir", bg="red", fg="white", command=self.on_close)
		self.btn_exit.pack(side="bottom", fill="x", pady=(20, 0))

		self.anim_running = False

	def crea_cuerpo_random(self):
		cx, cy = uniform(-80, 80), uniform(-80, 80)
		vx, vy = uniform(-15,15), uniform(-15,15)

		r = randint(128, 255)
		g = randint(128, 255)
		b = randint(128, 255)
		color = f"#{r:02X}{g:02X}{b:02X}"

		c = Cuerpo(
			forma  = choice(FORMAS),
			tamanyo= randint(2, 15),
			cola   = 200,
			masa   = uniform(0.5, 50),
			color  = color,
			x_inicial = cx,
			y_inicial = cy,
			vel_x = vx,
			vel_y = vy
		)
		self.espacio.anadir(c)
		self.dibuja()

	def open_manual_cuerpo(self):
		CuerpoDialog(self, lambda c: (
			self.espacio.anadir(c),
			self.dibuja()
		))

	def toggle_anim(self):
		if self.anim_running:
			if self.after_id:
				self.after_cancel(self.after_id)
				self.after_id = None
			self.btn_toggle.config(text="Iniciar", bg="green")
			pygame.mixer.music.stop()
		else:
			pygame.mixer.music.play(-1)
			self._schedule_next_frame()
			self.btn_toggle.config(text="Pausar", bg="orange")
		self.anim_running = not self.anim_running

	def reset(self):
		if self.after_id:
			self.after_cancel(self.after_id)
			self.after_id = None
		self.anim_running = False
		self.espacio.vaciar()
		self.dibuja()

	def _schedule_next_frame(self):
		self.espacio.paso()
		self.dibuja()
		delay = int(1000 / self.fps)
		self.after_id = self.after(delay, self._schedule_next_frame)

	def on_change_G(self, _=None):
		self.espacio.G = self.var_G.get()

	def on_change_dt(self, _=None):
		self.espacio.dt = self.var_dt.get()

	def on_change_fps(self, _=None):
		self.fps = self.var_fps.get()

	def pick_color(self):
		col = colorchooser.askcolor(initialcolor=self.canvas["bg"])[1]
		if col:
			self.canvas.configure(bg=col)

	def dibuja(self):
		self.canvas.delete("all")
		cx, cy = W/2, H/2
		esc     = 2
		for c in self.espacio.cuerpos:
			if len(c.traza) > 1:
				pts = []
				for x,y in c.traza:
					pts.extend((cx + x*esc, cy - y*esc))
				self.canvas.create_line(*pts, fill=c.color, width=1)

			x, y = cx + c.x*esc, cy - c.y*esc
			r    = c.tamanyo
			f = c.forma.lower()

			if f == 'o':
				self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=c.color, outline="")
			elif f == '*':
				self.canvas.create_text(x, y, text='★', fill=c.color, font=("Segoe UI", r*2))
			elif f == '+':
				self.canvas.create_line(x-r, y, x+r, y, fill=c.color, width=2)
				self.canvas.create_line(x, y-r, x, y+r, fill=c.color, width=2)
			elif f == 'x':
				self.canvas.create_line(x-r, y-r, x+r, y+r, fill=c.color, width=2)
				self.canvas.create_line(x-r, y+r, x+r, y-r, fill=c.color, width=2)
			elif f == '-':
				self.canvas.create_line(x-r, y, x+r, y, fill=c.color, width=2)
			else:
				self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=c.color, outline="")
				
	def on_close(self):
		try:
			pygame.mixer.music.stop()
		except:
			pass
		pygame.mixer.quit()
		self.destroy()

if __name__ == "__main__":
	Ventana().mainloop()