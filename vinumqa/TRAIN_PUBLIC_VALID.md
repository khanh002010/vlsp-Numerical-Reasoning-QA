# Full train + public validation, adaptive OCR

Chạy từ project root, dùng dữ liệu formatted mới có CV thật:

```powershell
python -m vinumqa.nlp_module.data_prep.format_training_data --input data/train/train.json --images data/train/train_images --output vinumqa/data/train_formatted.json
python -m vinumqa.nlp_module.data_prep.format_training_data --input data/public_test/public_test.json --images data/public_test/public_test_images --output vinumqa/data/public_test_formatted.json
python -m vinumqa.nlp_module.training.train_qlora --max-seq-length 8192
```

Không chạy bước split. Train đọc toàn bộ `train_formatted.json`; validation đọc `public_test_formatted.json`. Loader vẫn từ chối format cũ và QID trùng giữa hai tập. Chia sẻ ảnh/tài liệu giữa train/public không còn là lý do chặn, theo cấu hình validation được yêu cầu.

Nếu formatter báo gold không hợp lệ, xem file `.rejected.json` và sửa nhãn đã xác minh trước khi format lại để giữ đầy đủ tập train. `--skip-invalid` chỉ dành cho trường hợp chấp nhận loại các nhãn lỗi, không phải full train tuyệt đối.

Sau eval loss mỗi epoch, model hiện tại sinh autoregressive cho toàn bộ public test, không dùng output gold trong prompt. Kết quả:

```text
outputs/nlp_module/validation_predictions/epoch_1_step_N.json
outputs/nlp_module/validation_predictions/epoch_1_step_N.diagnostics.json
```

File kết quả có dạng `[{"qid": "...", "predicted": "add(1; 2)"}]`. Candidate sai DSL vẫn được ghi để đánh giá trung thực; lỗi generation ghi `predicted: ""` và lý do ở diagnostics. Mỗi epoch có file riêng, ghi atomically. Batch inference cũng xuất khóa `predicted`; khóa `program` chỉ dùng nội bộ và diagnostics.

Generation mỗi epoch làm tăng thời gian so với chỉ tính eval loss. Callback hiện hỗ trợ training một process/GPU, khôi phục chế độ train, gradient checkpointing và use_cache sau generation. Chưa benchmark GPU trong phiên sửa code.

OCR giữ `MAX_PIXELS=750000` cả resize và processor. Budget khởi đầu 1024/2048/4096 theo mật độ cạnh trên ảnh thumbnail; đây là heuristic độ phức tạp, không phải đếm chữ chính xác. Output gặp EOS thì dừng ngay; output chạm budget chưa EOS được chạy lại với budget gấp đôi, tối đa 8192. Nếu vẫn bị cắt, extraction báo lỗi và không cache bảng thiếu. Metadata lần chạy có tại `extractor.last_generation`.

Cache đổi version sang `chart-markdown-v5-adaptive-750k`; cache cũ giữ nguyên nhưng không dùng cho cấu hình mới. Lần đầu cần trích xuất lại ảnh. Giảm budget không tăng tốc ảnh vốn đã EOS sớm; lợi ích cần đo trên dữ liệu thực, và retry có thể tăng thời gian với ảnh được ước lượng quá thấp.

Tài liệu này thay thế phần split/train/validation trong `PIPELINE_V4.md`.
