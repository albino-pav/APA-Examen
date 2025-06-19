"""
simulation.py

Contains the Simulation class, which manages the list of bodies, gravitational interactions,
collision detection and merging, and the update loop for the simulation.
"""

import math
from logic.body import Body

class Simulation:
    def __init__(self):
        """
        Initializes the Simulation with an empty list of bodies and a default gravitational constant.
        """
        self.bodies = []
        self.gravitational_constant = 1.0

    def add_body(self, body):
        """
        Adds a new body to the simulation.
        """
        self.bodies.append(body)

    def detect_and_merge_collisions(self, morphing_enabled):
        """
        Detects collisions between bodies and merges them if morphing is enabled.
        If morphing is disabled, bodies do not merge upon collision.
        """

        if not morphing_enabled:
            return

        bodies_to_remove = []
        new_bodies = []

        for i, body1 in enumerate(self.bodies):
            for j, body2 in enumerate(self.bodies):
                if i != j and body1 not in bodies_to_remove and body2 not in bodies_to_remove:
                    dx = body2.position[0] - body1.position[0]
                    dy = body2.position[1] - body1.position[1]
                    distance = math.sqrt(dx**2 + dy**2)

                    if distance <= (int(body1.size) + int(body2.size)):
                        total_mass = body1.mass + body2.mass
                        total_size = math.sqrt(body1.size**2 + body2.size**2)
                        resulting_velocity = (
                            (body1.velocity[0] * body1.mass + body2.velocity[0] * body2.mass) / total_mass,
                            (body1.velocity[1] * body1.mass + body2.velocity[1] * body2.mass) / total_mass
                        )
                        resulting_position = body1.position if body1.mass >= body2.mass else body2.position
                        resulting_color = body1.color if body1.mass >= body2.mass else body2.color
                        resulting_shape = body1.shape if body1.mass >= body2.mass else body2.shape
                        resulting_size = body1.size if body1.mass >= body2.mass else body2.size
                        resulting_tail = body1.tail if body1.mass >= body2.mass else body2.tail

                        new_body = Body(
                            resulting_shape,
                            total_size,
                            resulting_tail,
                            total_mass,
                            resulting_color,
                            resulting_position,
                            resulting_velocity
                        )
                        new_bodies.append(new_body)
                        bodies_to_remove.append(body1)
                        bodies_to_remove.append(body2)

        for body in bodies_to_remove:
            if body in self.bodies:
                self.bodies.remove(body)

        self.bodies.extend(new_bodies)

    def compute_forces(self, delta_t):
        """
        Computes and applies gravitational forces between all pairs of bodies,
        updating their velocities according to Newton's law of gravitation.
        """

        for i, body1 in enumerate(self.bodies):
            total_force_x = 0
            total_force_y = 0
            for j, body2 in enumerate(self.bodies):
                if i != j:
                    dx = body2.position[0] - body1.position[0]
                    dy = body2.position[1] - body1.position[1]
                    distance = math.sqrt(dx**2 + dy**2)

                    if distance > 0:
                        force = self.gravitational_constant * (body1.mass * body2.mass) / (distance**2)
                        force_x = force * (dx / distance)
                        force_y = force * (dy / distance)
                        total_force_x += force_x
                        total_force_y += force_y

            body1.velocity = (
                body1.velocity[0] + (total_force_x / body1.mass) * delta_t,
                body1.velocity[1] + (total_force_y / body1.mass) * delta_t
            )

    def update(self, delta_t, morphing_enabled):
        """
        Advances the simulation by one time step:
        - Handles collisions and merging if morphing is enabled.
        - Computes gravitational forces and updates velocities.
        - Updates positions and trajectories of all bodies.
        """

        self.detect_and_merge_collisions(morphing_enabled)
        self.compute_forces(delta_t)
        for body in self.bodies:
            body.trajectory.append(body.position)
            if len(body.trajectory) > body.tail:
                body.trajectory.pop(0)
            body.position = (
                body.position[0] + body.velocity[0] * delta_t,
                body.position[1] + body.velocity[1] * delta_t
            )