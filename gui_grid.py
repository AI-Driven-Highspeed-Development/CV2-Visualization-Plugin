import numpy as np
from typing import Tuple, Optional
from .gui_component import GuiComponent

class GUIGrid(GuiComponent):
    """
    A grid layout component that automatically arranges child components in a grid pattern.
    """
    def __init__(
        self, 
        name: str, 
        parent: Optional[GuiComponent] = None, 
        position: Tuple[int, int] = (0, 0),
        rows: int = 2, 
        cols: int = 2,
        cell_width: int = 320,
        cell_height: int = 240,
        padding: int = 10,
        auto_size: bool = True
    ):
        """
        Initialize the grid layout component.
        
        Args:
            name: Name of the grid component
            parent: Parent component
            position: Position relative to parent
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            cell_width: Width of each grid cell
            cell_height: Height of each grid cell
            padding: Padding between grid cells
            auto_size: Whether to auto-size based on grid content
        """
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.padding = padding
        self.grid_children = []  # Track children added to specific grid positions
        
        # Calculate total grid dimensions
        total_width = cols * cell_width + (cols - 1) * padding
        total_height = rows * cell_height + (rows - 1) * padding
        
        super().__init__(name, total_width, total_height, parent, position, auto_size)
        
    def add_child_to_grid(self, child: GuiComponent, row: int, col: int) -> bool:
        """
        Add a child component to a specific grid position.
        
        Args:
            child: The child component to add
            row: Grid row (0-based)
            col: Grid column (0-based)
            
        Returns:
            bool: True if successfully added, False if position is out of bounds
        """
        if row >= self.rows or col >= self.cols or row < 0 or col < 0:
            print(f"Grid position ({row}, {col}) is out of bounds for {self.rows}x{self.cols} grid")
            return False
            
        # Calculate position within the grid
        x = col * (self.cell_width + self.padding)
        y = row * (self.cell_height + self.padding)
        
        # Set the child's position and parent
        child.position = (x, y)
        child.parent = self
        
        # Add to both the general children list and grid-specific tracking
        if child not in self.children:
            self.children.append(child)
            
        # Store grid position info
        grid_info = {'child': child, 'row': row, 'col': col}
        # Remove existing entry if child was already in grid
        self.grid_children = [item for item in self.grid_children if item['child'] != child]
        self.grid_children.append(grid_info)
        
        return True
        
    def add_child_auto(self, child: GuiComponent) -> bool:
        """
        Add a child component to the next available grid position.
        
        Args:
            child: The child component to add
            
        Returns:
            bool: True if successfully added, False if grid is full
        """
        # Find next available position
        for row in range(self.rows):
            for col in range(self.cols):
                # Check if position is occupied
                occupied = any(item['row'] == row and item['col'] == col for item in self.grid_children)
                if not occupied:
                    return self.add_child_to_grid(child, row, col)
                    
        print(f"Grid {self.name} is full ({self.rows}x{self.cols})")
        return False
        
    def remove_child_from_grid(self, child: GuiComponent):
        """
        Remove a child component from the grid.
        
        Args:
            child: The child component to remove
        """
        # Remove from grid tracking
        self.grid_children = [item for item in self.grid_children if item['child'] != child]
        
        # Remove from general children list
        self.remove_child(child)
        
    def get_grid_position(self, child: GuiComponent) -> Optional[Tuple[int, int]]:
        """
        Get the grid position of a child component.
        
        Args:
            child: The child component
            
        Returns:
            Tuple of (row, col) or None if not found
        """
        for item in self.grid_children:
            if item['child'] == child:
                return (item['row'], item['col'])
        return None
        
    def resize_grid(self, rows: int, cols: int):
        """
        Resize the grid and rearrange existing children.
        
        Args:
            rows: New number of rows
            cols: New number of columns
        """
        old_children = list(self.grid_children)
        self.rows = rows
        self.cols = cols
        
        # Recalculate total dimensions
        total_width = cols * self.cell_width + (cols - 1) * self.padding
        total_height = rows * self.cell_height + (rows - 1) * self.padding
        self._width_spec = total_width
        self._height_spec = total_height
        
        # Clear grid tracking
        self.grid_children = []
        
        # Re-add children to new grid
        for item in old_children:
            child = item['child']
            old_row = item['row']
            old_col = item['col']
            
            # If old position fits in new grid, keep it
            if old_row < rows and old_col < cols:
                self.add_child_to_grid(child, old_row, old_col)
            else:
                # Otherwise, add to next available position
                if not self.add_child_auto(child):
                    # If grid is too small, remove the child
                    self.remove_child(child)
                    
    def draw(self):
        """
        Draw the grid background (optional visual grid lines).
        """
        # Create a transparent canvas
        self.canvas = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        
        # Optionally draw grid lines for debugging
        # Uncomment the following lines if you want to see the grid structure
        # import cv2
        # 
        # # Draw vertical grid lines
        # for col in range(1, self.cols):
        #     x = col * (self.cell_width + self.padding) - self.padding // 2
        #     cv2.line(self.canvas, (x, 0), (x, self.height), (128, 128, 128, 100), 1)
        # 
        # # Draw horizontal grid lines
        # for row in range(1, self.rows):
        #     y = row * (self.cell_height + self.padding) - self.padding // 2
        #     cv2.line(self.canvas, (0, y), (self.width, y), (128, 128, 128, 100), 1)
