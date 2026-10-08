# Chỉ đọc lại ảnh lỗi

Dùng code mới và các file kết quả hiện tại trong cùng một thư mục. Không xóa store.
Dừng lượt OCR cũ trước khi chạy. Nếu đã import module trong notebook, restart kernel
để dùng code mới; restart kernel không yêu cầu xóa file kết quả.

```python
import subprocess
import sys

subprocess.run([
    sys.executable, "-u", "-m", "vinumqa.nlp_module.data_prep.retry_failed_structures",
    "--prepared-dir", "/kaggle/working/prepared",
    "--data-root", "/kaggle/working/vlsp-Numerical-Reasoning-QA/data",
    "--max-minutes", "90",
], cwd="/kaggle/working/vlsp-Numerical-Reasoning-QA", check=True)
```

Script chọn ảnh `error` trong từng file structured, không chọn `ok` hoặc `pending`.
Nếu store đã có kết quả thành công cho ảnh đó, dùng lại thay vì gọi CV. Trước khi sửa,
sao lưu store, structured và các sidecar hiện có vào `prepared/backups/retry_<timestamp>/`.
Sau từng ảnh, cập nhật store, file structured gốc và các file `.ocr_errors.json`,
`.rejected.json`. Tất cả câu hỏi tham chiếu ảnh được cập nhật cùng nhau. Kết quả thành
công của ảnh khác giữ nguyên. Chạy lại cùng lệnh để tiếp tục ảnh còn lỗi.

Giới hạn 90 phút áp dụng riêng từng split, kiểm tra giữa các ảnh; một ảnh đang chạy
có thể vượt thời điểm này. Mỗi lượt generation giữ giới hạn mềm 120 giây, 1024/2048 token.
Sau lượt đọc chính và retry, nếu vẫn lỗi thì đọc riêng legend, X, Y từ ảnh đầy đủ
(1024 token/phần). Mỗi phần được kiểm tra ngay. Nếu sai/lặp/hết token, CV xác định
bounding box (256 token) rồi đọc lại crop một lần (2048 token). Không có vòng lặp vô hạn.
Locator chấp nhận cả mảng bốn số và object left/top/right/bottom trong 0..1.
Nếu locator bị cắt hoặc sai cấu trúc, thử đúng một lượt chọn vùng top/middle/bottom/full
(128 token) rồi đọc crop đó; không nhận JSON chưa hoàn tất hay tự đoán tọa độ từ text.
Nếu Y bị nhầm chú giải/đơn vị, thêm một lượt phân loại trục độc lập (128 token).
Chỉ khi lượt này xác nhận numerical hoặc none mới xuất y_labels=[]; categorical/unknown
vẫn phải đọc nhãn từ ảnh, không xóa danh mục để vượt kiểm tra.
Crop không chứng minh đủ toàn ảnh: completeness=false; crop X còn có x_order_known=false.
Guard chặn chu kỳ nhãn lặp kéo dài, kể cả Q1–Q4 hoặc chuỗi số 0 trong danh sách nhãn.
Kết quả Y phải phân biệt numerical/categorical/none/unknown; không tự xóa nhãn chưa rõ.
Biểu đồ pie được chuẩn hóa series.axis=none vì không có trục Cartesian.
Không nhận
JSON bị cắt, không đoán tên series, không tự xóa nhãn X trùng để vượt validation.
Thiếu cờ completeness được coi là false, không phải true. Trần pixel vẫn 1.400.000.

Chưa đảm bảo mọi ảnh sẽ đọc đúng: ảnh tiếp tục lỗi vẫn được ghi lỗi với lý do và raw
generation trong store để kiểm tra. Dữ liệu có uncertainty/complete=false cần đối chiếu
ảnh khi đánh giá chất lượng, kể cả khi schema hợp lệ.

Kiểm tra trước khi training (không bỏ qua mẫu lỗi):

```python
from vinumqa.nlp_module.training.supervision import load_prepared_pair
train, valid = load_prepared_pair(
    "/kaggle/working/prepared/train_structured.json",
    "/kaggle/working/prepared/public_test_structured.json",
)
print(len(train), len(valid))
```
