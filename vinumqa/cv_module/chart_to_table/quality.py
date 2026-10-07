"""OCR output checks and retry policy, independent of the GPU runtime."""
import re

OCR_VERSION = "chart-markdown-v6-guarded-750k"
OCR_PROMPT = (
    "Read the chart and output its data as a Markdown table. "
    "Use one row per category or time period, in the order shown. Include the year "
    "with each quarter/month. Use separate columns for each series, with the original "
    "legend names and units in the headers. Preserve Vietnamese labels, signs and "
    "number formatting. Copy printed data values exactly. For values without a printed "
    "label, use ~ before an estimate only when the axis scale is readable; otherwise "
    "write N/A. Never present estimates as exact numbers. Include reference lines as "
    "separate named series. Output only the table, with one header and one separator row."
)
FALLBACK_PROMPT = (
    "Transcribe this chart into a Markdown data table. First column: category or full "
    "date. Other columns: named data series with units. Keep Vietnamese labels. Copy "
    "printed numbers exactly; prefix visually estimated values with ~; use N/A when "
    "unreadable. One row per category. Return only the table."
)


def repetition_reason(text):
    """Detect sustained textual cycles inside a cell, not repeated numeric values."""
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
