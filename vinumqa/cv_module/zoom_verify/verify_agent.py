"""
Verify Agent for Chart-to-Table.
Checks initial extracted tables for anomalies and invokes ZoomTool to re-extract if necessary.
"""

import re
import pandas as pd
import io
from typing import Optional, List
from vinumqa.cv_module.zoom_verify.zoom_tool import ZoomTool

class VerifyAgent:
    def __init__(self, extractor):
        """
        Initialize VerifyAgent with a ChartToTableExtractor instance.
        """
        self.extractor = extractor
        self.zoom_tool = ZoomTool()

    def has_anomalies(self, markdown_table: str) -> bool:
        """
        Heuristics to detect anomalies in the markdown table.
        Returns True if the table likely needs re-extraction via Zoom.
        """
        # If extraction failed
        if "Lỗi" in markdown_table or "Error" in markdown_table:
            return True
            
        # Parse markdown to simple rows
        lines = markdown_table.strip().split('\n')
        if len(lines) < 3: # Header, separator, at least 1 data row
            return True
            
        try:
            # Count columns in header
            header_cols = len([c for c in lines[0].split('|') if c.strip()])
            
            # Check for inconsistent column counts, missing values, or placeholder tokens
            missing_count = 0
            total_cells = 0
            
            for line in lines[2:]: # Skip header and separator
                cells = [c.strip() for c in line.split('|') if c.strip() or '|' in line]
                # Discount empty cells from the split logic
                cells = [c for c in line.split('|')[1:-1]] if line.startswith('|') else line.split('|')
                cells = [c.strip() for c in cells]
                
                if len(cells) != header_cols and len(cells) > 0:
                    return True # Inconsistent column count
                    
                for cell in cells:
                    total_cells += 1
                    if cell.lower() in ['', 'nan', 'null', 'n/a', 'none', '-']:
                        missing_count += 1
                        
            # If more than 30% of cells are missing/empty, it's anomalous
            if total_cells > 0 and (missing_count / total_cells) > 0.3:
                return True
                
            return False
            
        except Exception as e:
            return True # Any parsing error is considered anomalous

    def merge_quadrant_tables(self, tables: List[str]) -> str:
        """
        Merge 4 markdown tables extracted from quadrants into a single table.
        (This is a simplified heuristic merge. In reality, it requires careful alignment
        of rows and columns across quadrants or an LLM to merge them intelligently).
        """
        # For a robust merge, one would prompt an LLM to merge the 4 partial tables 
        # or use pandas to align on index/columns if they share headers.
        # Since this is a template, we return a concatenated version with a note.
        
        merged_table = "### Merged from Zoom\n"
        for i, table in enumerate(tables):
            merged_table += f"\n**Quadrant {i+1}**\n{table}\n"
            
        # In a full implementation, you would use an LLM call here:
        # prompt = f"Merge the following 4 partial tables into one cohesive Markdown table:\n{merged_table}"
        # final_table = self.llm.generate(prompt)
        # return final_table
        
        return merged_table

    def process(self, image_path: str, initial_table: str, temp_dir: str = "./temp_zoom") -> str:
        """
        Verify the initial table and re-extract using zoom if anomalies are found.
        """
        if not self.has_anomalies(initial_table):
            return initial_table
            
        print(f"Anomalies detected in {image_path}. Applying ZoomTool...")
        
        # 1. Get quadrants
        quad_paths = self.zoom_tool.process_and_save(image_path, temp_dir)
        if not quad_paths:
            return initial_table # Fallback
            
        # 2. Extract from each quadrant
        quad_tables = []
        for q_path in quad_paths:
            q_table = self.extractor.extract(q_path)
            quad_tables.append(q_table)
            
        # 3. Merge results
        merged_table = self.merge_quadrant_tables(quad_tables)
        return merged_table

if __name__ == "__main__":
    print("VerifyAgent module is ready.")
