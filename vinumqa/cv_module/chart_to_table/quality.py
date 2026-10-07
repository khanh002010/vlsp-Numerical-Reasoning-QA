"""OCR output checks and retry policy, independent of the GPU runtime."""
import re
from .prompts import GROUNDED_PROMPT, CONCISE_PROMPT

OCR_VERSION = "chart-markdown-v7-grounded-1400k"
OCR_PROMPT = GROUNDED_PROMPT
FALLBACK_PROMPT = CONCISE_PROMPT


def repeated_estimates_reason(text):
    """Flag a suspicious flat matrix of estimates, not an ordinary flat series.

    Twelve consecutive rows must copy the SAME estimate into every value column
    (at least two). This is a review heuristic, not proof the image is wrong.
    Exact repeated numbers, missing values and a flat reference line are allowed.
    """
    previous, run = None, 0
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [re.sub(r"\s+", "", cell) for cell in re.split(r"(?<!\\)\|", line[1:-1])]
        values = cells[1:]
        if (len(values) >= 2 and cells[0] and len(set(values)) == 1
                and re.fullmatch(r"~[-+]?\d[\d.,]*%?", values[0])):
            signature = tuple(values)
            run = run + 1 if signature == previous else 1
            previous = signature
            if run >= 12:
                return "suspicious_repeated_estimates: identical estimates across 12 rows and all series"
        else:
            previous, run = None, 0
    return None


def repetition_reason(text):
    """Detect sustained textual cycles inside a cell, not repeated numeric values."""
    suspicious = repeated_estimates_reason(text)
    if suspicious:
        return suspicious
    for line in text[-8192:].splitlines():
        words = re.findall(r"\w+", line.casefold())[-256:]
        for width in range(2, 25):
            for offset in range(width):
                end = len(words) - offset
                if end < width * 6:
                    continue
                block = words[end-width:end]
                # Zero-filled tables and repeating numeric measurements are legal.
                if len({w for w in block if w.isalpha()}) < 2:
                    continue
                if words[end-width*6:end] == block * 6:
                    return "inline_repetition: " + " ".join(block)
    return None


def validate_table(text, min_columns=1):
    if not isinstance(text, str):
        raise ValueError("OCR output is not text")
    reason = repetition_reason(text)
    if reason:
        raise ValueError(reason)
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if lines and lines[0].startswith("```") and lines[-1] == "```":
        lines = lines[1:-1]
    if len(lines) < 3 or any(not line.startswith("|") or not line.endswith("|") for line in lines):
        raise ValueError("Expected a complete Markdown table with data rows")
    rows = [re.split(r"(?<!\\)\|", line[1:-1]) for line in lines]
    width = len(rows[0])
    if width < min_columns or any(len(row) != width for row in rows):
        raise ValueError("Inconsistent Markdown column count")
    if any(not cell.strip() for cell in rows[0]):
        raise ValueError("Missing table column name")
    if any(not re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in rows[1]):
        raise ValueError("Missing Markdown header separator")
    if not any(any(cell.strip() for cell in row) for row in rows[2:]):
        raise ValueError("Table has no data")
    return "\n".join(lines)


def extract_with_retries(generate, budgets, attempts):
    """Grow only genuinely truncated output; retry bad output once with a new prompt."""
    budgets = list(budgets)
    if not budgets:
        raise ValueError("Empty OCR token schedule")
    for fallback in (False, True):
        schedule = budgets if not fallback else sorted(set([min(budgets[0], 2048)] + budgets))
        for budget in schedule:
            result = generate(budget, fallback)
            attempts.append({k: v for k, v in result.items() if k not in ("token_ids", "raw_text")}
                            | {"budget": budget, "fallback": fallback})
            reason = repetition_reason(result["text"])
            if result.get("stop_reason") == "repetition":
                reason = reason or "repetition"
            if not reason and result["eos"]:
                try:
                    return validate_table(result["text"], min_columns=2)
                except ValueError as error:
                    reason = str(error)
            if reason:
                attempts[-1]["quality_error"] = reason
                if fallback:
                    raise ValueError(f"OCR failed after alternate prompt: {reason}")
                # Restart with a new prompt, not a larger looping generation.
                break
            if not result["eos"] and len(result["token_ids"]) < budget:
                raise ValueError("OCR stopped without EOS")
        else:
            raise ValueError("OCR reached maximum token budget without EOS; incomplete table")
