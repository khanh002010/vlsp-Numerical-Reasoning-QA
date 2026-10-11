# Chạy lại private test với checkpoint hiện tại

Không bắt buộc train lại cho bản sửa này. `INSTRUCTION`, FORMAT_VERSION và kiến trúc adapter không đổi; code sửa việc dựng nguồn, kiểm tra và retry khi inference. Dùng lại `final` hoặc một checkpoint tương thích. Sửa dữ liệu OCR không tự cập nhật các file kết quả cũ: phải chạy inference lại. Accuracy chỉ tính được ở public test có đáp án; private test chỉ báo mức hoàn tất và lỗi kiểm tra.

Luồng mới ở `vinumqa.pipeline.repair_inference`, thay cho cell notebook cũ chỉ gọi `generate_with_prompt` một lần rồi bỏ trống câu bị loại.

## Cell 1 — cập nhật code

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
git pull --ff-only origin main
```

Giữ môi trường PyTorch/Transformers/bitsandbytes đang chạy được. Generator tự bật memory SDPA và autocast FP16 khi dùng CUDA; không cần đổi checkpoint hoặc cài lại thư viện chỉ vì bản sửa này.

## Cell 2 — chọn đầu vào và chạy

```python
import sys
import subprocess
from pathlib import Path

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
ADAPTER = Path('/kaggle/input/datasets/khanh002010/vlsp-final/outputs/nlp_module/final')
STORE = Path('/kaggle/working/prepared/private_chart_structures.json')
OUT = Path('/kaggle/working/private_repaired')

# Nếu store đang ở Kaggle Input, sao chép sang STORE một lần để có thể cập nhật.
# Giữ file đang có ở STORE để giữ tiến độ, không ghi đè bằng bản cũ.
assert STORE.is_file(), f'Chép private_chart_structures.json đã OCR vào: {STORE}'
assert (ADAPTER / 'adapter_config.json').is_file(), f'Sai đường dẫn checkpoint: {ADAPTER}'

command = [
    sys.executable, '-u', '-m', 'vinumqa.pipeline.repair_inference',
    '--input', str(REPO / 'data/private_test/private_test_cleaned.json'),
    '--images', str(REPO / 'data/private_test/private_test_images'),
    '--adapter', str(ADAPTER),
    '--structure-store', str(STORE),
    '--reviewed-structures', str(REPO / 'vinumqa/data/reviewed_private_structures.json'),
    '--output-dir', str(OUT),
    '--max-rounds', '3',
    '--max-hours', '10.5',
]

# Không bắt buộc. Đổi đường dẫn nếu diagnostics cũ ở Kaggle Input.
# Có file này giúp gom yêu cầu đọc lại CV ngay trước lượt NLP đầu.
previous = Path('/kaggle/working/submit/diagnostics.json')
if previous.is_file():
    command += ['--previous-diagnostics', str(previous)]

completed = subprocess.run(command, cwd=REPO)
if completed.returncode == 2:
    print('Đã lưu tiến độ; còn câu cần xử lý. Đọc summary/diagnostics, chạy lại cùng cell để tiếp tục.')
elif completed.returncode:
    raise RuntimeError(f'Pipeline lỗi, exit code={completed.returncode}; xem traceback phía trên.')
```

Lưu ý:

- Dùng JSON câu hỏi đã làm sạch, không truyền `private_chart_structures.json` vào `--input`. Store ảnh không có `samples`.
- Không chạy OCR/training khác đồng thời. Các lượt CV và NLP của runner này tách nhau, không giữ hai model cùng lúc.
- Đọc lại ảnh thiếu/lỗi một lượt trước NLP. Nếu ảnh vẫn lỗi, text và bảng còn dùng được; chỉ program cần ảnh đó mới bị chặn/yêu cầu CV.
- Các yêu cầu CV trong validation được thực thi giữa các lượt NLP, gom theo hash ảnh. Đọc xong lưu store ngay. Program vẫn giữ `chart_*`, không thực thi thành đáp án số.
- `reviewed_private_structures.json` chứa hai bản chép nhãn từ ảnh gốc đã kiểm tra trực quan, kèm provenance và SHA256. Không chứa QID, program hay đáp án chuẩn; chỉ áp dụng đúng bytes ảnh. Có thể bỏ đối số này để chỉ dùng CV tự động, nhưng hai lỗi OCR đã xác nhận sẽ chưa được sửa trực tiếp.
- Lượt đầu sinh lại toàn bộ câu bằng checkpoint cũ với hướng dẫn kiểm tra nguồn. Các lượt sau chỉ xử lý câu lỗi hoặc có nguồn đã đổi. Không mặc định tin 723 program được đánh dấu valid bởi notebook cũ.
- Khi chạy lại cùng output-dir, câu đã qua kiểm tra và nguồn chưa thay đổi được giữ lại. Adapter, dữ liệu hoặc policy thay đổi thì dùng output-dir mới. `--max-rounds` là số vòng tối đa cho mỗi lần chạy; giới hạn thời gian áp dụng cho mỗi lần chạy, không bao gồm thời gian trước đó.
- Giới hạn giờ là mềm: một lời gọi model/CV đang chạy được kết thúc theo giới hạn riêng của nó rồi mới dừng; runner dành một phần thời gian để lưu. Không bảo đảm toàn bộ private test xong trong một phiên T4; giữ cả STORE và OUT nếu chuyển phiên.

## Cell 3 — kiểm tra file kết quả

```python
import json

summary = json.loads((OUT / 'summary.json').read_text(encoding='utf-8'))
print(json.dumps(summary, ensure_ascii=False, indent=2))
results = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
assert len(results) == 980 and len({r['qid'] for r in results}) == 980
print('Program rỗng:', sum(not r['predicted'] for r in results))
print('Kết quả:', OUT / 'results.json')
```

Các file được cập nhật sau mỗi câu:

- `results.json`: `[{"qid": "...", "predicted": "..."}]` theo schema submission đang dùng trong repo; câu chưa qua kiểm tra có chuỗi rỗng.
- `results_program.json`: bản tương đương dùng `program` để thuận tiện đối chiếu.
- `diagnostics.json`: candidate, lỗi, cảnh báo, yêu cầu CV, lịch sử sửa; giữ candidate sai để xem xét.
- `state.json`: thông tin tiếp tục, fingerprint dữ liệu/adapter, trạng thái từng câu và các lượt inspect đã thực hiện.
- `summary.json`: `accepted_by_checks`, `unresolved`, `complete`; **không phải accuracy**.

Không coi `complete=true` là bằng chứng 100% program đúng. Bộ kiểm tra mới bắt nhãn bảng, phạm vi, bước tính không dùng, số không có nguồn và một số lỗi đơn vị; lỗi hiểu câu hỏi vẫn có thể lọt. Nếu muốn đo cải thiện, chạy cùng runner trên public test với store public, sau đó chấm với public ground truth. Không sửa ground truth và không cần train lại trước lần đo này.

## Kiểm thử local

```bash
python -m unittest tests.test_repair_inference tests.test_structure_pipeline tests.test_pipeline_v4
```

Các kiểm thử dùng reader/generator giả để kiểm tra điều phối, độc quyền GPU, retry, EOS, xuất kết quả và resume. Chúng không thay cho việc chạy checkpoint thật trên Kaggle hoặc đo accuracy.
