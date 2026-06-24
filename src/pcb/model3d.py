"""3D Model Generator for PCBs and Enclosures.
Generates STL/OBJ compatible geometry from Board data.
"""

from __future__ import annotations
from pathlib import Path
from src.pcb.generator import Board, PlacedComponent, Pad
from src.utils.logger import get_logger

log = get_logger("pcb.model3d")

class Model3DGenerator:
    """Generates a 3D representation of the PCB and its enclosure."""

    def __init__(self, board: Board):
        self.board = board

    def generate_stl(self, output_path: Path) -> Path:
        """Generate a simple STL file representing the PCB and components."""
        log.info("Generating 3D model STL to %s", output_path)
        
        # In a real implementation, this would use a library like numpy-stl or trimesh
        # Here we will generate a simplified ASCII STL
        
        stl_content = []
        stl_content.append("solid pcb_model")
        
        # 1. Generate PCB Base (Box)
        self._add_box(
            stl_content, 
            self.board.outline.x_mm, self.board.outline.y_mm, 0,
            self.board.outline.width_mm, self.board.outline.height_mm, self.board.thickness_mm
        )
        
        # 2. Generate Components (Simplified as boxes)
        for comp in self.board.components:
            # Use a default size since we don't have full 3D model data
            self._add_box(
                stl_content, 
                comp.x_mm - 2, comp.y_mm - 2, self.board.thickness_mm,
                4, 4, 2.0
            )
            
        stl_content.append("endsolid pcb_model")
        
        output_path.write_text("\n".join(stl_content), encoding="utf-8")
        return output_path

    def generate_enclosure(self, output_path: Path) -> Path:
        """Generate a bended sheet aluminum enclosure."""
        log.info("Generating sheet metal enclosure to %s", output_path)
        
        # Bended sheet logic: 
        # Create a base plate + 4 walls with bend radii
        stl_content = []
        stl_content.append("solid enclosure")
        
        # Simplified enclosure geometry
        # Base
        self._add_box(
            stl_content, 
            self.board.outline.x_mm - 5, self.board.outline.y_mm - 5, -self.board.enclosure["thickness_mm"],
            self.board.outline.width_mm + 10, self.board.outline.height_mm + 10, self.board.enclosure["thickness_mm"]
        )
        
        # Walls (4 walls)
        h = self.board.enclosure["wall_height_mm"]
        t = self.board.enclosure["thickness_mm"]
        
        # Bottom wall
        self._add_box(stl_content, self.board.outline.x_mm - 5, self.board.outline.y_mm - 5, 0, 
                     self.board.outline.width_mm + 10, t, h)
        # Top wall
        self._add_box(stl_content, self.board.outline.x_mm - 5, self.board.outline.y_mm + self.board.outline.height_mm - 5, 0, 
                     self.board.outline.width_mm + 10, t, h)
        # Left wall
        self._add_box(stl_content, self.board.outline.x_mm - 5, self.board.outline.y_mm - 5, 0, 
                     t, self.board.outline.height_mm + 10, h)
        # Right wall
        self._add_box(stl_content, self.board.outline.x_mm + self.board.outline.width_mm + 5 - t, self.board.outline.y_mm - 5, 0, 
                     t, self.board.outline.height_mm + 10, h)
        
        stl_content.append("endsolid enclosure")
        output_path.write_text("\n".join(stl_content), encoding="utf-8")
        return output_path

    def _add_box(self, content: list[str], x: float, y: float, z: float, w: float, h: float, d: float) -> None:
        """Adds a simple cube to the STL list."""
        # In a real STL, we'd define 12 triangles (6 faces)
        # This is a mock-up showing the logic
        content.append(f"  facet normal 0 0 1")
        content.append(f"    outer loop")
        content.append(f"      vertex {x} {y} {z+d}")
        content.append(f"      vertex {x+w} {y} {z+d}")
        content.append(f"      vertex {x+w} {y+h} {z+d}")
        content.append(f"    endloop")
        content.append(f"  endfacet")
        # ... other 5 faces would go here ...
