# Private inference: sửa lỗi, tiếp tục và xuất đủ program

Bản sửa dùng checkpoint v8 hiện tại, không đổi INSTRUCTION hoặc định dạng adapter. Cần chạy lại inference; kết quả submit cũ không tự thay đổi.

## Quy tắc xuất file

- `results.json` chỉ xuất khi tất cả QID có program không rỗng và vượt các kiểm tra hiện tại; schema là `qid`, `predicted`.
- `results_program.json` tương ứng dùng khóa `program`.
- Đang chạy hoặc còn lỗi: lưu `accepted.partial.json`, `unresolved.json`, `diagnostics.json`, `state.json`, `summary.json`. Không dùng partial để nộp.
- Câu lỗi được giữ candidate và lịch sử sửa; không thay bằng `add(0; 0)` hoặc loại QID.
- Hết thời gian: chạy lại đúng lệnh và output-dir để tiếp tục. File nộp cũ mất hiệu lực do nguồn đổi được đổi tên `.superseded`.
- `complete=true` nghĩa đủ program qua kiểm tra, không phải chứng nhận accuracy 100%.

## Cell Kaggle

Dùng repo đã cập nhật. Đổi ADAPTER nếu dataset checkpoint khác. Dùng output-dir mới cho policy này; state của policy cũ không tương thích.

```python
import os
import sys
import shutil
import subprocess
from pathlib import Path

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
ADAPTER = Path('/kaggle/input/datasets/khanh002010/vlsp-final/outputs/nlp_module/final')
PREP = Path('/kaggle/working/prepared')
STORE = PREP / 'private_chart_structures.json'
OUT = Path('/kaggle/working/private_repaired_v2')
INPUT = REPO / 'data/private_test/private_test_cleaned.json'
IMAGES = REPO / 'data/private_test/private_test_images'

assert (REPO / 'vinumqa/pipeline/repair_inference.py').is_file(), REPO
assert (ADAPTER / 'adapter_config.json').is_file(), ADAPTER
assert INPUT.is_file() and IMAGES.is_dir(), 'Thiếu dữ liệu private'
PREP.mkdir(parents=True, exist_ok=True)
if not STORE.is_file():
    source = REPO / 'prepared/private_chart_structures.json'
    assert source.is_file(), f'Thiếu store OCR: {source}'
    shutil.copy2(source, STORE)

# Subprocess mới tránh import nhầm code cũ trong kernel.
# Không giữ model OCR/training khác trên GPU cùng lúc.
env = os.environ.copy()
env['PYTHONPATH'] = str(REPO)
command = [
    sys.executable, '-u', '-m', 'vinumqa.pipeline.repair_inference',
    '--input', str(INPUT), '--images', str(IMAGES),
    '--adapter', str(ADAPTER), '--structure-store', str(STORE),
    '--reviewed-structures', str(REPO / 'vinumqa/data/reviewed_private_structures.json'),
    '--output-dir', str(OUT), '--max-rounds', '4',
    '--nlp-attempts', '2', '--max-hours', '10.5',
    '--nlp-device', 'cuda:0', '--progress-seconds', '30',
    '--max-generation-seconds', '120',
]
previous = REPO / 'submit/private_test/diagnostics.json'
if previous.is_file():
    command += ['--previous-diagnostics', str(previous)]

process = subprocess.run(command, cwd=REPO, env=env)
if process.returncode == 2:
    print('Đã lưu tiến độ. Còn câu trong unresolved.json; chưa xuất file nộp. Chạy lại cell để tiếp tục.')
elif process.returncode:
    raise RuntimeError(f'Pipeline dừng, exit={process.returncode}; xem lỗi bên trên. Tiến độ nằm trong OUT.')
```

`--max-rounds` áp dụng mỗi phiên. `--nlp-attempts` là số lượt sửa ngay cho lỗi DSL/Step 1/nguồn bảng. Thiếu nhãn ảnh chuyển sang CV trước. Giới hạn thời gian là mềm, có dự phòng lưu file. OOM dừng sớm thay vì đánh dấu cả tập lỗi.

## Log generation và cảnh báo Timeout định kỳ

`Timeout (0:03:00)!` từ `faulthandler.dump_traceback_later(180, repeat=True)` là dump stack định kỳ tính từ lúc bật bộ đếm, không phải exception hoặc bằng chứng một câu đã treo 180 giây. Trong log ngày 2026-10-12, câu 33 và 39 vẫn sinh xong và chuyển sang câu tiếp theo sau dump.

