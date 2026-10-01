"""
CV Pipeline Orchestrator.
Uses ChartToTableExtractor (Qwen2-VL) to extract tables from chart images.
Zoom/sliding-window is removed: EDA shows avg image resolution is ~622k pixels,
well within MAX_PIXELS=750k, so all images are kept at native resolution.
"""

from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor

class CVPipeline:
    def __init__(self, model_id: str = "Qwen/Qwen2-VL-2B-Instruct"):
        """
        Initialize the CV pipeline.
        Zoom Tool removed: image resolution in dataset is well within MAX_PIXELS=750k,
        so direct single-pass extraction is sufficient and ~2-3x faster.
        """
        print("Initializing CV Pipeline...")
        self.extractor = ChartToTableExtractor(model_id=model_id)
        self.image_cache = {}  # Cache: key=image_path, value=markdown table
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
        
        # Direct extraction (single pass, no zoom)
        final_table = self.extractor.extract(image_path)
        
        # Save to cache
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
