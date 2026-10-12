# Đọc lại ảnh bị đánh dấu trong audit

Reader `reviewed` hiện dùng recipe `region-evidence-v4`. Đây là thay đổi thuật toán;
chưa có số đo accuracy GPU mới cho 133 ảnh. Kiểm thử bằng mock chỉ xác nhận luồng
và các điều kiện từ chối, không thay thế việc xem kết quả OCR.

## Các nhóm lỗi được xử lý

| Nhóm lỗi audit | Thay đổi |
|---|---|
| Title tự sinh, lấy unit/legend/date/event làm title | Xác nhận có heading riêng, đối chiếu full-image và crop; từ chối unit đứng riêng |
| Mất series chính, hatch, đường ngưỡng | Inventory yêu cầu cả main quantity, legend và named reference lines; kiểm coverage lần riêng |
| Ghép giá trị điểm cuối vào series | Giữ raw text, tên phải là đoạn nguyên văn; direct label tách endpoint value |
| Tự dịch/viết lại China, US, tên viết tắt | Tên phải nằm trong raw text, raw text phải khớp crop; không dùng answer/program |
| Gán sai trái/phải, 100%/150% thành unit | Kiểm tồn tại thang số, crop thang số và unit; kiểm liên kết series–scale riêng |
| Bỏ năm 23/24/25/26 vì numerical | Xác nhận role lần riêng, prompt phân biệt năm viết tắt và numerical measurements |
| Ghép thừa quý không năm, mất hàng năm | Nhóm theo parent box và child boxes, không chấp nhận parented/unparented lẫn nhau; crop từng tầng |
| Gộp hai vùng, thứ tự callout sai | Một box mỗi nhãn, thứ tự theo vị trí X/Y; coverage toàn trục phải khớp |
| Đọc sai 22/2 thành 22/12; Mar-01 thành Mar-07 | Đọc crop nhãn rồi so chuỗi/đếm với toàn trục; bất đồng phải đọc lại vùng |
| Nguồn thực sự lặp ngày | Giữ x_tick_labels, không tự tăng năm, không đánh dấu dùng được bằng nhãn duy nhất |
| Bar âm/dương, bar ngang, chart có nhiều series | Không phụ thuộc detector chỉ hỗ trợ cột dương một màu; đọc vùng nhãn bất kể baseline |
| JSON dài/chạm giới hạn, sai enum | Tách nhiều nhiệm vụ nhỏ có schema, retry giới hạn; series_source được dựng từ nguồn chữ quan sát |
| Record ok nhưng sai bị cache bỏ qua | Store retry riêng chỉ gồm danh sách audit; giữ nguồn và provenance, lưu từng ảnh |

Các bbox do model đề xuất chỉ là vị trí ứng viên: text trong crop phải được đọc và
đối chiếu. Các quan sát model đồng ý nhau vẫn có thể cùng sai; `ok` không phải
chứng nhận human-verified. Các ảnh không trong queue được giữ lại theo yêu cầu,
với `reader_identity` cũ, không được gắn nhãn đã chạy recipe mới.

## Kaggle

Đồng bộ code mới vào repo. Đưa `tests/chart_structures.json` và
`reports/full_ocr_review/repair_queue.json` lên Kaggle, sửa đường dẫn nếu dùng Dataset.
Không dùng cell cũ `from_saved` trên store v3 để chạy reader v4: identity đã đổi.

```python
import subprocess, sys
subprocess.run([
    sys.executable, '-u', '-m', 'vinumqa.cv_module.repair_audited',
    '--source', '/kaggle/working/vlsp-Numerical-Reasoning-QA/tests/chart_structures.json',
    '--queue', '/kaggle/working/vlsp-Numerical-Reasoning-QA/reports/full_ocr_review/repair_queue.json',
    '--data-root', '/kaggle/working/vlsp-Numerical-Reasoning-QA/data',
    '--output-dir', '/kaggle/working/ocr_repair_v4',
    '--max-minutes', '90',
], cwd='/kaggle/working/vlsp-Numerical-Reasoning-QA', check=True)
```

Chỉ ảnh trong queue được đọc lại, bao gồm record cũ `ok`. Tiếp tục cùng cell/cùng
output sẽ bỏ qua ảnh đã đọc lại thành công; ảnh retry còn lỗi được thử lại một lượt.
90 phút được kiểm tra giữa các ảnh, không cắt ngang inference đang chạy. Các crop
và kiểm tra bổ sung làm lượt OCR tốn thời gian hơn reader cũ; chưa có benchmark GPU.

Output:

- `source_snapshot.json`: bản gốc giữ nguyên.
- `retried_chart_structures.json`: chỉ ảnh được đọc lại, có log generation/crop.
- `chart_structures.json`: toàn bộ ảnh, cập nhật các ảnh được chọn; có provenance.
- `repair_manifest.json`: fingerprint nguồn/queue; ngăn resume nhầm dữ liệu.

Sau OCR cần đánh giá lại bằng pixel, đặc biệt nhóm quý–năm, nhiều trục và ảnh có
nguồn lặp tick. Store mới không tự viết lại `train_structured.json` hay checkpoint.
Chuẩn bị lại dữ liệu NLP từ store sau khi kiểm tra, rồi mới train/evaluate.
