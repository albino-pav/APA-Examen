import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

class Cuerpo:
	def __init__(self, forma, tamanyo, cola, masa, color, x_inicial, y_inicial, vel_x, vel_y):
		self.forma = forma
		self.tamanyo = tamanyo
		self.cola = cola
		self.masa = masa
		self.color = color
		self.x = x_inicial
		self.y = y_inicial
		self.vx  = vel_x
		self.vy  = vel_y

		self.traza = []


FORMAS = ['o', '*', '+', 'x', '-']

class CuerpoDialog(tk.Toplevel):
	def __init__(self, parent, on_accept):
		super().__init__(parent)
		self.title("Crear Cuerpo")
		self.on_accept = on_accept
		self.resizable(False, False)

		frm = ttk.Frame(self, padding=10)
		frm.grid()

		ttk.Label(frm, text="Forma:").grid(row=0, column=0, sticky="e")
		self.var_forma = tk.StringVar(value=FORMAS[0])
		ttk.Combobox(frm, values=FORMAS, textvariable=self.var_forma, width=3, state="readonly")\
			.grid(row=0, column=1, sticky="w")

		ttk.Label(frm, text="Tamaño:").grid(row=1, column=0, sticky="e")
		self.var_tam = tk.IntVar(value=6)
		ttk.Entry(frm, textvariable=self.var_tam, width=5).grid(row=1, column=1, sticky="w")

		ttk.Label(frm, text="Cola:").grid(row=2, column=0, sticky="e")
		self.var_cola = tk.IntVar(value=100)
		ttk.Entry(frm, textvariable=self.var_cola, width=5).grid(row=2, column=1, sticky="w")

		ttk.Label(frm, text="Masa:").grid(row=3, column=0, sticky="e")
		self.var_masa = tk.DoubleVar(value=1.0)
		ttk.Entry(frm, textvariable=self.var_masa, width=7).grid(row=3, column=1, sticky="w")

		ttk.Label(frm, text="Color:").grid(row=4, column=0, sticky="e")
		self.btn_color = ttk.Button(frm, text=" ", width=3, command=self.pick_color)
		self.btn_color.grid(row=4, column=1, sticky="w")
		self.color = "#ffffff"
		self._update_color_button()

		ttk.Label(frm, text="Posición X:").grid(row=5, column=0, sticky="e")
		self.var_x = tk.DoubleVar(value=0.0)
		ttk.Entry(frm, textvariable=self.var_x, width=8).grid(row=5, column=1, sticky="w")

		ttk.Label(frm, text="Posición Y:").grid(row=6, column=0, sticky="e")
		self.var_y = tk.DoubleVar(value=0.0)
		ttk.Entry(frm, textvariable=self.var_y, width=8).grid(row=6, column=1, sticky="w")

		ttk.Label(frm, text="Vel X:").grid(row=7, column=0, sticky="e")
		self.var_vx = tk.DoubleVar(value=0.0)
		ttk.Entry(frm, textvariable=self.var_vx, width=8).grid(row=7, column=1, sticky="w")

		ttk.Label(frm, text="Vel Y:").grid(row=8, column=0, sticky="e")
		self.var_vy = tk.DoubleVar(value=0.0)
		ttk.Entry(frm, textvariable=self.var_vy, width=8).grid(row=8, column=1, sticky="w")

		btns = ttk.Frame(frm)
		btns.grid(row=9, column=0, columnspan=2, pady=(10,0))
		ttk.Button(btns, text="Aceptar", command=self._on_ok).pack(side="left", padx=5)
		ttk.Button(btns, text="Cancelar", command=self.destroy).pack(side="left")

		self.transient(parent)
		self.grab_set()
		self.wait_window(self)

	def pick_color(self):
		col = colorchooser.askcolor(initialcolor=self.color)[1]
		if col:
			self.color = col
			self._update_color_button()

	def _update_color_button(self):
		self.btn_color.configure(style="Color.TButton")
		style = ttk.Style(self)
		style.configure("Color.TButton", background=self.color)
		# self.btn_color.configure(background=self.color)

	def _on_ok(self):
		try:
			c = Cuerpo(
				forma      = self.var_forma.get(),
				tamanyo    = self.var_tam.get(),
				cola       = self.var_cola.get(),
				masa       = self.var_masa.get(),
				color      = self.color,
				x_inicial  = self.var_x.get(),
				y_inicial  = self.var_y.get(),
				vel_x      = self.var_vx.get(),
				vel_y      = self.var_vy.get(),
			)
		except Exception as e:
			messagebox.showerror("Error", f"Valores inválidos:\n{e}")
			return

		self.on_accept(c)
		self.destroy()
