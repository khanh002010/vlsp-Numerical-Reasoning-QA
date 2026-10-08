# Độ dài token cho pipeline training hiện tại

Đã đo toàn bộ 1.725 train + 459 public_test bằng tokenizer Qwen/Qwen2.5-7B-Instruct,
revision `a09a35458c702b33eeacc393d103063234e8bc28`, Transformers 5.19.0.
Ghép prompt/completion đúng như train_qlora.py, gọi encode_supervised thực tế:
không thêm special token tự động, thêm một EOS cho đáp án. Không tải trọng số model.

| Tập | Trung bình | P95 | P99 | Dài nhất | Sau padding bội 8 |
|---|---:|---:|---:|---:|---:|
| Train | 2746,86 | 4192 | 5881 | 6051 | 6056 |
| Public test | 3681,62 | 6451 | 7401 | 7487 | 7488 |

Percentile theo nearest-rank. Số mẫu vượt giới hạn:

| Giới hạn | Train | Public test |
|---|---:|---:|
| 4096 | 111 | 155 |
| 5120 | 26 | 60 |
| 6144 | 0 | 47 |
| 7168 | 0 | 20 |
| 7488 | 0 | 0 |
| 7680 | 0 | 0 |

Tối thiểu để encoder nhận tất cả là 7487; collator pad tối đa thành 7488.
Dùng `--max-seq-length 7680` để có chút dư. 6144 chỉ đủ train, không đủ public validation.
Train hiện dùng chung một giới hạn cho cả hai tập.

Mẫu train dài nhất: `4f4d66ed-e484-53eb-abec-f2bcac77700b`, prompt 5767 + target/EOS 284,
7 ảnh; riêng văn bản cấu trúc ảnh đo độc lập là 1518 token.
Mẫu public dài nhất: `b4825aa5-f9c4-51f7-bc1d-2f643c979577`, prompt 7209 + target/EOS 278,
13 ảnh; riêng văn bản cấu trúc ảnh đo độc lập là 2781 token. Số token thành phần đo riêng
không dùng để cộng lại tổng vì tokenizer có thể ghép khác tại ranh giới.

Đã kiểm tra 248 ảnh được tham chiếu (187 train, 61 public): không thiếu file, không có
hash sai với artifact, Pillow đọc/xác minh file thành công. NLP nhận cấu trúc đã lưu,
không nhận pixel/visual token trực tiếp. Đây không phải kiểm tra chất lượng nội dung OCR.

Giới hạn đủ dữ liệu không đảm bảo đủ VRAM. Collator pad động theo batch (hiện microbatch=1),
không pad mọi mẫu lên max_seq_length. Đổi 8182 thành 7680 không làm ngắn mẫu đã đo,
nên không phải cách khắc phục lỗi OOM tại cross_entropy. Muốn giảm bộ nhớ cần sửa
tính loss/logits hoặc giảm context có kiểm soát, giữ nguyên program mục tiêu.

Chi tiết từng mẫu trong samples.csv, ảnh trong images.csv; summary.json lưu SHA256
hai artifact và revision tokenizer để tái lập kết quả. Chạy lại sau khi thay dữ liệu:

```bash
python -m vinumqa.nlp_module.training.audit_token_lengths --prepared-dir prepared --data-root data
```
