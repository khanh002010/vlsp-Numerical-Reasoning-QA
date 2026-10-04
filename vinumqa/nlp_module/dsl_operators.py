"""
ViNumQA DSL (Domain Specific Language) Operator Definitions
============================================================
14 operators extracted from train.json (1725 samples).
Used by:
  - NLP Module (Qwen2.5-7B fine-tuning prompt)
  - Symbolic Executor (runtime dispatch)
  - Data Augmentation (synthetic sample generation)

Frequency order (from EDA on training set):
  subtract: 1005 | chart_at: 850 | divide: 619 | multiply: 358
  add: 264 | chart_max: 128 | table_max: 121 | table_average: 107
  greater: 103 | table_min: 98 | chart_min: 93 | chart_average: 89
  table_sum: 54 | chart_sum: 32
"""

from typing import Union

Number = Union[int, float]


# ==============================================================
# OPERATOR DEFINITIONS (Sorted by frequency)
# ==============================================================

DSL_OPERATORS = {

    # ----------------------------------------------------------
    # 1. ARITHMETIC OPERATORS (Phép toán số học)
    # ----------------------------------------------------------

    "subtract": {
        "signature": "subtract(a; b)",
        "args": ["a: number", "b: number"],
        "returns": "number",
        "description": "Tính hiệu a - b. Đây là toán tử phổ biến nhất (1005 lần).",
        "example_program": "chart_at(Image 1; P/B trượt; Jul-21; none); subtract(#0; 2.1)",
        "example_meaning": "Đọc giá trị P/B từ biểu đồ tại Jul-21, sau đó trừ đi 2.1",
        "impl": lambda a, b: a - b,
    },

    "divide": {
        "signature": "divide(a; b)",
        "args": ["a: number", "b: number (denominator, != 0)"],
        "returns": "number",
        "description": "Tính thương a / b. Dùng cho tính tỷ lệ và phần trăm (619 lần).",
        "example_program": "multiply(46976; 100); divide(#0; 169736)",
        "example_meaning": "Tính (46976 * 100) / 169736 → Tỷ lệ phần trăm",
        "impl": lambda a, b: a / b if b != 0 else None,
    },

    "multiply": {
        "signature": "multiply(a; b)",
        "args": ["a: number", "b: number"],
        "returns": "number",
        "description": "Tính tích a * b. Thường dùng để nhân với 100 khi tính % (358 lần).",
        "example_program": "multiply(46976; 100); divide(#0; 169736)",
        "example_meaning": "Nhân 46976 với 100 để đổi sang đơn vị %, sau đó chia",
        "impl": lambda a, b: a * b,
    },

    "add": {
        "signature": "add(a; b)",
        "args": ["a: number", "b: number"],
        "returns": "number",
        "description": "Tính tổng a + b. Dùng để cộng nhiều giá trị lại (264 lần).",
        "example_program": "chart_at(Image 4; Ocean Park 3; Doanh thu; none); chart_at(Image 4; Ocean Park 4; Doanh thu; none); add(#0; #1)",
        "example_meaning": "Đọc doanh thu của 2 dự án rồi cộng lại",
        "impl": lambda a, b: a + b,
    },

    "greater": {
        "signature": "greater(a; b)",
        "args": ["a: number", "b: number"],
        "returns": "bool (1 nếu a > b, 0 nếu không)",
        "description": "So sánh a > b. Dùng để trả lời câu hỏi dạng 'Có/Không' (103 lần).",
        "example_program": "table_sum(Table 1; LNST; FY18; FY19); greater(28063; #0)",
        "example_meaning": "Tính tổng LNST FY18-FY19, sau đó kiểm tra xem 28063 > tổng đó không",
        "impl": lambda a, b: 1 if a > b else 0,
    },

    "exp": {
        "signature": "exp(a; b)",
        "args": ["a: number", "b: number"],
        "returns": "number",
        "description": "Tính lũy thừa a^b.",
        "example_program": "exp(1.05; 3)",
        "example_meaning": "Tính 1.05 mũ 3",
        "impl": lambda a, b: a ** b,
    },

    # ----------------------------------------------------------
    # 2. CHART OPERATORS (Đọc dữ liệu từ Biểu đồ)
    # ----------------------------------------------------------

    "chart_at": {
        "signature": "chart_at(image_id; series_name; x_label; y_label_or_none)",
        "args": [
            "image_id: str   (e.g. 'Image 1')",
            "series_name: str (tên đường/cột trong biểu đồ, e.g. 'P/B trượt')",
            "x_label: str    (giá trị trên trục X, e.g. 'Jul-21', '2023')",
            "y_label_or_none: str  (giá trị trên trục Y hoặc 'none' nếu không cần lọc thêm)",
        ],
        "returns": "number",
        "description": "Đọc một điểm dữ liệu cụ thể từ biểu đồ. Toán tử đặc thù nhất của bài toán VQA (850 lần).",
        "example_program": "chart_at(Image 1; P/B trượt; Jul-21; none)",
        "example_meaning": "Trả về giá trị P/B tại điểm Jul-21 trên đường 'P/B trượt' trong Image 1",
    },

    "chart_max": {
        "signature": "chart_max(image_id; series_name; x_start_or_none; x_end_or_none)",
        "args": [
            "image_id: str",
            "series_name: str (tên đường/cột cần tìm max)",
            "x_start_or_none: str (điểm bắt đầu trên trục X hoặc 'none' = toàn bộ)",
            "x_end_or_none: str   (điểm kết thúc trên trục X hoặc 'none' = toàn bộ)",
        ],
        "returns": "number",
        "description": "Tìm giá trị lớn nhất của một series trong biểu đồ (128 lần).",
        "example_program": "chart_max(Image 1; CAGR 2020 - 2023 (%); none; none)",
        "example_meaning": "Tìm giá trị CAGR lớn nhất trong toàn bộ series của Image 1",
    },

    "chart_min": {
        "signature": "chart_min(image_id; series_name; x_start_or_none; x_end_or_none)",
        "args": [
            "image_id: str",
            "series_name: str",
            "x_start_or_none: str",
            "x_end_or_none: str",
        ],
        "returns": "number",
        "description": "Tìm giá trị nhỏ nhất của một series trong biểu đồ (93 lần).",
        "example_program": "chart_min(Image 4; Suất sinh lời tài sản bình quân; 2013; 2021)",
        "example_meaning": "Tìm ROA nhỏ nhất trong khoảng năm 2013 đến 2021",
    },

    "chart_average": {
        "signature": "chart_average(image_key; name; start; end)",
        "args": [
            "image_key: str",
            "name: str",
            "start: str",
            "end: str",
        ],
        "returns": "number",
        "description": "Tính trung bình các điểm dữ liệu trong một khoảng trên biểu đồ (89 lần).",
        "example_program": "chart_average(Image 1; 2023; Thang 1; Thang 6)",
        "example_meaning": "Tính trung bình giá trị trong Image 1 từ Tháng 1 đến Tháng 6 năm 2023",
    },

    "chart_sum": {
        "signature": "chart_sum(image_id; series_name; x_start_or_none; x_end_or_none)",
        "args": [
            "image_id: str",
            "series_name: str",
            "x_start_or_none: str",
            "x_end_or_none: str",
        ],
        "returns": "number",
        "description": "Tính tổng các điểm dữ liệu trong một series trên biểu đồ (32 lần). [HIẾM - cần Data Augmentation]",
        "example_program": "chart_sum(Image 1; Chi tieu 2024E; none; none)",
        "example_meaning": "Tính tổng toàn bộ giá trị trong series 'Chi tiêu 2024E' của Image 1",
    },

    "chart_total": {
        "signature": "chart_total(image_id; x_label; y_label_or_none; series_name_or_none)",
        "args": [
            "image_id: str",
            "x_label: str",
            "y_label_or_none: str",
            "series_name_or_none: str",
        ],
        "returns": "number",
        "description": "Tính tổng các thành phần tại một điểm x trên biểu đồ.",
        "example_program": "chart_total(Image 1; Jan-25; none; none)",
        "example_meaning": "Tính tổng các giá trị tại Jan-25 trên Image 1",
    },

    # ----------------------------------------------------------
    # 3. TABLE OPERATORS (Đọc dữ liệu từ Bảng)
    # ----------------------------------------------------------

    "table_max": {
        "signature": "table_max(table_id; column_name; row_start_or_none; row_end_or_none)",
        "args": [
            "table_id: str   (e.g. 'Table 1')",
            "column_name: str (tên cột cần tìm max)",
            "row_start_or_none: str (nhãn hàng bắt đầu hoặc 'none' = toàn bảng)",
            "row_end_or_none: str   (nhãn hàng kết thúc hoặc 'none' = toàn bảng)",
        ],
        "returns": "number",
        "description": "Tìm giá trị lớn nhất trong một cột của bảng (121 lần).",
        "example_program": "table_max(Table 1; Dau tu cong (%); 2021; 2025F)",
        "example_meaning": "Tìm tỷ lệ đầu tư công lớn nhất trong khoảng năm 2021 đến 2025F",
    },

    "table_min": {
        "signature": "table_min(table_id; column_name; row_start_or_none; row_end_or_none)",
        "args": [
            "table_id: str",
            "column_name: str",
            "row_start_or_none: str",
            "row_end_or_none: str",
        ],
        "returns": "number",
        "description": "Tìm giá trị nhỏ nhất trong một cột của bảng (98 lần).",
        "example_program": "table_min(Table 1; Doanh thu ban le danh nghia (%); 2021; 2025F)",
        "example_meaning": "Tìm tỷ lệ doanh thu bán lẻ nhỏ nhất từ 2021 đến 2025F",
    },

    "table_average": {
        "signature": "table_average(table_id; column_name; row_start; row_end)",
        "args": [
            "table_id: str",
            "column_name: str",
            "row_start: str",
            "row_end: str",
        ],
        "returns": "number",
        "description": "Tính trung bình các giá trị trong một cột của bảng (107 lần).",
        "example_program": "table_average(Table 1; ROE (%); 2025F; 2027F)",
        "example_meaning": "Tính ROE trung bình trong khoảng dự báo 2025F-2027F",
    },

    "table_sum": {
        "signature": "table_sum(table_id; column_name; row_start; row_end)",
        "args": [
            "table_id: str",
            "column_name: str",
            "row_start: str",
            "row_end: str",
        ],
        "returns": "number",
        "description": "Tính tổng các giá trị trong một cột của bảng (54 lần).",
        "example_program": "table_sum(Table 1; LNST (ty dong); FY18; FY19)",
        "example_meaning": "Tính tổng lợi nhuận sau thuế từ FY18 đến FY19",
    },
}


