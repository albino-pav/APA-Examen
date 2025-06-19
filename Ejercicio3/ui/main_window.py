"""
main_window.py

Main application window for the 2D gravitational bodies simulator.
Handles the main GUI, simulation controls, and visualization canvas.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import colorchooser
from ui.create_body_window import open_create_body_window
from logic.simulation import Simulation

def start_application():
    """
    Initializes and runs the main application window.
    Sets up the main canvas, control panels, and simulation logic.
    """

    root = ttk.Window(themename="darkly")
    root.geometry("1400x900")
    root.title("Planetary Simulator")
    root.iconbitmap("assets/galaxia-espiral.ico")

    viewer = tk.Canvas(root, bg="#1a237e", width=900, height=800)
    viewer.pack(side="left", fill="both", expand=True)

    simulation = Simulation()

    def redraw_bodies():
        """
        Redraws all bodies and their trajectories on the canvas based on the current simulation state.
        """
        viewer.delete("all")
        for body in simulation.bodies:
            x, y = body.position
            r = int(body.size)
            shape = body.shape
            color = body.color
            if len(body.trajectory) > 1:
                viewer.create_line(
                    *[coord for pos in body.trajectory for coord in pos],
                    fill=color,
                    width=1
                )
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

    def update_simulation():
        """
        Updates the simulation state by advancing time, applying morphing if enabled,
        and redrawing the bodies. Called periodically while the simulation is running.
        """
        delta_t = time_slider.get()
        simulation.update(delta_t, morphing_enabled.get())
        redraw_bodies()
        if btn_start["text"] == "Pause":
            root.after(33, update_simulation)

    def start_pause_simulation():
        """
        Handles the logic for starting, pausing, and resuming the simulation based on the button state.
        """
        if btn_start["text"] == "Start":
            btn_start.config(text="Pause")
            update_simulation()
        elif btn_start["text"] == "Pause":
            btn_start.config(text="Continue")
        elif btn_start["text"] == "Continue":
            btn_start.config(text="Pause")
            update_simulation()

    controls_frame = ttk.Frame(root, padding=10)
    controls_frame.pack(side=RIGHT, fill=Y)

    buttons_frame = ttk.Frame(controls_frame)
    buttons_frame.pack(side=BOTTOM, fill=X, pady=10)

    btn_start = ttk.Button(buttons_frame, text="Start", bootstyle=SUCCESS, width=10, command=start_pause_simulation)
    btn_start.pack(side=LEFT, padx=5)

    btn_restart = ttk.Button(buttons_frame, text="Restart", bootstyle=WARNING, width=10, command=lambda: restart_simulation())
    btn_restart.pack(side=LEFT, padx=5)

    btn_reset = ttk.Button(buttons_frame, text="Reset", bootstyle=SECONDARY, width=10, command=lambda: reset_simulation())
    btn_reset.pack(side=LEFT, padx=5)

    btn_quit = ttk.Button(buttons_frame, text="Quit", bootstyle=DANGER, width=10, command=root.quit)
    btn_quit.pack(side=LEFT, padx=5)

    color_frame = ttk.Frame(controls_frame)
    color_frame.pack(side=TOP, fill=X, pady=10)

    color_label = ttk.Label(color_frame, text="Galactic background color:")
    color_label.pack(side=LEFT, padx=5)

    def change_background_color():
        """
        Opens a color chooser dialog and sets the canvas background color to the selected color.
        """
        color = colorchooser.askcolor(title="Select a color")[1]
        if color:
            viewer.config(bg=color)

    btn_color = ttk.Button(color_frame, text="Change color", bootstyle=INFO, command=change_background_color)
    btn_color.pack(side=LEFT, padx=5)

    params_frame = ttk.LabelFrame(controls_frame, text="General Parameters")
    params_frame.pack(side=TOP, fill=X, pady=10, padx=5)

    gravity_frame = ttk.Frame(params_frame)
    gravity_frame.pack(fill=X, pady=5)
    gravity_label = ttk.Label(gravity_frame, text="Gravitational Constant:")
    gravity_label.pack(side=LEFT, padx=5)
    def update_gravitational_constant(value):
        """
        Updates the gravitational constant in the simulation with the value from the slider.
        """
        simulation.gravitational_constant = float(value)
    gravity_slider = ttk.Scale(gravity_frame, from_=0.1, to=10, orient=HORIZONTAL, command=update_gravitational_constant)
    gravity_slider.set(5.0)
    gravity_slider.pack(side=LEFT, fill=X, expand=True, padx=10)

    time_frame = ttk.Frame(params_frame)
    time_frame.pack(fill=X, pady=5)
    time_label = ttk.Label(time_frame, text="Time Increment:")
    time_label.pack(side=LEFT, padx=5)
    time_slider = ttk.Scale(time_frame, from_=0.01, to=3.0, orient=HORIZONTAL)
    time_slider.set(0.7)
    time_slider.pack(side=LEFT, fill=X, expand=True, padx=10)

    btn_create_body = ttk.Button(controls_frame, text="Create Body", bootstyle=PRIMARY, command=lambda: open_create_body_window(root, viewer, simulation))
    btn_create_body.pack(side=TOP, pady=10)

    morphing_enabled = ttk.BooleanVar(value=False)
    morphing_frame = ttk.Frame(controls_frame)
    morphing_frame.pack(fill=X, pady=5)
    morphing_checkbox = ttk.Checkbutton(
        morphing_frame,
        text="Enable Morphing",
        variable=morphing_enabled,
        bootstyle=SUCCESS
    )
    morphing_checkbox.pack(side=LEFT, padx=5)

    image_and_text_frame = ttk.Frame(controls_frame)
    image_and_text_frame.pack(fill=X, pady=10)

    from PIL import Image, ImageTk
    image = Image.open("assets/galaxia-espiral.png")
    image = image.resize((180, 180), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    image_label = ttk.Label(image_and_text_frame, image=photo)
    image_label.image = photo
    image_label.pack(pady=(0, 5))

    text_label = ttk.Label(
        image_and_text_frame,
        text="Planetary Simulator",
        font=("Helvetica", 16, "bold")
    )
    text_label.pack()

    small_text_label = ttk.Label(
        image_and_text_frame,
        text="Made by Marti Dominguez",
        font=("Helvetica", 10)
    )
    small_text_label.pack()

    description_text = (
        "This simulator lets you create and visualize the gravitational interactions between multiple bodies in 2D.\n"
        "You can add planets, stars, or random bodies, adjust physical parameters, and watch as they orbit, collide, or escape.\n"
        "\n"
        "How to use:\n"
        "- Use 'Create Body' to manually add a new object with custom properties.\n"
        "- Use 'Create Star' to place a massive, stationary star at the center.\n"
        "- Use the random body generator for quick chaos (see note below).\n"
        "- Adjust the gravitational constant and time increment for different dynamics.\n"
        "- Enable or disable morphing to control whether bodies merge on collision.\n"
        "\n"
        "Notes:\n"
        "- If you use the random body generator, be aware: unpredictable and wild behaviors may occur.\n"
        "- Any resulting black holes, cosmic spaghetti, or existential crises are entirely your responsibility. ;)"
    )
    description_label = ttk.Label(
        image_and_text_frame,
        text=description_text,
        font=("Helvetica", 9),
        justify="left",
        wraplength=250
    )
    description_label.pack(pady=(10, 0))

    def restart_simulation():
        """
        Resets all bodies to their initial positions and velocities, and clears their trajectories.
        """
        for body in simulation.bodies:
            body.position = body.initial_position
            body.velocity = body.initial_velocity
            body.trajectory.clear()
        redraw_bodies()

    def reset_simulation():
        """
        Removes all bodies from the simulation and clears the canvas.
        """
        simulation.bodies.clear()
        viewer.delete("all")

    root.mainloop()