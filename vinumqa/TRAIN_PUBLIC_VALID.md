# CV đọc cấu trúc → NLP sinh program → kiểm tra → thực thi tùy chọn

Luồng mặc định dùng `vinumqa-v8-structures`. CV đọc tiêu đề, loại biểu đồ, series,
nhãn trục, đơn vị, vùng ảnh và phần chưa chắc chắn. Không yêu cầu vẽ lại mọi điểm
thành bảng số. NLP nhận cấu trúc + context + câu hỏi và giữ các toán tử `chart_*`.

**Cần chuẩn bị dữ liệu và train adapter mới.** File formatted/adapter cũ khác hợp
đồng prompt, không dùng trực tiếp. Giữ file cũ và dùng tên `*_structured.json` mới.
`ocr_token_probe` vẫn thử Markdown cũ, không đo JSON cấu trúc của luồng mới.

## Chuẩn bị dữ liệu trên Kaggle

Chạy từ thư mục gốc repository (notebook thêm `!` trước Python hoặc dùng `%%bash`).

```bash
python -m vinumqa.nlp_module.data_prep.format_training_data \
  --input data/train/train.json --images data/train/train_images \
  --output /kaggle/working/prepared/train_structured.json \
  --structure-store /kaggle/working/prepared/chart_structures.json \
  --max-minutes 600

python -m vinumqa.nlp_module.data_prep.format_training_data \
  --input data/public_test/public_test.json --images data/public_test/public_test_images \
  --output /kaggle/working/prepared/public_test_structured.json \
  --structure-store /kaggle/working/prepared/chart_structures.json \
  --max-minutes 600
```

`--max-minutes` là giới hạn mềm **của từng lệnh**, kiểm tra giữa các ảnh. Không cộng
hai lượt 600 phút rồi mặc định vừa một phiên 12 giờ; chia phiên nếu không đủ giờ.
CV thử 1024 token, chỉ tăng đến 2048 nếu chạm trần token. Mỗi lượt generation có
`max_time=120` giây (giới hạn mềm theo bước sinh, không gồm tải model/tiền xử lý).
Lặp/JSON sai/hết thời gian được lưu lỗi; không có vòng tăng đến 16K như Markdown cũ.

Trần **1.400.000 pixel** giữ nguyên. Ảnh dưới trần giữ kích thước riêng trước
processor; ảnh lớn được thu nhỏ giữ tỷ lệ. Processor vẫn căn theo lưới patch Qwen.

Sau từng ảnh, chương trình ghi bằng file tạm + flush/fsync + replace:

- `chart_structures.json`: cấu trúc/lỗi, chẩn đoán generation và đọc bổ sung, theo
  SHA-256 nội dung ảnh. Cùng ảnh được dùng lại giữa nhiều câu, kể cả Image ID/tên
  file khác. Đây là dữ liệu bền trên đĩa, không dùng thư mục cache Markdown cũ.
- Hai file `*_structured.json`: `images` và `samples`; mẫu `ready` đã có đầy đủ
  input training. Mẫu `pending`/`error` giữ `source` gốc và lý do.
- `*.ocr_errors.json`: ảnh lỗi; `*.rejected.json`: QID chưa sẵn sàng.

Ảnh lỗi đã ghi trong store không đọc lại ở câu/phiên sau. Thêm `--retry-failed` để
thử lại. Lỗi khởi tạo model dừng chương trình, không đánh dấu ảnh hỏng. Dùng store
và output mới nếu thay hợp đồng/model/prompt; không trộn dữ liệu theo hai hợp đồng.

Tiếp tục bằng cùng lệnh và đường dẫn, mặc định từ ảnh 1 nhưng dùng lại ảnh đã lưu.
Có thể thêm `--start-image 50`: STT theo lần đầu tên ảnh xuất hiện **trong từng file
input**, không cộng dồn train và public test. Tham số này không cắt tập train. Nếu
chưa có kết quả ảnh 1–49, các mẫu liên quan còn pending.

Giữ ba file chính bằng Kaggle Output/Dataset để mang sang phiên sau. Hai file
`*_structured.json` đủ để train; store và ảnh gốc dùng cho inference đọc bổ sung.
Chỉ ghi `/kaggle/working` mà không giữ Output/Dataset không bảo đảm còn khi mất phiên.

