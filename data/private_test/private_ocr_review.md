# Private test: danh sách OCR cần sửa

83 ảnh được lọc bằng tên và SHA-256 ảnh gốc, giữ nguyên từng record. 5 ảnh error + 41 ảnh ok có lỗi đã phát hiện = 46 ảnh đọc lại. 37 ảnh ngoài queue giữ nguyên; chưa chứng nhận chính xác từng ký tự.

Danh sách tái sử dụng bằng chứng rà soát toàn bộ trước đó: cấu trúc ok hiện tại và ảnh gốc không đổi. Không có ground truth program private được dùng để sửa ảnh.

## Hướng xử lý

- 37 ảnh có vấn đề tiêu đề: chỉ nhận chữ thực sự in trên ảnh; không tự đặt tiêu đề theo chủ đề. Nhóm này có thể trùng nhóm lỗi khác.
- Nhãn thời gian: đọc nguyên ký tự, vị trí và năm cha; không nhầm 23–26 thành thang số hay 22/2 thành 22/12.
- Series/đơn vị/trục: kiểm kê legend và đường tham chiếu, đọc riêng đơn vị và xác nhận thang trái/phải.
- 5 lỗi pipeline: 2 nguồn series không hợp lệ, 2 thiếu vai trò trục, 1 chưa xác nhận no-legend. Đọc lại vùng tương ứng với reader v4; không bỏ kiểm tra để biến lỗi thành ok.
- Chạy repair_audited với queue này và output mới để buộc đọc lại cả ok sai. Mỗi ảnh xong lưu vào store mới và merged store; source không đổi. Chạy lại cùng cell sẽ bỏ qua ảnh đã đọc lại thành công.
- Reader v4 chưa được kiểm chứng accuracy trên các ảnh này; cần đối chiếu output trước khi đưa vào validation NLP.

## Danh sách đầy đủ 46 ảnh

### 00ff8c6b-9761-5380-85bc-76851b020292.png

Trạng thái cũ: `ok`.
- [P2] title: Tiêu đề OCR không xuất hiện trên ảnh (ví dụ Trend of Economic Growth, Treasury Yield Curve, Time Series, GDP Growth Rate). Hướng sửa: Để title rỗng khi không có tiêu đề in trên ảnh; không tự đặt tên chủ đề.

### 0666db9a-eb16-54f3-ba88-7a7245f9a730.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 18c3c075-e750-5792-817c-45b3289c4031.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 1a4aa378-9797-5a35-8ca2-8fe2f96e3723.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 1dfb709e-aed5-5fdf-a697-fa703b595bd4.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 1ea34911-7a4d-526f-a1b8-fe05058d9d5e.png

Trạng thái cũ: `ok`.
- [P2] title: Tiêu đề OCR không xuất hiện trên ảnh (ví dụ Trend of Economic Growth, Treasury Yield Curve, Time Series, GDP Growth Rate). Hướng sửa: Để title rỗng khi không có tiêu đề in trên ảnh; không tự đặt tên chủ đề.

### 216ce409-b9fc-5a61-b643-bb18fd318c1d.png

Trạng thái cũ: `ok`.
- [P2] title: Chỉ lấy phụ đề Dòng vốn vào cổ phiếu theo thị trường theo tháng; bỏ heading chính phía trên. Hướng sửa: Lưu riêng heading và subtitle, không làm mất heading.

### 24a20439-d303-5cf3-8d22-d2b84b0815af.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 25fc2521-43a0-5232-ad3a-2254cb646dbd.png

Trạng thái cũ: `ok`.
- [P2] title: Chỉ lấy phụ đề Dòng vốn vào cổ phiếu theo thị trường theo tháng; bỏ heading chính phía trên. Hướng sửa: Lưu riêng heading và subtitle, không làm mất heading.

### 3b15ceae-f79f-546e-a743-75037b37298e.png

