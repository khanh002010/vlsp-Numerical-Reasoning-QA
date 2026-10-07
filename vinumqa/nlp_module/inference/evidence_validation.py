"""Check chart label bindings and Step-1 argument positions without executing lookups."""
import json
from vinumqa.utils.dsl_parser import validate_program, parse_program
from vinumqa.cv_module.structure import validate_structure


def validate_evidence(program, charts, sources, evidence=None):
    valid, reason = validate_program(program, sources=sources)
    if not valid: return {"valid": False, "errors": [reason], "cv_requests": []}
    steps = parse_program(program)
    errors, requests = [], []
    for step in steps:
        if not step.operator.startswith("chart_"): continue
        image_id = step.args[0]
        if image_id not in charts:
            errors.append(f"Missing chart structure for {image_id}")
            continue
        chart = validate_structure(charts[image_id])
        total = step.operator == "chart_total"
        series = step.args[3] if total else step.args[1]
        names = [s["name"] for s in chart["series"]]
        if series not in names and not (total and series == "none"):
            errors.append(f"Step {step.step_id}: unverified series {series!r} in {image_id}; available={names}")
            requests.append({"image_id": image_id, "kind": "inspect", "region": "full", "series": series})
        if step.operator in {"chart_at", "chart_total"}:
            x, y = step.args[1:3] if total else step.args[2:4]
            labels = [(x, "x_labels", "x_axis"), (y, "y_labels", "y_axis")]
        else:
            start, end = step.args[2:4]
            labels = [(start, "x_labels", "x_axis"), (end, "x_labels", "x_axis")]
            if start != "none" and end != "none" and start in chart["x_labels"] and end in chart["x_labels"]:
                if not chart["x_order_known"]:
                    errors.append(f"Step {step.step_id}: chart range order needs a full-image inspection")
                    requests.append({"image_id": image_id, "kind": "inspect", "region": "full", "series": series})
                elif chart["x_labels"].index(start) > chart["x_labels"].index(end):
                    errors.append(f"Step {step.step_id}: reversed chart range {start!r} -> {end!r}")
        for label, field, region in labels:
            if label != "none" and label not in chart[field]:
                errors.append(f"Step {step.step_id}: unverified {field} label {label!r} in {image_id}")
                requests.append({"image_id": image_id, "kind": "inspect", "region": "full", "series": series if series != "none" else ""})
    if evidence is not None:
        try:
            plan = json.loads(evidence) if isinstance(evidence, str) else evidence
            if not isinstance(plan, list) or len(plan) != len(steps): raise ValueError("Step 1 must describe every operation")
            for step, declared in zip(steps, plan):
                if not isinstance(declared, dict) or declared.get("step") != step.step_id or declared.get("operator") != step.operator:
                    raise ValueError("Step-1 operation order differs from the program")
                expected = [{"position": i, "value": arg} for i, arg in enumerate(step.args)]
                if declared.get("arguments") != expected:
                    raise ValueError(f"Step {step.step_id}: argument positions/references differ between Step 1 and program")
        except (ValueError, TypeError) as error:
            errors.append(str(error))
    unique = {json.dumps(r, sort_keys=True): r for r in requests}
    return {"valid": not errors, "errors": errors, "cv_requests": list(unique.values()),
            "scope": "DSL, source labels, range order and declared operand positions; not a proof of question understanding"}
