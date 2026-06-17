import re
import json
from typing import Any, Dict, List, Optional

try:
    import yaml
except Exception:
    yaml = None

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)
BRACE_BLOCK_RE = re.compile(r"\{.*\}", re.S)


def _try_load_json(s: str) -> Optional[Any]:
    try:
        return json.loads(s)
    except Exception:
        return None


def _extract_json_block(s: str) -> Optional[str]:
    m = JSON_BLOCK_RE.search(s)
    if m:
        return m.group(1)
    m2 = BRACE_BLOCK_RE.search(s)
    if m2:
        return m2.group(0)
    return None


def _lines_to_dict(s: str) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    for line in s.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if not k:
            continue
        lv = v.lower()
        if lv in ("true", "false"):
            val: Any = lv == "true"
        else:
            try:
                val = int(v)
            except Exception:
                try:
                    val = float(v)
                except Exception:
                    val = v
        d[k] = val
    return d


def _try_load_yaml(s: str) -> Optional[Any]:
    if yaml is None:
        return None
    try:
        return yaml.safe_load(s)
    except Exception:
        return None


def jsonfy(raw: str) -> Dict[str, Any]:
    """Convert a model text output into a Python dict following the expected schema.

    Strategy:
    1) Extract JSON block (```json ... ``` or first {...}) and parse.
    2) Try to parse the whole text as JSON.
    3) Try to parse as YAML (if PyYAML is available).
    4) Fall back to a simple key:value per-line heuristic.

    Raises ValueError if no valid dict can be produced.
    """
    block = _extract_json_block(raw)
    if block:
        parsed = _try_load_json(block)
        if isinstance(parsed, dict):
            return parsed

    parsed = _try_load_json(raw)
    if isinstance(parsed, dict):
        return parsed

    parsed = _try_load_yaml(raw)
    if isinstance(parsed, dict):
        return parsed

    d = _lines_to_dict(raw)
    if d:
        return d

    raise ValueError("No se pudo convertir la salida del modelo a JSON válido")


# Validation / normalization helpers


def _ensure_steps(sol: Dict[str, Any]) -> List[Dict[str, Any]]:
    steps = sol.get("steps") or []
    normalized: List[Dict[str, Any]] = []
    for s in steps:
        if not isinstance(s, dict):
            continue
        sn = s.get("step_number")
        desc = s.get("description")
        try:
            sn_i = int(sn) if sn is not None else None
        except Exception:
            sn_i = None
        if sn_i is None or desc is None:
            continue
        normalized.append({"step_number": sn_i, "description": str(desc)})
    normalized.sort(key=lambda x: x["step_number"])  # ensure order
    return normalized


def _ensure_hints(hints: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for h in (hints or []):
        if not isinstance(h, dict):
            continue
        lvl = h.get("level")
        content = h.get("content")
        try:
            lvl_i = int(lvl) if lvl is not None else None
        except Exception:
            lvl_i = None
        if lvl_i is None or content is None:
            continue
        out.append({"level": lvl_i, "content": str(content)})
    out.sort(key=lambda x: x["level"])
    return out


def validate_and_normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate required fields and normalize types according to the schema.

    Required schema:
      - problem_type: str
      - difficulty: str
      - solution: { steps: [ { step_number: int, description: str }, ... ] }
      - final_answer: str
      - verification: str
      - hints: [ { level: int, content: str }, ... ]
    """
    required = ["problem_type", "difficulty", "solution", "final_answer", "verification", "hints"]
    for k in required:
        if k not in data:
            raise ValueError(f"Campo obligatorio ausente: {k}")

    problem_type = str(data.get("problem_type"))
    difficulty = str(data.get("difficulty"))

    sol = data.get("solution") or {}
    if not isinstance(sol, dict):
        raise ValueError("solution debe ser un objeto")
    steps = _ensure_steps(sol)

    final_answer = str(data.get("final_answer") or "")
    verification = str(data.get("verification") or "")
    hints = _ensure_hints(data.get("hints"))

    normalized = {
        "problem_type": problem_type,
        "difficulty": difficulty,
        "solution": {"steps": steps},
        "final_answer": final_answer,
        "verification": verification,
        "hints": hints,
    }
    return normalized
