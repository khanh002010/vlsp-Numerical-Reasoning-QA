"""Validate focused observations before spending time on the next image region."""
import json
from vinumqa.cv_module.structure_output import parse_structure_output


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
