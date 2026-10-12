"""Conservative source/graph checks; never claims semantic or official accuracy."""
import re
import unicodedata
from decimal import Decimal
from vinumqa.data.context import dict_to_markdown_table
from vinumqa.utils.dsl_parser import parse_program, validate_program, MATH_OPS

REVIEW_VERSION = "source-review-v2-private"
REVIEW_GUIDANCE = """Kiểm tra trước khi trả lời:
- Chọn đúng ảnh, series, ô bảng và mốc thời gian theo câu hỏi; không chọn nguồn chỉ vì tên gần giống.
- Giữ nhãn nguồn, gồm 1H26/6M26/2026F; không tự đổi sang năm hoặc ngày khác.
- Với câu hỏi 'giá trị số', so các con số được yêu cầu; không tự đổi thành bài toán khác.
- Phân biệt giá trị tuyệt đối với cột tăng trưởng svck., phần trăm với điểm phần trăm.
- Giữ đơn vị đích. Chỉ đổi tỷ/nghìn tỷ/triệu khi cần, không nhân 1000 thêm lần nữa.
- Hỏi tổng/chênh lệch hai nhánh phải ghép cả hai ở bước cuối; mọi bước phải góp vào kết quả.
- Trung bình/tổng tại các mốc rời rạc: dùng chart_at từng mốc và add/divide nếu aggregate cả khoảng sẽ lấy thêm điểm.
- Số cụ thể chỉ lấy từ text/bảng. Không dùng nhãn số trong chart structure làm giá trị dữ liệu.
- DSL phẳng: không dùng biểu thức lồng, sum(...), hoặc a+b trong đối số. Dùng các bước và #N.
- Step 1 phải mô tả đúng mọi bước và thứ tự đối số của Step 2.
- Trước khi chọn số, xác định đại lượng, kỳ, đơn vị và nguồn của cả tử số/mẫu số. Hai số cùng xuất hiện trong context chưa đủ chứng minh chúng trả lời câu hỏi.
- Tách chú thích sự kiện khỏi tên series; không dùng một Image khác chỉ vì thiếu nhãn. Với bảng nhiều tầng, dùng đầy đủ header cha@con và đúng hàng chỉ tiêu.
- Nếu không biết giá trị điểm ảnh, vẫn sinh chart_* từ nhãn đã xác minh; không cần tính đáp án số. Không thay chart_* bằng số đoán.
"""


def table_axes(html):
    headers, body = table_grid(html)
    keys = table_key_columns(body)
    primary = keys[-1] if keys else 0
    return [h for i, h in enumerate(headers) if i != primary], [r[primary] for r in body]


def table_grid(html):
    """Use the same merged-cell/header renderer as the model, including all key columns."""
    lines = dict_to_markdown_table({"Table 1": html}).splitlines()
    cells = lambda line: [x.strip().replace("\\|", "|") for x in re.split(r"(?<!\\)\|", line)[1:-1]]
    if len(lines) < 3:
        return [], []
    headers = cells(lines[1])
    return headers, [(cells(line) + [''] * len(headers))[:len(headers)] for line in lines[3:] if line.startswith('|')]


def table_key_columns(body):
    """Leading nonnumeric columns are candidate keys (group, ticker, metric...)."""
    if not body:
        return []
    keys = [0]
    for i in range(1, len(body[0])):
        values = [r[i] for r in body if r[i]]
        if not values or any(re.search(r'\d', v) for v in values):
            break
        keys.append(i)
    return keys


def table_binding_axes(html, metric):
    headers, body = table_grid(html)
    keys = table_key_columns(body)
    axes = []
    if metric in headers:
        axes.extend([r[k] for r in body] for k in keys)
    if any(metric == r[k] for r in body for k in keys):
        axes.append([h for i, h in enumerate(headers) if i not in keys])
    return headers, [r[k] for r in body for k in keys], axes