Trạng thái cũ: `error`.
Lỗi pipeline: `Invalid series_source`.
- [P0] pipeline_error: Invalid series_source Hướng sửa: Đọc lại nguồn tên series; chuẩn hóa enum có kiểm chứng, không biến lỗi enum thành ảnh không đọc được.

### 3b72e65d-e76f-5c50-8aba-79f53139e822.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 3dc5c74e-8b68-59df-8236-1b62c19c4338.png

Trạng thái cũ: `error`.
Lỗi pipeline: `No-legend single-quantity chart has not been confirmed`.
- [P0] pipeline_error: No-legend single-quantity chart has not been confirmed Hướng sửa: Đọc lại legend/heading riêng; không ép chart có legend thành single-series.

### 418403af-683c-58e5-8449-3f7fd6080d96.png

Trạng thái cũ: `error`.
Lỗi pipeline: `Both axis roles must be observed`.
- [P0] pipeline_error: Both axis roles must be observed Hướng sửa: Đọc riêng trục ngang và dọc. Các ảnh này là bar ngang: danh mục/năm ở Y, thang số ở X.

### 4270d95f-80c7-5053-a7ea-a87dc6ad3b85.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 4631ed34-86f2-5d32-a65e-e6d7d5073fb2.png

Trạng thái cũ: `ok`.
- [P1] series: Legend ghi Net % Expecting Stronger Economy (RHS); OCR dùng câu Net % of fund managers expecting a stronger economy (RHS) từ chú thích trên đồ thị. Hướng sửa: Giữ tên legend nguyên bản; tách chú thích mô tả.

### 4b85425f-6df1-5879-8ee6-e931ca10c766.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 4f2a37ed-6a06-586a-9382-0791236b10a0.png

Trạng thái cũ: `ok`.
- [P2] title: Chỉ lấy phụ đề Dòng vốn vào cổ phiếu theo thị trường theo tháng; bỏ heading chính phía trên. Hướng sửa: Lưu riêng heading và subtitle, không làm mất heading.

### 5392064e-44c7-5e8c-9f72-7c1c3ac79d2c.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### 5952a5bf-ed2e-5fc9-8112-825eef6cc97d.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 5a8ae9c2-0995-59f4-81bb-a0635e2cce44.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### 5fb2a577-8af6-50f3-9ec2-314343a0fa48.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 6cab794b-84b1-5538-b87a-435cf95278d5.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 6f376170-1fc2-591a-8f03-74455f01f1b7.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 77cbdf0b-4547-5626-87cc-0e61531da76d.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### 78526d89-01a1-5e62-b74f-5683c0813dbe.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### 7b746361-0d23-5abf-8206-b5f6f9e202df.png

Trạng thái cũ: `ok`.
- [P2] title: Tiêu đề OCR không xuất hiện trên ảnh (ví dụ Trend of Economic Growth, Treasury Yield Curve, Time Series, GDP Growth Rate). Hướng sửa: Để title rỗng khi không có tiêu đề in trên ảnh; không tự đặt tên chủ đề.

### 7f11f93c-3dd9-55ff-aae5-e0221b0a2a19.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 7fba7a8a-86fc-585c-8521-866dd10211a3.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### 84af4e65-bb51-5772-b89d-6ffb23dc7c20.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### 871b2b4c-841f-56eb-91fe-af1128b048d9.png

Trạng thái cũ: `error`.
Lỗi pipeline: `Both axis roles must be observed`.
- [P0] pipeline_error: Both axis roles must be observed Hướng sửa: Đọc riêng trục ngang và dọc. Các ảnh này là bar ngang: danh mục/năm ở Y, thang số ở X.

### 926e2e51-8065-5b07-bc44-664339805903.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### 9a8538f2-9491-5125-852a-1103cdddabba.png

Trạng thái cũ: `ok`.
- [P2] title: Tiêu đề OCR không xuất hiện trên ảnh (ví dụ Trend of Economic Growth, Treasury Yield Curve, Time Series, GDP Growth Rate). Hướng sửa: Để title rỗng khi không có tiêu đề in trên ảnh; không tự đặt tên chủ đề.

