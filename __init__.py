"""
CV2 Visualization Plugin

A comprehensive GUI framework for OpenCV-based visualization components.
"""

# Version and metadata
__version__ = "1.0.0"
folder_path = __file__.split("__init__.py")[0]
type_name = "plugin"
requirements = ["opencv-python", "numpy"]

# Import main classes
from .gui_component import GuiComponent
from .gui_base import GUIBase
from .gui_grid import GUIGrid

__all__ = [
    "GuiComponent",
    "GUIBase", 
    "GUIGrid"
]