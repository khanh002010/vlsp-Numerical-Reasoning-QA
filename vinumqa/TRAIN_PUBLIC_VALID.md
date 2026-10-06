# OCR ghi trực tiếp và training từ file đã chuẩn bị

Chạy từ thư mục gốc project:

```bash
python -m vinumqa.nlp_module.data_prep.format_training_data --input data/train/train.json --images data/train/train_images --output vinumqa/data/train_formatted.json
python -m vinumqa.nlp_module.data_prep.format_training_data --input data/public_test/public_test.json --images data/public_test/public_test_images --output vinumqa/data/public_test_formatted.json
python -m vinumqa.nlp_module.training.train_qlora --max-seq-length 8192
```

Không split: training dùng toàn bộ train, validation dùng public test. QID trùng giữa hai tập và format cũ không hợp lệ vẫn bị từ chối.

## Lưu từng ảnh vào file chính

Formatter ghi file --output ngay khi bắt đầu và sau từng ảnh bằng file tạm + flush/fsync + replace. Nếu tắt giữa chừng, các ảnh đã ghi vẫn còn; file JSON không bị ghi dở. Không đọc/ghi `outputs/cv_cache/` trong luồng chuẩn bị dữ liệu này. Cache OCR của luồng inference khác giữ nguyên và không tự nhập vào output mới.

File chính là object `artifact_version: vinumqa-prepared-v1`, gồm:

- `images`: tên ảnh, index, status (`pending`, `ok`, `error`), Markdown hoặc lỗi.
- `samples`: mỗi QID có status (`pending`, `ready`, `error`). Mẫu ready chứa dữ liệu training trong `data`; mẫu lỗi/chưa đủ ảnh giữ `source` gốc và lý do.
- `summary`: số mẫu ready/error/pending.

Ảnh lỗi vẫn được ghi vào file chính và được sao sang `<output-stem>.ocr_errors.json`. Danh sách QID chưa sẵn sàng nằm ở `<output-stem>.rejected.json`. Các ảnh thành công tiếp theo vẫn được ghi bình thường. Lỗi khởi tạo model dừng tiến trình nhưng giữ tiến độ đã lưu; không đánh dấu ảnh là lỗi vì vấn đề môi trường.

Training đọc được cả object mới lẫn JSON list hợp lệ từ formatter cũ. Formatter không ghi đè file list cũ: nếu output đã là kiểu cũ, dùng tên output mới để giữ dữ liệu cũ.

## Tiếp tục OCR từ ảnh số N

Thứ tự ảnh tính từ 1, theo lần đầu tên ảnh xuất hiện trong dataset. Ảnh dùng chung chỉ có một số thứ tự, ổn định giữa các lần chạy cùng input.

```bash
python -m vinumqa.nlp_module.data_prep.format_training_data \
  --input data/train/train.json --images data/train/train_images \
  --output vinumqa/data/train_formatted.json --start-image 50
```

`--start-image` mặc định 1 và chỉ áp dụng OCR, không cắt tập training. Giữ cùng input/output khi tiếp tục. Ảnh đã lưu thành công hoặc lỗi không OCR lại. Thêm `--retry-failed` để thử lại ảnh lỗi từ số N trở đi. Nếu bắt đầu ở N nhưng output chưa có kết quả 1..N-1, các ảnh trước đó giữ pending; chạy lại từ 1 để bổ sung. Khi input hoặc hợp đồng định dạng đổi, chọn output mới.

Log terminal hiện `[OCR image N/TOTAL] filename: START/SAVED_OK/SAVED_ERROR`, kèm thời gian và thống kê mẫu. Mỗi lượt tăng token vẫn có log budget, số token và thời gian.

## Training trên notebook khác

Lưu/tải hai file formatted hoặc đưa vào Kaggle Dataset. Khi training không cần ảnh gốc, model OCR hay cache OCR; chỉ cần base model NLP và dependency training. Trước khi kết thúc phiên Kaggle, lưu notebook output hoặc tải file để giữ qua phiên.

```bash
python -m vinumqa.nlp_module.training.train_qlora \
  --train-data /kaggle/input/vinumqa-prepared/train_formatted.json \
  --val-data /kaggle/input/vinumqa-prepared/public_test_formatted.json \
  --output-dir /kaggle/working/outputs/nlp_module \
  --max-seq-length 8192
```

Thay `vinumqa-prepared` bằng đường dẫn dataset của bạn. Mặc định mọi mẫu phải ready. Nếu chấp nhận chỉ train/evaluate trên phần dữ liệu sẵn sàng, thêm `--skip-unready`; log báo số mẫu bị loại khỏi mỗi tập. Validation khi đó là tập con, không đủ QID public test. Mẫu lỗi vẫn giữ trong file nguồn. `--skip-invalid` ở formatter chỉ còn là cờ tương thích; mẫu lỗi luôn được lưu.

Sau mỗi epoch, tính eval loss rồi sinh kết quả vào `outputs/nlp_module/validation_predictions/epoch_N_step_S.json` và `.diagnostics.json` (hoặc dưới --output-dir). File kết quả dùng `[{"qid": "...", "predicted": "..."}]`. Prompt generation không chứa gold. Callback hiện hỗ trợ một process/GPU; đây chưa phải training TPU.

## Cấu hình OCR

Giới hạn ảnh 750.000 pixel. Budget khởi đầu 1024/2048/4096 theo heuristic mật độ cạnh; chạm trần chưa EOS thì sinh lại với budget gấp đôi đến tối đa 16384. Nếu vẫn không hoàn thành, lưu trạng thái lỗi. Retry sinh lại từ đầu vẫn có thể tốn thời gian với bảng dài.

T4 dùng SDPA; FlashAttention-2 chỉ được chọn khi phần cứng và thư viện phù hợp. Model/processor ưu tiên snapshot local đầy đủ để tránh tokenizer gọi Hub rồi gặp HTTP 429. Cache thiếu thì tải bổ sung; nếu vẫn bị 429, giữ cache, chờ khoảng retry hoặc cấu hình HF_TOKEN qua Kaggle Secrets. Không ghi token vào source/log.

Tài liệu này thay thế hướng dẫn split/train/validation và lưu OCR cũ trong PIPELINE_V4.md.
