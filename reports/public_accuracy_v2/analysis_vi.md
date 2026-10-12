# Đối chiếu public_test và sửa pipeline để cải thiện accuracy

Ngày: 2026-10-12. Đã so toàn bộ 459 QID trong `submit/public_test/results.json` với
`data/public_test/public_test.json`. Không sửa ground truth, kết quả nộp hoặc đưa đáp án
public vào dữ liệu train. Chưa chạy lại model GPU; các số dưới đây là baseline, không phải
accuracy của model sau sửa.

## 1. Kết quả và vị trí lỗi

Metric giữ nguyên `programs_equivalent` của repo: **240/459 = 52,29%**.
Đây là bộ so sánh cục bộ, chưa phải kết quả evaluator chính thức của cuộc thi.
Không thiếu/thừa/trùng QID. Target trong prepared public khớp dữ liệu gốc.

| Nhóm toán tử trong gold | Đúng / tổng | Accuracy |
|---|---:|---:|
| Số học | 115/182 | 63,19% |
| Chart | 78/199 | 39,20% |
| Table | 47/75 | 62,67% |
| Chart + table | 0/3 | 0% |

219 câu không khớp được phân loại không giao nhau:

| Khác biệt | Số câu |
|---|---:|
| Cùng chuỗi toán tử, khác đối số | 112 |
| Khác toán tử hoặc chuỗi bước | 93 |
| Cùng cây phụ thuộc nhưng khác cách viết số/thứ tự khai báo bước | 11 |
| Rỗng hoặc sai cú pháp | 3 |

112/93 là phân loại khác biệt, không phải bằng chứng rằng mỗi câu chỉ có một nguyên nhân.
Chi tiết từng QID, question, gold, prediction, lỗi validator và ảnh liên quan nằm trong
[audit.json](audit.json). Nhóm 11 chỉ là metric chẩn đoán; không tự cộng vào accuracy.

## 2. Những nguyên nhân đã kiểm chứng

### Chọn sai số, nguồn và kỳ

`9ee8c9d7-e6aa-5279-bb41-56adac7b882c` hỏi lợi nhuận gộp/doanh thu 2023.
Gold `divide(370; 532)` nhưng model sinh `divide(532; 657)`: lấy doanh thu hai năm.
Cả ba số đều có trong context nên kiểm tra “số có tồn tại” không bắt được lỗi này.

`9031d0bd-4724-5bb3-a54a-e6da0fbfa9a9` đảo `divide(5800; 1717)` thành
`divide(1717; 5800)`. `ddfd9968-2114-5f51-b8e5-0ec8f99efc74` dùng phép nhân
thay cho lấy tác động tổng trừ tác động trực tiếp. Đây là lỗi hiểu quan hệ và vai trò
đối số; chỉ tăng token hoặc kiểm tra cú pháp không giải quyết được.

### Làm tắt, sai phạm vi và đơn vị

23 câu không khớp mất toàn bộ toán tử chart so với gold; 9 câu mất table.
Đây là dấu hiệu cần xem nguồn từng câu, không tự động kết luận tất cả đều bịa số.
`2481009b-3fef-58e9-86cc-c22eebe6c28f` thay hai `chart_sum` và `add` bằng
`add(19.64; 22.56)`. `bed4e850-a504-5677-9307-184caea40c71` lấy trung bình
một khoảng ngân hàng thay vì đúng ba ngân hàng rời rạc. `0fae53ec-ddac-597f-9286-a186987659dc`
thiếu bước đổi đơn vị nhân 1000.

### OCR có cấu trúc hợp lệ nhưng thiếu thông tin

119/459 gold public không qua kiểm tra gắn nhãn với OCR hiện có, liên quan 36 ảnh.
342/1.725 target train cũng không qua kiểm tra này. Các số này gồm OCR thiếu/sai,
alias và mốc thời gian không in thành tick riêng; **không phải tỷ lệ OCR sai so với ảnh**.
JSON `ready` chỉ xác nhận khả năng dựng mẫu, không chứng minh thông tin khớp pixel.

Đã nhìn trực tiếp bốn ảnh public khó, chép lại nhãn từ pixel:

| Ảnh | Đối chiếu |
|---|---|
| `0059817e-3b8f-4abe-a6ab-149a48319b72.png` | Legend đủ; OCR thiếu cả 6 nhãn X. |
| `78e21af7-0e0e-4474-94e5-11140ffd27a3.png` | Có 4 series, OCR trả 3 và sai tên; bỏ toàn bộ 42 tick X. |
| `8d9fb0be-8aa6-40a3-8c45-9215ac5cdb85.png` | Mất phân biệt các lần tăng giá điện trong cùng năm; tên đầy đủ so với gold viết ngắn là vấn đề alias riêng. |
| `526ab4b8-a979-423f-84c0-997021186e77.png` | Thiếu legend T12/2023 và các nhóm ngành. |

