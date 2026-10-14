# Inference chọn nguồn → sinh program → sửa lỗi

Bật bằng `--three-pass` trong `vinumqa.pipeline.repair_inference`. Không cần train lại; giữ nguyên định dạng Step 1/Step 2 của checkpoint. Chế độ cũ vẫn dùng được khi bỏ flag, để so sánh trên public test.

1. Chọn nguồn: tối đa 512 token JSON gồm tác vụ toán học, Image/Table/Text, series, nhãn cần tìm và trích dẫn nguyên văn. Không đọc ground truth. Kiểm tra nguồn tồn tại, tên series thuộc đúng ảnh, trích dẫn xuất hiện trong context. Nhãn cần tìm không bị loại chỉ vì không nằm trong các tick thưa được in.
2. Sinh program: dùng toàn bộ context gốc và kế hoạch đã qua kiểm tra; kế hoạch là đề xuất, không phải ground truth. Nếu kế hoạch lỗi/không hoàn tất, cung cấp lỗi và yêu cầu chọn lại từ context khi sinh program. Giữ tối đa 1536 token cho định dạng checkpoint hiện tại.
3. Khi program bị từ chối, cung cấp program cùng lỗi kiểm tra cụ thể và sửa tối đa một lần. Nếu đủ dữ liệu và program vượt kiểm tra ngay thì bỏ lượt sửa. Nếu cần bằng chứng ảnh, dùng hàng đợi CV giữa các vòng hiện có; không nạp CV và NLP cùng lúc.

Mỗi vòng có tối đa ba lần sinh NLP cho một câu với `--nlp-attempts 2`. Có thể có nhiều vòng khi CV bổ sung thông tin; giới hạn tổng bằng `--max-rounds`/`--max-hours`. Thời gian inference có thể tăng; chưa đo accuracy hay tốc độ GPU. JSON lựa chọn nguồn không dùng bộ ràng buộc toán tử DSL. Kế hoạch có thể sai ngữ nghĩa dù qua kiểm tra cấu trúc, nên vẫn kiểm tra toàn bộ program cuối.

Trong cell chạy hiện tại, thêm:

```python
command += ['--three-pass', '--nlp-attempts', '2']
```

Dùng `--output-dir` mới, ví dụ `/kaggle/working/private_three_pass`. Không dùng lại `state.json` của chế độ cũ vì policy đã thay đổi. Các lần chạy tiếp cùng chế độ và thư mục mới sẽ resume. Có thể truyền `--previous-diagnostics` từ lần cũ để cung cấp lỗi trước đó.

`diagnostics.json`/`state.json` lưu thêm `source_selection`: raw output, kế hoạch, lỗi kiểm tra, số token và thời gian. `repair_history` lưu các program/lỗi ở lượt sinh và sửa. Các câu chưa giải quyết vẫn được lưu để retry; không bảo đảm không còn unresolved hoặc accuracy tăng trước khi đo trên public test.