def source_catalog(tables):
    """Small binding guide; raw tables remain in context, not truncated or replaced."""
    catalog = {}
    for name, html in tables.items():
        headers, body = table_grid(html)
        keys = table_key_columns(body)
        catalog[name] = {'headers': headers, 'row_keys': [[r[k] for r in body] for k in keys]}
    return catalog


def fold(text):
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def structure_concerns(chart):
    """Review hints, not schema rejection or invented replacement labels."""
    reasons = []
    ys = chart.get("y_labels", [])
    # Numeric data/ticks were incorrectly accepted as categorical Y labels.
    if len(ys) >= 3 and all(re.fullmatch(r"[-+()\d.,%\s]+", x) for x in ys):
        if not all(re.fullmatch(r"(?:19|20)\d{2}", x) for x in ys):
            reasons.append("Y labels look like numerical ticks/data; verify axes and categories from pixels")
    names = [fold(s["name"]) for s in chart.get("series", [])]
    if any(n in {"cao nhất 1 năm", "thấp nhất 1 năm"} for n in names):
        reasons.append("Verify whether high/low captions are X categories rather than colored legend series")
    if not names:
        reasons.append("No verified series names")
    if chart.get('kind') != 'pie' and not chart.get('x_labels') and not chart.get('y_labels'):
        reasons.append("No X labels; inspect the actual category/time axis")
    if any('(phải)' in n and s.get('axis') == 'left' for n, s in zip(names, chart.get('series', []))):
        reasons.append("Right-axis legend has left-axis metadata")
    return reasons


def numeric_values(text):
    """Both plausible locales for ambiguous tokens; do not silently choose a locale."""
    values = set()
    for token in re.findall(r"(?<!\w)[+-]?\d+(?:[.,]\d+)*(?!\w)", text):
        variants = {token.replace(",", ""), token.replace(".", "").replace(",", ".")}
        if "," not in token:
            variants.add(token)
        for v in variants:
            try:
                values.add(float(v))
            except ValueError:
                pass
    return values


