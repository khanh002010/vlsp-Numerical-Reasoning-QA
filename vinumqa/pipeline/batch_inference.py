"""
Batch Inference Script for ViNumQA.
Runs the Full Pipeline over a test dataset and outputs a submission file.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from vinumqa.pipeline.full_pipeline import ViNumQAPipeline

def run_batch_inference(test_json_path: str, output_path: str, img_dir: str, lora_path: str = None):
    """
    Run the end-to-end pipeline on the test set.
    """
    if not os.path.exists(test_json_path):
        print(f"Test file not found: {test_json_path}")
        return
        
    with open(test_json_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
        
    print(f"Loaded {len(test_data)} test samples.")
    
    # Initialize Pipeline
    if lora_path is None:
        lora_path = str(PROJECT_ROOT / "outputs" / "nlp_module" / "final")
        
    pipeline = ViNumQAPipeline(
        cv_model_id="Qwen/Qwen2-VL-2B-Instruct",
        nlp_model_id="Qwen/Qwen2.5-7B-Instruct",
        nlp_lora_weights=lora_path,
        use_zoom=True,
        use_reflection=True
    )
    
    results = []
    
    for i, sample in enumerate(test_data):
        print(f"Processing sample {i+1}/{len(test_data)} (QID: {sample['qid']})")
        
        question = sample['qa']['question']
        texts = "\n".join(sample.get('text', []))
        tables_dict = sample.get('tables', {})
        
        # Resolve image paths keeping the image key
        image_dict = {}
        if 'images' in sample:
            for img_key, img_filename in sample['images'].items():
                img_path = os.path.join(img_dir, img_filename)
                image_dict[img_key] = img_path
                
        # Run Pipeline
        output = pipeline.run(texts, tables_dict, image_dict, question)
        
        answer = output['reasoning_result'].get('answer', None)
        program = output['reasoning_result'].get('program', "")
        
        results.append({
            "qid": sample['qid'],
            "answer": answer,
            "program": program
        })
        
        # Save intermediate occasionally
        if (i + 1) % 10 == 0:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
    # Final save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Batch inference completed. Results saved to {output_path}")

if __name__ == "__main__":
    import sys
    
    test_file = sys.argv[1] if len(sys.argv) > 1 else str(PROJECT_ROOT / "test.json")
    img_dir = sys.argv[2] if len(sys.argv) > 2 else str(PROJECT_ROOT / "test_images")
    lora_path = sys.argv[3] if len(sys.argv) > 3 else None
    output_file = str(PROJECT_ROOT / "submission.json")
    
    print(f"Starting batch inference on {test_file}...")
    run_batch_inference(test_file, output_file, img_dir, lora_path)
