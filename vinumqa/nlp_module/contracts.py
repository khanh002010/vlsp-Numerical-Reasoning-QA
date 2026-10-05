"""Shared, versioned training/inference contract; no model dependencies."""
import json
import re
from vinumqa.nlp_module.dsl_operators import DSL_OPERATORS
from vinumqa.utils.dsl_parser import parse_program, validate_program

FORMAT_VERSION = "vinumqa-v4"
RESPONSE_PREFIX = "### Response\n| Step | Output |\n|---|---|\n"
DSL_HINT_SHORT = "Operators: " + ", ".join(DSL_OPERATORS) + "."
INSTRUCTION = """### Instruction
Sinh reasoning program từ bằng chứng trong context để trả lời câu hỏi.
Step 1: Ghi các literal/lookup có nhóm và vai trò đối số dưới dạng JSON, giữ giá trị lặp.
Step 2: Chỉ viết program DSL. Mỗi operation được đánh số từ 0. #N chỉ tham chiếu
operation trước đó trong Step 2, không tham chiếu danh sách evidence ở Step 1.
Đọc điểm biểu đồ bằng chart_at; đọc tổng/trung bình/cực trị đúng nguồn và phạm vi.
Với số cụ thể trong văn bản/bảng có thể dùng literal; không ép mọi ô bảng thành aggregate.
Giữ nguyên Image/Table ID, tên series, nhãn hàng/cột và mốc thời gian. Không dịch nhãn.
Không tính sẵn lookup biểu đồ thành số. Không rút gọn chuỗi reasoning thành đáp án cuối.
Phân biệt chênh lệch a-b, tỷ số a/b, tăng trưởng (new-old)/old*100 và điểm phần trăm.
Giữ thứ tự đối số của subtract/divide/greater/exp. Số DSL dùng dấu chấm thập phân.
Math có 2 đối số; table/chart có 4 đối số; phân cách đối số và bước bằng dấu ;.
""" + "\n" + "\n".join(v["signature"] for v in DSL_OPERATORS.values())

def input_text(context, question, images=""):
    if images:
        context = context.rstrip() + "\n\n### Images Available\n" + images
    return f"### Context\n{context.strip()}\n\n### Question\n{question}"

def build_prompt(context, question, images=""):
    return f"{INSTRUCTION}\n\n{input_text(context, question, images)}\n\n{RESPONSE_PREFIX}"

def evidence_from_program(program):
    """Argument supervision, not invented coordinates for unaligned numeric literals."""
    valid, reason = validate_program(program)
    if not valid: raise ValueError(reason)
    return json.dumps([{"step": s.step_id, "operator": s.operator,
        "arguments": [{"position": i, "value": a} for i, a in enumerate(s.args) if not a.startswith("#")]}
        for s in parse_program(program)], ensure_ascii=False, separators=(",", ":"))

def parse_response(text):
    # Permit line breaks inside a cell, but never use partially generated cells.
    result = {"extracted_values": "", "program": "", "raw_output": text}
    for step, key in [(1, "extracted_values"), (2, "program")]:
        matches = re.findall(r"(?:^|\n)\s*\|\s*" + str(step) + r"\s*\|\s*(.*?)\s*\|(?=\s*(?:\n|$))", text, re.S)
        if len(matches) == 1: result[key] = matches[0].strip()
    result["valid"], result["validation_error"] = validate_program(result["program"])
    return result

def source_ids(context):
    return set(re.findall(r"\*\*((?:Image|Table) [1-9]\d*)\*\*", context))
