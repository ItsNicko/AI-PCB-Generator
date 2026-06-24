import pytest
import json
from src.ai.client import AIClient, AIClientError
from src.ai.schemas import CircuitSpec

def test_parse_response_valid_json():
    client = AIClient(api_key="test")
    raw = '{"name": "Test Circuit", "components": [], "nets": [], "board": {}, "constraints": {}}'
    spec = client._parse_response(raw)
    assert spec.name == "Test Circuit"

def test_parse_response_with_markdown_fences():
    client = AIClient(api_key="test")
    raw = '```json\n{"name": "Test Circuit", "components": [], "nets": [], "board": {}, "constraints": {}}\n```'
    spec = client._parse_response(raw)
    assert spec.name == "Test Circuit"

def test_parse_response_with_text_before_json():
    client = AIClient(api_key="test")
    raw = 'Here is the circuit specification:\n```json\n{"name": "Test Circuit", "components": [], "nets": [], "board": {}, "constraints": {}}\n```'
    spec = client._parse_response(raw)
    assert spec.name == "Test Circuit"

def test_parse_response_with_trailing_text():
    client = AIClient(api_key="test")
    raw = '```json\n{"name": "Test Circuit", "components": [], "nets": [], "board": {}, "constraints": {}}\n```\nHope this helps!'
    spec = client._parse_response(raw)
    assert spec.name == "Test Circuit"

def test_parse_response_invalid_json():
    client = AIClient(api_key="test")
    raw = '{"name": "Test Circuit", "components":'
    with pytest.raises(AIClientError, match="AI response is not valid JSON"):
        client._parse_response(raw)

def test_parse_response_with_single_quotes():
    client = AIClient(api_key="test")
    raw = "{'name': 'Test Circuit', 'components': [], 'nets': [], 'board': {}, 'constraints': {}}"
    spec = client._parse_response(raw)
    assert spec.name == "Test Circuit"
