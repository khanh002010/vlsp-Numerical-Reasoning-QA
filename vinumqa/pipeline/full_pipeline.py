"""
ViNumQA Full Pipeline.
Integrates CV Module (Chart-to-Table) and NLP Module (Reasoning Synthesis)
to answer questions end-to-end.

Key feature: Inline Context Builder
  - Images/Tables are converted to Markdown and injected INLINE at the exact
    position of their ### Image N ### / ### Table N ### placeholders in text.
  - Placeholders are removed after injection to eliminate noise for the NLP model.
"""

from vinumqa.cv_module.pipeline import CVPipeline
from vinumqa.nlp_module.pipeline import NLPPipeline
import os
import re


# ==============================================================
# CONTEXT BUILDER: Inline placeholder injection
# ==============================================================

def build_inline_context(
    text_segments: list,
    tables_dict: dict,
    image_dict: dict,        # key -> image path (absolute)
    cv_pipeline: CVPipeline,
) -> str:
    """
    Build a clean, unified context string from text, tables, and images.

    Strategy:
      1. Convert every HTML table (tables_dict) to Markdown.
      2. Convert every chart image (image_dict) to Markdown via CV Pipeline (cached).
      3. Walk through text_segments in order:
         - If a segment is "### Table N ###"  → replace it with the Markdown table.
         - If a segment is "### Image N ###"  → replace it with the Markdown table
           produced by Qwen2-VL reading that chart image.
         - Otherwise                          → keep the segment as-is.
      4. Join all resulting segments with double newlines.
         No placeholders remain; no dangling labels.

    Args:
        text_segments:  item['text']  (list of strings from train/test JSON)
        tables_dict:    item['tables'] (dict: "Table 1" -> HTML string)
        image_dict:     dict of "Image 1" -> absolute image file path
        cv_pipeline:    Initialised CVPipeline instance (handles cache internally)

    Returns:
        str: Clean, inline-enriched context ready for the NLP module.
    """
    from vinumqa.nlp_module.data_prep.format_training_data import dict_to_markdown_table

    # --- Pre-convert HTML tables to Markdown (reuse existing helper) ---
    table_md_map: dict[str, str] = {}
    if tables_dict:
        for tbl_key, tbl_html in tables_dict.items():
            md = dict_to_markdown_table({tbl_key: tbl_html})
            # dict_to_markdown_table prepends "**Table N**\n", strip key header
            # to get plain Markdown for inline insertion
            table_md_map[tbl_key] = md

    # --- Pre-convert chart images to Markdown ---
    image_md_map: dict[str, str] = {}
    for img_key, img_path in image_dict.items():
        if os.path.exists(img_path):
            image_md_map[img_key] = cv_pipeline.process_image(img_path)
        else:
            print(f"[WARNING] Image not found: {img_path}")
            image_md_map[img_key] = f"[Image not found: {img_path}]"

    # --- Walk segments and inject inline ---
    # Placeholder pattern: ### Image 1 ### or ### Table 1 ### (case-insensitive)
    placeholder_re = re.compile(
        r'^###\s*(Image|Table)\s+(\d+)\s*###$', re.IGNORECASE
    )

    result_segments: list[str] = []
    for seg in text_segments:
        m = placeholder_re.match(seg.strip())
        if m:
            kind = m.group(1).capitalize()   # "Image" or "Table"
            num  = m.group(2)                 # "1", "2", ...
            key  = f"{kind} {num}"            # e.g. "Image 1"

            if kind == "Table" and key in table_md_map:
                result_segments.append(table_md_map[key])
            elif kind == "Image" and key in image_md_map:
                result_segments.append(image_md_map[key])
            # If key not found, silently drop the placeholder (no noise injected)
        else:
            result_segments.append(seg)

    return "\n\n".join(result_segments)


# ==============================================================
# PIPELINE CLASS
# ==============================================================

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

        # 2. NLP Phase: Generate and execute reasoning program
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
