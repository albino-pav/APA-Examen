import math

class Simulacion:
    def __init__(self):
        self.cuerpos = []
        self.constante_gravitacional = 1.0  # Valor inicial de G

    def agregar_cuerpo(self, cuerpo):
        self.cuerpos.append(cuerpo)

    def calcular_fuerzas(self):
        # Inicializar lista de aceleraciones
        aceleraciones = []

        for i, cuerpo1 in enumerate(self.cuerpos):
            fuerza_total_x = 0
            fuerza_total_y = 0

            for j, cuerpo2 in enumerate(self.cuerpos):
                if i != j:
                    dx = cuerpo2.posicion[0] - cuerpo1.posicion[0]
                    dy = cuerpo2.posicion[1] - cuerpo1.posicion[1]
                    distancia = math.sqrt(dx**2 + dy**2)

                    if distancia > 0:
                        fuerza = self.constante_gravitacional * (cuerpo1.masa * cuerpo2.masa) / (distancia ** 2)
                        fuerza_x = fuerza * (dx / distancia)
                        fuerza_y = fuerza * (dy / distancia)
                        fuerza_total_x += fuerza_x
                        fuerza_total_y += fuerza_y

            # Guardar aceleración total para este cuerpo
            aceleracion_x = fuerza_total_x / cuerpo1.masa
            aceleracion_y = fuerza_total_y / cuerpo1.masa
            aceleraciones.append((aceleracion_x, aceleracion_y))

        return aceleraciones

    def actualizar(self, delta_t):
        aceleraciones = self.calcular_fuerzas()

        for i, cuerpo in enumerate(self.cuerpos):
            # Guardar posición actual en la trayectoria
            cuerpo.trayectoria.append(cuerpo.posicion)
            if len(cuerpo.trayectoria) > cuerpo.cola:
                cuerpo.trayectoria.pop(0)

            # Aplicar aceleración a velocidad
            cuerpo.velocidad = (
                cuerpo.velocidad[0] + aceleraciones[i][0] * delta_t,
                cuerpo.velocidad[1] + aceleraciones[i][1] * delta_t
            )

            # Actualizar posición con nueva velocidad
            cuerpo.posicion = (
                cuerpo.posicion[0] + cuerpo.velocidad[0] * delta_t,
                cuerpo.posicion[1] + cuerpo.velocidad[1] * delta_t
            )
