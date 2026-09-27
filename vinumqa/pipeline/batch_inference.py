"""
Batch Inference Script for ViNumQA.
Runs the Full Pipeline over a test dataset and outputs a submission file.
"""

import json
import os
from vinumqa.pipeline.full_pipeline import ViNumQAPipeline

def run_batch_inference(test_json_path: str, output_path: str, img_dir: str):
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
    # For actual execution on Kaggle T4, configure models appropriately.
    pipeline = ViNumQAPipeline(
        cv_model_id="Qwen/Qwen2-VL-2B-Instruct",
        nlp_model_id="Qwen/Qwen2.5-7B-Instruct",
        use_zoom=True,
        use_reflection=True
    )
    
    results = []
    
    for i, sample in enumerate(test_data):
        print(f"Processing sample {i+1}/{len(test_data)} (QID: {sample['qid']})")
        
        question = sample['qa']['question']
        texts = "\n".join(sample.get('text', []))
        
        # Resolve image paths
        image_paths = []
        if 'images' in sample:
            for img_key, img_filename in sample['images'].items():
                img_path = os.path.join(img_dir, img_filename)
                image_paths.append(img_path)
                
        # Run Pipeline
        output = pipeline.run(texts, image_paths, question)
        
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
    # run_batch_inference("test.json", "submission.json", "test_images/")
    print("Batch inference script ready.")