Trên **riêng bốn ảnh được chọn vì có vấn đề**, series precision 7/9 = 77,78%,
recall 7/12 = 58,33%; X-label precision 13/15 = 86,67%, recall 13/84 = 15,48%.
Không ngoại suy thành accuracy toàn bộ ảnh. Chưa chấm các giá trị điểm, đơn vị,
trục trái/phải và thứ tự series. Reference và cách chuẩn hóa nằm trong
[pixel_references.json](pixel_references.json), số liệu ở [ocr_before.json](ocr_before.json).

### Prompt train khác prompt suy luận và lựa chọn checkpoint chưa theo program

Formatter cũ không có source-review guidance và catalog header/row-key mà repair
inference sử dụng. Step 1 chỉ giám sát operator/đối số, chưa chứng minh số ứng với đúng
đại lượng/kỳ. Bản sửa đồng bộ phần hướng dẫn và catalog nguồn ở train/validation/inference,
nhưng không tuyên bố đã có annotation ngữ nghĩa đầy đủ cho mọi số.

Cấu hình cũ warmup 100 trên khoảng 324 optimizer steps (~30,9%). Đây là cấu hình
cần thử nghiệm lại, chưa chứng minh là nguyên nhân riêng gây giảm accuracy.
Trước đây không giữ riêng checkpoint có program accuracy tốt nhất sau mỗi epoch.

### Validator từ chối cả một số gold hợp lệ

Đã sửa trường hợp nguồn ghi `4%` nhưng program dùng `0.04`, tương tự `64%`/`0.64`.
Chỉ cho phép chuyển khi nguồn có dấu `%`; không chia mọi số cho 100.
Replay gold: số câu bị semantic validator cảnh báo giảm **5 xuống 3**.
Ba câu còn lại có literal không xác minh được trong text/table/question; cần rà nguồn
và nhãn gốc, không thêm whitelist lấy từ public ground truth.
Sửa validator không biến prediction cũ thành đúng: baseline vẫn là 240/459.

## 3. Thay đổi đã triển khai

- Cho chọn Qwen2.5-VL-7B, hỗ trợ NF4 trên T4; loader chọn đúng kiến trúc từ config.
  Chế độ `parts` đọc legend/X/Y riêng ngay lần đầu, thay vì chờ JSON tổng thất bại.
  Giữ trần 1.400.000 pixel và tỷ lệ/kích thước riêng của ảnh theo processor.
- Store lưu model, quantization và chế độ đọc; inference mở lại đúng cấu hình.
  Không dùng lẫn kết quả model 2B cũ với store 7B mới.
- Profile `source-review-v1` thống nhất prompt và catalog bảng; chặn trộn profile giữa
  train/valid hoặc âm thầm ghi lại artifact bằng profile khác.
- Giữ program đích và `chart_*`; không thay bằng đáp án số. Thêm augmentation tùy chọn
  đổi Image/Table ID đồng bộ trong context, câu hỏi, chart và target, chỉ áp dụng train.
- Xuất metrics mỗi epoch; giữ adapter `best_program` theo Program Accuracy trên đủ tập valid.
  Có thêm raw-candidate accuracy để thấy candidate đúng bị validator loại.
  Lượt valid dở do hết giờ không thay thế checkpoint tốt nhất.
- Cho cấu hình warmup theo tỷ lệ bước, LR và số epoch; kiểm tra manifest khi resume.
- Thêm công cụ audit toàn bộ lỗi, audit target/OCR và chấm nhãn OCR từ reference pixel.

7B/NF4, warmup và augmentation là phương án cần đo trên dữ liệu này, không phải cam kết
sẽ tăng điểm. Code mới hỗ trợ so sánh có kiểm soát thay vì mặc định model mới luôn tốt hơn.

## 4. Việc phải chạy trên GPU để xác nhận cải thiện

Hướng dẫn và cell chạy: [ACCURACY_RETRAIN.md](../../vinumqa/ACCURACY_RETRAIN.md).
Thử OCR trên bốn ảnh trước, rồi đọc lại train/public vào folder mới. Audit nhãn còn
bất đồng, đo token bằng đúng tokenizer, train adapter mới và valid toàn bộ 459 QID.
Giữ checkpoint/kết quả cũ làm baseline. Không resume optimizer cũ lên dữ liệu/prompt mới.

Máy local hiện chỉ có PyTorch CPU, chưa có PEFT; chưa thể đo accuracy của model sau sửa.
Kiểm thử code không thay thế được việc chạy OCR, training và đánh giá GPU.
