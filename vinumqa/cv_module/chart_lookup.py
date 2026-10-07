"""Resolve chart operations only on explicit execution; never rewrite the program."""
import math
from statistics import mean


def resolve_chart(store, path, operator, a, b, c, allow_estimates=False):
    lookup = {"operator": operator, "arguments": [a, b, c]}
    result = store.read_values(path, lookup)
    if not isinstance(result, dict) or result.get("complete") is not True:
        raise ValueError("Incomplete chart evidence; refusing an aggregate/lookup")
    points = result.get("points")
    if not isinstance(points, list) or not points: raise ValueError("No chart points")
    chart = store.get(path)
    names = {s["name"] for s in chart["series"]}
    seen, values = set(), []
    for p in points:
        if not isinstance(p, dict): raise ValueError("Malformed chart point")
        key = (p.get("series"), p.get("x_label"), p.get("y_label", "none"))
        if key in seen: raise ValueError("Duplicate chart point")
        seen.add(key)
        if key[0] not in names: raise ValueError("Point has an unverified series")
        value = p.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Unreadable/non-finite chart point")
        basis = p.get("basis")
        if basis not in {"printed", "estimated"}: raise ValueError("Unknown value provenance")
        if basis == "estimated" and not allow_estimates: raise ValueError("Estimated chart values require allow_estimates=True")
        if not isinstance(p.get("raw_value"), str) or not p["raw_value"].strip():
            raise ValueError("Missing raw value evidence")
        if operator == "chart_at":
            if key != (a, b, c): raise ValueError("Point does not match chart_at arguments")
        elif operator == "chart_total":
            if key[1:3] != (a, b) or c != "none" and key[0] != c:
                raise ValueError("Component does not match chart_total scope")
        elif key[0] != a:
            raise ValueError("Point is outside the requested series")
        values.append(value)
    if operator == "chart_at":
        if len(values) != 1: raise ValueError("chart_at needs exactly one point")
        return values[0]
    if operator == "chart_total":
        if c == "none" and not chart["series_complete"]:
            raise ValueError("Cannot total an incomplete set of series")
        expected = names if c == "none" else {c}
        if {p["series"] for p in points} != expected: raise ValueError("Missing chart_total components")
        return sum(values)
    # Sparse axis ticks are not all the underlying observations: do not invent sums.
    if not chart["x_labels_complete"] or not chart.get("x_order_known", True):
        raise ValueError("Cannot aggregate a curve with incomplete point/category coverage")
    labels = chart["x_labels"]
    start = 0 if b == "none" else labels.index(b)
    end = len(labels) - 1 if c == "none" else labels.index(c)
    if start > end: raise ValueError("Reversed lookup range")
    wanted = labels[start:end+1]
    if any(p.get("y_label", "none") != "none" for p in points):
        raise ValueError("Ambiguous secondary category in aggregate points")
    if len(points) != len(wanted) or {p["x_label"] for p in points} != set(wanted):
        raise ValueError("Missing/extra points in aggregate range")
    functions = {"chart_max": max, "chart_min": min, "chart_sum": sum, "chart_average": mean}
    if operator not in functions: raise ValueError(f"Unknown chart operator: {operator}")
    return functions[operator](values)
