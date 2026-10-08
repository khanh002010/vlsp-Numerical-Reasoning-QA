"""Validate focused observations before spending time on the next image region."""
import json
import re
from vinumqa.cv_module.structure import validate_box
from vinumqa.cv_module.structure_output import parse_structure_output


def parse_visual_choice(text, field):
    """Decode a closed choice, never extract a keyword from ambiguous prose.

    Only for complete classifier/region generations, not chart structures or values.
    """
    choices = {"region": {"top", "middle", "bottom", "full"},
               "y_axis_type": {"numerical", "categorical", "none", "unknown"}}
    if field not in choices:
        raise ValueError("Unsupported visual choice field")
    text = text.strip()
    if text.startswith('```') and text.endswith('```'):
        text = '\n'.join(text.splitlines()[1:-1]).strip()
    try:
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result: raise ValueError("Duplicate classifier field")
                result[key] = value
            return result
        value = json.loads(text, object_pairs_hook=unique)
    except json.JSONDecodeError:
        value = text
    if isinstance(value, dict):
        if set(value) != {field}: raise ValueError("Expected one visual choice field")
        value = value[field]
    if not isinstance(value, str): raise ValueError("Visual choice must be a string")
    value = re.sub(r'\s+', ' ', value).strip().lower().rstrip('.').strip()
    if field == "y_axis_type":
        statements = {
            "the vertical y axis is a numerical scale": "numerical",
            "the y axis is a numerical scale": "numerical",
            "the vertical y axis is categorical": "categorical",
            "the y axis is categorical": "categorical",
            "the vertical y axis is absent": "none",
            "the y axis is absent": "none",
        }
        value = statements.get(value, value)
    if value not in choices[field]:
        raise ValueError("Ambiguous or unsupported visual choice: " + text[:120])
    return {field: value}


def normalize_locator_box(value):
    """Accept equivalent coordinate encodings, never infer units or fix geometry."""
    if isinstance(value, dict):
        if set(value) != {"left", "top", "right", "bottom"}:
            raise ValueError("Locator object needs exactly left/top/right/bottom")
        value = [value[key] for key in ("left", "top", "right", "bottom")]
    return validate_box(value)


def validate_part(phase, value):
    if not isinstance(value, dict):
        raise ValueError("Focused read must be an object")
    base = dict(title="", kind="unknown", series=[], x_labels=[], y_labels=[],
                x_labels_complete=False, series_complete=False, uncertain=[])
    keys = {
        "legend": ("title", "kind", "series", "series_complete"),
        "x_axis": ("x_labels", "x_labels_complete"),
        "y_axis": ("y_labels",),
    }[phase]
    for key in keys:
        if key not in value and not key.endswith("_complete"):
            raise ValueError("Focused read missing " + key)
        if key in value:
            base[key] = value[key]
    base["uncertain"] = value.get("uncertain", [])
    # Require an explicit observation of the Y axis, not a guess from chart kind.
    if phase == "y_axis":
        axis_type = value.get("y_axis_type", "unknown")
        if axis_type not in {"numerical", "categorical", "none", "unknown"}:
            raise ValueError("Invalid y_axis_type")
        if axis_type in {"numerical", "none"}:
            if base["y_labels"]:
                raise ValueError("Numerical/absent Y axis must have empty category labels; re-read")
        elif base["y_labels"] and axis_type == "unknown":
            raise ValueError("Confirm whether Y labels are categories, not legend or units")
    parsed, repairs = parse_structure_output(json.dumps(base, ensure_ascii=False))
    return {**{key: parsed[key] for key in keys}, "uncertain": parsed["uncertain"]}, repairs
