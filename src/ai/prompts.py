"""Prompt templates for the AI circuit design engine.

The system prompt instructs GPT-4o to act as an expert electronics
engineer that outputs structured JSON matching our CircuitSpec schema.
"""

from __future__ import annotations

from src.ai.schemas import CircuitSpec

# ---------------------------------------------------------------------------
# JSON schema (exported for structured output mode)
# ---------------------------------------------------------------------------

CIRCUIT_SPEC_SCHEMA = CircuitSpec.model_json_schema()

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are the "PCB Design Engine", a world-class hardware architect and PCB layout expert. Your goal is to transform vague user ideas into mathematically correct, electrically sound, and manufacture-ready circuit specifications.

## CORE PHILOSOPHY
You don't just "guess" connections; you engineer them. You consider:
1. **Power Integrity**: Every IC must have decoupling capacitors (100nF) as close to the power pin as possible.
2. **Signal Integrity**: High-frequency signals need appropriate termination or bypassing.
3. **Physical Realizability**: Components must have real-world footprints and compatible pinouts.
4. **Completeness**: A "One-Shot" design means zero missing connections. Every single pin must be accounted for.

## STRICT ENGINEERING RULES
1. **Component Selection**: Use industry-standard parts (e.g., LM7805, NE555, ESP32-S3, 0805 passives).
2. **Pin Mapping**: 
   - You MUST list EVERY pin for every component. 
   - Pin numbers must be strings ("1", "2", "3").
   - For ICs, follow the official datasheet pinout exactly.
3. **Net Integrity**:
   - Nets must connect at least 2 pins.
   - Every pin on every component MUST be attached to a net.
   - Unused pins must be tied to GND or VCC (as per datasheet) or placed on an "NC" net.
4. **Power Rails**:
   - Define clear power nets (e.g., "3V3", "5V", "GND").
   - Include a power source (connector, battery, or regulator).
5. **Physicals**:
   - Assign packages (0402, 0603, 0805, SOT-23, TQFP, etc.).
   - Suggest a board size that allows for a realistic layout (no overlapping components).
6. **Constraints**:
   - Power traces: 0.5mm - 1.0mm.
   - Signal traces: 0.2mm - 0.3mm.
   - Clearance: 0.2mm.

## JSON OUTPUT REQUIREMENTS
- Output ONLY the JSON object.
- No markdown fences, no preamble, no postamble.
- Ensure the JSON is strictly valid (double quotes, no trailing commas).
- The "description" field should act as your "Engineering Note", explaining the design choices made to achieve the user's goal.
"""

EDIT_SYSTEM_PROMPT = """\
You are now in "Iterative Edit Mode". You will be provided with an existing circuit specification and a request for changes.

## YOUR OBJECTIVE
Modify the existing design to accommodate the user's request while maintaining the integrity of the rest of the circuit.

## RULES FOR EDITING
1. **Preserve Stability**: Do not change existing components or nets unless the user specifically asks to modify them or they must be changed to support the new feature.
2. **Consistency**: Maintain the same naming convention (R1, C1, etc.). If you add new components, use the next available number.
3. **Re-Validate**: After making changes, ensure that:
   - All pins are still connected.
   - Power rails are still intact.
   - No duplicate reference designators exist.
4. **Delta Analysis**: In the "description" field, explicitly list what was changed, added, or removed.

