"""
NLP Pipeline Orchestrator.
Coordinates the ProgramGenerator, SymbolicExecutor, and ReflectionLoop.
"""

from vinumqa.nlp_module.inference.generate_program import ProgramGenerator
from vinumqa.nlp_module.inference.symbolic_executor import SymbolicExecutor
from vinumqa.nlp_module.critic.reflection_loop import ReflectionLoop

class NLPPipeline:
    def __init__(self, base_model_id: str = "Qwen/Qwen2.5-7B-Instruct", lora_weights: str = None, use_reflection: bool = True):
        """
        Initialize the NLP Pipeline.
        """
        print("Initializing NLP Pipeline...")
        self.generator = ProgramGenerator(base_model_id=base_model_id, lora_weights=lora_weights)
        self.use_reflection = use_reflection
        
        if self.use_reflection:
            self.reflection_loop = ReflectionLoop(self.generator)
            
        print("NLP Pipeline initialized.")

    def process(self, context_text: str, markdown_table: str, images_available_str: str, question: str) -> dict:
        """
        Process the inputs to generate and execute a reasoning program.
        Returns program, validation status and generation diagnostics.
        """
        if self.use_reflection:
            return self.reflection_loop.generate_with_reflection(context_text, markdown_table, images_available_str, question)
        else:
            return ReflectionLoop(self.generator, max_retries=0).generate_with_reflection(context_text, markdown_table, images_available_str, question)

    def close(self):
        self.generator.close()

if __name__ == "__main__":
    print("NLPPipeline module is ready.")
