"""
create_body_window.py

Dialog window for creating and adding new bodies to the simulation.
Allows manual or random creation of bodies with customizable properties.
"""

import tkinter as tk
from tkinter import ttk, colorchooser
import random
from logic.body import Body

def open_create_body_window(root, viewer, simulation):
    """
    Opens a new window for creating a body.
    Lets the user specify properties or create random bodies, and adds them to the simulation.
    """

    body_window = tk.Toplevel(root)
    body_window.title("Create Body")
    body_window.geometry("600x950")

    def draw_body(shape, size, color, position):
        """
        Draws a body with the given shape, size, color, and position on the viewer canvas.
        """
        x, y = position
        r = int(size)
        if shape == "*":
            viewer.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
        elif shape == "+":
            viewer.create_line(x - r, y, x + r, y, fill=color, width=2)
            viewer.create_line(x, y - r, x, y + r, fill=color, width=2)
        elif shape == "X":
            viewer.create_line(x - r, y - r, x + r, y + r, fill=color, width=2)
            viewer.create_line(x - r, y + r, x + r, y - r, fill=color, width=2)
        elif shape == "O":
            viewer.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
        elif shape == ".":
            viewer.create_oval(x - 1, y - 1, x + 1, y + 1, fill=color, outline="")

    def create_random_bodies():
        """
        Creates multiple bodies with random properties and adds them to the simulation.
        """
        for _ in range(random_var.get()):
            shape = random.choice(["*", "+", "X", "O", "."])
            size = random.choice(["1", "2", "4", "6", "8", "10", "12", "14", "16"])
            color = f"#{random.randint(0, 0xFFFFFF):06x}"
            position = (random.uniform(100, 800), random.uniform(100, 800))
            velocity = (random.uniform(-2, 2), random.uniform(-2, 2))
            tail = random.choice(["0", "10", "100", "1000", "10000", "100000", "1000000"])
            mass = random.uniform(3.0, 9.0)
            new_body = Body(shape, size, tail, mass, color, position, velocity)
            simulation.add_body(new_body)
            draw_body(shape, size, color, position)

    def accept_body():
        """
        Creates a new body with the properties specified by the user and adds it to the simulation.
        """
        shape = shape_var.get()
        size = size_var.get()
        tail = tail_var.get()
        mass = mass_var.get()
        color = color_var.get()
        position = (pos_x_var.get(), pos_y_var.get())
        velocity = (vel_x_var.get(), vel_y_var.get())
        new_body = Body(shape, size, tail, mass, color, position, velocity)
        simulation.add_body(new_body)
        x, y = position
        r = int(size)
        viewer.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
        pos_x_var.set(round(random.uniform(0, 900), 2))
        pos_y_var.set(round(random.uniform(0, 900), 2))
        vel_x_var.set(round(random.uniform(-5, 5), 2))
        vel_y_var.set(round(random.uniform(-5, 5), 2))

    shape_frame = tk.Frame(body_window)
    shape_frame.pack(fill=tk.X, pady=5, padx=10)
    shape_label = tk.Label(shape_frame, text="Shape:")
    shape_label.pack(side=tk.LEFT, padx=5)
    shape_var = tk.StringVar(value="*")
    shape_menu = ttk.Combobox(shape_frame, textvariable=shape_var, values=["*", "+", "X", "O", "."])
    shape_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

    size_frame = tk.Frame(body_window)
    size_frame.pack(fill=tk.X, pady=5, padx=10)
    size_label = tk.Label(size_frame, text="Size:")
    size_label.pack(side=tk.LEFT, padx=5)
    size_var = tk.StringVar(value="8")
    size_menu = ttk.Combobox(size_frame, textvariable=size_var, values=["1", "2", "4", "6", "8", "10", "12", "14", "16"])
    size_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

    tail_frame = tk.Frame(body_window)
    tail_frame.pack(fill=tk.X, pady=5, padx=10)
    tail_label = tk.Label(tail_frame, text="Tail:")
    tail_label.pack(side=tk.LEFT, padx=5)
    tail_var = tk.StringVar(value="100")
    tail_menu = ttk.Combobox(tail_frame, textvariable=tail_var, values=["0", "10", "100", "1000", "10e4", "10e5", "10e6"])
    tail_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)

    mass_frame = tk.Frame(body_window)
    mass_frame.pack(fill=tk.X, pady=5, padx=10)
    mass_label = tk.Label(mass_frame, text="Mass:")
    mass_label.pack(side=tk.LEFT, padx=5)
    mass_var = tk.DoubleVar(value=1.0)
    mass_entry = tk.Entry(mass_frame, textvariable=mass_var)
    mass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    color_frame = tk.Frame(body_window)
    color_frame.pack(fill=tk.X, pady=5, padx=10)
    color_label = tk.Label(color_frame, text="Color:")
    color_label.pack(side=tk.LEFT, padx=5)
    color_var = tk.StringVar(value="#FFFF00")
    def select_color():
        """
        Opens a color chooser dialog and sets the color variable to the selected color.
        """
        color = colorchooser.askcolor(title="Select a color")[1]
        if color:
            color_var.set(color)
    color_button = tk.Button(color_frame, text="Select", command=select_color)
    color_button.pack(side=tk.LEFT, padx=5)

    position_frame = tk.LabelFrame(body_window, text="Position")
    position_frame.pack(fill=tk.X, pady=10, padx=10)
    pos_x_label = tk.Label(position_frame, text="X Coordinate:")
    pos_x_label.grid(row=0, column=0, padx=5, pady=5)
    pos_x_var = tk.DoubleVar(value=100)
    pos_x_entry = tk.Entry(position_frame, textvariable=pos_x_var)
    pos_x_entry.grid(row=0, column=1, padx=5, pady=5)
    pos_y_label = tk.Label(position_frame, text="Y Coordinate:")
    pos_y_label.grid(row=1, column=0, padx=5, pady=5)
    pos_y_var = tk.DoubleVar(value=100)
    pos_y_entry = tk.Entry(position_frame, textvariable=pos_y_var)
    pos_y_entry.grid(row=1, column=1, padx=5, pady=5)
    pos_reset_button = tk.Button(position_frame, text="Reset", command=lambda: (pos_x_var.set(0.0), pos_y_var.set(0.0)))
    pos_reset_button.grid(row=2, column=0, columnspan=2, pady=5)

    velocity_frame = tk.LabelFrame(body_window, text="Velocity")
    velocity_frame.pack(fill=tk.X, pady=10, padx=10)
    vel_x_label = tk.Label(velocity_frame, text="X Coordinate:")
    vel_x_label.grid(row=0, column=0, padx=5, pady=5)
    vel_x_var = tk.DoubleVar(value=-2.08)
    vel_x_entry = tk.Entry(velocity_frame, textvariable=vel_x_var)
    vel_x_entry.grid(row=0, column=1, padx=5, pady=5)
    vel_y_label = tk.Label(velocity_frame, text="Y Coordinate:")
    vel_y_label.grid(row=1, column=0, padx=5, pady=5)
    vel_y_var = tk.DoubleVar(value=1.19)
    vel_y_entry = tk.Entry(velocity_frame, textvariable=vel_y_var)
    vel_y_entry.grid(row=1, column=1, padx=5, pady=5)
    vel_reset_button = tk.Button(velocity_frame, text="Reset", command=lambda: (vel_x_var.set(0.0), vel_y_var.set(0.0)))
    vel_reset_button.grid(row=2, column=0, columnspan=2, pady=5)

    random_frame = tk.Frame(body_window)
    random_frame.pack(fill=tk.X, pady=10, padx=10)
    random_button = tk.Button(random_frame, text="Create", command=create_random_bodies)
    random_button.pack(side=tk.LEFT, padx=5)
    random_var = tk.IntVar(value=4)
    random_entry = tk.Entry(random_frame, textvariable=random_var, width=5)
    random_entry.pack(side=tk.LEFT, padx=5)
    random_text = tk.Label(random_frame, text="random bodies")
    random_text.pack(side=tk.LEFT, padx=5)

    buttons_frame = tk.Frame(body_window)
    buttons_frame.pack(fill=tk.X, pady=10, padx=10)
    show_button = tk.Button(buttons_frame, text="Show")
    show_button.pack(side=tk.LEFT, padx=5)
    accept_button = tk.Button(buttons_frame, text="Accept", command=accept_body)
    accept_button.pack(side=tk.LEFT, padx=5)
    exit_button = tk.Button(buttons_frame, text="Exit", command=body_window.destroy)
    exit_button.pack(side=tk.LEFT, padx=5)

    def create_star():
        """
        Creates a massive, stationary star at the center of the canvas and adds it to the simulation.
        """
        shape = "O"
        size = 24
        tail = 0
        mass = 35.0
        color = "#FFFF00"
        position = (450, 450)
        velocity = (0, 0)
        star = Body(shape, size, tail, mass, color, position, velocity)
        simulation.add_body(star)
        draw_body(shape, size, color, position)

    btn_create_star = tk.Button(body_window, text="Create Star", command=create_star)
    btn_create_star.pack(side=tk.TOP, pady=10)