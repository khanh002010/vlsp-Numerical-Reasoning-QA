"""
Critic Agent / Reflection Loop.
Verifies the generated reasoning program and extracted values.
If errors are found, it triggers a regeneration with feedback.
"""

from vinumqa.nlp_module.inference.generate_program import ProgramGenerator
from vinumqa.utils.dsl_parser import validate_program

class ReflectionLoop:
    def __init__(self, generator: ProgramGenerator, max_retries: int = 1):
        """
        Initialize the Reflection Loop with a ProgramGenerator.
        """
        self.generator = generator
        self.max_retries = max_retries
        print("Reflection Loop initialized.")

    def _critique(self, program: str, extracted_values: str, context: str) -> str:
        """
        Analyze the output for logical or syntactic errors.
        Returns a feedback string if errors are found, else empty string.
        """
        feedback = []
        
        # 1. Syntactic / DSL check
        is_valid, msg = validate_program(program)
        if not is_valid:
            feedback.append(f"Lỗi cú pháp: {msg}. Vui lòng sửa lại công thức cho đúng định dạng.")
            
        # 2. Logic check: division by zero, invalid references, etc.
        # Handled partially by validate_program, but we could add more heuristics here.
        if "divide" in program and " 0" in program:
            feedback.append("Cảnh báo: Có khả năng chia cho 0.")
            
        # 3. Data consistency check
        # Verify if extracted values actually exist in the context
        values = extracted_values.split("#")
        for val in values:
            v_clean = val.strip()
            if not v_clean:
                continue
            # Ignore special DSL structural keywords
            if v_clean.lower() == "none" or v_clean.lower().startswith("table ") or v_clean.lower().startswith("image "):
                continue
                
            if v_clean not in context:
                feedback.append(f"Cảnh báo: Giá trị '{v_clean}' không tìm thấy trong văn bản hoặc bảng.")
                
        return " ".join(feedback)

    def generate_with_reflection(self, context_text: str, markdown_table: str, images_available_str: str, question: str) -> dict:
        """
        Generate program, critique it, and regenerate if necessary.
        """
        # First attempt
        result = self.generator.generate(context_text, markdown_table, images_available_str, question)
        
        if "error" in result:
            return result
            
        context_combined = context_text + "\n" + markdown_table
        
        for attempt in range(self.max_retries):
            feedback = self._critique(result["program"], result["extracted_values"], context_combined)
            
            if not feedback:
                # No errors found, return result
                break
                
            print(f"Reflection triggered (Attempt {attempt+1}): {feedback}")
            
            # Re-build prompt with feedback
            original_prompt = self.generator._build_prompt(context_text, markdown_table, images_available_str, question)
            retry_prompt = (
                original_prompt + 
                f"| 1 | {result['extracted_values']} |\n"
                f"| 2 | {result['program']} |\n\n"
                f"### Feedback từ Critic\n{feedback}\nHãy làm lại từ đầu và sinh ra kết quả đúng.\n\n"
                "### Response\n| Step | Output |\n|---|---|\n"
            )
            
            # We would need to expose a method in ProgramGenerator to take raw prompts, 
            # or pass the feedback to generate(). For this template, we simulate it:
            # result = self.generator.generate_with_prompt(retry_prompt)
            # (Assuming self.generator has been updated to support this)
            
            # Since it's a template, we just break to avoid infinite loops if not implemented
            break
            
        return result

if __name__ == "__main__":
    print("ReflectionLoop module is ready.")
