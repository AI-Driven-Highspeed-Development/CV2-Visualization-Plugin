import cv2
import numpy as np
from typing import Tuple
from .gui_component import GuiComponent

class GUIBase(GuiComponent):
    """A top-level component that represents a window and a canvas to draw on."""
    def __init__(self, name: str, width: int, height: int):
        """Initializes the window with a black canvas."""
        super().__init__(name, width, height)
        self.name = name

    def draw(self):
        """Window-specific drawing logic (e.g., background)."""
        # The canvas is already cleared in the render method.
        # Custom background drawing could go here.
        pass


    def show(self):
        """Displays the window's canvas."""
        if self.canvas is not None:
            cv2.imshow(self.name, self.canvas)


    def render(self):
        """Clears the canvas and renders all child components."""
        if self.canvas is None:
            self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        else:
            self.canvas.fill(0)  # Clear canvas to black
        super().render(self.canvas)