## OUTPUT
Return the FULL updated JSON specification. Do not return a "diff"; return the entire complete object.
"""

# ---------------------------------------------------------------------------
# Few-shot examples (user/assistant pairs)
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Simple LED circuit with a 5V power supply, red LED, and current-limiting resistor.",
    },
    {
        "role": "assistant",
        "content": """\
{
  "name": "Simple LED Circuit",
  "description": "A basic circuit with a 5V supply, 330Ω current-limiting resistor, and a red LED. The resistor limits current to approximately 10mA.",
  "components": [
    {
      "ref": "J1",
      "value": "Conn_01x02",
      "category": "connector",
      "package": "PinHeader_1x02_P2.54mm",
      "description": "2-pin power input connector (5V and GND)",
      "pins": [
        {"number": "1", "name": "VIN", "electrical_type": "power_in"},
        {"number": "2", "name": "GND", "electrical_type": "power_in"}
      ]
    },
    {
      "ref": "R1",
      "value": "330Ω",
      "category": "resistor",
      "package": "0805",
      "description": "Current limiting resistor for LED (5V - 2V) / 330Ω ≈ 9mA",
      "pins": [
        {"number": "1", "name": "1", "electrical_type": "passive"},
        {"number": "2", "name": "2", "electrical_type": "passive"}
      ]
    },
    {
      "ref": "D1",
      "value": "Red LED",
      "category": "led",
      "package": "LED_0805",
      "description": "Standard red LED, Vf ≈ 2V",
      "pins": [
        {"number": "1", "name": "A", "electrical_type": "passive"},
        {"number": "2", "name": "K", "electrical_type": "passive"}
      ]
    }
  ],
  "nets": [
    {"name": "VCC", "connections": [{"ref": "J1", "pin": "1"}, {"ref": "R1", "pin": "1"}]},
    {"name": "LED_A", "connections": [{"ref": "R1", "pin": "2"}, {"ref": "D1", "pin": "1"}]},
    {"name": "GND", "connections": [{"ref": "D1", "pin": "2"}, {"ref": "J1", "pin": "2"}]}
  ],
  "board": {"width_mm": 30.0, "height_mm": 20.0, "layers": 2, "thickness_mm": 1.6},
  "constraints": {"trace_width_mm": 0.3, "clearance_mm": 0.2, "via_diameter_mm": 0.8, "via_drill_mm": 0.4}
}""",
    },
    {
        "role": "user",
        "content": "LM7805 5V voltage regulator circuit with input/output connectors and bypass capacitors.",
    },
    {
        "role": "assistant",
        "content": """\
{
  "name": "LM7805 5V Voltage Regulator",
  "description": "Linear 5V regulator from 7-12V input. Includes input/output bypass caps.",
  "components": [
    {
      "ref": "J1", "value": "Conn_01x02", "category": "connector",
      "package": "PinHeader_1x02_P2.54mm", "description": "Power input connector",
      "pins": [
        {"number": "1", "name": "VIN", "electrical_type": "power_in"},
        {"number": "2", "name": "GND", "electrical_type": "power_in"}
      ]
    },
    {
      "ref": "U1", "value": "LM7805", "category": "regulator",
      "package": "TO-220-3", "description": "5V 1.5A positive linear voltage regulator",
      "pins": [
        {"number": "1", "name": "IN",  "electrical_type": "power_in"},
        {"number": "2", "name": "GND", "electrical_type": "power_in"},
        {"number": "3", "name": "OUT", "electrical_type": "power_out"}
      ]
    },
    {
      "ref": "C1", "value": "100nF", "category": "capacitor",
      "package": "0805", "description": "Input bypass capacitor",
      "pins": [
        {"number": "1", "name": "1", "electrical_type": "passive"},
        {"number": "2", "name": "2", "electrical_type": "passive"}
      ]
    },
    {
      "ref": "C2", "value": "10uF", "category": "capacitor",
      "package": "0805", "description": "Output bypass capacitor",
      "pins": [
        {"number": "1", "name": "1", "electrical_type": "passive"},
        {"number": "2", "name": "2", "electrical_type": "passive"}
      ]
    },
    {
      "ref": "J2", "value": "Conn_01x02", "category": "connector",
      "package": "PinHeader_1x02_P2.54mm", "description": "5V output connector",
      "pins": [
        {"number": "1", "name": "5V",  "electrical_type": "power_out"},
        {"number": "2", "name": "GND", "electrical_type": "power_in"}
      ]
    }
  ],
  "nets": [
    {"name": "VIN",     "connections": [{"ref": "J1", "pin": "1"}, {"ref": "U1", "pin": "1"}, {"ref": "C1", "pin": "1"}]},
    {"name": "GND",     "connections": [{"ref": "J1", "pin": "2"}, {"ref": "U1", "pin": "2"}, {"ref": "C1", "pin": "2"}, {"ref": "C2", "pin": "2"}, {"ref": "J2", "pin": "2"}]},
    {"name": "VOUT_5V", "connections": [{"ref": "U1", "pin": "3"}, {"ref": "C2", "pin": "1"}, {"ref": "J2", "pin": "1"}]}
  ],
  "board": {"width_mm": 40.0, "height_mm": 30.0, "layers": 2, "thickness_mm": 1.6},
  "constraints": {"trace_width_mm": 0.5, "clearance_mm": 0.2, "via_diameter_mm": 0.8, "via_drill_mm": 0.4}
}""",
    },
]

# ---------------------------------------------------------------------------
# Helper: build full message list
# ---------------------------------------------------------------------------

def build_messages(user_prompt: str, current_spec: CircuitSpec | None = None) -> list[dict[str, str]]:
    """Construct the full message history for the OpenAI API call.
    
    If current_spec is provided, the AI enters "Edit Mode".
    """
    if current_spec:
        # Edit Mode
        messages: list[dict[str, str]] = [
            {"role": "system", "content": EDIT_SYSTEM_PROMPT},
            {"role": "user", "content": f"CURRENT DESIGN:\n{current_spec.model_dump_json(indent=2)}\n\nREQUESTED CHANGES: {user_prompt}"},
        ]
    else:
        # New Design Mode
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        messages.extend(FEW_SHOT_EXAMPLES)
        messages.append({"role": "user", "content": user_prompt})
    
    return messages
