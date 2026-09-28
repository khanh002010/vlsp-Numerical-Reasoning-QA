"""
ViNumQA Full Pipeline.
Integrates CV Module (Chart-to-Table) and NLP Module (Reasoning Synthesis) 
to answer questions end-to-end.
"""

from vinumqa.cv_module.pipeline import CVPipeline
from vinumqa.nlp_module.pipeline import NLPPipeline
import os

class ViNumQAPipeline:
    def __init__(self, 
                 cv_model_id: str = "Qwen/Qwen2-VL-2B-Instruct",
                 nlp_model_id: str = "Qwen/Qwen2.5-7B-Instruct",
                 nlp_lora_weights: str = None,
                 use_zoom: bool = True,
                 use_reflection: bool = True):
        """
        Initialize the complete end-to-end pipeline.
        """
        print("Initializing ViNumQA Full Pipeline...")
        
        # Initialize CV Module
        self.cv_pipeline = CVPipeline(use_zoom=use_zoom, model_id=cv_model_id)
        
        # Initialize NLP Module
        self.nlp_pipeline = NLPPipeline(base_model_id=nlp_model_id, 
                                        lora_weights=nlp_lora_weights, 
                                        use_reflection=use_reflection)
        
        print("End-to-end Pipeline initialized successfully.")

    def run(self, context_text: str, tables_dict: dict, image_dict: dict, question: str) -> dict:
        """
        Run the full pipeline on a single query.
        Returns the final answer and intermediate reasoning steps.
        """
        from vinumqa.nlp_module.data_prep.format_training_data import dict_to_markdown_table
        
        # 1. Process HTML tables
        html_tables_md = dict_to_markdown_table(tables_dict)
        
        # 2. CV Phase: Extract tables from all images
        extracted_tables = []
        image_keys = []
        for img_key, img_path in image_dict.items():
            image_keys.append(img_key)
            if os.path.exists(img_path):
                md_table = self.cv_pipeline.process_image(img_path)
                extracted_tables.append(f"**{img_key}**\n{md_table}")
            else:
                print(f"Warning: Image not found {img_path}")
                
        cv_tables_md = "\n\n".join(extracted_tables)
        
        # Combine all tables
        combined_markdown_tables = ""
        if html_tables_md:
            combined_markdown_tables += html_tables_md
        if combined_markdown_tables and cv_tables_md:
            combined_markdown_tables += "\n\n"
        if cv_tables_md:
            combined_markdown_tables += cv_tables_md
            
        images_available_str = ", ".join(image_keys)
        
        # 3. NLP Phase: Generate and execute reasoning program
        result = self.nlp_pipeline.process(context_text, combined_markdown_tables, images_available_str, question)
        
        return {
            "extracted_tables": combined_markdown_tables,
            "reasoning_result": result
        }

if __name__ == "__main__":
    print("ViNumQA Full Pipeline is ready.")
