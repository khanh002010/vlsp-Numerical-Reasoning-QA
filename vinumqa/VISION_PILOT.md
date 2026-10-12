# Pilot PaddleOCR-VL-1.6 và Qwen với kiểm tra cấu trúc mới

PaddleOCR-VL-1.6 là model chuyên OCR/document parsing 0,9B, có các tác vụ OCR,
chart recognition và text spotting. Kết quả document parsing trong
[model card](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6) là cơ sở để thử,
không chứng minh nó hơn Qwen trên biểu đồ tiếng Việt này. Baseline mới nhất của bạn
là **Qwen2.5-VL-7B 4-bit**, không còn là Qwen2-VL-2B.

Chế độ Paddle dùng Transformers theo ví dụ chính thức, chạy FP16 trên T4 (không BF16),
không cần cài PaddlePaddle hoặc bitsandbytes cho riêng Paddle. Chưa chạy trọng số GPU
trong môi trường local: cần kết quả Kaggle để xác nhận tương thích và chất lượng thực tế.

## 1. Cập nhật code và phụ thuộc

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
git pull --ff-only origin main
python -m pip install --upgrade 'transformers>=5.0.0' accelerate Pillow
python -c "import torch; assert torch.cuda.is_available(); print(torch.__version__, torch.cuda.get_device_name(0))"
```

Mỗi cell sau tạo process riêng để dùng phiên bản thư viện vừa cài. Không chạy hai
cell model đồng thời. Paddle giữ trần 1.400.000 pixel, không bật upscale gấp đôi
trong ví dụ spotting của model card; processor có thể làm tròn theo patch grid.

## 2. Thử Paddle trên đúng bốn ảnh

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
python -u -m vinumqa.cv_module.paddle_pilot \
  --images data/public_test/public_test_images \
  --reference reports/public_accuracy_v2/pixel_references.json \
  --output-dir /kaggle/working/paddle_pilot_v1 \
  --device cuda:0 --tasks ocr chart spotting \
  --max-new-tokens 4096 --max-seconds 240
```

Kết quả: `/kaggle/working/paddle_pilot_v1/paddle_pilot.json`. Mỗi ảnh có text thô,
số token, thời gian, EOS, kích thước ảnh và SHA256 theo từng tác vụ. Lưu sau mỗi tác vụ;
chạy lại cùng cell bỏ qua tác vụ đã kết thúc EOS. EOS không bảo đảm chữ đọc đúng.

File reference chỉ chọn tên ảnh, không đưa đáp án/nhãn chuẩn vào model. Paddle nhận
đúng prompt gốc `OCR:`, `Chart Recognition:`, `Spotting:`. Nó không phải model Qwen
tuân theo schema JSON tùy ý. Vì thế đây là **bài thử Paddle độc lập**, chưa thay reader
production bằng Paddle: kết quả thô không được giả gắn `ready` thành chart structure.
Chart table do Paddle sinh cũng không được đưa vào NLP để làm mất `chart_*`.

Sau khi xem text spotting/chart thực tế, mới có căn cứ chọn Paddle làm OCR đầu vào
và xây ánh xạ tọa độ/nhãn cho format thực tế của nó. Không tự đoán format, đơn vị tọa độ
hay lấy số trong bảng Paddle làm đáp án.

## 3. Thử bốn bản sửa cấu trúc trên Qwen

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
python -m pip install --upgrade 'bitsandbytes>=0.46.1'
python -u -m vinumqa.cv_module.structure_pilot \
  --model Qwen/Qwen2.5-VL-7B-Instruct --four-bit \
  --images data/public_test/public_test_images \
  --reference reports/public_accuracy_v2/pixel_references.json \
  --output-dir /kaggle/working/prepared_accuracy_v2
```

Folder mới quan trọng: store cũ `parts` chứa lỗi nhưng status=ok, nên không được tái
sử dụng khi đo recipe `reviewed`. Script từ chối trộn hai recipe.

Các thay đổi:

1. Đọc layout độc lập trước: hướng plot, trục số/category/time và tiêu đề. Trục Y số
   không chạy bước chép category Y. Trục ngang vẫn được đọc row names, không xóa Y
   trên mọi biểu đồ. Kết quả mâu thuẫn vai trò bị từ chối, không ép qua bằng cách bỏ nhãn.
2. Đọc nhãn X/Y có box theo từng vị trí; mỗi item chứa các dòng thuộc cùng một nhãn.
   Nhãn nhiều dòng được đọc lại bằng crop chính vị trí đó. Không deduplicate năm và
   không nối “Lần 1/Lần 2” theo thứ tự text toàn ảnh. Tọa độ phải normalized 0..1;
   không tự coi `bbox_2d` không rõ hệ tọa độ là normalized.
3. Với một series không có legend, khi CV xác nhận title là tên series, có thể tạo alias
   bằng cách bỏ hậu tố kỳ/đơn vị có quy tắc. Ví dụ `Giá điện từ 2009 - 2023 (VND/kWh)`
   có alias `Giá điện`. Lưu cả tên gốc, alias và căn cứ. Không fuzzy-match P/E, TB năm,
   hoặc các series gần tên. Validator và executor hiểu alias nhưng program giữ `chart_*`.
4. Pilot chấm thêm Y, tiêu đề và đơn vị theo từng series. Y chuẩn rỗng dùng exact-image
   rate và số nhãn thừa; recall 0/0 được ghi null, không ngụy tạo điểm 100%.

Kết quả cần xem:

- `/kaggle/working/prepared_accuracy_v2/chart_structures.json`
- `/kaggle/working/prepared_accuracy_v2/ocr_accuracy_pilot.json`
- `/kaggle/working/paddle_pilot_v1/paddle_pilot.json`

Chấm lại file Qwen pilot cũ bằng scorer mới cho thấy series recall 100%, X recall 95,24%,
nhưng Y đúng chỉ **1/4 ảnh**, title **3/4**, unit **6/12 series**. Baseline mở rộng được
lưu ở `reports/public_accuracy_v2/pilot_7b_expanded_score.json`.

Chưa train ngay: so nhãn gốc và mới theo tất cả các trường. Chưa có số đo chứng minh
bản đọc mới hoặc Paddle tốt hơn sau thay đổi. Nếu đạt yêu cầu, tiếp tục OCR full train/public
theo [ACCURACY_RETRAIN.md](ACCURACY_RETRAIN.md) với `--cv-read-mode reviewed` và folder mới.
