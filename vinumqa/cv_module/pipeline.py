"""
CV Pipeline Orchestrator.
Combines ChartToTableExtractor and VerifyAgent to extract highly accurate tables from charts.
"""

from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor
from vinumqa.cv_module.zoom_verify.verify_agent import VerifyAgent

class CVPipeline:
    def __init__(self, use_zoom: bool = True, model_id: str = "Qwen/Qwen2-VL-2B-Instruct"):
        """
        Initialize the complete CV pipeline.
        :param use_zoom: Whether to enable the Zoom Tool for anomaly correction.
        """
        print("Initializing CV Pipeline...")
        self.extractor = ChartToTableExtractor(model_id=model_id)
        self.use_zoom = use_zoom
        self.image_cache = {} # Cache to store extracted markdown tables
        
        if self.use_zoom:
            self.verify_agent = VerifyAgent(self.extractor)
        print("CV Pipeline initialized.")

    def process_image(self, image_path: str) -> str:
        """
        Process a single chart image and return a Markdown table.
        Uses caching to avoid reprocessing the same image.
        """
        if image_path in self.image_cache:
            print(f"Loading cached table for {image_path}...")
            return self.image_cache[image_path]
            
        print(f"Extracting table from {image_path}...")
        
        # 1. Initial extraction
        initial_table = self.extractor.extract(image_path)
        
        # 2. Verify and potentially Zoom
        if self.use_zoom:
            final_table = self.verify_agent.process(image_path, initial_table)
        else:
            final_table = initial_table
            
        # 3. Save to cache
        self.image_cache[image_path] = final_table
        return final_table

    def process_batch(self, image_paths: list) -> dict:
        """
        Process a batch of images and return a dictionary mapping paths to tables.
        """
        results = {}
        for path in image_paths:
            results[path] = self.process_image(path)
        return results

if __name__ == "__main__":
    # Test pipeline initialization
    # pipeline = CVPipeline(use_zoom=True)
    # table = pipeline.process_image("test_image.png")
    # print(table)
    print("CVPipeline module is ready.")