### 9ae8a913-bbde-5e80-b7eb-a0141d28f2cd.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### a5606c59-d6db-526a-be03-dee5d3434726.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### a69d19d0-26de-5153-867c-8c892bb0023e.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.

### ac13e759-aac5-5c28-98c4-848876b178b1.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### b198223a-a17b-5457-806d-b30b26b8f67c.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa chú thích sự kiện Đợt 2 kỳ họp Quốc hội thứ 8, khóa XV vào title; đây là annotation có mũi tên. Hướng sửa: Lưu annotation riêng; không coi là tiêu đề biểu đồ.

### b6e10525-24fa-5b36-a87e-b9d0b11bd5be.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### c3a3bd35-a222-5fd4-8f18-31f6d5ea0df6.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

### c55672e9-0c8e-56b6-8da7-1f01eb35a248.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.
- [P0] x_labels/layout: Ảnh có ticks 23, 24, 25, 26 nhưng x_labels=[]; X bị phân loại numerical nên bị bỏ qua. Hướng sửa: Lưu nguyên các ticks 23,24,25,26 và bằng chứng vị trí; không tự thêm thế kỷ từ ảnh.

### cd4ed896-a73b-5014-8e10-f508531c8dc1.png

Trạng thái cũ: `ok`.
- [P2] title: Đưa đơn vị/nhãn trục như (%), Tỷ đồng, Nghìn tỷ VND vào title, dù ảnh không có tiêu đề riêng. Hướng sửa: Tách axis title và unit; title riêng để rỗng.
- [P0] unit/series: Unit của series phải là 1.000,2.000,...5.000: đó là mốc trục, không phải đơn vị; (phải) bị đọc thành (phái). Hướng sửa: Tách numerical ticks khỏi unit; giữ chính xác chữ phải trong legend.

### ce0de681-e1f9-5690-bae6-fbc8f71af898.png

Trạng thái cũ: `error`.
Lỗi pipeline: `Invalid series_source`.
- [P0] pipeline_error: Invalid series_source Hướng sửa: Đọc lại nguồn tên series; chuẩn hóa enum có kiểm chứng, không biến lỗi enum thành ảnh không đọc được.

### d25dc943-70a2-5cdf-a890-0e4decfc7aa6.png

Trạng thái cũ: `ok`.
- [P0] axis: Có series bị gán right dù đồ thị chỉ có thang số bên trái (T12/2023 hoặc Reform Package). Hướng sửa: Đối chiếu vị trí thang số thực tế; không đồng nhất line với right axis.

### d6060652-0ea6-5d64-8d0e-a224e0f07c42.png

Trạng thái cũ: `ok`.
- [P0] x_labels: Ảnh ghi 22/2/19, 22/2/20...; OCR nhiều lần đọc thành 22/12/19, 22/12/20... và có bước 22/12/26 thừa. Hướng sửa: Đọc lại từng nhãn xoay và so thứ tự vị trí; chuỗi từ 22/8/18 đến 22/2/26.

### dcbaab2b-1334-5c7c-81e2-4b5ddab51c7c.png

Trạng thái cũ: `ok`.
- [P1] series: Tên series bị gắn giá trị cuối đường như 32.4%, 19.7%, 17.5%... vào name. Hướng sửa: Giữ raw_text; tách tên và point annotation có tọa độ, không dùng giá trị điểm cuối làm định danh series.

### e6380f47-6ac4-53fe-916a-76e2ccb11b9e.png

Trạng thái cũ: `ok`.
- [P2] title: Title ghép từ legend, nhãn ngày/tháng hoặc mốc trục; không có dòng tiêu đề riêng tương ứng trong ảnh. Hướng sửa: Chỉ nhận heading có vị trí/bằng chứng; giữ legend và ticks ở trường riêng.

