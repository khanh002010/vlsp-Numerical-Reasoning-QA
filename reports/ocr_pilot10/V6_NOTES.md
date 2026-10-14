# Kiểm thử reader v6

Sửa các điểm chặn quan sát được trong pilot v5: đọc tiêu đề/tên series không yêu cầu box; định vị bằng lượt riêng chỉ có một hệ tọa độ 0..1. Kiểm tra tiêu đề bằng chữ đọc từ crop, thay cho hai lượt toàn ảnh vừa chép chữ vừa định vị. Với trường hợp không thấy tiêu đề, có một lượt kiểm tra lại sự vắng mặt.

Lỗi crop series chỉ thử lại vị trí đó, không đọc lại toàn bộ danh sách. Các stage tiêu đề, series, trục X và Y chạy độc lập. Stage đã hoàn tất được lưu trong `generation.completed_stages`; lỗi lưu trong `generation.failed_stages`. Quan sát trung gian lưu trong `generation.observations`. Báo cáo pilot có thêm `stage_progress`.

Ảnh còn lỗi vẫn ở trạng thái error; thông tin trung gian chưa được tự động đưa vào NLP hoặc tính thành đáp án tham chiếu. Không đoán hệ tọa độ khi model trả sai, không tự sửa chữ theo tên ticker. Nếu model vẫn không tuân thủ, cần xem log mới; kiểm tra đơn vị không chứng minh độ chính xác OCR GPU.

Chạy lại đúng 10 ảnh, chỉ Qwen2.5:

```bash
%%bash
set -euo pipefail
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
git pull --ff-only origin main
export CUDA_VISIBLE_DEVICES=0
export PYTHONUNBUFFERED=1
python -u -m vinumqa.cv_module.structure_pilot \
  --model Qwen/Qwen2.5-VL-7B-Instruct --four-bit \
  --images data/public_test/public_test_images \
  --reference reports/ocr_pilot10/pixel_references.json \
  --output-dir /kaggle/working/ocr_pilot10_qwen25_text_location_v6
```

Không dùng output v5 vì contract đã đổi. Rerun cùng output v6 giữ ảnh thành công, thử lại ảnh lỗi. Tải cả chart_structures.json, ocr_accuracy_pilot.json, timings.json. Đọc đầy đủ hơn có thể tốn thời gian hơn lần v5 vốn dừng sớm.
