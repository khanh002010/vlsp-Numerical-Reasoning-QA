# Chạy lại OCR và training để cải thiện Program Accuracy

Baseline public: 240/459 (52,29%) theo `programs_equivalent` hiện tại. Xem
[phân tích lỗi](../reports/public_accuracy_v2/analysis_vi.md) trước khi so kết quả mới.
Các cell dưới đây giả định repo đã được cập nhật ở
`/kaggle/working/vlsp-Numerical-Reasoning-QA`, môi trường training cũ đang hoạt động
và GPU đã bật. File `reports/public_accuracy_v2/pixel_references.json` là dữ liệu
reference cần thiết cho cell thử OCR và được lưu cùng code trên Git.
Đợt sửa trục/nhãn nhiều dòng dùng `reviewed` và folder mới `prepared_accuracy_v4`.
Chạy bài thử Paddle và Qwen theo [VISION_PILOT.md](VISION_PILOT.md) trước khi OCR toàn bộ.

OCR và training chạy ở các process/phiên riêng. Không nạp CV và NLP đồng thời.
Giữ folder dữ liệu, checkpoint cũ để đối chiếu; kết quả mới ghi vào folder riêng.

## 1. Thử OCR trên bốn ảnh đã chép nhãn trực tiếp

Qwen2.5-VL-7B có kiến trúc/model class khác Qwen2-VL; loader mới đã hỗ trợ cả hai.
[Model card chính thức](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) có kết quả
ChartQA cao hơn Qwen2-VL-7B, nhưng không chứng minh điểm trên dữ liệu này.
[NF4](https://huggingface.co/docs/transformers/quantization/bitsandbytes) giảm bộ nhớ
trọng số để thử trên T4; chất lượng cần đo lại sau quantization.

Cell này đọc tên file từ reference, chỉ đưa ảnh và prompt tổng quát cho CV.
Các nhãn reference được dùng để chấm sau OCR, không đưa vào model.

```python
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
python -u - <<'PY'
import json
from pathlib import Path
from vinumqa.cv_module.structure_store import ChartStructureStore, SavedVisionFailure

refs = json.loads(Path('reports/public_accuracy_v2/pixel_references.json').read_text(encoding='utf-8'))
store = ChartStructureStore(
    '/kaggle/working/prepared_accuracy_v4/chart_structures.json',
    model_id='Qwen/Qwen2.5-VL-7B-Instruct', load_in_4bit=True, read_mode='reviewed',
)
try:
    for i, name in enumerate(refs['images'], 1):
        print(f'PILOT {i}/{len(refs["images"])}: {name}', flush=True)
        try:
            store.get(Path('data/public_test/public_test_images') / name, retry_failed=True)
        except SavedVisionFailure as error:
            print(f'Đã lưu lỗi: {error}', flush=True)
finally:
    store.close()
PY
python -m vinumqa.evaluation.score_ocr_labels \
  --prepared /kaggle/working/prepared_accuracy_v4/chart_structures.json \
  --reference reports/public_accuracy_v2/pixel_references.json \
  --output /kaggle/working/ocr_accuracy_pilot.json
```

So với `reports/public_accuracy_v2/ocr_before.json`: series recall 58,33%,
X-label recall 15,48%. Phải xem cả precision, recall và nhãn missing/extra;
không đánh giá chỉ bằng trạng thái `ok`. Đây là bốn ảnh khó, không đại diện toàn bộ tập.
Nếu thử FP16 trên GPU đủ bộ nhớ, bỏ `load_in_4bit=True` và dùng **store mới**;
không ghi lẫn hai cấu hình vào cùng store.

## 2. OCR train/public và dựng prompt mới

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
for split in train public_test; do
  python -u -m vinumqa.nlp_module.data_prep.format_training_data \
    --input "data/${split}/${split}.json" \
    --images "data/${split}/${split}_images" \
    --output "/kaggle/working/prepared_accuracy_v4/${split}_structured.json" \
    --structure-store /kaggle/working/prepared_accuracy_v4/chart_structures.json \
    --cv-model Qwen/Qwen2.5-VL-7B-Instruct \
    --cv-4bit --cv-read-mode reviewed --prompt-profile source-review-v1 \
    --retry-failed --max-minutes 240
done
```

Giới hạn 240 phút áp dụng từng split, kiểm tra giữa các ảnh. Mỗi ảnh được lưu ngay.
Chạy lại cùng cell để tiếp tục; ảnh đã thành công lấy từ store, ảnh lỗi được thử lại.
Không dùng script retry cũ với cấu hình mặc định 2B cho store 7B.
Nếu hết thời gian mà còn pending/error, hoàn tất OCR trước bước training.
Lưu/download `prepared_accuracy_v4` để dùng phiên sau; training chỉ cần hai file structured.

## 3. Kiểm tra dữ liệu và đo chính xác token

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
python -m vinumqa.evaluation.audit_supervision \
  --train-data /kaggle/working/prepared_accuracy_v4/train_structured.json \
  --val-data /kaggle/working/prepared_accuracy_v4/public_test_structured.json \
  --output /kaggle/working/supervision_accuracy.json
python -m vinumqa.nlp_module.training.audit_token_lengths \
  --prepared-dir /kaggle/working/prepared_accuracy_v4 \
  --data-root data \
  --output-dir /kaggle/working/token_audit_accuracy
```

Audit dừng nếu còn mẫu chưa ready; không tự bỏ câu khỏi mẫu số accuracy.
`target_binding_failed` chỉ ra nhãn program chưa liên kết được với OCR. Review các ảnh
liên quan: phân biệt nhãn thiếu/sai với alias hoặc mốc nằm giữa tick. Không chép nhãn
từ public program vào OCR để làm cho kiểm tra qua. Không yêu cầu con số này bằng 0
bằng cách nới validator hoặc bỏ mẫu.

Token audit dùng đúng prompt/completion/EOS của trainer, không nạp model weights.
`summary.json -> combined -> max_padded_to_8` là budget không cắt mẫu của bộ dữ liệu mới.
Không lấy lại budget cũ vì catalog bảng và OCR mới làm độ dài thay đổi.

## 4. Train adapter mới, lưu kết quả và checkpoint tốt nhất mỗi epoch

Chạy trong phiên GPU mới sau khi đã lưu dữ liệu OCR. Cell này giữ LR cũ, chỉ đổi
warmup thành 5% để giảm số biến thử nghiệm; chưa bật augmentation.

```python
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
PREP = Path('/kaggle/working/prepared_accuracy_v4')
summary = json.loads(Path('/kaggle/working/token_audit_accuracy/summary.json').read_text())
budget = summary['combined']['max_padded_to_8']
env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'
print('Max sequence length:', budget, flush=True)
subprocess.run([
    sys.executable, '-u', '-m', 'vinumqa.nlp_module.training.train_qlora',
    '--train-data', str(PREP / 'train_structured.json'),
    '--val-data', str(PREP / 'public_test_structured.json'),
    '--output-dir', '/kaggle/working/outputs/nlp_accuracy',
    '--max-seq-length', str(budget),
    '--epochs', '3', '--learning-rate', '0.0002', '--warmup-ratio', '0.05',
    '--max-train-hours', '10.5', '--save-steps', '50',
], cwd=REPO, env=env, check=True)
```

Training vẫn đọc full train; public chỉ dùng validation. `max-train-hours` là giới hạn
mềm, gồm loading/evaluation, không đảm bảo hoàn tất ba epoch trong một phiên T4.
Hết giờ thì giữ nguyên dữ liệu/cấu hình và thêm
`--resume-from-checkpoint /.../checkpoint-N` vào cell để tiếp tục phiên sau.
Không resume checkpoint cũ khi đã thay OCR/prompt/dataset; manifest sẽ từ chối.

Trong `outputs/nlp_accuracy`:

- `checkpoint-N`: có optimizer/scheduler/RNG để resume training.
- `best_program`: adapter có Program Accuracy cao nhất trong các lượt valid hoàn tất;
  dùng inference, không chứa đủ trạng thái để resume training.
- `validation_predictions/epoch_*.json`: `qid`, `predicted`.
- `epoch_*.metrics.json`: Program Accuracy sau kiểm tra, accuracy candidate thô và
  số candidate đúng bị loại. `complete=false` không được chọn làm best.
- `epoch_*.diagnostics.json` và `.cv_requests.json` nếu có: lỗi và yêu cầu CV chưa xử lý.

Muốn thử augmentation đổi ID nguồn, chạy một output-dir mới với `--augment-source-ids`.
Nó chỉ áp dụng train và tăng số mẫu/bước; chạy lại token audit ở cell 3 với cùng cờ
`--augment-source-ids` để lấy budget cho đúng dữ liệu augmented.
Đây là thử nghiệm riêng, không mặc định bảo đảm tăng accuracy. Thử LR `0.0001` cũng
cần một run riêng rồi so cùng bộ valid, tránh ghi đè baseline.

## 5. Valid đầy đủ bằng best adapter, có vòng CV sửa cấu trúc khi cần

Không chạy cell này đồng thời với training. `repair_inference` loại program/answer gốc
khỏi đầu vào model; ground truth chỉ đọc sau ở bước chấm. Nếu CV bổ sung cấu trúc,
store được cập nhật; giữ bản sao store ban đầu nếu muốn replay chính xác từng cấu hình.

```python
import subprocess
import sys
from pathlib import Path

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
run = subprocess.run([
    sys.executable, '-u', '-m', 'vinumqa.pipeline.repair_inference',
    '--input', 'data/public_test/public_test.json',
    '--images', 'data/public_test/public_test_images',
    '--adapter', '/kaggle/working/outputs/nlp_accuracy/best_program',
    '--structure-store', '/kaggle/working/prepared_accuracy_v4/chart_structures.json',
    '--output-dir', '/kaggle/working/public_accuracy_validation',
    '--max-rounds', '3', '--nlp-attempts', '2',
    '--max-hours', '10.5', '--nlp-device', 'cuda:0',
], cwd=REPO)
if run.returncode == 2:
    print('Đã lưu tiến độ; xem unresolved.json và chạy lại cùng cell để tiếp tục.')
elif run.returncode:
    raise RuntimeError(f'Validation lỗi, exit code={run.returncode}')
```

`results.json` chỉ xuất khi đủ QID được kiểm tra chấp nhận. Trạng thái accepted không phải
accuracy. Các câu unresolved vẫn nằm trong diagnostics; không tự điền program giả.
Muốn so checkpoint khác, chọn output-dir khác.

## 6. Chấm lại đúng ground truth gốc

```bash
%%bash
set -e
cd /kaggle/working/vlsp-Numerical-Reasoning-QA
python -m vinumqa.evaluation.audit_accuracy \
  --source data/public_test/public_test.json \
  --predictions /kaggle/working/public_accuracy_validation/results.json \
  --prepared /kaggle/working/prepared_accuracy_v4/public_test_structured.json \
  --output /kaggle/working/public_accuracy_validation/accuracy_audit.json
```

`accuracy` và `correct` là kết quả mới so 459 gold; so với 240/459 ban đầu.
Phần binding trong audit dùng snapshot prepared, còn repair có thể cập nhật store sau đó;
không nhầm snapshot này với cấu trúc cuối trong diagnostics.
Nếu chưa có `results.json`, có thể chấm file `validation_predictions/epoch_*.json`:
câu rỗng vẫn tính sai, mẫu số giữ nguyên. Tỷ lệ accepted và số lỗi validator giảm
không thay thế được Program Accuracy.