## Training T4 16 GB và resume

Nên tách phiên chuẩn bị ảnh khỏi phiên train. Training không nạp CV, không cần ảnh.
Mặc định Qwen2.5-7B QLoRA 4-bit NF4, FP16, SDPA, gradient checkpointing, microbatch 1,
gradient accumulation 16 (effective batch 16). Đây là cấu hình giảm VRAM, chưa phải
kết quả benchmark T4 trên dữ liệu này.

```bash
python -m vinumqa.nlp_module.training.train_qlora \
  --train-data /kaggle/input/vinumqa-prepared/train_structured.json \
  --val-data /kaggle/input/vinumqa-prepared/public_test_structured.json \
  --output-dir /kaggle/working/outputs/nlp_structures \
  --max-seq-length 4096 --max-train-hours 10.5 --save-steps 50
```

Đổi tên Dataset theo thực tế. Dùng toàn bộ train và public test làm validation,
không split. Mọi mẫu phải ready; chỉ thêm `--skip-unready` khi chấp nhận tập con.
QID trùng giữa hai tập bị từ chối. Tokenization kiểm tra độ dài trước khi nạp model,
**không cắt mất target**. Nếu `Sequence overflow`, tăng `--max-seq-length` (ví dụ
8192), với chi phí VRAM/thời gian cao hơn. 4096 không bảo đảm mọi mẫu đều vừa.

Lưu checkpoint mỗi 50 optimizer step và sau epoch, giữ hai checkpoint gần nhất.
`--max-train-hours 10.5` tính từ đầu tiến trình, gồm tải model/validation; yêu cầu
dừng/lưu trước mốc đó 10 phút. Đây là giới hạn mềm tại step/epoch/từng câu sinh
validation: bước dài, eval loss hoặc I/O có thể vượt mốc. Không cam kết 3 epoch vừa
12 giờ. Khi dừng sớm vì thời gian, không tạo `final` như thể đã train xong.

Để resume, giữ nguyên lệnh trên và thêm:

```bash
--resume-from-checkpoint /kaggle/input/my-checkpoints/checkpoint-100
```

Phải giữ **toàn bộ thư mục checkpoint**: adapter, tokenizer, optimizer, scheduler,
Trainer/RNG và `pipeline_manifest.json`. Chỉ adapter đủ inference, không đủ resume
optimizer. Manifest kiểm tra cùng dữ liệu/prompt/sequence length. Lưu checkpoint
thành Output/Dataset trước khi hết phiên.

## Validation mỗi epoch

Sau mỗi epoch: eval loss rồi sinh program public test, ghi ngay từ đầu và cập nhật
sau từng câu vào `<output-dir>/validation_predictions/`:

```text
epoch_N_step_S.json
epoch_N_step_S.diagnostics.json
epoch_N_step_S.cv_requests.json  # nếu cần CV
```

Kết quả dùng `[{"qid":"...","predicted":"chart_at(...); subtract(...)"}]`.
Câu sai kiểm tra/chưa sinh có `predicted: ""`; xem diagnostics trước khi nộp.
Câu còn lại khi hết budget có `pending_time_budget`. Gold chỉ là target/eval loss,
không đưa vào prompt sinh dự đoán.

Callback **không nạp CV cùng model đang train**. Khi cần nhãn mới, nó ghi yêu cầu
vào `.cv_requests.json`; chạy batch inference từ checkpoint sau đó để giải quyết.
Callback không tự tiếp tục file epoch đang dở khi resume train; có thể inference
riêng từ checkpoint đó. Hỗ trợ một process/GPU, chưa phải TPU/distributed training.

## Inference và đọc bổ sung

Store phải ở đường dẫn **ghi được**. Nếu nằm trong `/kaggle/input`, sao chép sang
`/kaggle/working/prepared` trước để lưu đọc bổ sung.

```bash
python -m vinumqa.pipeline.batch_inference \
  --input data/public_test/public_test.json \
  --images data/public_test/public_test_images \
  --adapter /kaggle/working/outputs/nlp_structures/final \
  --structure-store /kaggle/working/prepared/chart_structures.json \
  --max-cv-requests 2 --output /kaggle/working/submission.json
```

