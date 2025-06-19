"""
body.py

Defines the Body class, representing a physical object in the simulation with properties
such as shape, size, mass, color, position, velocity, and trajectory.
"""

class Body:
    def __init__(self, shape, size, tail, mass, color, position, velocity):
        """
        Initializes a new Body with the given properties.
        Stores initial position and velocity for possible resets.
        """
        self.shape = shape
        self.size = int(size)
        self.tail = int(tail)
        self.mass = mass
        self.color = color
        self.position = position
        self.velocity = velocity
        self.initial_position = position
        self.initial_velocity = velocity
        self.trajectory = []