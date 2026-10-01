# 📊 Báo Cáo Phân Tích Dữ Liệu Khám Phá (EDA) - VLSP 2026 ViTNumChart

Dưới đây là báo cáo phân tích chi tiết được tạo tự động bằng Python dựa trên tệp `train.json`. Báo cáo này giúp chúng ta có cái nhìn tổng quan về khối lượng dữ liệu, cấu trúc văn bản, và độ phức tạp của các công thức toán học (Program DSL).

## 1. Tổng Quan Kích Thước (Overview)
- **Tổng số câu hỏi (Samples):** 1725 câu
- **Độ dài văn bản trung bình:** ~634 từ / 1 câu hỏi
- **Độ dài văn bản lớn nhất (Max):** 2073 từ
- **Số lượng hàm toán học (Operators) độc nhất:** 14 hàm

---

## 2. Phân Bố Độ Dài Văn Bản (Context Length Distribution)
Phân tích này rất quan trọng để thiết lập tham số `max_seq_length` trong quá trình Fine-tuning mô hình ngôn ngữ lớn (LLM).

![Phân bố độ dài văn bản](file:///C:/Users/USER/.gemini/antigravity-ide/brain/51c01346-4495-4380-91d2-3a4633691feb/scratch/text_length.png)

> [!TIP]
> **Nhận xét:** Đa số các đoạn văn bản (context) dài từ 200 đến 800 từ. Khá hiếm câu vượt quá 2000 từ. 
> Do đó, cấu hình `max_seq_length = 2048` hoặc `4096` trong `lora_config.py` là cực kỳ an toàn và tối ưu bộ nhớ VRAM, đảm bảo không có đoạn văn nào bị cắt xén dẫn đến mất dữ kiện.

---

## 3. Khối Lượng Truyền Thông (Media Density - Ảnh & Bảng)
Phân tích xem mỗi câu hỏi đòi hỏi năng lực xử lý thị giác (Vision) và HTML nặng đến mức nào.

![Thống kê Ảnh và Bảng](file:///C:/Users/USER/.gemini/antigravity-ide/brain/51c01346-4495-4380-91d2-3a4633691feb/scratch/media_counts.png)

> [!NOTE]
> **Nhận xét:**
> - **Về Hình ảnh:** Kỷ lục có câu hỏi phải đọc cùng lúc **7 bức ảnh**. Tuy nhiên, đại đa số chỉ rơi vào khoảng từ 1 đến 2 ảnh. Điều này cho thấy tính năng **Caching** ở `CVPipeline` của chúng ta là một bước đi cực kỳ sáng suốt!
> - **Về Bảng HTML:** Mức độ phụ thuộc vào bảng HTML không cao (nhiều nhất là 2 bảng / câu).

---

## 4. Tần Suất Hàm Toán Học (Operators Frequency)
Giúp chúng ta biết mô hình AI sẽ được "học tập" nhiều nhất ở những dạng toán nào.

![Tần suất Toán tử](file:///C:/Users/USER/.gemini/antigravity-ide/brain/51c01346-4495-4380-91d2-3a4633691feb/scratch/operators.png)

> [!IMPORTANT]
> **Nhận xét:** 
> - 3 Hàm cơ bản là `subtract` (trừ), `divide` (chia) và `add` (cộng) áp đảo toàn bộ tập dữ liệu.
> - Hàm `chart_at` (Trích xuất điểm dữ liệu từ biểu đồ) được gọi vô cùng nhiều, cho thấy tính chất VQA đặc thù của cuộc thi.
> - **Rủi ro:** Các hàm như `table_min`, `exp` (mũ) xuất hiện quá ít. AI có thể sẽ rất lúng túng khi gặp các hàm này ở tập Test do thiếu dữ liệu học. Bạn nên cân nhắc viết thêm dữ liệu tự tạo (Data Augmentation) cho các hàm này.

---

## 5. Độ Phức Tạp Của Bước Giải (Reasoning Steps)
Một câu hỏi cần bao nhiêu dòng code để tìm ra đáp án cuối cùng?

![Phân bố số bước giải](file:///C:/Users/USER/.gemini/antigravity-ide/brain/51c01346-4495-4380-91d2-3a4633691feb/scratch/steps_count.png)

> [!NOTE]
> **Nhận xét:** 
> Phần lớn các câu hỏi có độ dài từ **2 đến 5 bước giải**. 
> Tuy nhiên, có những câu phức tạp đỉnh điểm lên tới hơn **15 bước giải** liên tiếp (rất có khả năng là các câu tính tổng chuỗi thời gian nhiều năm). Điều này chứng minh vòng lặp **Reflection Loop** kết hợp với **Symbolic Executor** là bắt buộc phải có, vì AI gần như không thể nhẩm chay đúng một công thức dài 15 bước mà không bị nhầm biến số `#N`.
