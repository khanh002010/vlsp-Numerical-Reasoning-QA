# Kiểm tra OCR mới và kích thước toàn bộ ảnh — 2026-10-07

## Phạm vi đo

Đọc và giải mã đầy đủ 248 file PNG trong `data/train/train_images` (187 ảnh) và `data/public_test/public_test_images` (61 ảnh). Không có ảnh hỏng, không có tham chiếu ảnh bị thiếu, toàn bộ 248 ảnh đều được JSON tương ứng gọi và có SHA-256 khác nhau. Không thay đổi ảnh gốc hoặc cấu hình pipeline.

`inventory.json` lưu chiều rộng, chiều cao, tổng pixel, megapixel, DPI nếu có, dung lượng file, SHA-256, số lần tham chiếu và kích thước dự kiến ở từng ngưỡng cho mỗi ảnh. Đo pixel bằng chiều rộng × chiều cao; DPI và dung lượng KB không phải số pixel model nhìn thấy. `audit_pixels.py` tái tạo inventory từ file gốc, không chạy OCR.

## Phân bố độ phân giải

| Tập | Số ảnh | Pixel nhỏ nhất | Trung vị | Pixel lớn nhất |
|---|---:|---:|---:|---:|
| Train | 187 | 139.258 | 494.429 | 1.366.970 |
| Public test | 61 | 213.400 | 487.152 | 1.341.900 |
| Tổng | 248 | 139.258 | 492.746,5 | 1.366.970 |

Phân vị theo nearest rank cho cả tập: P75 = 650.691; P90 = 1.059.320; P95 = 1.202.290; P99 = 1.322.896 pixel. Trung vị trong bảng là trung bình hai phần tử giữa vì có 248 ảnh.

| Ngưỡng max_pixels | Ảnh không vượt ngưỡng | Tỷ lệ | Train phải thu nhỏ | Public test phải thu nhỏ | Tổng pixel xử lý so với 750k |
|---|---:|---:|---:|---:|---:|
| 500.000 | 127/248 | 51,21% | 92 | 29 | -15,59% |
| 750.000 | 191/248 | 77,02% | 40 | 17 | Mốc so sánh |
| 1.000.000 | 219/248 | 88,31% | 13 | 16 | +8,10% |
| 1.003.520 | 219/248 | 88,31% | 13 | 16 | +8,19% |
| 1.250.000 | 241/248 | 97,18% | 4 | 3 | +12,13% |
| 1.400.000 | 248/248 | 100% | 0 | 0 | +12,48% |

Các số này mô phỏng phép thu nhỏ giữ tỷ lệ hiện có trong `preprocess_image`; Qwen processor còn có thể làm tròn kích thước. Tổng pixel được cộng một lần cho mỗi ảnh riêng biệt, không nhân với số câu hỏi dùng ảnh. Phần trăm pixel không phải phần trăm thời gian hoặc VRAM: chưa benchmark model trên GPU ở các ngưỡng mới.

Ảnh lớn nhất: train `20089351-ed31-4b96-ac3e-d92e068b2221.png`, 1462 × 935 = 1.366.970 pixel. Ảnh public test lớn nhất: `62b510e5-15c3-4c46-967c-372176b0bd4d.png`, 1350 × 994 = 1.341.900 pixel.

## Khuyến nghị theo mục tiêu giữ chi tiết

Nếu ưu tiên giữ chi tiết gốc để đọc chữ nhỏ, đề xuất thử **max_pixels = 1.400.000**, giữ kích thước riêng của mỗi ảnh và không ép ảnh nhỏ lên mức này. Không ảnh nào trong tập hiện tại bị thu nhỏ chỉ vì vượt ngưỡng đó. Đây là đề xuất từ kích thước đo được, chưa phải ngưỡng đạt độ chính xác/tốc độ tốt nhất đã benchmark.

