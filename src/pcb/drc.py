"""Design Rule Check (DRC) engine for PCB layouts.
Detects clearance violations between traces and pads.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.pcb.generator import Board, TraceSegment, Pad
from src.utils.logger import get_logger

log = get_logger("pcb.drc")

@dataclass
class DRCViolation:
    type: str  # 'clearance', 'short', 'overlap'
    net_a: str
    net_b: str
    pos_a: tuple[float, float]
    pos_b: tuple[float, float]
    distance: float
    min_distance: float
    description: str

class DRCEngine:
    """Checks a Board for physical design rule violations."""

    def __init__(self, board: Board):
        self.board = board
        self.clearance = board.constraints.clearance_mm

    def run(self) -> list[DRCViolation]:
        """Run all DRC checks and return a list of violations."""
        violations = []
        
        # 1. Pad-to-Pad clearance
        violations.extend(self._check_pad_clearance())
        
        # 2. Trace-to-Trace clearance
        violations.extend(self._check_trace_clearance())
        
        # 3. Trace-to-Pad clearance
        violations.extend(self._check_trace_pad_clearance())
        
        log.info("DRC complete: found %d violations", len(violations))
        return violations

    def _check_pad_clearance(self) -> list[DRCViolation]:
        violations = []
        pads = self.board.get_all_pads()
        
        for i in range(len(pads)):
            for j in range(i + 1, len(pads)):
                p1, p2 = pads[i], pads[j]
                if p1.net_name == p2.net_name:
                    continue
                
                dist = self._dist_pads(p1, p2)
                if dist < self.clearance:
                    violations.append(DRCViolation(
                        type='clearance',
                        net_a=p1.net_name,
                        net_b=p2.net_name,
                        pos_a=(p1.x_mm, p1.y_mm),
                        pos_b=(p2.x_mm, p2.y_mm),
                        distance=dist,
                        min_distance=self.clearance,
                        description=f"Pad {p1.component_ref}-{p1.number} too close to {p2.component_ref}-{p2.number}"
                    ))
        return violations

    def _check_trace_clearance(self) -> list[DRCViolation]:
        violations = []
        traces = self.board.traces
        
        for i in range(len(traces)):
            for j in range(i + 1, len(traces)):
                t1, t2 = traces[i], traces[j]
                if t1.layer != t2.layer:
                    continue
                if t1.net_name == t2.net_name:
                    continue
                
                dist = self._dist_segments(
                    (t1.start_x, t1.start_y), (t1.end_x, t1.end_y),
                    (t2.start_x, t2.start_y), (t2.end_x, t2.end_y)
                )
                
                # Actual clearance is dist minus half of each trace width
                effective_dist = dist - (t1.width_mm / 2) - (t2.width_mm / 2)
                
                if effective_dist < self.clearance:
                    violations.append(DRCViolation(
                        type='clearance',
                        net_a=t1.net_name,
                        net_b=t2.net_name,
                        pos_a=((t1.start_x + t1.end_x)/2, (t1.start_y + t1.end_y)/2),
                        pos_b=((t2.start_x + t2.end_x)/2, (t2.start_y + t2.end_y)/2),
                        distance=effective_dist,
                        min_distance=self.clearance,
                        description="Trace-to-trace clearance violation"
                    ))
        return violations

    def _check_trace_pad_clearance(self) -> list[DRCViolation]:
        violations = []
        traces = self.board.traces
        pads = self.board.get_all_pads()
        
        for t in traces:
            for p in pads:
                if t.net_name == p.net_name:
                    continue
                
                # Only check if on the same layer
                # Simplification: assume trace layer is always compatible with pad
                # In real KiCad, this is more complex.
                
                dist = self._dist_point_segment(
                    (p.x_mm, p.y_mm),
                    (t.start_x, t.start_y), (t.end_x, t.end_y)
                )
                
                effective_dist = dist - (t.width_mm / 2) - (p.width_mm / 2)
                
                if effective_dist < self.clearance:
                    violations.append(DRCViolation(
                        type='clearance',
                        net_a=t.net_name,
                        net_b=p.net_name,
                        pos_a=((t.start_x + t.end_x)/2, (t.start_y + t.end_y)/2),
                        pos_b=(p.x_mm, p.y_mm),
                        distance=effective_dist,
                        min_distance=self.clearance,
                        description=f"Trace {t.net_name} too close to pad {p.component_ref}-{p.number}"
                    ))
        return violations

    # ── Geometry Helpers ──────────────────────────────────────────────────────

    def _dist_pads(self, p1: Pad, p2: Pad) -> float:
        """Center-to-center distance minus pad radii."""
        dist = math.sqrt((p1.x_mm - p2.x_mm)**2 + (p1.y_mm - p2.y_mm)**2)
        return dist - (p1.width_mm / 2) - (p2.width_mm / 2)

    def _dist_point_segment(self, p: tuple[float, float], s1: tuple[float, float], s2: tuple[float, float]) -> float:
        """Shortest distance from point p to line segment s1-s2."""
        px, py = p
        x1, y1 = s1
        x2, y2 = s2
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        return math.sqrt((px - nearest_x)**2 + (py - nearest_y)**2)

    def _dist_segments(self, s1_start: tuple[float, float], s1_end: tuple[float, float],
                       s2_start: tuple[float, float], s2_end: tuple[float, float]) -> float:
        """Shortest distance between two line segments."""
        # Check endpoints of s1 against s2
        d1 = self._dist_point_segment(s1_start, s2_start, s2_end)
        d2 = self._dist_point_segment(s1_end, s2_start, s2_end)
        # Check endpoints of s2 against s1
        d3 = self._dist_point_segment(s2_start, s1_start, s1_end)
        d4 = self._dist_point_segment(s2_end, s1_start, s1_end)
        
        return min(d1, d2, d3, d4)
