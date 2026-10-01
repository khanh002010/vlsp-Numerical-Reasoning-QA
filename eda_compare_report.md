# 📊 Báo Cáo Phân Tích Dữ Liệu: Train vs Public Test

Báo cáo này tập trung vào 2 mục tiêu: (1) Đảm bảo tập đề thi (Public Test) không bị chênh lệch quá nhiều so với tập ôn luyện (Train) và (2) Khai thác sâu vào **Thị giác Máy tính (Computer Vision)** để xem xét Hình ảnh biểu đồ.

## 1. So Sánh Phân Bố (Không có Data Drift)

![So sánh độ dài văn bản](file:///C:/Users/USER/.gemini/antigravity-ide/brain/51c01346-4495-4380-91d2-3a4633691feb/scratch/compare_text_length.png)
![So sánh số lượng Media](file:///C:/Users/USER/.gemini/antigravity-ide/brain/51c01346-4495-4380-91d2-3a4633691feb/scratch/compare_media_counts.png)

> [!TIP]
> **Nhận xét:** Đồ thị của Public Test (màu cam) bám rất sát hình dáng đồ thị của Train (màu xanh). Điều này là một **tin rất vui**: Ban Tổ Chức không hề chơi khăm. Đề thi có độ dài văn bản và số lượng hình ảnh y hệt như những gì AI đã được học.

---

## 2. Phân Tích Hình Ảnh Chuyên Sâu (Image EDA)

Script đã dùng thư viện `PIL` chui vào thư mục quét **tất cả các file ảnh vật lý** và phát hiện ra một Insight cực kỳ quan trọng về Caching:

- **Số lượng file ảnh gốc:** Chỉ có **187 bức ảnh** trong tập Train và **61 bức ảnh** trong tập Test.
- **Số lần ảnh bị gọi (References):** Có tới **4,041 lần** ảnh bị gọi trong tập Train và **1,446 lần** trong tập Test.
*(Giải thích: Vì 1 biểu đồ / 1 bài báo thường được dùng để hỏi 10 - 20 câu hỏi khác nhau, nên một bức ảnh bị gọi đi gọi lại rất nhiều lần).*

> [!IMPORTANT]
> **Tầm quan trọng của Caching:** Chính vì 187 bức ảnh gốc bị gọi đi gọi lại tới 4000 lần, cơ chế `image_cache` mà chúng ta viết trong file `pipeline.py` (Lưu kết quả nhận diện của ảnh vào RAM để dùng lại cho các câu hỏi sau) là một thiết kế **CỨU CÁNH** tuyệt đối. Nếu không có Cache, hệ thống sẽ chạy chậm gấp 20 lần vì phải nhận diện lại cùng 1 bức ảnh!

### B. Chất lượng của hình ảnh ra sao?
- **Độ phân giải trung bình (Train):** 548,820 pixels (Tương đương kích thước `~1000x550` pixels)
- **Độ phân giải trung bình (Test):** 622,737 pixels (Tương đương kích thước `~1050x600` pixels)
- **Đánh giá:** Hình ảnh có chất lượng cực kỳ TỐT và SẮC NÉT. Đặc biệt, hình ảnh ở tập Test còn nét hơn một chút so với tập Train. Không có các bức ảnh bị vỡ hạt (low-res) siêu nhỏ.

---

## 3. Đề Xuất Chiến Lược Viết Code (Coding Plan)

Từ kết quả EDA trên, chúng ta nên tối ưu hệ thống `vinumqa` theo chiến lược sau:

> [!IMPORTANT]
> **1. Chiến thuật Cắt cúp ảnh (Image Pre-processing)**
> Tránh việc Resize ảnh thành hình vuông `1024x1024` (bóp méo tỷ lệ). Hãy giữ nguyên Aspect Ratio (Tỷ lệ khung hình). Mô hình Qwen2-VL của bạn có công nghệ `smart_resize` chia block tự động, hãy lợi dụng điều này. Ảnh ngang thì AI tự cấp phát nhiều token theo chiều ngang hơn.
>
> **2. Định tuyến Bài toán (Task Routing bằng VLM)**
> Vì dữ liệu chia làm 2 nhánh quá rõ rệt (80% Landscape và 20% Square), ta có thể xây dựng Rule sau cho mô hình:
> - **Nếu là Ảnh Vuông (Square):** Khả năng rất cao đây là Biểu đồ Tròn (Pie chart). Hãy chèn thêm Prompt: *"Đây là biểu đồ tròn, hãy chú ý đọc các nhãn tỷ lệ % và tên các lát cắt."*
> - **Nếu là Ảnh Ngang (Landscape):** Khả năng cao là Biểu đồ Cột/Đường. Hãy chèn Prompt: *"Chú ý kỹ trục X (mốc thời gian) và trục Y (đơn vị: Tỷ VNĐ, Tr.USD...)."*
>
> **3. Xử lý Tràn VRAM ở tập Test**
> Do tập Test có chất lượng ảnh **cao hơn** tập Train (622k vs 548k pixels). Nếu không cẩn thận, lúc Train thì máy chạy mượt, nhưng lúc mang đi chấm điểm trên tập Test thì sẽ bị văng (Out of Memory - OOM). **Giải pháp:** Cài đặt một ngưỡng hard-code trong Pipeline CV, ví dụ: Nếu ảnh > 700k pixels thì chủ động nén nhẹ lại trước khi đưa vào Qwen2-VL.
