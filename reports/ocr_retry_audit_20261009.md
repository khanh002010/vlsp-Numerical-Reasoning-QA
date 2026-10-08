# Kiểm tra kết quả OCR cập nhật ngày 2026-10-09

## Lượt mới nhất: 4 ảnh lỗi

Train 1718 ready / 7 error (1 ảnh), public_test 385 ready / 74 error (3 ảnh), pending=0.
Các ảnh: edf4f430, bd062164, 31854725, 9ccd08ec. Raw output phân loại Y là câu
`The vertical Y axis is a numerical scale.` và chọn vùng là `full`, đều có EOS.
Parser JSON tổng quát từ chối các câu trả lời này trước khi nhánh phục hồi sử dụng được.

Bản localized-fields-v4 dùng bộ đọc lựa chọn riêng cho classify_y_axis/locate_coarse_*:
chấp nhận enum JSON, enum văn bản hoặc một số câu khẳng định đầy đủ có nghĩa tương đương.
Không dò keyword trong câu phủ định/mơ hồ, không nhận output bị cắt. Giữ raw output và
parsed_choice trong diagnostics. 116 kiểm thử qua, gồm kiểm thử đường generate với
phản hồi mock trùng raw Kaggle. Chưa chạy GPU lại hoặc thay đổi artifact. Việc sửa parser
không chứng minh bước đọc legend tiếp theo sẽ thành công; vẫn cần retry và kiểm tra kết quả.

## Lượt cập nhật tiếp theo: 6 ảnh lỗi

Kết quả mới: train 1718 ready / 7 error (1 ảnh lỗi), public_test 333 ready / 126 error
(5 ảnh lỗi). Không có pending. Cả sáu dừng tại locator: ba lần tọa độ sai định dạng,
ba lần locator sinh thêm nội dung và chạm giới hạn token. Object tọa độ hợp lệ với
left/top/right/bottom bị code cũ từ chối vì chỉ chấp nhận mảng. Một kết quả còn là
danh sách lồng nhau chứa cả nhãn và tọa độ, không thể coi là một box hợp lệ.

Bản sửa localized-fields-v3 nhận object bốn tọa độ có kiểm tra hình học; locator lỗi
chuyển sang một lượt chọn vùng top/middle/bottom/full hữu hạn. Với lỗi Y, phân loại
trục trong lượt đọc riêng không yêu cầu sinh danh sách nhãn. Chỉ kết quả numerical/none
mới dẫn đến danh sách Y rỗng. Chưa sửa artifact hoặc chạy GPU lại; 111 test CPU/mock qua.

## Lượt trước: 9 ảnh lỗi

Dữ liệu đọc từ `prepared/`, chưa thực hiện OCR GPU lại hoặc sửa artifact.

| Tập | Ready | Error | Ảnh lỗi |
|---|---:|---:|---:|
| train | 1633 | 92 | 4 |
| public_test | 333 | 126 | 5 |

Không còn pending. Chín ảnh lỗi gồm:

| Ảnh | Nguyên nhân quan sát được trong raw generation |
|---|---|
| 91833dc9-7f8c-4480-a38d-e91332c41d97 | Lặp Q1–Q4 hàng trăm lần; ảnh thực tế gồm 16 quý dưới bốn năm 2018–2021 |
| b9dd9800-0e5b-43ca-84d9-955b460f4870 | Đưa chú giải GTGD ròng và % +/- vào Y; focused X còn đọc nhầm VPB thành VTB |
| e0161323-b293-46f5-9037-3a23f8599478 | Gán axis=x cho series của pie |
| edf4f430-e67e-4966-8fc1-2bca5c715aab | Đưa đơn vị % vào danh sách Y |
| 9a3fd5f9-bf4a-4a47-aaba-077cf59cffee | Đưa chú giải Index và % +/- vào Y |
| bd062164-5bd0-43bb-9ee3-15e1b5c6305d | Đưa đơn vị % vào danh sách Y |
| 31854725-508e-4207-a106-f57b3f18334f | Chèn Jan-22 giữa Jan-21 và May-21, rồi lặp Jan-22 |
| 68ba3ef1-119a-4f7e-8651-3d5d9e694c54 | Tự liệt kê ngày lùi và cả ngày vô hiệu; ảnh thực tế nhãn xoay từ 29/7/2022 đến 31/8/2022 |
| 9ccd08ec-17a6-4701-8390-36d04362ed67 | Dịch tên, bịa tiêu đề và lặp series; ảnh thực tế chú giải ở dưới: Ấn Độ, Indonesia, Thái Lan, Việt Nam |

Đã xem trực tiếp ảnh 91833dc9, b9dd9800, 68ba3ef1, 9ccd08ec để đối chiếu.
Các dòng còn lại mô tả đầu ra đã lưu; chưa chứng nhận nội dung OCR đúng ảnh.

Sửa code: chặn chu kỳ nhãn lặp trong generation; axis pie=none; validation từng phần;
phân loại trục Y trước khi chấp nhận danh mục; yêu cầu vị trí vùng từ ảnh và crop lại
một lần khi đọc phần đó thất bại. Lưu prompt, box, lỗi và raw output để truy nguyên.
Giữ lỗi nếu crop vẫn không vượt validation. Không suy ra dữ liệu từ đáp án ground truth.

107 kiểm thử CPU/mock đã qua. Chưa chạy Qwen trên GPU cho chín ảnh này. Schema hợp lệ
không chứng minh độ chính xác nội dung; ví dụ VPB/VTB vẫn có thể cần đối chiếu ảnh.
Dùng lại script `retry_failed_structures` với artifact hiện tại để xử lý chín ảnh lỗi,
sao lưu và cập nhật sau từng ảnh như trước.
