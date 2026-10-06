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

OCR giữ `MAX_PIXELS=750000` cả resize và processor. Budget khởi đầu 1024/2048/4096 theo mật độ cạnh trên ảnh thumbnail; đây là heuristic độ phức tạp, không phải đếm chữ chính xác. Output gặp EOS thì dừng ngay; output chạm budget chưa EOS được chạy lại với budget gấp đôi, tối đa 16384. Nếu vẫn bị cắt hoặc extraction lỗi/kết quả không hợp lệ, ghi lỗi vào `outputs/cv_cache/failures/`. Các lần gặp cùng nội dung ảnh và model sẽ bỏ qua OCR, kể cả chạy lại script. Lỗi khởi tạo model không đánh dấu ảnh lỗi. Metadata lần chạy có tại `extractor.last_generation`.

Log terminal hiện `[OCR image N/TOTAL; seen=M] filename: STATUS`, trong đó N là số thứ tự ảnh theo lần đầu gặp trong tiến trình, M là số đường dẫn ảnh duy nhất đã gặp (không phải số ảnh thành công). TOTAL do formatter đếm từ dataset, gồm cả cache hit. Các trạng thái là START, DONE, CACHE_HIT, FAILED, SKIP_FAILED. Mỗi lượt tăng token có log budget, số token thực sinh và thời gian. Log sự kiện ảnh và metadata các lượt generation hoàn tất được lưu nối tiếp ở `outputs/cv_cache/progress.jsonl`. Số thứ tự đếm lại từ 1 khi khởi động tiến trình mới.

Ảnh bị bỏ qua không được thay bằng bảng giả. Formatter tiếp tục duyệt mẫu, ghi các QID thiếu context vào `.rejected.json`, rồi báo lỗi và không ghi đè dataset nếu còn lỗi ảnh. Muốn thử lại một ảnh đã đánh dấu thất bại sau khi xử lý nguyên nhân, chỉ xóa file JSON tương ứng trong `failures/` (trường `image` chứa tên ảnh).

Cache thành công vẫn dùng version `chart-markdown-v5-adaptive-750k`, nên nâng trần lên 16384 không buộc OCR lại các ảnh đã thành công ở v5. Cache v4 không được đọc. Giảm budget không tăng tốc ảnh vốn đã EOS sớm; retry sinh lại từ đầu có thể tăng thời gian với ảnh được ước lượng quá thấp.

Tài liệu này thay thế phần split/train/validation trong `PIPELINE_V4.md`.

Trên Kaggle T4, OCR tự chọn `sdpa`, không yêu cầu cài `flash_attn`. FlashAttention-2 chỉ được chọn khi mọi GPU nhìn thấy thuộc Ampere/Ada/Hopper và Transformers xác nhận thư viện khả dụng. Log khởi tạo hiển thị backend đã chọn. Nếu khởi tạo model thất bại, formatter dừng ngay, không nạp lại model theo từng câu hỏi và không đánh dấu ảnh là lỗi. Khởi động lại tiến trình sau khi cập nhật code để dùng cấu hình mới.
