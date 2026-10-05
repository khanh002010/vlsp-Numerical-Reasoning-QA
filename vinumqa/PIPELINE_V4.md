# Pipeline v4

Pipeline đã sửa các lỗi xác định trong audit v3: decimal DSL, parser/validator, retry, nguồn Image/Table, prompt chung, bảng có header nhiều tầng, CV cache, completion-only loss và split theo tài liệu/ảnh.

## Chạy từ project root

```powershell
python -m unittest discover -s tests -v
python -X utf8 -m vinumqa.data.prepare_dataset
python -m vinumqa.nlp_module.data_prep.format_training_data --input vinumqa/data/train_split.json --images data/train/train_images --output vinumqa/data/train_split_formatted.json --skip-invalid
python -m vinumqa.nlp_module.data_prep.format_training_data --input vinumqa/data/val_split.json --images data/train/train_images --output vinumqa/data/val_split_formatted.json --skip-invalid
python -m vinumqa.nlp_module.training.train_qlora --max-seq-length 8192
python -m vinumqa.pipeline.batch_inference --input data/public_test/public_test.json --images data/public_test/public_test_images --adapter outputs/nlp_module/final --output submission_v4.json
```

Hai bước CV/train cần môi trường GPU và dependencies của project. CV chạy thật lần đầu và lưu cache trong `outputs/cv_cache`; lần sau dùng cache theo nội dung ảnh, model ID và cache version. Khi thay model revision hoặc prompt CV, đổi cache version. Không sinh placeholder khi CV thất bại.

`--skip-invalid` chỉ loại gold không hợp lệ và ghi QID/lý do vào file `.rejected.json`; không bỏ qua lỗi CV. Cần kiểm tra file này, đặc biệt mẫu train có newline giữa hai operation nhưng thiếu dấu chấm phẩy. Dữ liệu gốc không bị tự sửa. Muốn chặn mọi mẫu bị loại, bỏ flag này.

Formatter giữ nguyên raw value tiếng Việt (ví dụ `79.000`, `14,8`); literal trong DSL luôn là số dùng dấu chấm thập phân. Việc chuyển raw value sang literal phụ thuộc ngữ cảnh/đơn vị, không được xóa dấu chấm toàn cục.

## Huấn luyện

- Train dùng `train_split_formatted.json`, val dùng `val_split_formatted.json`; không dùng public làm eval mặc định.
- Loader kiểm tra version/prompt, target parse được, QID độc nhất và không giao tài liệu/ảnh train-val.
- Prompt và padding có label -100; completion giữ label và EOS. Collator giữ nguyên mask, kể cả khi padding token bằng EOS.
- Tokenization không truncate target. Nếu vượt budget, lệnh dừng với số token prompt/target. Tăng `--max-seq-length` nếu GPU cho phép hoặc rút context có kiểm chứng rồi format lại. 8192 là cấu hình khởi đầu, chưa được benchmark VRAM trên GPU của bạn.
- Adapter lưu tokenizer và `pipeline_manifest.json`. File formatted/adapter v3 không tương thích contract v4; cần format và train lại. `ProgramGenerator(..., allow_legacy_adapter=True)` chỉ dành cho so sánh trực tiếp với adapter cũ, không phải chế độ mặc định của batch.

## Kiểm tra khi inference

- Decoder giới hạn toàn bộ tên operator, có trạng thái riêng mỗi hàng và chỉ xét token mới sinh. Đây chưa phải grammar đầy đủ cho mọi đối số.
- Validator kiểm tra arity, numeric types, reference lùi, source IDs và chia cho 0 khi biết giá trị. Chưa chứng minh label/phạm vi/ý nghĩa câu hỏi đúng; vẫn cần đo Program Accuracy sau train.
- Reflection kiểm tra cả lần sinh cuối; số trong câu hỏi/hằng số 100 không bị kiểm tra bằng substring context.
- Batch lưu `.diagnostics.json` gồm raw output, candidate, lỗi, lịch sử retry và prompt hash. Chạy lại để retry các câu lỗi, giữ câu đã hợp lệ. Chỉ xuất submission đủ QID khi mọi câu qua kiểm tra cấu trúc. Khi đổi dữ liệu/adapter dùng output khác.
- Executor math hoạt động; table/chart cần resolver callable được cung cấp tường minh. Không còn trả None im lặng cho lookup chưa hỗ trợ. Pipeline thi sinh program, không giả vờ đã thực thi lookup từ Markdown.

`compile_plan` nhận node ID và reference có kiểu để sinh `#N` đúng. Đây là API cho bước tiếp theo nếu huấn luyện model sinh plan; pipeline mặc định vẫn huấn luyện/sinh DSL trực tiếp để không thay nhãn nhiệm vụ cùng lúc. Evidence Step 1 giữ nhóm operation, vị trí đối số và giá trị lặp; không tuyên bố đã có tọa độ nguồn cho mọi literal chưa align.

## Phạm vi kiểm chứng

Test offline bao gồm 459 gold public round-trip, decimal, reference, nguồn, compiler, retry, token mask/EOS, overflow, table header, split không giao ảnh, cache và batch resume. Chưa train/inference lại Qwen hoặc benchmark CUDA trong phiên sửa code này; chưa có số accuracy v4.
