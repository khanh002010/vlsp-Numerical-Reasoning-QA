import json
import os
from vinumqa.utils.dsl_parser import parse_program, execute_program, MATH_OPS

def evaluate_submission(submission_path, test_path, output_csv):
    with open(submission_path, 'r', encoding='utf-8') as f:
        preds = json.load(f)
        
    with open(test_path, 'r', encoding='utf-8') as f:
        tests = json.load(f)
        
    test_dict = {item['qid']: item['qa']['program'] for item in tests}
    
    results = []
    shortcut_count = 0
    em_count = 0
    
    for pred in preds:
        qid = pred['qid']
        pred_prog = pred['program']
        gt_prog = test_dict.get(qid, "")
        
        # 1. Exact Match (So khớp chuỗi)
        is_em = (pred_prog.strip() == gt_prog.strip())
        if is_em:
            em_count += 1
            
        # 2. Kiểm tra xem có phải "Shortcut" (chỉ toàn phép toán Math) không
        is_shortcut = False
        final_answer = None
        
        if pred_prog:
            steps = parse_program(pred_prog)
            # Nếu tất cả các bước đều là Math Ops (không dùng Table/Chart)
            if all(step.operator in MATH_OPS for step in steps):
                is_shortcut = True
                shortcut_count += 1
                try:
                    # Chạy thử công thức để ra kết quả số
                    exec_res = execute_program(steps)
                    if exec_res:
                        final_answer = exec_res[max(exec_res.keys())]
                except Exception as e:
                    final_answer = f"LỖI: {e}"
                    
        results.append({
            "QID": qid,
            "Ground_Truth": gt_prog,
            "Model_Predict": pred_prog,
            "Is_Shortcut": is_shortcut,
            "Calculated_Answer": final_answer
        })
        
    print(f"Tổng số câu: {len(preds)}")
    print(f"Số câu giống hệt đáp án gốc (Exact Match): {em_count}")
    print(f"Số câu Model 'đi tắt' (Chỉ dùng toán học): {shortcut_count}")
    
    # Save to CSV for easy inspection
    import csv
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["QID", "Ground_Truth", "Model_Predict", "Is_Shortcut", "Calculated_Answer"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nĐã xuất kết quả so sánh ra file: {output_csv}")
    print("Bạn có thể mở file CSV này bằng Excel để kiểm tra xem con số cuối cùng Model tính ra có hợp lý với đề bài không.")

if __name__ == "__main__":
    # Thay đổi đường dẫn cho phù hợp với Kaggle
    sub_path = "content.json" if os.path.exists("content.json") else r"d:\VS CODE\vlsp Numerical Reasoning QA\submission.json"
    test_path = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\public_test\public_test.json"
    out_csv = "evaluation_report.csv"
    
    if os.path.exists(sub_path):
        evaluate_submission(sub_path, test_path, out_csv)
    else:
        print(f"Không tìm thấy file {sub_path}")