1.250.000 giữ 97,18% ảnh dưới ngưỡng, nhưng tổng pixel xử lý chỉ thấp hơn ngưỡng 1.400.000 khoảng 0,31%; vì vậy nếu ưu tiên chi tiết gốc, ngưỡng 1.400.000 có cơ sở hơn cho tập này. Nếu ưu tiên tốc độ trên T4, 750.000 vẫn là phương án thử đối chứng, đổi lại 57 ảnh bị giảm kích thước. Một ảnh riêng lẻ lớn nhất có thể tăng khoảng 82% diện tích xử lý khi bỏ cap 750k dù tổng cả tập chỉ tăng 12,48%.

Tăng max_pixels không buộc model sinh nhiều token văn bản. Pixel/visual token là đầu vào ảnh, còn max_new_tokens là trần đầu ra. Tài liệu Qwen minh họa cấu hình 1280 × 28 × 28 = 1.003.520 pixel và lưu ý độ phân giải cao hơn tốn thêm tính toán: https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct#image-resolution-for-performance-boost

## Kết quả OCR vừa tải về

`test ocr/summary.json` xác nhận model `Qwen/Qwen2-VL-2B-Instruct`, OCR version `chart-markdown-v6-guarded-750k`, greedy, cùng ảnh GDP `dcb828d6-2de7-4858-af50-d0f33fcd4ebb.png`. Ảnh gốc 1424 × 929 = 1.322.896 pixel; sau bước resize local còn 1072 × 699 = 749.328 pixel. Chiều rộng và chiều cao còn khoảng 75,2%; diện tích còn 56,6% so với gốc.

Ảnh gốc có 24 quý từ 1Q19 đến 4Q24, chú giải gồm Tăng trưởng GDP và Mức TB trước Covid. Có cột âm gần -5% và đỉnh gần 15%. Model lại sinh hàng theo năm, thêm series sai, và điền ~5.0% vào các cột.

| Trần token | Thời gian (giây) | Hàng dữ liệu gồm hàng cuối bị cắt | Năm cuối tự sinh |
|---|---:|---:|---:|
| 1024 | 60,18 | 36 | 2054 |
| 2048 | 112,69 | 73 | 2091 |
| 4096 | 223,16 | 146 | 2164 |
| 8192 | 507,67 | 292 | 2310 |
| 16384 | 1426,20 | 585 | 2603 |

Cả năm lượt đều eos=false, usable=false và repetition=null. Có nội dung mang hình thức bảng nhưng không phải bảng dữ liệu đáng tin cậy. Guard hiện tại tìm lặp chữ trong từng dòng và bỏ qua chuỗi thuần số để tránh bắt nhầm; mỗi hàng ở đây có năm khác nhau nên guard bỏ sót. Kiểm tra cấu trúc Markdown không kiểm tra tính đúng của số liệu với ảnh. Phát hiện và giới hạn việc tự kéo dài danh mục/thời gian là phần cần cải thiện tiếp; chưa triển khai trong lần rà soát này.

## Có nên bỏ prompt?

Qwen2-VL-2B-Instruct là model sinh văn bản theo chỉ dẫn. Không có chỉ dẫn tác vụ thì không có cơ sở bảo đảm đầu ra là Markdown hoặc đúng dữ liệu biểu đồ. Hướng đối chứng hợp lý hơn là prompt ngắn: "Extract the data in this chart as a Markdown table. Preserve the original labels."

Chưa chạy thử prompt rỗng hoặc prompt ngắn trên GPU, nên chưa kết luận phương án nào chính xác hơn. Trong code hiện tại, truyền `prompt=""` vẫn dùng prompt mặc định do biểu thức `prompt or self.base_prompt`; đó không phải một lần test không prompt thật sự. Markdown có thể biểu diễn nội dung dữ liệu, không giữ nguyên hình dạng/màu sắc/bố cục của biểu đồ như một bản sao ảnh.

Tài liệu gốc mô tả model được instruction-tune và minh họa ảnh kèm text instruction: https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct#quickstart

Để kiểm chứng nguyên nhân: giữ cùng model/ảnh/budget và so sánh prompt hiện tại với prompt ngắn, mỗi prompt ở 750.000 và 1.400.000 pixel. Đánh giá mốc thời gian, series, số hàng, giá trị, trạng thái EOS và thời gian; không chọn kết quả chỉ vì hết lặp hay Markdown hợp lệ.
