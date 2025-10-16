import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")

        # Contenedor real donde colocarás tus widgets
        self.content = ttk.Frame(self.canvas)
        self.content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        # Inserta el frame dentro del canvas
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        # Soporte para rueda del ratón
        self.content.bind_all("<MouseWheel>", self._on_mousewheel)
        self.content.bind_all("<Button-4>", self._on_mousewheel)   # Linux
        self.content.bind_all("<Button-5>", self._on_mousewheel)   # Linux

    def _on_mousewheel(self, event):
        # Windows/Mac/Linux
        delta = 0
        if event.num == 4:
            delta = -120
        elif event.num == 5:
            delta = 120
        else:
            delta = -1 * int(event.delta)
        self.canvas.yview_scroll(int(delta/120), "units")