# ==============================================================
# HELPER: Generate System Prompt for NLP Fine-tuning
# ==============================================================

def get_dsl_system_prompt() -> str:
    """
    Returns the DSL definition block to be prepended to the NLP model's
    system prompt during both fine-tuning and inference.
    """
    lines = [
        "## Hệ thống Toán tử DSL (Domain Specific Language)",
        "Bạn phải sinh ra chương trình (program) chỉ sử dụng các toán tử sau:",
        "",
        "### Nhóm 1: Phép toán số học",
        "  - subtract(a; b)     → a - b",
        "  - divide(a; b)       → a / b",
        "  - multiply(a; b)     → a * b",
        "  - add(a; b)          → a + b",
        "  - greater(a; b)      → 1 nếu a > b, ngược lại 0",
        "  - exp(a; b)          → a ^ b",
        "",
        "### Nhóm 2: Đọc dữ liệu từ Biểu đồ (image_id là 'Image 1', 'Image 2'...)",
        "  - chart_at(image_id; series_name; x_label; y_label_or_none)             → một điểm số",
        "  - chart_max(image_id; series_name; x_start_or_none; x_end_or_none)      → số lớn nhất",
        "  - chart_min(image_id; series_name; x_start_or_none; x_end_or_none)      → số nhỏ nhất",
        "  - chart_average(image_key; name; start; end)  → số trung bình",
        "  - chart_sum(image_id; series_name; x_start_or_none; x_end_or_none)      → tổng",
        "  - chart_total(image_id; x_label; y_label_or_none; series_name_or_none)  → tổng các thành phần",
        "",
        "### Nhóm 3: Đọc dữ liệu từ Bảng (table_id là 'Table 1', 'Table 2'...)",
        "  - table_max(table_id; column_name; row_start_or_none; row_end_or_none)     → số lớn nhất",
        "  - table_min(table_id; column_name; row_start_or_none; row_end_or_none)     → số nhỏ nhất",
        "  - table_average(table_id; column_name; row_start; row_end)                → số trung bình",
        "  - table_sum(table_id; column_name; row_start; row_end)                    → tổng",
        "",
        "### Quy tắc viết Program",
        "  - Mỗi bước trung gian được lưu tự động: bước 0 là #0, bước 1 là #1...",
        "  - Dùng 'none' khi không cần giới hạn phạm vi.",
        "  - Dấu phân cách giữa các đối số là dấu chấm phẩy (;).",
        "  - Kết quả bước trước dùng lại bằng #N (e.g. subtract(#0; #1)).",
        "  - CHỈ được dùng 16 toán tử trên, không tự tạo toán tử mới.",
    ]
    return "\n".join(lines)


# ==============================================================
# QUICK REFERENCE (Summary for inspection)
# ==============================================================

OPERATOR_NAMES = list(DSL_OPERATORS.keys())  # 16 operators

RARE_OPERATORS = ["chart_sum", "table_sum", "exp", "chart_total"]  # < 55 samples → cần Data Augmentation


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"Total DSL operators defined: {len(DSL_OPERATORS)}")
    print(f"Rare operators (need augmentation): {RARE_OPERATORS}")
    print()
    print(get_dsl_system_prompt())
