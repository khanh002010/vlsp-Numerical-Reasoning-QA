# Pilot 10 ảnh trên Kaggle

So sánh Qwen2.5-VL-7B NF4 với Qwen3-VL-4B FP16 bằng cùng reader `reviewed`, cùng 10 ảnh, trần 1.400.000 pixel. Đây là so sánh hai cấu hình triển khai, không phải phép đo riêng tác động của lượng tử hóa.

4 ảnh khó đã được dùng để chỉnh pipeline; 6 ảnh bổ sung được chọn ngẫu nhiên với seed 20261014. Chấm riêng hai nhóm. Nhãn tham chiếu của 6 ảnh được chép từ ảnh gốc; không lấy từ program hay output OCR. Không suy rộng kết quả 10 ảnh ra toàn bộ dữ liệu.

`y_labels` trong hợp đồng hiện tại là nhãn phân loại trên Y, không phải các vạch số của trục Y. Pilot chấm series, thứ tự nhãn X/Y, tiêu đề và đơn vị theo series. Chưa chấm giá trị số, vạch số trên trục hoặc accuracy program NLP. `status=ok` chỉ có nghĩa vượt kiểm tra cấu trúc, không bảo đảm đọc đúng.

## Chuẩn bị

Đồng bộ code mới và `reports/ocr_pilot10/pixel_references.json` vào repo trên Kaggle trước khi chạy. Không cần train/OCR lại toàn bộ dữ liệu. Dùng môi trường GPU đã chạy pilot Qwen2.5; Transformers cần có `Qwen3VLForConditionalGeneration`, bitsandbytes cần hoạt động cho baseline. Không nâng đồng loạt thư viện trong phiên đang chạy.

## Cell chạy hai model tuần tự

```python
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
REFERENCE = REPO / 'reports/ocr_pilot10/pixel_references.json'
assert REFERENCE.is_file(), 'Cần đồng bộ code và reference pilot10 mới lên Kaggle.'

# Thư mục mới cho reader v6; không dùng store pilot v4/v5.
PILOT10 = Path('/kaggle/working/ocr_pilot10_text_location_v6')
print('Output:', PILOT10, flush=True)

env = dict(os.environ, CUDA_VISIBLE_DEVICES='0', PYTHONUNBUFFERED='1')
subprocess.run([sys.executable, '-c',
    'import torch; from transformers import Qwen3VLForConditionalGeneration; '
    'from transformers.utils import is_bitsandbytes_available; '
    'assert torch.cuda.is_available(), "GPU required"; '
    'assert is_bitsandbytes_available(), "bitsandbytes unavailable"'],
    cwd=REPO, env=env, check=True)

for name, model, quant in [
    ('qwen25_7b_nf4', 'Qwen/Qwen2.5-VL-7B-Instruct', ['--four-bit']),
    ('qwen3_4b_fp16', 'Qwen/Qwen3-VL-4B-Instruct', []),
]:
    print('\nRUN:', name, flush=True)
    subprocess.run([
        sys.executable, '-u', '-m', 'vinumqa.cv_module.structure_pilot',
        '--model', model, *quant,
        '--images', str(REPO / 'data/public_test/public_test_images'),
        '--reference', str(REFERENCE),
        '--output-dir', str(PILOT10 / name),
    ], cwd=REPO, env=env, check=True)

print('Hoàn tất. Tải toàn bộ folder:', PILOT10, flush=True)
```

Mỗi subprocess kết thúc sẽ giải phóng model trước khi model tiếp theo được nạp. Chỉ dùng GPU 0 để đo trên một T4 16 GB. Không chạy NLP hoặc OCR khác cùng lúc. 10 ảnh × 2 model = 20 lượt đọc cấu trúc; mỗi lượt có thể gồm nhiều lần sinh/crop/retry, không phải 20 lần `generate`.

Mỗi model ghi `chart_structures.json`, `ocr_accuracy_pilot.json`, `timings.json`. Thành công được tái sử dụng khi chạy lại cùng thư mục; ảnh lỗi được thử lại. Thời gian cache hit không tính vào tốc độ OCR. Thời gian nạp/download model không tính vào thời gian từng ảnh. VRAM đo là bộ nhớ tensor allocated từng GPU, không phải tổng VRAM tiến trình.

Muốn benchmark lại từ đầu, đặt `PILOT10` sang thư mục mới; không xóa kết quả cũ. Nếu phiên Kaggle mới, gán lại đường dẫn output đã khôi phục để resume. Gửi cả hai thư mục kết quả để đối chiếu từng nhãn và ảnh; chưa train lại hoặc thay reader production chỉ dựa trên tỷ lệ `ok`.
