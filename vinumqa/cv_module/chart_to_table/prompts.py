"""Prompt candidates; selection needs image-grounded evaluation, not format alone."""

GROUNDED_PROMPT = (
    "Extract the data in this image as one Markdown table. "
    "First column: category labels exactly as shown, in image order. Keep quarters and "
    "months; combine them with a grouped year only when that year is visible. "
    "Other columns: the actual data series, using their original names and units. "
    "Arrows, gridlines and axis ticks are not extra series or data points. "
    "Copy printed data values exactly, including signs. For unlabelled points, read each "
    "value independently from its series' axis and prefix estimates with ~; use N/A if "
    "unreadable. Never fill cells by repeating an axis tick. Preserve Vietnamese text. "
    "Do not add categories, dates or series absent from the image. "
    "End the table immediately after the last visible category. Output only the table."
)

CONCISE_PROMPT = (
    "Convert this chart to a Markdown data table. Copy the visible category labels, "
    "series names, units and printed values exactly. Keep each series on its own axis. "
    "Mark visually estimated values with ~ and unreadable values N/A. "
    "Keep the categories in image order and stop at the last one. "
    "Do not invent or extend the data. Output only the table."
)

LITERAL_PROMPT = (
    "Transcribe only the information visibly printed in this image into a Markdown "
    "table. Keep original category labels, series names, units, signs and Vietnamese "
    "text. One row per visible category, in image order. Copy printed data values "
    "exactly; write N/A for values without a readable data label. Do not estimate, "
    "invent additional dates or repeat rows. Stop at the last category. Output only the table."
)

PROMPT_CANDIDATES = {"grounded": GROUNDED_PROMPT, "concise": CONCISE_PROMPT, "literal": LITERAL_PROMPT}
DEFAULT_PROMPT = "grounded"
