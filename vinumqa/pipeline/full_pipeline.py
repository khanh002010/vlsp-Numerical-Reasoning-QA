"""
ViNumQA Full Pipeline.
Integrates CV Module (Chart-to-Table) and NLP Module (Reasoning Synthesis)
to answer questions end-to-end.

Key feature: Inline Context Builder
  - Images/Tables are converted to Markdown and injected INLINE at the exact
    position of their ### Image N ### / ### Table N ### placeholders in text.
  - Placeholders are removed after injection to eliminate noise for the NLP model.
"""

# ==============================================================
# CONTEXT BUILDER: Inline placeholder injection
# ==============================================================

from vinumqa.data.context import build_inline_context


class ViNumQAPipeline:
    def __init__(self,
                 cv_model_id: str = "Qwen/Qwen2-VL-2B-Instruct",
                 nlp_model_id: str = "Qwen/Qwen2.5-7B-Instruct",
                 nlp_lora_weights: str = None,
                 use_reflection: bool = True):
        """
        Initialize the complete end-to-end pipeline.
        Note: Zoom Tool has been removed. EDA shows image resolution averages ~622k pixels,
        well within max_pixels=750k, so single-pass extraction is sufficient.
        """
        from vinumqa.cv_module.pipeline import CVPipeline
        from vinumqa.nlp_module.pipeline import NLPPipeline
        print("Initializing ViNumQA Full Pipeline...")

        # Initialize CV Module (no zoom)
        self.cv_pipeline = CVPipeline(model_id=cv_model_id)

        # Initialize NLP Module
        self.nlp_pipeline = NLPPipeline(
            base_model_id=nlp_model_id,
            lora_weights=nlp_lora_weights,
            use_reflection=use_reflection
        )

        print("End-to-end Pipeline initialized successfully.")

    def run(self,
            text_segments: list,
            tables_dict: dict,
            image_dict: dict,
            question: str) -> dict:
        """
        Run the full pipeline on a single query.

        Args:
            text_segments: item['text'] from JSON  (list of strings, may contain placeholders)
            tables_dict:   item['tables'] from JSON (dict: key -> HTML string)
            image_dict:    dict of image_key -> ABSOLUTE path to image file
            question:      the question string

        Returns:
            dict with 'inline_context' (assembled context) and 'reasoning_result'.
        """
        # 1. Build inline context: inject images/tables at placeholder positions
        inline_context = build_inline_context(
            text_segments=text_segments,
            tables_dict=tables_dict,
            image_dict=image_dict,
            cv_pipeline=self.cv_pipeline,
        )

        # 2. Generate and validate the competition program (no guessed execution).
        images_available_str = ", ".join(image_dict.keys())
        result = self.nlp_pipeline.process(
            inline_context, "", images_available_str, question
        )

        return {
            "inline_context": inline_context,
            "reasoning_result": result
        }


if __name__ == "__main__":
    print("ViNumQA Full Pipeline is ready.")