def validate_semantics(program, tables, text_segments, question):
    valid, reason = validate_program(program)
    if not valid:
        return {"valid": False, "errors": [reason], "warnings": []}
    steps = parse_program(program)
    errors, warnings = [], []
    used = {int(a[1:]) for s in steps for a in s.args if re.fullmatch(r"#\d+", a)}
    unused = sorted(set(range(len(steps) - 1)) - used)
    if unused:
        errors.append(f"Unused intermediate steps {unused}; connect all reasoning branches to the final result")
    for s in steps:
        if not s.operator.startswith("table_"):
            continue
        if s.args[0] not in tables:
            errors.append(f"Unknown table {s.args[0]}")
            continue
        metric, start, end = s.args[1:]
        columns, rows, axes = table_binding_axes(tables[s.args[0]], metric)
        if not axes:
            errors.append(f"Step {s.step_id}: table metric {metric!r} does not exist; columns={columns}, rows={rows}")
            continue
        matching = [axis for axis in axes if all(x == "none" or x in axis for x in (start, end))]
        if not matching:
            errors.append(f"Step {s.step_id}: table range {start!r}..{end!r} is not on the metric's other axis; available={axes}")
        elif start != "none" and end != "none":
            # Aggregate endpoints select an inclusive interval in either display direction.
            # Financial tables often put the newest period first; this isn't a reversed subtraction.
            for axis in matching:
                lo, hi = sorted((axis.index(start), axis.index(end)))
                mentioned = {v for v in axis if v and re.search(r'(?<!\w)' + re.escape(v) + r'(?!\w)', question, re.I)}
                if s.operator in {'table_average', 'table_sum'} and len(mentioned) >= 3 and not any(re.search(r'\d', v) for v in mentioned):
                    selected = set(axis[lo:hi+1])
                    if mentioned <= selected and selected != mentioned:
                        errors.append(f"Step {s.step_id}: question names discrete rows {sorted(mentioned)}; this range includes additional rows. Use individual lookups or source literals.")
        # Only enforce growth columns when the named metric has an explicit YoY sibling.
        q = fold(question)
        if "@" in metric and "tăng trưởng" in q and ("cùng kỳ" in q or "svck" in q):
            prefix = metric.rsplit("@", 1)[0]
            yoy = [c for c in columns if c.startswith(prefix + "@") and "svck" in fold(c)]
            if yoy and metric not in yoy:
                errors.append(f"Step {s.step_id}: question asks YoY growth; verify growth column {yoy}, not absolute value {metric!r}")
    # Facts only from text/tables/question, never numeric chart labels.
    source_text = "\n".join(text_segments) + "\n" + question
    if tables:
        source_text += "\n" + dict_to_markdown_table(tables)
    numbers = numeric_values(source_text)
    # A literal fraction may be the exact representation of a printed percentage.
    # Do not divide *all* source numbers by 100: require an explicit percent sign.
    percent_fractions = set()
    for match in re.finditer(r'([+-]?\d+(?:[.,]\d+)*)\s*%', source_text):
        percent_fractions.update(float(Decimal(str(n)) / 100) for n in numeric_values(match[1]))
    # Common unit conversions may be written as literals already (e.g. 425.3
    # nghin ty -> 425300 ty). Do not reject those as invented numeric facts.
    amounts = set()
    for match in re.finditer(r"([+-]?\d+(?:[.,]\d+)*)\s*(?:nghìn\s+tỷ|tỷ|triệu)\b", source_text, re.I):
        amounts.update(numeric_values(match[1]))
    converted = {abs(n * scale) for n in amounts for scale in (0.001, 1000., 0.000001, 1000000.)}
    magnitudes = {abs(n) for n in numbers}
    constants = {-1., 0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 100., 1000., 1000000., 1000000000.}
    for s in steps:
        if s.operator not in MATH_OPS:
            continue
        for a in s.args:
            if a.startswith("#"):
                continue
            n = float(a)
            if n not in constants and n not in numbers and n not in percent_fractions:
                if abs(n) in magnitudes or abs(n) in converted:
                    warnings.append(f"Step {s.step_id}: verify sign/unit conversion for {a} against its source")
                else:
                    errors.append(f"Step {s.step_id}: literal {a} has no matching number in text/table/question; use source facts and explicit operations")
    # A currency amount minus a ratio of two amounts is dimensionally inconsistent.
    amount_numbers = amounts
    dimensions = {}
    compare_raw_numbers = any(x in fold(question) for x in ("giá trị số", "đơn vị số"))
    for s in steps:
        if s.operator not in MATH_OPS:
            dimensions[s.step_id] = "unknown"
            continue
        dims = [dimensions.get(int(a[1:]), "unknown") if a.startswith("#")
                else "amount" if float(a) in amount_numbers and float(a) not in constants else "scalar" for a in s.args]
        a, b = dims
        out = "unknown"
        if s.operator in {"subtract", "add"}:
            if {a, b} == {"amount", "ratio"} and not compare_raw_numbers:
                errors.append(f"Step {s.step_id}: adding/subtracting money and a dimensionless ratio; verify units")
            if a == b:
                out = a
        elif s.operator == "divide":
            if a == b == "amount": out = "ratio"
            elif a == "amount" and b in {"scalar", "ratio"}: out = "amount"
            elif a == b == "scalar": out = "scalar"
        elif s.operator == "multiply":
            if a == "amount" and b in {"scalar", "ratio"} or b == "amount" and a in {"scalar", "ratio"}: out = "amount"
        dimensions[s.step_id] = out
    return {"valid": not errors, "errors": list(dict.fromkeys(errors)), "warnings": warnings,
            "scope": "Source labels, literal support, dependency graph and limited unit checks; not proof of semantic correctness"}
