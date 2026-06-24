"""Connectivity verifier for PCB layouts.
Ensures that routed traces correctly connect all pins of a net.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Optional

from src.pcb.generator import Board, Pad
from src.utils.logger import get_logger

log = get_logger("pcb.verifier")

@dataclass
class ConnectivityError:
    net_name: str
    missing_connections: list[tuple[str, str]] # (ref, pin)
    description: str

class ConnectivityVerifier:
    """Verifies that the physical routing matches the logical netlist."""

    def __init__(self, board: Board):
        self.board = board

    def verify(self, spec_nets: list) -> list[ConnectivityError]:
        """Verify connectivity for all nets in the specification."""
        errors = []
        
        # Build adjacency graph: pad -> set of connected pads
        adj = defaultdict(set)
        
        # Traces connect pads? 
        # Actually, our TraceSegment just has start/end points.
        # We need to map those points back to pads.
        
        all_pads = self.board.get_all_pads()
        
        def find_pad_at(x: float, y: float, net_name: str) -> Optional[Pad]:
            for p in all_pads:
                if p.net_name == net_name and abs(p.x_mm - x) < 0.1 and abs(p.y_mm - y) < 0.1:
                    return p
            return None

        for trace in self.board.traces:
            p_start = find_pad_at(trace.start_x, trace.start_y, trace.net_name)
            p_end = find_pad_at(trace.end_x, trace.end_y, trace.net_name)
            
            if p_start and p_end:
                adj[p_start].add(p_end)
                adj[p_end].add(p_start)

        # Check each net
        for net_spec in spec_nets:
            net_name = net_spec.name
            required_pads = self.board.get_pads_for_net(net_name)
            
            if not required_pads:
                continue
                
            # Start BFS from the first pad
            start_pad = required_pads[0]
            visited = {start_pad}
            queue = deque([start_pad])
            
            while queue:
                curr = queue.popleft()
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            # Find which required pads were not visited
            missing = [
                (p.component_ref, p.number) 
                for p in required_pads 
                if p not in visited
            ]
            
            if missing:
                errors.append(ConnectivityError(
                    net_name=net_name,
                    missing_connections=missing,
                    description=f"Net {net_name} is disconnected. {len(missing)} pads unreachable."
                ))
                
        log.info("Connectivity verification complete: found %d errors", len(errors))
        return errors
