"""Bounded retries; validate every candidate including the last one."""
from vinumqa.utils.dsl_parser import validate_program
from vinumqa.nlp_module.contracts import source_ids, RESPONSE_PREFIX

class ReflectionLoop:
    def __init__(self, generator, max_retries=1):
        if max_retries < 0: raise ValueError("max_retries must be nonnegative")
        self.generator, self.max_retries = generator, max_retries

    def _critique(self, program, extracted_values, context):
        valid, reason = validate_program(program, sources=source_ids(context))
        return "" if valid else reason

    def generate_with_reflection(self, context_text, markdown_table, images_available_str, question):
        original = self.generator._build_prompt(context_text, markdown_table, images_available_str, question)
        prompt = original
        history = []
        for attempt in range(self.max_retries + 1):
            result = self.generator.generate_with_prompt(prompt)
            if "cv_request" in result:
                return {**result, "valid": False, "attempts": history}
            if result.get("error"):
                return {**result, "valid": False, "attempts": history}
            feedback = self._critique(result.get("program", ""), result.get("extracted_values", ""), context_text + "\n" + markdown_table)
            history.append({"program": result.get("program", ""), "validation_error": feedback,
                            "raw_output": result.get("raw_output", "")})
            if not feedback:
                return {**result, "valid": True, "validation_error": "", "attempts": history}
            prompt = (original + f"| 1 | {result.get('extracted_values', '')} |\n| 2 | {result.get('program', '')} |\n"
                      + "\n### Validation feedback\n" + feedback
                      + "\nSửa program theo câu hỏi và nguồn gốc trong context.\n\n" + RESPONSE_PREFIX)
        return {**result, "valid": False, "error": "Validation failed after retries",
                "validation_error": feedback, "attempts": history}
