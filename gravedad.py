import math
import tkinter as tk
from tkinter import ttk, colorchooser


class Cuerpo:
    def __init__(self, x, y, vx, vy, masa, radio, color):
        self.x = x              # Posición en X
        self.y = y              # Posición en Y
        self.vx = vx            # Velocidad en X
        self.vy = vy            # Velocidad en Y
        self.masa = masa        # Masa del cuerpo
        self.radio = radio      # Radio del cuerpo
        self.color = color      # Color del cuerpo

    def distancia(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.hypot(dx, dy)

    def atraccion(self, other, G):
        dx = other.x - self.x
        dy = other.y - self.y
        suavizado = 0.5  
        dist_sq = dx**2 + dy**2 + suavizado**2
        distancia = math.sqrt(dist_sq)
        fuerza = G * other.masa / dist_sq  
        fx = fuerza * dx / distancia
        fy = fuerza * dy / distancia
        return fx, fy
    
    def update(self, fx, fy, dt):
        ax = fx / self.masa
        ay = fy / self.masa
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

class Simulacion:
    def __init__(self):

        # Usaremos unidades escaladas
        self.escalaMasa = 5.972e24      # 1 unidad de masa = masa de la Tierra
        self.escalaDistancia = 1e9          # 1 unidad de distancia = 1 Gm
        self.G_real = 39.5        # m^3 / kg / s^2

        # Escalamos G a nuestras unidades simuladas
        self.G = self.G_real * (self.escalaMasa) / (self.escalaDistancia**3)

        self.cuerpos = []
        self.encendido = False
        self.dt = 0.1             # Paso de tiempo

    def añadirCuerpo(self, cuerpo):
        self.cuerpos.append(cuerpo)

    def reset(self):
        self.cuerpos.clear()

    def fijarDt(self, dt):
        self.dt = dt

    def step(self):
        dt = self.dt
        G = self.G
        n = len(self.cuerpos)

        # Calculamos aceleraciones actuales
        aceleraciones = []
        for i, cuerpo in enumerate(self.cuerpos):
            ax, ay = 0, 0
            for j, other in enumerate(self.cuerpos):
                if i == j:
                    continue
                dx = other.x - cuerpo.x
                dy = other.y - cuerpo.y
                dist_sq = dx**2 + dy**2 + 5**2  
                dist = math.sqrt(dist_sq)
                fuerza = G * other.masa / dist_sq
                ax += fuerza * dx / dist
                ay += fuerza * dy / dist
            aceleraciones.append((ax, ay))

        # Actualizamos posiciones usando la aceleración
        for i, cuerpo in enumerate(self.cuerpos):
            ax, ay = aceleraciones[i]
            cuerpo.x += cuerpo.vx * dt + 0.5 * ax * dt**2
            cuerpo.y += cuerpo.vy * dt + 0.5 * ay * dt**2

        # Recalculamos aceleraciones con nuevas posiciones
        aceleracionesNuevas = []
        for i, cuerpo in enumerate(self.cuerpos):
            ax, ay = 0, 0
            for j, other in enumerate(self.cuerpos):
                if i == j:
                    continue
                dx = other.x - cuerpo.x
                dy = other.y - cuerpo.y
                dist_sq = dx**2 + dy**2 + 5**2  
                dist = math.sqrt(dist_sq)
                fuerza = G * other.masa / dist_sq
                ax += fuerza * dx / dist
                ay += fuerza * dy / dist
            aceleracionesNuevas.append((ax, ay))

        # Actualizamos velocidades con el promedio de aceleraciones
        for i, cuerpo in enumerate(self.cuerpos):
            ax_old, ay_old = aceleraciones[i]
            ax_new, ay_new = aceleracionesNuevas[i]
            cuerpo.vx += 0.5 * (ax_old + ax_new) * dt
            cuerpo.vy += 0.5 * (ay_old + ay_new) * dt

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación Gravitacional")
        self.root.configure(bg='gray15')
        ttk.Style().theme_use('clam')
        ttk.Style().configure('.', foreground='gray70',background='gray30')
        
        
        # Parametros
        self.width = 800
        self.height = 600
        self.sim = Simulacion()
        self.encendido = False

        # Marco
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="black")
        self.canvas.pack(side=tk.LEFT)

        # Panel derecho
        panelControl = ttk.Frame(root)
        panelControl.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Controles de simulacion
        ttk.Button(panelControl, text="Iniciar", command=self.empezar).pack(fill='x')
        ttk.Button(panelControl, text="Pausar", command=self.pausa).pack(fill='x')
        ttk.Button(panelControl, text="Reiniciar", command=self.reset).pack(fill='x')

        # Velocidad
        ttk.Label(panelControl, text="Velocidad: ").pack(pady=5)
        self.velocidad = tk.DoubleVar(value=1)
        ttk.Scale(panelControl, from_=0.1, to=10, variable=self.velocidad, orient='horizontal', command=self.defineVelocidad).pack(fill='x')

        # Crear cuerpo
        ttk.Label(panelControl, text="Añadir cuerpo").pack(pady=10)

        self.entradas = {}
        for label in ["x", "y", "vx", "vy", "masa", "radio"]:
            ttk.Label(panelControl, text=label, background='gray30').pack()
            entrada = ttk.Entry(panelControl, background='gray30')
            entrada.pack(fill='x')
            self.entradas[label] = entrada

        self.color = "#505050"
        ttk.Button(panelControl, text="Color", command=self.eligeColor).pack(pady=5)
        ttk.Button(panelControl, text="Añadir", command=self.añadeCuerpo).pack(fill='x')

        self.dibujar()
    
    def eligeColor(self):
        self.color = colorchooser.askcolor()[1]

    def añadeCuerpo(self):
        try:
            x = float(self.entradas["x"].get())
            y = float(self.entradas["y"].get())
            vx = float(self.entradas["vx"].get())
            vy = float(self.entradas["vy"].get())
            masa = float(self.entradas["masa"].get())
            radio = float(self.entradas["radio"].get())

            cuerpo = Cuerpo(x, y, vx, vy, masa, radio, self.color)
            self.sim.añadirCuerpo(cuerpo)
        except ValueError:
            print("Entrada erronea")

    def defineVelocidad(self, val):
        self.sim.fijarDt(float(val))

    def empezar(self):
        self.encendido = True
        self.run()

    def pausa(self):
        self.encendido = False

    def reset(self):
        self.encendido = False
        self.sim.reset()
        self.canvas.delete("all")

    def run(self):
        if self.encendido:
            self.sim.step()
            self.dibujar()
            self.root.after(16, self.run) 

    def simulacionPantalla(self, x, y):
        cx = self.width // 2
        cy = self.height // 2
        return cx + x, cy - y  

    def pantallaSimulacion(self, x, y):
        cx = self.width // 2
        cy = self.height // 2
        return x - cx, cy - y

    def dibujar(self):
        self.canvas.delete("all")

        self.canvas.delete("all")
    
        # Rejilla
        espaciadoRejilla = 50       # Espaciado en pixels
        cx = self.width // 2
        cy = self.height // 2

        # Lineas verticales
        for x in range(cx % espaciadoRejilla, self.width, espaciadoRejilla):
            self.canvas.create_line(x, 0, x, self.height, fill="#222222")

        # Lineas horizontales
        for y in range(cy % espaciadoRejilla, self.height, espaciadoRejilla):
            self.canvas.create_line(0, y, self.width, y, fill="#222222")

        # Ejes principales
        self.canvas.create_line(cx, 0, cx, self.height, fill="#4444FF", width=2)    # Eje Y
        self.canvas.create_line(0, cy, self.width, cy, fill="#FF4444", width=2)     # Eje X

        for cuerpo in self.sim.cuerpos:
            x, y = self.simulacionPantalla(cuerpo.x, cuerpo.y)
            r = cuerpo.radio
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=cuerpo.color)


if __name__ == "__main__":
    root = tk.Tk()
    gui = Interfaz(root)
    root.mainloop()