import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import estereo
#import simpleaudio as sa
import os, wave, contextlib, tempfile, pathlib 
import pygame

pygame.mixer.init()

TMP_MONO      = "tmp_mono.wav"
TMP_STEREO    = "tmp_estereo.wav"
TMP_CODI      = "tmp_codificado.wav"
TMP_DESCODI   = "tmp_descodificado.wav"

class ManejoSenyales:
	def __init__(self, ventana):
		ventana.title("Programa de Manejo de Señales Estéreo")
		self.nb = ttk.Notebook(ventana)
		self.nb.pack(fill="both", expand=True)

		self.channel = None 

		self.pestanyaEstereoMono()
		self.pestanyaMonoEstereo()
		self.pestanyaCodificar()
		self.pestanyaDescodificar()

	def pestanyaEstereoMono(self):
		contenido = ttk.Frame(self.nb, padding=10)
		self.nb.add(contenido, text="Estereo to Mono")
		contenido.columnconfigure(0, weight=1)
		contenido.columnconfigure(1, weight=0)

		self.inEstereo = None
		self.outMono = None

		btn_obre = ttk.Button(contenido, text="Abrir WAV estéreo", command=self.abrirEstereo)
		btn_obre.grid(row=0, column=0, sticky="ew", padx=20, pady=5)

		self.lblEstereo = ttk.Label(contenido, text="Ningun fichero cargado")
		self.lblEstereo.grid(row=1, column=0, sticky="ew", padx=20, pady=(0,10))

		butReproducirEstereo = ttk.Button(contenido, text="Reproducir estéreo", command=lambda:self.reproducir(self.inEstereo))
		butReproducirEstereo.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

		butParar = ttk.Button(contenido, text="Parar", command=self.parar)
		butParar.grid(row=2, column=1, sticky="ew", padx=20, pady=2)

		butConvertirMono = ttk.Button(contenido, text="Convertir a mono", command=self.convertirMono)
		butConvertirMono.grid(row=3, column=0, sticky="ew", padx=20, pady=5)

		butReproducirMono = ttk.Button(contenido, text="Reproducir mono", command=lambda:self.reproducir(self.outMono))
		butReproducirMono.grid(row=4, column=0, sticky="ew", padx=20, pady=5)
		
		butParar2 = ttk.Button(contenido, text="Parar", command=self.parar)
		butParar2.grid(row=4, column=1, sticky="ew", padx=20, pady=2)

		butGuardarMono = ttk.Button(contenido, text="Guardar mono", command=lambda:self.guardar(self.outMono))
		butGuardarMono.grid(row=5, column=0, sticky="ew", padx=20, pady=5)


	def pestanyaMonoEstereo(self):
		contenido = ttk.Frame(self.nb, padding=10)
		self.nb.add(contenido, text="Mono to Estéreo")
		contenido.columnconfigure(0, weight=1)
		contenido.columnconfigure(1, weight=0)

		self.inMonoL = None
		self.inMonoR = None
		self.outStereo = None

		butAbrirL = ttk.Button(contenido, text="Abrir canal L", command=lambda: self.abrirMono("L"))
		butAbrirL.grid(row=0, column=0, sticky="ew", padx=20, pady=5)

		self.lblMonoL = ttk.Label(contenido, text="Ningun canal L")
		self.lblMonoL.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

		butAbrirR = ttk.Button(contenido, text="Abrir canal R", command=lambda: self.abrirMono("R"))
		butAbrirR.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

		self.lblMonoR = ttk.Label(contenido, text="Ningun canal R")
		self.lblMonoR.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

		butConvertir = ttk.Button(contenido, text="Convertie a estéreo", command=self.convertirEstereo)
		butConvertir.grid(row=4, column=0, sticky="ew", padx=20, pady=5)

		butReproducir = ttk.Button(contenido, text="Reproducir estéreo", command=lambda: self.reproducir(self.outStereo))
		butReproducir.grid(row=5, column=0, sticky="ew", padx=20, pady=5)

		butParar = ttk.Button(contenido, text="Parar", command=self.parar)
		butParar.grid(row=5, column=1, sticky="ew", padx=20, pady=2)

		butGuardar = ttk.Button(contenido, text="Guardar audio estéreo", command=lambda: self.guardar(self.outStereo))
		butGuardar.grid(row=6, column=0, sticky="ew", padx=20, pady=5)


	def pestanyaCodificar(self):
		contenido = ttk.Frame(self.nb)
		self.nb.add(contenido, text="Codificar Estéreo")
		contenido.columnconfigure(0, weight=1)
		contenido.columnconfigure(1, weight=0)

		self.inCodeEstereo = None
		self.outCodeEstereo = None

		butAbrir = ttk.Button(contenido, text="Abrir WAV estéreo", command=self.abrirCodEstereo)
		butAbrir.grid(row=0, column=0, sticky="ew", padx=20, pady=5)

		self.lblCodIn = ttk.Label(contenido, text="Ningun fichero cargado")
		self.lblCodIn.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

		butCod = ttk.Button(contenido, text="Codificar a 32 bits", command=self.codificacion32bits)
		butCod.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

		butReproducir = ttk.Button(contenido, text="Reproducir audio codificado", command=lambda: self.reproducir(self.outCodeEstereo))
		butReproducir.grid(row=3, column=0, sticky="ew", padx=20, pady=5)

		butParar = ttk.Button(contenido, text="Parar", command=self.parar)
		butParar.grid(row=3, column=1, sticky="ew", padx=20, pady=2)

		butGuardar = ttk.Button(contenido, text="Guardar audio codificado", command=lambda: self.guardar(self.outCodeEstereo))
		butGuardar.grid(row=4, column=0, sticky="ew", padx=20, pady=5)


	def pestanyaDescodificar(self):
		contenido = ttk.Frame(self.nb)
		self.nb.add(contenido, text="Descodificar Estéreo")
		contenido.columnconfigure(0, weight=1)
		contenido.columnconfigure(1, weight=0)

		self.inCodEntrada = None
		self.outDecEstereo = None

		butAbrir = ttk.Button(contenido, text="Abrir WAV codificado", command=self.abrirDecodificado)
		butAbrir.grid(row=0, column=0, sticky="ew", padx=20, pady=5)

		self.lblDecIn = ttk.Label(contenido, text="Cap fitxer carregat")
		self.lblDecIn.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

		butDecodificar = ttk.Button(contenido, text="Descodificad a 16 bits", command=self.decodificacion32bits)
		butDecodificar.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

		butReproducir = ttk.Button(contenido, text="Reproducir audio restaurado", command=lambda: self.reproducir(self.outDecEstereo))
		butReproducir.grid(row=3, column=0, sticky="ew", padx=20, pady=5)

		butParar = ttk.Button(contenido, text="Parar", command=self.parar)
		butParar.grid(row=3, column=1, sticky="ew", padx=20, pady=2)

		butGuardar = ttk.Button(contenido, text="Guardar audio estéreo resultante", command=lambda: self.guardar(self.outDecEstereo))
		butGuardar.grid(row=4, column=0, sticky="ew", padx=20, pady=5)



	''' Utils '''

	def abrirEstereo(self):
		self.inEstereo = filedialog.askopenfilename(filetypes=[("WAV","*.wav")])
		if self.inEstereo:
			self.lblEstereo.config(text=os.path.basename(self.inEstereo))

	def abrirMono(self, canal):
		path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
		if not path: return
		if canal == "L":
			self.inMonoL = path
			if path:
				self.lblMonoL.config(text=os.path.basename(path))
		elif canal == "R":
			self.inMonoR = path
			if path:
				self.lblMonoR.config(text=os.path.basename(path))

	def abrirCodEstereo(self):
		self.inCodeEstereo = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
		if self.inCodeEstereo:
			self.lblCodIn.config(text=os.path.basename(self.inCodeEstereo))

	def abrirDecodificado(self):
		self.inCodEntrada = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
		if self.inCodEntrada:
			self.lblDecIn.config(text=os.path.basename(self.inCodEntrada))

	def reproducir(self, ruta):
		if not ruta or not os.path.exists(ruta):
			messagebox.showerror("Error", "No hi ha cap arxiu WAV seleccionat")
			return

		if self.channel and self.channel.get_busy():
			self.channel.stop()

		try:
			snd = pygame.mixer.Sound(ruta)
			self.channel = snd.play()
		except pygame.error as e:
			messagebox.showerror("Error al reproduir", str(e))

	def convertirMono(self):
		if not self.inEstereo:
			messagebox.showerror("Error","Tria un WAV estèreo primer")
			return
		self.outMono = TMP_MONO
		estereo.estereo2mono(self.inEstereo, self.outMono)
		messagebox.showinfo("Fet","Conversió a mono completada")

	def convertirEstereo(self):
		if not (self.inMonoL and self.inMonoR):
			messagebox.showerror("Error","Tria els dos canals mono")
			return
		self.outStereo = TMP_STEREO
		estereo.mono2estereo(self.inMonoL, self.inMonoR, self.outStereo)
		messagebox.showinfo("Fet","Mono→Estèreo completat")

	def guardar(self, origen):
		if not origen or not os.path.exists(origen):
			messagebox.showerror("Error","No hi ha res per guardar"); return
		dest = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV","*.wav")])
		if dest:
			with open(origen,'rb') as f_in, open(dest,'wb') as f_out:
				f_out.write(f_in.read())
			messagebox.showinfo("Guardat",f"Fitxer desat a\n{dest}")

	def codificacion32bits(self):
		if not self.inCodeEstereo:
			messagebox.showerror("Error","Tria un WAV estèreo primer"); return
		self.outCodeEstereo = TMP_CODI
		estereo.codEstereo(self.inCodeEstereo, self.outCodeEstereo)
		messagebox.showinfo("Fet","Codificació completada")

	def decodificacion32bits(self):
		if not self.inCodEntrada:
			messagebox.showerror("Error","Tria el WAV codificat"); return
		self.outDecEstereo = TMP_DESCODI
		estereo.decEstereo(self.inCodEntrada, self.outDecEstereo)
		messagebox.showinfo("Fet","Descodificació completada")

	def parar(self):
		pygame.mixer.stop()
		pygame.mixer.quit()
		pygame.mixer.init()
		self.channel = None

if __name__ == "__main__":
	ventana = tk.Tk()

	ventana.geometry("800x600")
	app = ManejoSenyales(ventana)
	ventana.mainloop()


