import pytest
from co_tutor.utils.jsonfy import jsonfy, validate_and_normalize


def test_json_block_parsing():
    raw = 'Some explanation\n```json\n{"problem_type": "math", "difficulty": "básico", "solution": {"steps":[{"step_number":1, "description":"Paso 1"}]}, "final_answer":"42", "verification":"Comprobar", "hints": [{"level":1, "content":"Pista"}] }\n```\n'
    parsed = jsonfy(raw)
    assert parsed["problem_type"] == "math"


def test_plain_json_parsing():
    raw = '{"problem_type":"mathematics","difficulty":"básico","solution":{"steps":[{"step_number":1,"description":"A"}]},"final_answer":"R","verification":"V","hints":[{"level":1,"content":"H"}]}'
    parsed = jsonfy(raw)
    assert parsed["difficulty"] == "básico"


def test_yaml_parsing():
    raw = "problem_type: mathematics\n difficulty: básico\n solution:\n  steps:\n    - step_number: 1\n      description: Paso 1\n final_answer: Res\n verification: Ver\n hints:\n  - level: 1\n    content: P" 
    parsed = jsonfy(raw)
    assert parsed["problem_type"] == "mathematics"


def test_key_value_heuristic():
    raw = "problem_type: mathematics\nfinal_answer: 10\nverification: check\nhints: []\nsolution: { 'steps': [ {'step_number': 1, 'description': 'P1'} ] }"
    parsed = jsonfy(raw)
    assert "problem_type" in parsed


def test_validate_and_normalize_success():
    data = {
        "problem_type": "mathematics",
        "difficulty": "básico",
        "solution": {"steps": [{"step_number": 1, "description": "P1"}]},
        "final_answer": "R",
        "verification": "V",
        "hints": [{"level": 1, "content": "H"}],
    }
    norm = validate_and_normalize(data)
    assert norm["solution"]["steps"][0]["step_number"] == 1


def test_validate_missing_field():
    data = {"problem_type":"math"}
    with pytest.raises(ValueError):
        validate_and_normalize(data)
