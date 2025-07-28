from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np

class GuiComponent:
    """
    A base class for all GUI components, managing hierarchy, positioning, and rendering.
    """
    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        parent: Optional[GuiComponent] = None,
        position: Tuple[int, int] = (0, 0),
        canvas: Optional[np.ndarray] = None,
    ):
        """
        Initializes a GuiComponent.

        Args:
            name (str): The name of the component.
            width (int): The width of the component.
            height (int): The height of the component.
            parent (Optional[GuiComponent]): The parent component. Defaults to None.
            position (Tuple[int, int]): The (x, y) position relative to the parent. Defaults to (0, 0).
            canvas (Optional[np.ndarray]): The canvas to draw on. Defaults to None.
        """
        self.name = name
        self.parent = parent
        self.children: List[GuiComponent] = []
        self.position = position
        self._width = width
        self._height = height
        self.canvas = canvas

        if self.parent:
            self.parent.add_child(self)

    @property
    def width(self) -> int:
        """The width of the component."""
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value

    @property
    def height(self) -> int:
        """The height of the component."""
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value

    @property
    def abs_position(self) -> Tuple[int, int]:
        """The absolute (x, y) position on the base component (screen)."""
        if self.parent:
            parent_abs_pos = self.parent.abs_position
            return (parent_abs_pos[0] + self.position[0], parent_abs_pos[1] + self.position[1])
        return self.position

    @property
    def total_width(self) -> int:
        """The total width of the component, including outbound children."""
        max_r_x = self.width
        for child in self.children:
            child_r_x = child.position[0] + child.total_width
            if child_r_x > max_r_x:
                max_r_x = child_r_x
        return max_r_x

    @property
    def total_height(self) -> int:
        """The total height of the component, including outbound children."""
        max_r_y = self.height
        for child in self.children:
            child_r_y = child.position[1] + child.total_height
            if child_r_y > max_r_y:
                max_r_y = child_r_y
        return max_r_y

    def add_child(self, child: GuiComponent):
        """Adds a child component."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child: GuiComponent):
        """Removes a child component."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def render(self, surface: Optional[np.ndarray] = None):
        """
        Renders the component and its children on a given surface.
        This method should be overridden by subclasses to provide specific drawing logic.
        """
        # 1. Draw this component on the surface (subclass responsibility)
        target_surface = surface if surface is not None else self.canvas
        if target_surface is None:
            raise ValueError("Render called without a surface and no canvas is set.")

        target_surface = self.draw(target_surface)
        if target_surface is None:
            raise ValueError("Draw method did not return a valid surface.")
        
        # 2. Recursively render children
        for child in self.children:
            target_surface = child.render(target_surface)

    def draw(self, surface: np.ndarray) -> np.ndarray:
        """
        The drawing logic for the component itself. Subclasses must implement this.
        
        Args:
            surface: The surface to draw on (e.g., a CV2 image).

        Returns:
            The modified surface after drawing the component.
        """
        raise NotImplementedError("Subclasses must implement the draw method.")
        return surface

