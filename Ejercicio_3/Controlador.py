import time, threading

class Controlador:
	def __init__(self, espacio, fps=30):
		self.espacio = espacio
		self.fps = fps
		self.callback = None
		self.run = False

	def setCallback(self, func):
		self.callback = func

	def start(self):
		if self.run:
			return
		self.run = True
		threading.Thread(target=self.loop, daemon=True).start()

	def stop(self):
		self.run = False

	def loop(self):
		periodo = 1 / self.fps
		while self.run:
			t0 = time.perf_counter()
			self.espacio.paso()
			if self.callback:
				self.callback()
			d = periodo - (time.perf_counter()-t0)
			if d>0:
				time.sleep(d)

