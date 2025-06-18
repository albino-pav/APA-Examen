class Cuerpo:
    def __init__(self, forma, tamano, cola, masa, color, posicion, velocidad):
        self.forma = forma
        self.tamano = tamano
        self.cola = int(cola)  # Longitud máxima de la cola
        self.masa = masa
        self.color = color
        self.posicion = posicion
        self.velocidad = velocidad
        self.posicion_inicial = posicion  # Guardar la posición inicial
        self.velocidad_inicial = velocidad  # Guardar la velocidad inicial
        self.trayectoria = []  # Lista para almacenar las posiciones anteriores