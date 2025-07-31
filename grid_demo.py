"""
Example demonstrating the GUIGrid system for organizing components.
"""

import cv2
import numpy as np

from plugins.cv2_visualization_plugin.gui_base import GUIBase
from plugins.cv2_visualization_plugin.gui_grid import GUIGrid
from plugins.cv2_visualization_plugin.gui_component import GuiComponent

class DemoComponent(GuiComponent):
    """Simple demo component that displays colored rectangles."""
    
    def __init__(self, name: str, color: tuple, width: int = 100, height: int = 100):
        super().__init__(name, width, height)
        self.color = color
        
    def draw(self):
        """Draw a colored rectangle."""
        self.canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        self.canvas[:, :, :3] = self.color  # Set RGB
        self.canvas[:, :, 3] = 255  # Set alpha to fully opaque

def main():
    """Demo the grid system with colored components."""
    
    # Create main window
    main_window = GUIBase("Grid System Demo", 800, 600)
    
    # Create a 3x3 grid
    grid = GUIGrid(
        "demo_grid",
        parent=main_window,
        position=(50, 50),
        rows=3,
        cols=3,
        cell_width=120,
        cell_height=100,
        padding=20
    )
    
    # Colors for demonstration
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (128, 128, 128), # Gray
        (255, 128, 0),  # Orange
        (128, 0, 255)   # Purple
    ]
    
    # Add components to the grid
    for i, color in enumerate(colors):
        component = DemoComponent(f"demo_{i}", color, width=100, height=80)
        grid.add_child_auto(component)
    
    print("Grid Demo Controls:")
    print("- Press 'q' to quit")
    print("- Press 'r' to resize grid to 2x2")
    print("- Press 'e' to resize grid back to 3x3")
    
    try:
        while True:
            # Render and display
            main_window.render()
            main_window.show()
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Resize to 2x2
                grid.resize_grid(2, 2)
                print("Resized grid to 2x2")
            elif key == ord('e'):
                # Resize to 3x3
                grid.resize_grid(3, 3)
                print("Resized grid to 3x3")
                
    finally:
        cv2.destroyAllWindows()
        print("Demo closed.")

if __name__ == "__main__":
    main()
