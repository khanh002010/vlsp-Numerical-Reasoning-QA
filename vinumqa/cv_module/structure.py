"""Portable chart structure and requests. This module never imports a GPU library."""
import json
import math

STRUCTURE_VERSION = "chart-structure-v1"
STORE_VERSION = "vinumqa-chart-store-v1"
STRUCTURE_PROMPT = '''Read the chart structure, not the numerical data at every point.
Return ONLY a JSON object with these fields:
{"title":"", "kind":"line/bar/pie/mixed/table/unknown", "series":[{"name":"exact legend text","color":"","axis":"left/right/none","unit":""}], "x_labels":[], "y_labels":[], "x_labels_complete":false, "series_complete":false, "regions":{}, "uncertain":[]}
Copy original Vietnamese spelling and visible category/time labels, in image order.
Combine grouped labels only with their visible parent. Never extend dates or invent names.
x_labels/y_labels are category labels, not numerical axis ticks. If the time axis has
only sparse ticks, x_labels_complete must be false. No legend? Use the printed series
title if unambiguous; otherwise leave series empty and explain in uncertain.
regions may contain legend, x_axis, y_axis, plot boxes [left,top,right,bottom] normalized
to 0..1; omit any box you cannot locate. Do not transcribe curves into guessed values.
Mark completeness true only when all relevant labels are readable. No program or answer.'''


def json_object(text):
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        text = "\n".join(text.splitlines()[1:-1]).strip()
    value = json.loads(text)
    if not isinstance(value, dict): raise ValueError("Expected a JSON object")
    return value


def strings(value, field):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{field} must be a list of nonempty strings")
    result = [x.strip() for x in value]
    if len(set(result)) != len(result): raise ValueError(f"Duplicate labels in {field}")
    return result


def validate_box(box):
    if (not isinstance(box, (list, tuple)) or len(box) != 4 or
        any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in box) or
        not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1)):
        raise ValueError("Crop box must be [left, top, right, bottom] within 0..1")
    return list(box)


def validate_structure(value):
    if isinstance(value, str): value = json_object(value)
    if not isinstance(value, dict): raise ValueError("Chart structure must be an object")
    if value.get("structure_version", STRUCTURE_VERSION) != STRUCTURE_VERSION:
        raise ValueError("Unknown chart structure version")
    result = {"structure_version": STRUCTURE_VERSION}
    for key in ("title", "kind"):
        if not isinstance(value.get(key), str): raise ValueError(f"Missing chart {key}")
        result[key] = value[key].strip()
    series = value.get("series")
    if not isinstance(series, list): raise ValueError("Missing chart series")
    result["series"] = []
    for s in series:
        if not isinstance(s, dict) or not isinstance(s.get("name"), str) or not s["name"].strip():
            raise ValueError("Each series needs its visible name")
        row = {"name": s["name"].strip()}
        for field in ("color", "axis", "unit"):
            if not isinstance(s.get(field, ""), str): raise ValueError(f"Invalid series {field}")
            row[field] = s.get(field, "").strip()
        result["series"].append(row)
    strings([s["name"] for s in result["series"]], "series")
    for key in ("x_labels", "y_labels", "uncertain"):
        result[key] = strings(value.get(key, []), key)
    for key in ("x_labels_complete", "series_complete"):
        if not isinstance(value.get(key), bool): raise ValueError(f"Missing completeness flag {key}")
        result[key] = value[key]
    if not isinstance(value.get("x_order_known", True), bool): raise ValueError("Invalid x_order_known")
    result["x_order_known"] = value.get("x_order_known", True)
    regions = value.get("regions", {})
    if not isinstance(regions, dict): raise ValueError("regions must be an object")
    result["regions"] = {k: validate_box(box) for k, box in regions.items()
                         if k in {"legend", "x_axis", "y_axis", "plot"}}
    return result


def validate_request(value, image_ids):
    if not isinstance(value, dict) or value.get("image_id") not in image_ids:
        raise ValueError("CV request references an unavailable Image ID")
    if value.get("kind", "inspect") != "inspect":
        raise ValueError("NLP may request structure inspection only; numerical lookups belong to the executor")
    region = value.get("region", "full")
    if region not in {"full", "legend", "x_axis", "y_axis", "plot"}: raise ValueError("Unknown image region")
    series = value.get("series", "")
    if not isinstance(series, str) or len(series) > 200: raise ValueError("Invalid series hint")
    result = {"image_id": value["image_id"], "kind": "inspect", "region": region, "series": series}
    if "box" in value: result["box"] = validate_box(value["box"])
    return result


def render_structure(image_id, structure):
    chart = validate_structure(structure)
    # Coordinates stay in the store; uncertainty remains visible to NLP.
    chart.pop("regions", None)
    return "Chart structure (not a numerical table):\n" + json.dumps(
        {"image_id": image_id, **chart}, ensure_ascii=False, separators=(",", ":"))


def merge_observation(original, observation, full=False):
    observation = validate_structure(observation)
    if full: return observation
    original = validate_structure(original)
    names = {s["name"] for s in original["series"]}
    original["series"].extend(s for s in observation["series"] if s["name"] not in names)
    for key in ("x_labels", "y_labels"):
        original[key] = list(dict.fromkeys(original[key] + observation[key]))
    # A crop never proves global completeness or global temporal ordering.
    original["x_labels_complete"] = False
    original["series_complete"] = False
    original["x_order_known"] = False
    return validate_structure(original)
