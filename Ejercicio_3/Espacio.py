import math
from Cuerpo import Cuerpo

class Espacio:
	def __init__(self, g=1000.0, dt=1.0):
		self.cuerpos = []
		self.G = g # gravedad
		self.dt = dt # paso temporal
	
	def anadir(self, c):
		if not isinstance(c, Cuerpo):
			raise TypeError("Solo se puede anyadir un 'Cuerpo'")
		self.cuerpos.append(c)

	def vaciar(self):
		self.cuerpos.clear()

	def paso(self):
		n = len(self.cuerpos)
		ax = [0.0] * n #acceleraciones en x
		ay = [0.0] * n #acceleraciones en y

		for i in range(n):
			ci = self.cuerpos[i]
			for j in range(i+1, n):
				cj = self.cuerpos[j]
				dx, dy = cj.x - ci.x, cj.y - ci.y
				r2     = dx*dx + dy*dy + 1e-9
				inv_r3 = 1.0 / (r2 * math.sqrt(r2))
				f      = self.G * inv_r3

				ax_i =  f * dx * cj.masa
				ay_i =  f * dy * cj.masa
				ax_j = -f * dx * ci.masa
				ay_j = -f * dy * ci.masa

				ax[i] += ax_i; ay[i] += ay_i
				ax[j] += ax_j; ay[j] += ay_j

		for i, c in enumerate(self.cuerpos):
			c.vx += ax[i] * self.dt
			c.vy += ay[i] * self.dt
			c.x  += c.vx * self.dt
			c.y  += c.vy * self.dt

			c.traza.append((c.x, c.y))
			if len(c.traza) > c.cola:
				c.traza.pop(0)