`--adapter` cũng nhận `checkpoint-N` có manifest/tokenizer. Batch lưu diagnostics
sau từng câu và dùng lại câu đã hợp lệ khi chạy lại. Nếu còn lỗi, báo lỗi và không
ghi đè submission bằng dự đoán chưa hợp lệ.

NLP có thể trả JSON riêng thay cho Step 1/2:

```json
{"cv_request":{"image_id":"Image 1","kind":"inspect","region":"legend","series":"TCB"}}
```

`region`: full/legend/x_axis/y_axis/plot; tùy chọn `box: [left,top,right,bottom]`
chuẩn hóa 0..1. Có tọa độ thì CV đọc crop; thiếu tọa độ thì đọc ảnh đầy đủ với yêu
cầu tập trung vùng/series. Series NLP nêu chỉ là gợi ý, không phải nhãn đã xác minh.
Validator cũng tự yêu cầu đọc lại nếu phát hiện nhãn thiếu, không phụ thuộc hoàn
toàn vào việc NLP biết yêu cầu CV.

Mỗi câu tối đa 2 yêu cầu CV và 1 lượt sửa program. Kết quả/lỗi đọc bổ sung được lưu
để không gọi lại cùng yêu cầu. Pipeline giải phóng NLP trước khi nạp CV rồi giải
phóng CV trước khi nạp lại NLP. Tiết kiệm VRAM đỉnh nhưng nạp lại NLP vẫn tốn thời
gian; chuẩn bị cấu trúc cả public test trước inference giúp giảm chuyển model.

Kiểm tra gồm DSL, nguồn Image/Table, series, nhãn, thứ tự khoảng và đối số Step 1
đối chiếu program (kể cả `#N`). Không tự đảo đối số hoặc đổi nhãn để vượt kiểm tra.
Crop không tự chứng minh thứ tự toàn ảnh. Nhãn chưa xác minh được bị từ chối.
Kiểm tra nhất quán **không chứng minh** CV đọc đúng pixel hoặc model hiểu đúng câu
hỏi: Step 1/program có thể cùng chọn sai toán tử. Nhãn viết khác gold/mốc thưa cần
đánh giá thêm, không tự tạo mốc không nhìn thấy để khớp gold.

## Thực thi số là tùy chọn

Mặc định `pipeline.run(...)` chỉ sinh/kiểm tra program. Thêm `execute=True` để lấy
`result["answer"]`; `result["reasoning_result"]["program"]` vẫn nguyên các `chart_*`.
Có thể tạo pipeline như sau, gọi `close()` khi dùng xong:

```python
from vinumqa.pipeline.full_pipeline import ViNumQAPipeline

pipeline = ViNumQAPipeline(
    nlp_lora_weights="outputs/nlp_structures/final",
    structure_store="prepared/chart_structures.json",
)
try:
    result = pipeline.run(
        text_segments=sample.get("text", []),
        tables_dict=sample.get("tables", {}),
        image_dict={key: "data/public_test/public_test_images/" + name
                    for key, name in sample.get("images", {}).items()},
        question=sample["qa"]["question"],
        execute=True,
    )
    print(result["reasoning_result"]["program"], result["answer"])
finally:
    pipeline.close()
```

Executor gọi CV lấy điểm và nguồn bằng chứng rồi tự tính aggregate. Cùng lookup
dùng lại kết quả lưu. Đọc số thất bại: `answer=None`, có `execution_error`, không sửa
program. `table_*` cần cung cấp `table_resolvers` để thực thi; HTML vẫn có trong
context khi sinh program.

Mặc định chỉ nhận số CV khai là in trực tiếp, có `raw_value`; khai báo này vẫn cần
đối chiếu ảnh. `allow_estimates=True` cho phép ước lượng đường/cột, không biến chúng
thành số chính xác. Aggregate đòi đủ điểm trong phạm vi, total đòi đủ series. Đường
liên tục với mốc thưa không được coi là đã khôi phục toàn bộ điểm để tính tổng.

## Kiểm thử

```bash
python -m unittest discover -s tests
```

Các test dùng model/reader giả kiểm tra lưu/resume, dùng chung ảnh, đọc bổ sung,
vòng đời CV/NLP, đối số, program giữ nguyên, numeric coverage, validation và budget.
Chúng không thay thế kiểm chứng chất lượng OCR, VRAM và thời gian trên GPU thật.
