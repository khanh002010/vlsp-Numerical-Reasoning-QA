"""
Zoom Tool for Chart Image processing.
Inspired by ChartAgent (ACL), this tool crops dense chart images into quadrants
to allow the VLM to read sparse values more accurately without OOM.
"""

from PIL import Image
from typing import List, Tuple
import os

class ZoomTool:
    def __init__(self, target_size: Tuple[int, int] = (1024, 1024)):
        """
        Initialize ZoomTool.
        :param target_size: The size to which each quadrant is resized.
        """
        self.target_size = target_size

    def get_quadrants(self, image: Image.Image) -> List[Image.Image]:
        """
        Splits an image into 4 quadrants (top-left, top-right, bottom-left, bottom-right).
        Returns a list of 4 cropped images.
        """
        width, height = image.size
        
        # Calculate midpoints
        mid_w = width // 2
        mid_h = height // 2
        
        # Define 4 quadrants (left, upper, right, lower)
        boxes = [
            (0, 0, mid_w, mid_h),           # Top-Left
            (mid_w, 0, width, mid_h),       # Top-Right
            (0, mid_h, mid_w, height),      # Bottom-Left
            (mid_w, mid_h, width, height)   # Bottom-Right
        ]
        
        quadrants = []
        for box in boxes:
            quadrant = image.crop(box)
            # Optional: resize to target_size to give the VLM more resolution to work with
            if self.target_size:
                quadrant = quadrant.resize(self.target_size, Image.Resampling.LANCZOS)
            quadrants.append(quadrant)
            
        return quadrants

    def process_and_save(self, image_path: str, output_dir: str) -> List[str]:
        """
        Loads an image, splits into quadrants, and saves them to output_dir.
        Returns the paths to the saved quadrants.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        try:
            image = Image.open(image_path)
            quadrants = self.get_quadrants(image)
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            saved_paths = []
            
            for i, quad in enumerate(quadrants):
                quad_name = f"{base_name}_quadrant_{i}.png"
                quad_path = os.path.join(output_dir, quad_name)
                quad.save(quad_path)
                saved_paths.append(quad_path)
                
            return saved_paths
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    zoom_tool = ZoomTool()
    print("ZoomTool module is ready.")
