"""
widgets.py

Contains custom Tkinter widget classes for the application, such as LabeledSlider,
which combines a label, a slider, and a value display.
"""

import tkinter as tk
from tkinter import ttk

class LabeledSlider(tk.Frame):
    def __init__(self, parent, label, from_, to, initial, command=None):
        """
        Initializes a labeled slider widget with a label, a slider, and a value display.
        Optionally accepts a command to call when the slider value changes.
        """
        super().__init__(parent)
        self.label = tk.Label(self, text=label)
        self.label.pack(side=tk.LEFT, padx=5)

        self.value = tk.StringVar(value=str(initial))
        self.slider = ttk.Scale(self, from_=from_, to=to, orient=tk.HORIZONTAL, command=self._on_slide)
        self.slider.set(initial)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.value_label = tk.Label(self, textvariable=self.value)
        self.value_label.pack(side=tk.LEFT, padx=5)

        self.command = command

    def _on_slide(self, value):
        """
        Updates the displayed value when the slider is moved and calls the command if provided.
        """
        self.value.set(f"{float(value):.1f}")
        if self.command:
            self.command(value)