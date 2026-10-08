"""Conservative syntax cleanup for CV JSON; never complete truncated structures."""
import json
import re
from copy import deepcopy
from vinumqa.cv_module.structure import validate_structure
from vinumqa.cv_module.chart_to_table.quality import repetition_reason


def json_repetition_reason(text):
    reason = repetition_reason(text)
    if reason:
        return reason
    # The ordinary text guard deliberately ignores punctuation. In chart JSON,
    # sustained arrays of empty strings/parentheses are not useful labels either.
    if re.search(r'(?:"[\s()\[\]{}%]*"\s*,\s*){12}', text):
        return "Repeated empty/punctuation-only JSON labels"
    return None


def repair_json_syntax(text):
    """Quote bare object keys/remove trailing commas OUTSIDE quoted strings only."""
    output, in_string, escaped, repairs = [], False, False, []
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            output.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
        elif ch == ',' and re.match(r'\s*[}\]]', text[i + 1:]):
            repairs.append("removed trailing comma")
            i += 1
            continue
        if ch in '{,':
            output.append(ch)
            i += 1
            match = re.match(r'(\s*)([A-Za-z_][A-Za-z_0-9]*)(\s*:)', text[i:])
            if match:
                output.append(match[1] + json.dumps(match[2]) + match[3])
                repairs.append("quoted key: " + match[2])
                i += len(match[0])
            continue
        output.append(ch)
        i += 1
    return ''.join(output), repairs


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_structure_output(text):
    """Only call for complete generations. Keep original text in attempt diagnostics."""
    reason = json_repetition_reason(text)
    if reason: raise ValueError(reason)
    text = text.strip()
    if text.startswith('```') and text.endswith('```'):
        text = '\n'.join(text.splitlines()[1:-1]).strip()
    repairs = []
    try:
        value = json.loads(text, object_pairs_hook=_unique_object)
    except json.JSONDecodeError:
        fixed, repairs = repair_json_syntax(text)
        value = json.loads(fixed, object_pairs_hook=_unique_object)
    if not isinstance(value, dict): raise ValueError("Expected a JSON object")
    value = deepcopy(value)
    # Missing evidence of completeness must never become an affirmative claim.
    for field in ("x_labels_complete", "series_complete"):
        if field not in value:
            value[field] = False
            repairs.append("defaulted missing " + field + " to false")
    # y_labels is a vocabulary, not a positional series of values. Remove empty
    # entries and exact duplicates only; retain numeric strings (could be categories).
    if isinstance(value.get("y_labels"), list):
        cleaned = []
        for label in value["y_labels"]:
            if label is None or isinstance(label, str) and not label.strip():
                repairs.append("removed empty y label")
                continue
            if not isinstance(label, str):
                raise ValueError("y_labels must contain strings; re-read category labels")
            label = label.strip()
            if label in cleaned:
                repairs.append("removed duplicate y label")
                continue
            if not any(ch.isalnum() for ch in label):
                raise ValueError("Punctuation-only y label; re-read chart structure")
            cleaned.append(label)
        value["y_labels"] = cleaned
    # Do NOT deduplicate series: same name + different colors may be a misread legend.
    return validate_structure(value), list(dict.fromkeys(repairs))
