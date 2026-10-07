"""One context builder for formatting and inference. Preserve raw table cell text."""
import re
from pathlib import Path
from html.parser import HTMLParser

class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.depth, self.cell = [], 0, None

    def handle_starttag(self, tag, attrs):
        if tag == "table": self.depth += 1
        if self.depth != 1: return
        if tag == "tr": self.rows.append([])
        if tag in {"td", "th"}:
            if not self.rows: self.rows.append([])
            self.cell = {**dict(attrs), "tag": tag, "text": ""}
            self.rows[-1].append(self.cell)
        if tag == "br" and self.cell is not None: self.cell["text"] += " "

    def handle_endtag(self, tag):
        if tag == "table": self.depth -= 1
        if tag in {"td", "th"}: self.cell = None

    def handle_data(self, data):
        if self.depth == 1 and self.cell is not None: self.cell["text"] += data

def dict_to_markdown_table(tables):
    output = []
    for name, html in tables.items():
        parser = _TableParser()
        parser.feed(html)
        grid = {}
        rows = parser.rows
        for r, row in enumerate(rows):
            c = 0
            for cell in row:
                while (r, c) in grid: c += 1
                value = re.sub(r"\s+", " ", cell["text"]).strip().replace("|", "\\|")
                rs, cs = int(cell.get("rowspan", 1)), int(cell.get("colspan", 1))
                for dr in range(rs):
                    for dc in range(cs): grid[r + dr, c + dc] = value
                c += cs
        if not grid: raise ValueError(f"{name}: empty table")
        width = max(c for _, c in grid) + 1
        # Consecutive all-th rows or merged first-row column headers form header paths.
        header_count = 1
        first = rows[0]
        if any(int(c.get("colspan", 1)) > 1 and c["text"].strip() for c in first) and len(rows) > 1:
            header_count = max(2, max(int(c.get("rowspan", 1)) for c in first))
        while header_count < len(rows) and rows[header_count] and all(c["tag"] == "th" for c in rows[header_count]):
            header_count += 1
        headers = []
        for c in range(width):
            path = list(dict.fromkeys(grid.get((r, c), "") for r in range(header_count)))
            headers.append("@".join(x for x in path if x) or f"column_{c}")
        lines = [f"**{name}**", "| " + " | ".join(headers) + " |", "|" + "---|" * width]
        for r in range(header_count, len(rows)):
            lines.append("| " + " | ".join(grid.get((r, c), "") for c in range(width)) + " |")
        output.append("\n".join(lines))
    return "\n\n".join(output)

def build_inline_context(text_segments, tables_dict, image_dict, cv_pipeline, prepared_images=None, chart_structures=None):
    if not isinstance(text_segments, list): raise TypeError("text_segments must be a list")
    blocks = {k: dict_to_markdown_table({k: v}) for k, v in tables_dict.items()}
    for key, path in image_dict.items():
        if chart_structures is not None:
            from vinumqa.cv_module.structure import render_structure
            blocks[key] = f"**{key}**\n" + render_structure(key, chart_structures[key])
            continue
        if prepared_images is not None:
            table = prepared_images[key]
        else:
            if cv_pipeline is None: raise ValueError("Real CV extraction/cache is required; placeholders are not training data")
            if not Path(path).is_file(): raise FileNotFoundError(path)
            table = cv_pipeline.process_image(str(path))
        if not table.strip() or "| Lỗi |" in table or "extracted by CV Module" in table:
            raise ValueError(f"CV extraction failed for {key}")
        blocks[key] = f"**{key}**\n{table}"
    output, used = [], set()
    pattern = re.compile(r"^###\s*(Image|Table)\s+(\d+)\s*###$", re.I)
    for segment in text_segments:
        m = pattern.fullmatch(segment.strip())
        if m:
            key = f"{m[1].capitalize()} {m[2]}"
            if key not in blocks: raise ValueError(f"Unresolved source placeholder: {key}")
            output.append(blocks[key]); used.add(key)
        else: output.append(segment)
    output.extend(v for k, v in blocks.items() if k not in used)
    return "\n\n".join(output)
