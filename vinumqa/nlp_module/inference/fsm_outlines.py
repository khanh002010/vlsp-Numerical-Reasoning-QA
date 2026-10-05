"""
MỨC ĐỘ 3: FINITE STATE MACHINE (FSM) CONSTRAINED DECODING
Yêu cầu cài đặt: pip install outlines

File này minh họa cách sử dụng thư viện `outlines` để ép buộc (force) 
LLM sinh ra chính xác cú pháp DSL mà không thể sai dù chỉ 1 dấu phẩy.
Khác với LogitsProcessor chỉ kiểm tra chữ cái đầu, FSM kiểm tra toàn bộ chuỗi.
"""

# Lưu ý: Cần cài đặt outlines trước khi sử dụng file này
# try:
#     import outlines
# except ImportError:
#     raise ImportError("Vui lòng cài đặt thư viện outlines: pip install outlines")

class FSMLogicGenerator:
    def __init__(self, model, tokenizer):
        """
        Khởi tạo FSM Generator với mô hình Qwen2.5 đã nạp LoRA.
        """
        import outlines
        
        # 1. Bọc mô hình HuggingFace bằng outlines
        self.outlines_model = outlines.models.Transformers(model, tokenizer)
        
        # 2. Định nghĩa Regex ngữ pháp tuyệt đối (Absolute Grammar Regex)
        # - Step 1: Phải có chữ "| 1 |" và các giá trị cách nhau bằng dấu #
        # - Step 2: Phải có chữ "| 2 |"
        # - Bên trong Step 2: Bắt buộc gọi đúng tên hàm, mở ngoặc (, điền tham số cách nhau bởi dấu ;, đóng ngoặc ).
        
        math_ops = r"(?:add|subtract|multiply|divide|greater|exp)"
        table_ops = r"(?:table_max|table_min|table_sum|table_average)"
        chart_ops = r"(?:chart_sum|chart_average|chart_max|chart_min|chart_total|chart_at)"
        
        # Hàm toán học luôn có 2 tham số (số hoặc #N)
        math_regex = rf"{math_ops}\([^;)]+; [^;)]+\)"
        
        # Hàm bảng/biểu đồ luôn có 4 tham số
        table_chart_regex = rf"(?:{table_ops}|{chart_ops})\([^;)]+; [^;)]+; [^;)]+; [^;)]+\)"
        
        # Một bước (step) có thể là hàm toán học HOẶC hàm bảng/biểu đồ
        step_regex = rf"(?:{math_regex}|{table_chart_regex})"
        
        # Toàn bộ biểu thức regex cho Step 2 (các bước cách nhau bằng dấu chấm phẩy)
        program_regex = rf"{step_regex}(?:; {step_regex})*"
        
        # Tổng hợp Regex cho toàn bộ bảng Output
        full_regex = rf"\| 1 \| [^\n]+ \|\n\| 2 \| {program_regex} \|"
        
        # 3. Biên dịch FSM
        self.generator = outlines.generate.regex(self.outlines_model, full_regex)
        
    def generate_with_fsm(self, prompt: str) -> str:
        """
        Sinh ra kết quả với FSM. Mô hình sẽ bị "khóa mồm" và chỉ có thể 
        nhả ra các ký tự khớp với full_regex.
        """
        # Outlines sẽ tự động kiểm soát quá trình generate dưới nền
        result = self.generator(prompt, max_tokens=768, temperature=0.0)
        return result
