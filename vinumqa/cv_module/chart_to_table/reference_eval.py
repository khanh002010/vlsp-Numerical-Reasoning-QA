"""Compare an OCR table with human-checked image labels and printed values.

References may contain ordered ``categories``, ``series`` headers (excluding the
first/category column), and ``cells`` with category, series and exact value.
Whitespace is normalized; units, signs, spelling and number formatting are not.
Passing a partial reference only verifies the supplied labels/cells, never the
accuracy of the entire chart or of visually estimated values.
"""
from collections import Counter
import re


def _normalize(value):
    return " ".join(value.split())


def _parse_table(text):
    if not isinstance(text, str):
        raise ValueError("OCR output must be text")
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if lines and lines[0].startswith("```"):
        if len(lines) < 2 or lines[-1] != "```":
            raise ValueError("Unclosed Markdown code fence")
        lines = lines[1:-1]
    if len(lines) < 3:
        raise ValueError("Expected a Markdown header, separator and data rows")
    rows = []
    for line in lines:
        if not line.startswith("|") or not line.endswith("|"):
            raise ValueError("Expected one complete pipe-delimited Markdown table")
        rows.append([_normalize(cell.replace(r"\|", "|"))
                     for cell in re.split(r"(?<!\\)\|", line[1:-1])])
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Inconsistent Markdown column count")
    if any(not name for name in rows[0]):
        raise ValueError("Missing table header")

    def separator(row):
        return all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)

    if not separator(rows[1]):
        raise ValueError("Missing Markdown header separator")
    data = [row for row in rows[2:] if not separator(row)]
    if not data:
        raise ValueError("Table has no data rows")
    return rows[0], data


def _reference_labels(reference, key):
    if key not in reference:
        return None
    values = reference[key]
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        raise ValueError(f"Reference {key} must be a list of strings")
    values = [_normalize(item) for item in values]
    if any(not item for item in values) or len(values) != len(set(values)):
        raise ValueError(f"Reference {key} contains empty or duplicate labels")
    return values


def _duplicates(values):
    return [value for value, count in Counter(values).items() if count > 1]


def evaluate_reference(text: str, reference: dict) -> dict:
    """Return exact-label/cell comparisons, with no inferred accuracy score."""
    result = {
        "expected_category_count": None, "actual_category_count": None,
        "expected_series_count": None, "actual_series_count": None,
        "missing_categories": [], "extra_categories": [], "duplicate_categories": [],
        "missing_series": [], "extra_series": [], "duplicate_series": [],
        "category_order_matches": None, "cell_comparisons": [],
        "correct_cells": 0, "wrong_cells": 0, "missing_cells": 0,
        "cell_accuracy": None, "cell_coverage": None,
        "reference_passed": False,
        "caveat": "No reference cells supplied; numeric accuracy has not been measured.",
    }
    try:
        if not isinstance(reference, dict):
            raise ValueError("Reference must be an object")
        expected_categories = _reference_labels(reference, "categories")
        expected_series = _reference_labels(reference, "series")
        cells = reference.get("cells", [])
        if not isinstance(cells, list):
            raise ValueError("Reference cells must be a list")
        normalized_cells = []
        seen_cells = set()
        for cell in cells:
            if not isinstance(cell, dict) or any(
                not isinstance(cell.get(key), str) for key in ("category", "series", "value")
            ):
                raise ValueError("Each reference cell requires category, series and value strings")
            normalized = {key: _normalize(cell[key]) for key in ("category", "series", "value")}
            if any(not value for value in normalized.values()):
                raise ValueError("Reference cell fields must not be empty")
            pair = (normalized["category"], normalized["series"])
            if pair in seen_cells:
                raise ValueError("Reference cells contain a duplicate category/series pair")
            seen_cells.add(pair)
            normalized_cells.append(normalized)
        if expected_categories is not None:
            result["expected_category_count"] = len(expected_categories)
        if expected_series is not None:
            result["expected_series_count"] = len(expected_series)
        if normalized_cells:
            result["caveat"] = "Reference cells supplied, but numeric accuracy could not be measured."
        headers, rows = _parse_table(text)
    except ValueError as error:
        result["error"] = str(error)
        return result

    categories = [row[0] for row in rows]
    series = headers[1:]
    result["actual_category_count"] = len(categories)
    result["actual_series_count"] = len(series)
    result["duplicate_categories"] = _duplicates(categories)
    result["duplicate_series"] = _duplicates(series)
    for key, expected, actual in (("categories", expected_categories, categories),
                                  ("series", expected_series, series)):
        if expected is not None:
            result[f"missing_{key}"] = [item for item in expected if item not in actual]
            result[f"extra_{key}"] = list(dict.fromkeys(item for item in actual if item not in expected))
    if expected_categories is not None:
        result["category_order_matches"] = categories == expected_categories

    for cell in normalized_cells:
        category, name, expected = cell["category"], cell["series"], cell["value"]
        comparison = {"category": category, "series": name, "expected": expected, "actual": None}
        if categories.count(category) != 1 or series.count(name) != 1:
            comparison["status"] = "missing"
            comparison["reason"] = "Category or series is absent or ambiguous (duplicate label)"
            result["missing_cells"] += 1
        else:
            actual = rows[categories.index(category)][series.index(name) + 1]
            comparison["actual"] = actual
            comparison["status"] = "missing" if not actual else "correct" if actual == expected else "wrong"
            result[comparison["status"] + "_cells"] += 1
        result["cell_comparisons"].append(comparison)
    if normalized_cells:
        count = len(normalized_cells)
        result["cell_accuracy"] = result["correct_cells"] / count
        result["cell_coverage"] = (count - result["missing_cells"]) / count
        result["caveat"] = (
            "Cell accuracy covers only the supplied reference cells and uses exact strings "
            "after whitespace normalization. It does not measure unreferenced cells or estimates."
        )
    has_reference = expected_categories is not None or expected_series is not None or bool(normalized_cells)
    result["reference_passed"] = bool(has_reference and not any(
        result[key] for key in ("missing_categories", "extra_categories", "duplicate_categories",
                               "missing_series", "extra_series", "duplicate_series",
                               "wrong_cells", "missing_cells")
    ) and result["category_order_matches"] is not False)
    if not has_reference:
        result["caveat"] = "No categories, series or reference cells supplied; image accuracy has not been measured."
    return result
