# Rà soát ảnh và ngân sách token OCR — 2026-10-07

## Phạm vi và phương pháp

Đã đọc giải mã toàn bộ 248 PNG (187 train, 61 public_test), thống kê kích thước, SHA-256 và số lần được JSON gọi. Xem trực quan toàn bộ ảnh qua 8 contact sheet; xem thêm ảnh gốc của các biểu đồ dài/phức tạp. Không có file ảnh hỏng, không trùng nội dung nhị phân giữa 248 ảnh, tất cả đều được dataset tham chiếu.

Chưa chạy Qwen2-VL trên GPU cho toàn bộ tập. Không có formatted/output OCR hoặc log token đầy đủ tại workspace trong lần rà soát. Vì vậy không có phân vị token P95/P99 thực đo và không khẳng định tỷ lệ ảnh chắc chắn dưới 8192 token. Số thứ tự trong inventory/contact sheets được sắp theo tên file (train trước public_test), KHÔNG phải ordinal --start-image của formatter.

## Số liệu đo trực tiếp

| Tập | Số ảnh | >750.000 pixel | Budget heuristic 1024 | Budget heuristic 2048 | Budget heuristic 4096 |
|---|---:|---:|---:|---:|---:|
| Train | 187 | 40 | 73 | 114 | 0 |
| Public test | 61 | 17 | 24 | 37 | 0 |
| Tổng | 248 | 57 | 97 | 151 | 0 |

191/248 ảnh (77,0%) không vượt 750k pixel; 57 ảnh còn lại được code resize. Pixel nhỏ nhất 139.258, lớn nhất 1.366.970; trung vị theo phần tử giữa phía trên 494.429. Budget heuristic được tính sau cùng phép resize 750k như pipeline. Đây là output của heuristic mật độ cạnh hiện tại, không phải nhu cầu token được đo hay bảo đảm đủ nội dung.

## Nhận xét trực quan

Ảnh chủ yếu là biểu đồ tài chính đơn lẻ: cột/nhóm cột/cột chồng, đường, tròn, kết hợp nhiều series. Nhiều ảnh chỉ có khoảng vài đến vài chục mốc hoặc danh mục. Không thấy dạng trang scan đầy văn bản hoặc bảng hàng trăm dòng. Tuy nhiên biểu đồ đường dài có thể chứa nhiều điểm hơn số mốc trục được in, nên việc tái tạo toàn bộ chuỗi không có độ dài xác định chỉ từ ảnh.

Ví dụ xem ở kích thước gốc:
- Train `840c962d-2c6f-464f-b471-c9524074cda5.png`: 4 series giá thép, 36 tháng 2022–2024. Bảng rộng theo tháng tiết kiệm token hơn lặp tên series dài ở từng hàng.
- Train `5b6a4ff2-1950-4c49-833d-116d601a2f65.png`: nhiều series với trục thời gian 2018–2023, nhiều giá trị không được in trực tiếp.
- Public `78e21af7-0e0e-4474-94e5-11140ffd27a3.png`: chuỗi P/E nhiều năm và đường trung bình. Cần phân biệt các mốc đọc được và nội suy đường, không dùng số token lớn để ép sinh dữ liệu không quan sát được.
- Train `2b907a99-3cff-4cfd-8e91-28425e81d664.png`: đồ thị nền đen, hai trục, chữ nhỏ. Độ khó đọc số không đồng nghĩa cần output dài hơn.

## Đề xuất (ước lượng, không phải benchmark)

Nếu giữ retry tăng dần: bắt đầu 2048, rồi 4096, rồi 8192. 1024 có thể đủ nhiều biểu đồ đơn giản nhưng tăng khả năng phải sinh lại. 8192 có vẻ dư cho phần lớn nội dung biểu đồ quan sát được nếu xuất Markdown gọn; chưa có bằng chứng cần 16384 làm mặc định toàn tập. Không đặt min_new_tokens=8192: để 0/không ép độ dài tối thiểu. max_new_tokens là trần, EOS cho phép dừng sớm.

Nếu ưu tiên tốc độ hơn cơ chế tăng dần, một lần generate với max_new_tokens=8192 tránh chi phí retry từ đầu, nhưng output lặp/hallucination sẽ chạy lâu hơn nếu không có kiểm soát. Chưa thay cấu hình code trong lần rà soát này.

Ngân sách khởi đầu dự kiến: biểu đồ đơn giản 1024, nhiều series hoặc vài chục mốc 2048, đồ thị dài/dày 4096 và 8192 dự phòng. Không suy ra các mức này trực tiếp từ diện tích ảnh hoặc mật độ cạnh. Hai log người dùng đã cung cấp có 150 và 243 token, chỉ là hai ví dụ, không đại diện toàn tập.

Muốn kết luận định lượng cần lấy token thực sinh + trạng thái EOS + kiểm tra nội dung OCR trên toàn bộ ảnh. Output bị cắt không được coi là độ dài hoàn chỉnh; EOS cũng không chứng minh đầy đủ/chính xác. Khi một output chạm 8192, cần kiểm tra xem bảng có thật sự dài hay bị lặp/sinh thừa trước khi tăng trần.

Lưu ý training hiện mặc định max_seq_length=8192 cho toàn bộ prompt + target. Một ảnh OCR gần 8192 token có thể tự làm mẫu vượt giới hạn training, đặc biệt câu hỏi có nhiều ảnh.

Nguồn về ý nghĩa min/max token và EOS: https://huggingface.co/docs/transformers/main/main_classes/text_generation

Chi tiết từng ảnh: inventory.json. Script tái tạo: audit_images.py. Hình tổng quan: sheet_01.jpg đến sheet_08.jpg.
