"""Parser for KiCad .kicad_mod footprint files.
Provides extraction of pad positions, sizes, and types.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

log = get_logger("pcb.footprint_parser")

@dataclass
class FootprintPad:
    number: str
    type: str  # 'smd' or 'thru_hole'
    shape: str # 'circle', 'rect', 'oval'
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float
    drill_mm: float = 0.0
    layers: list[str] = field(default_factory=list)

@dataclass
class Footprint:
    name: str
    pads: list[FootprintPad]

def _tokenize(text: str) -> list[str]:
    """Split S-expression text into tokens."""
    # Matches parentheses, quoted strings, or non-whitespace sequences
    return re.findall(r'\(|\)|"[^"]*"|[^\s()]+', text)

def parse_footprint(filepath: Path) -> Optional[Footprint]:
    """Parse a .kicad_mod file and return a Footprint object.
    
    Returns None if the file is not a valid footprint or cannot be parsed.
    """
    try:
        text = filepath.read_text(encoding='utf-8')
    except Exception as e:
        log.error("Could not read footprint file %s: %s", filepath, e)
        return None

    tokens = _tokenize(text)
    if not tokens:
        return None

    # The first token should be '(' and the second the 'footprint' keyword
    if len(tokens) < 3 or tokens[0] != '(' or tokens[1] != 'footprint':
        return None

    name = tokens[2].strip('"')
    pads = []
    
    pos = 3
    while pos < len(tokens):
        if tokens[pos] == '(':
            # Look for '(pad ...)'
            if pos + 1 < len(tokens) and tokens[pos + 1] == 'pad':
                pad_data, next_pos = _parse_pad(tokens, pos)
                if pad_data:
                    pads.append(pad_data)
                pos = next_pos
            else:
                # Skip other blocks like (zone ...)
                pos = _skip_block(tokens, pos)
        else:
            pos += 1

    return Footprint(name=name, pads=pads)

def _skip_block(tokens: list[str], pos: int) -> int:
    """Skip a balanced ( ... ) block."""
    depth = 0
    while pos < len(tokens):
        if tokens[pos] == '(':
            depth += 1
        elif tokens[pos] == ')':
            depth -= 1
            if depth == 0:
                return pos + 1
        pos += 1
    return pos

def _parse_pad(tokens: list[str], pos: int) -> tuple[Optional[FootprintPad], int]:
    """Parse a (pad ...) block."""
    # (pad "number" type shape (at x y) (size w h) ... )
    depth = 0
    pad_tokens = []
    
    start_pos = pos
    while pos < len(tokens):
        t = tokens[pos]
        if t == '(':
            depth += 1
        elif t == ')':
            depth -= 1
            if depth == 0:
                pad_tokens.append(t)
                return _extract_pad_info(pad_tokens), pos + 1
        pad_tokens.append(t)
        pos += 1
        
    return None, pos

def _extract_pad_info(tokens: list[str]) -> Optional[FootprintPad]:
    """Extract physical properties from pad tokens."""
    try:
        # Tokens: ['(', 'pad', '"1"', 'smd', 'rect', '(', 'at', '0', '0', ')', ...]
        number = tokens[2].strip('"')
        pad_type = tokens[3] # 'smd' or 'thru_hole'
        shape = tokens[4]    # 'rect', 'oval', 'circle'
        
        x, y = 0.0, 0.0
        w, h = 0.0, 0.0
        drill = 0.0
        
        # Find (at x y) and (size w h) and (drill d)
        i = 5
        while i < len(tokens):
            if tokens[i] == '(':
                if i + 1 < len(tokens) and tokens[i+1] == 'at':
                    x = float(tokens[i+2])
                    y = float(tokens[i+3])
                    i += 4
                elif i + 1 < len(tokens) and tokens[i+1] == 'size':
                    w = float(tokens[i+2])
                    h = float(tokens[i+3])
                    i += 4
                elif i + 1 < len(tokens) and tokens[i+1] == 'drill':
                    drill = float(tokens[i+2])
                    i += 3
                else:
                    # skip unknown block
                    depth = 1
                    i += 1
                    while i < len(tokens) and depth > 0:
                        if tokens[i] == '(': depth += 1
                        elif tokens[i] == ')': depth -= 1
                        i += 1
            else:
                i += 1
                
        return FootprintPad(
            number=number,
            type=pad_type,
            shape=shape,
            x_mm=x,
            y_mm=y,
            width_mm=w,
            height_mm=h,
            drill_mm=drill
        )
    except Exception:
        return None