Bản sửa in `[NLP generate]`, heartbeat `[NLP progress]` mỗi 30 giây, `[NLP generated]` và `[SAVE]`. Heartbeat có số token đã sinh và thời gian từ bước token cuối; nó không gọi CUDA và không tự chứng nhận GPU còn tiến triển. `generated_tokens=0` có thể là đang prefill. Raw output hiển thị 300 ký tự đầu; không suy ra program bị cắt chỉ từ dòng debug đó.

NLP mặc định 4-bit, FP16, trên `cuda:0`; `--nlp-device auto` cho phép chia model nếu cần. Một GPU tránh truyền giữa hai GPU không cần thiết, nhưng vẫn có thể OOM nếu context lớn; không tự cắt context để tránh OOM. Chưa đo tốc độ thực tế trên T4 của người dùng.

`--max-generation-seconds` là giới hạn mềm của Transformers, không thể ngắt CUDA forward đang kẹt. Generation chạy đồng bộ; không bỏ rơi thread GPU sau timeout rồi chạy câu khác trên cùng model. EOS được nhận diện theo toàn bộ danh sách stop token của model.

Lỗi chỉ thiếu nhãn trục trong cấu trúc chưa đọc đủ được chuyển vào hàng đợi CV khi còn vòng CV tiếp theo. Sai series/DSL vẫn được NLP sửa; nếu lặp lại cùng candidate và cùng lỗi thì dừng các lượt retry dư trong vòng đó. CV chạy sau lượt NLP, không nạp đồng thời hai model. Không tự hợp thức hóa nhãn hoặc số không có bằng chứng.

Cell có `faulthandler` ở ngoài vẫn sẽ in Timeout định kỳ: dùng lại `subprocess.run(command, cwd=REPO, env=env)` như trên để dùng heartbeat mới thay cho dump định kỳ. Giữ INPUT, ADAPTER, STORE, OUT của lượt đang chạy (kể cả INPUT chỉ gồm 228 câu); bản sửa runtime này không thay run identity. Không đổi INPUT 228 câu thành toàn bộ 980 câu trong cùng OUT.

## Cell kiểm tra kết quả

```python
import json

summary = json.loads((OUT / 'summary.json').read_text(encoding='utf-8'))
print(json.dumps(summary, ensure_ascii=False, indent=2))
if summary['complete']:
    rows = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
    source_rows = json.loads(INPUT.read_text(encoding='utf-8'))
    assert [r['qid'] for r in rows] == [r['qid'] for r in source_rows]
    assert all(isinstance(r['predicted'], str) and r['predicted'].strip() for r in rows)
    print('File nộp:', OUT / 'results.json', '—', len(rows), 'program không rỗng')
else:
    print('Chưa có file nộp hoàn chỉnh. Còn', summary['unresolved'], 'câu.')
    print('Lỗi/candidate:', OUT / 'unresolved.json')
```

## Cơ chế sửa

- Bộ sửa nhãn có 83 entry theo SHA256; một entry có thể chỉ sửa vài trường (ví dụ bỏ tiêu đề tự bịa), không chứng nhận toàn bộ ảnh chính xác. Trường đã đối chiếu được bảo vệ khỏi CV ghi lại nhãn sai. Không dùng program private làm đáp án.
- CV đọc legend/X/Y riêng. Request có vùng cụ thể chỉ đọc trường đó. Yêu cầu lỗi tạm thời được retry có giới hạn.
- NLP nhận catalog header/khóa hàng bảng và phản hồi lỗi; khi sửa phải nối các nhánh, chọn đúng đại lượng/kỳ/đơn vị và giữ toán tử chart.
- Validator hỗ trợ khóa hàng ở cột thứ hai, bảng thời gian xếp ngược; chỉ chuẩn hóa typography rõ ràng, không bỏ dấu hoặc đoán tên gần giống.
- CV và NLP giải phóng luân phiên. QID chung ảnh dùng một store; sửa ảnh làm vô hiệu kết quả phụ thuộc.
- Giữ STORE và OUT giữa các phiên. Không bảo đảm checkpoint giải quyết đúng mọi câu trong một phiên T4. Cổng xuất file bảo đảm không nộp nhầm program rỗng.

## Kiểm thử local

```bash
python -m unittest discover -s tests
```

Test dùng model giả để kiểm tra điều phối, lỗi nguồn, retry, dừng OOM, resume và điều kiện xuất file. Cần chạy checkpoint thật trên Kaggle để đo số câu giải quyết được và chất lượng program.
