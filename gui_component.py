from __future__ import annotations
from typing import List, Tuple, Optional, Callable, Union
import numpy as np

class GuiComponent:
    """
    A base class for all GUI components, managing hierarchy, positioning, and rendering.
    """
    def __init__(
        self,
        name: str,
        width: Union[int, Callable[[int], int], str] = 0,
        height: Union[int, Callable[[int], int], str] = 0,
        parent: Optional[GuiComponent] = None,
        position: Tuple[int, int] = (0, 0),
        auto_size: bool = False
    ):
        """
        Initializes a GuiComponent.

        Args:
            name (str): The name of the component.
            width (Union[int, Callable[[int], int], str]): Width of the component. Can be:
                - int: Fixed width
                - Callable: Function that takes children's total width and returns component width
                - str: Special strings like "auto" for automatic sizing
            height (Union[int, Callable[[int], int], str]): Height of the component (same options as width)
            parent (Optional[GuiComponent]): The parent component. Defaults to None.
            position (Tuple[int, int]): The (x, y) position relative to the parent. Defaults to (0, 0).
            auto_size (bool): Whether to automatically size based on children. Defaults to False.
        """
        self.name = name
        self.parent = parent
        self.children: List[GuiComponent] = []
        self.position = position
        self._width_spec = width
        self._height_spec = height
        self.auto_size = auto_size
        self.canvas = None  # Canvas to store rendered output

        if self.parent:
            self.parent.add_child(self)

    def _calculate_size(self, spec: Union[int, Callable[[int], int], str], children_total: int) -> int:
        """
        Calculate the actual size based on the specification and children's total size.
        
        Args:
            spec: The size specification (int, callable, or string)
            children_total: The total size of children
            
        Returns:
            The calculated size
        """
        if isinstance(spec, int):
            return spec
        elif callable(spec):
            return spec(children_total)
        elif isinstance(spec, str):
            if spec == "auto":
                return children_total
            else:
                # Parse expressions like "auto+10", "auto*1.2", etc.
                if "auto" in spec:
                    try:
                        # Replace "auto" with the children_total value
                        expression = spec.replace("auto", str(children_total))
                        # Evaluate simple mathematical expressions
                        return int(eval(expression))
                    except:
                        return children_total
        return 0

    @property
    def width(self) -> int:
        """The width of the component."""
        if self.auto_size or not isinstance(self._width_spec, int):
            children_total_width = max([child.position[0] + child.width for child in self.children] + [0])
            return self._calculate_size(self._width_spec, children_total_width)
        return self._width_spec

    @width.setter
    def width(self, value: Union[int, Callable[[int], int], str]):
        self._width_spec = value

    @property
    def height(self) -> int:
        """The height of the component."""
        if self.auto_size or not isinstance(self._height_spec, int):
            children_total_height = max([child.position[1] + child.height for child in self.children] + [0])
            return self._calculate_size(self._height_spec, children_total_height)
        return self._height_spec

    @height.setter
    def height(self, value: Union[int, Callable[[int], int], str]):
        self._height_spec = value

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


    def _blend_canvas_to_surface(self, canvas_slice: np.ndarray, target_slice: np.ndarray) -> np.ndarray:
        """
        Blends a canvas slice onto a target surface slice, handling channel mismatches.
        
        Args:
            canvas_slice: The source canvas slice to blend
            target_slice: The target surface slice to blend onto
            
        Returns:
            The blended result
        """
        # If canvas has 4 channels (BGRA) and target has 3 (BGR), blend using alpha
        if len(canvas_slice.shape) == 3 and canvas_slice.shape[2] == 4 and len(target_slice.shape) == 3 and target_slice.shape[2] == 3:
            # Extract RGB and alpha channels
            canvas_rgb = canvas_slice[:, :, :3]
            alpha = canvas_slice[:, :, 3:4] / 255.0
            
            # Alpha blending: result = alpha * foreground + (1 - alpha) * background
            return (alpha * canvas_rgb + (1 - alpha) * target_slice).astype(target_slice.dtype)
        else:
            # Direct assignment if channels match
            return canvas_slice

    def render(self, target_surface: Optional[np.ndarray] = None, render_position: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Renders the component and its children on a given surface.
        
        Args:
            target_surface: The surface to render onto
            render_position: Position where this component should be rendered (controlled by parent)
        """
        if target_surface is None:
            raise ValueError("Render called without a surface and no canvas is set.")
        
        # Use render_position if provided by parent, otherwise use own position
        if render_position is not None:
            abs_x, abs_y = render_position
        else:
            abs_x, abs_y = self.abs_position
        
        # Draw this component on the surface
        self.draw()
        
        if self.canvas is not None:
            # Place the rendered surface at the specified position
            h, w = self.canvas.shape[:2]
            target_h, target_w = target_surface.shape[:2]
            
            # Ensure we don't go out of bounds
            end_x = min(abs_x + w, target_w)
            end_y = min(abs_y + h, target_h)
            
            if abs_x >= 0 and abs_y >= 0 and abs_x < target_w and abs_y < target_h:
                # Handle channel mismatch between canvas and target surface
                canvas_slice = self.canvas[0:end_y-abs_y, 0:end_x-abs_x]
                target_slice = target_surface[abs_y:end_y, abs_x:end_x]
                
                # Blend the canvas onto the target surface
                blended = self._blend_canvas_to_surface(canvas_slice, target_slice)
                target_surface[abs_y:end_y, abs_x:end_x] = blended
        
        # Render children at their positions relative to this component's render position
        for child in self.children:
            # Calculate child's absolute position based on this component's render position
            child_abs_x = abs_x + child.position[0]
            child_abs_y = abs_y + child.position[1]
            child.render(target_surface, (child_abs_x, child_abs_y))
            

    def draw(self) -> np.ndarray:
        """
        The drawing logic for the component itself. Subclasses must implement this.
        
        Args:
            surface: The surface to draw on (e.g., a CV2 image).

        Returns:
            The modified surface after drawing the component.
        """
        raise NotImplementedError("Subclasses must implement the draw method.")
        return None

