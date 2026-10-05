# Đối chiếu toàn bộ 459 câu của evaluation_report_v3.csv

Các cờ là chẩn đoán tự động, có thể chồng lấp; không phải điểm chính thức. Số thứ tự dòng CSV tính header là dòng 1.
`lookup_omitted_math_only` chỉ xác nhận bỏ lookup so với gold, không khẳng định kết quả số đúng.
`same_math_value_non_exact` chỉ là trùng kết quả của các hằng số, không chứng minh quy trình tương đương.

## Dòng 2 — bed4e850-a504-5677-9307-184caea40c71

Lãi suất cho vay mua nhà sau thời gian ưu đãi trung bình của ba ngân hàng VCB, CTG và Standard Charter là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `add(9; 9); add(#0; 8.8); divide(#1; 3)`
- Model: `table_average(Table 1; Lãi suất cho vay mua nhà; none; 3Q24)`
- #0: operator add -> table_average
- #0 arg0: '9' -> 'Table 1'
- #0 arg1: '9' -> 'Lãi suất cho vay mua nhà'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> '3Q24'
- #1: missing gold step #1: add(#0; 8.8)
- #2: missing gold step #2: divide(#1; 3)

## Dòng 3 — a8849fe2-cc8c-5a24-ae9e-4804fa503b8d

Biên độ chênh lệch giữa mức % thay đổi cao nhất và thấp nhất của nhóm cổ phiếu tác động tiêu cực nhất đến thị trường trong tháng là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 2; % +/-; none; none); chart_min(Image 2; % +/-; none; none); subtract(#0; #1)`
- Model: `subtract(-7; -1)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 2' -> '-7'
- #0 arg1: '% +/-' -> '-1'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 2; % +/-; none; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 4 — e55ef634-b777-5470-9d6a-75fe742d73e3

Tỷ lệ tăng giá kỳ vọng (%) của cổ phiếu IMP từ giá hiện tại ngày 31/1/2024 lên giá mục tiêu 1 năm là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(76000; 61100); divide(#0; 61100); multiply(#1; 100)`
- Model: `subtract(76000; 61000); divide(#0; 61000); multiply(#1; 100)`
- #0 arg1: '61100' -> '61000'
- #1 arg1: '61100' -> '61000'

## Dòng 5 — b36cd841-19f1-544e-b95f-fb0234949122

Trong năm 2024, mức sinh lời của cổ phiếu CTG cao hơn bao nhiêu phần trăm so với chỉ số VNIndex?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(39; 12.1)`
- Model: `divide(39; 12.1)`
- #0: operator subtract -> divide

## Dòng 6 — f1127438-f623-586c-8267-b5fc895a26c7

Tại ngày 9/2/2023, P/E ước tính có cao hơn mức P/E trung bình 5 năm hay không?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 9/2/2023; none); chart_at(Image 1; TB 5 năm; 9/2/2023; none); greater(#0; #1)`
- Model: `chart_average(Image 1; P/E; none; 2023-02-09; 100; none); divide(11.0; #0); subtract(#1; 1)`
- Vi phạm kiểm tra: arity@0:6!=4
- #0: operator chart_at -> chart_average
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #0 arg2: '9/2/2023' -> 'none'
- #0 arg3: 'none' -> '2023-02-09'
- #0 arg4: '<absent>' -> '100'
- #0 arg5: '<absent>' -> 'none'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '11.0'
- #1 arg1: 'TB 5 năm' -> '#0'
- #1 arg2: '9/2/2023' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator greater -> subtract
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '1'

## Dòng 7 — 0d74cdb1-d6f1-556e-b84b-7d1992550266

P/E hiện tại của IMP thấp hơn mức P/E trung bình giai đoạn 2019-2023 bao nhiêu lần?

- Nhãn: both_math_only, invalid_reference, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, strict_invalid
- Ground truth: `subtract(20.08; 16)`
- Model: `divide(#1; #2)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#2
- #0: operator subtract -> divide
- #0 arg0: '20.08' -> '#1'
- #0 arg1: '16' -> '#2'

## Dòng 8 — 0dffe7d8-88e4-5eac-9860-e6371fb7930a

Tại ngày 30/9/2022, nếu lấy điểm số VNIndex trừ đi mức tham chiếu của VNIndex, kết quả chênh lệch là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 30/9/2022; none); chart_at(Image 1; Tham chiếu VNIndex; 30/9/2022; none); subtract(#0; #1)`
- Model: `subtract(250; 1000)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '250'
- #0 arg1: 'VNIndex' -> '1000'
- #0 arg2: '30/9/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Tham chiếu VNIndex; 30/9/2022; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 9 — 0df809eb-c59b-53b9-a8aa-9ea8aa8b7c43

Giá mục tiêu của PVD cao hơn giá hiện tại tại ngày 31/12/2024 bao nhiêu đồng?

- Nhãn: both_math_only, invalid_reference, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, strict_invalid
- Ground truth: `subtract(28700; 23700)`
- Model: `divide(#1; #2)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#2
- #0: operator subtract -> divide
- #0 arg0: '28700' -> '#1'
- #0 arg1: '23700' -> '#2'

## Dòng 10 — 692f4883-1511-547a-8f1c-4c79e0bd3361

Doanh thu của HBC thay đổi bao nhiêu phần trăm từ năm tài chính 2015 sang năm tài chính 2016?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(10766; 5078); divide(#0; 5078); multiply(#1; 100)`
- Model: `divide(112; 100); subtract(#0; 18822)`
- #0: operator subtract -> divide
- #0 arg0: '10766' -> '112'
- #0 arg1: '5078' -> '100'
- #1: operator divide -> subtract
- #1 arg1: '5078' -> '18822'
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 11 — a9b041a5-8d7e-5afc-acd4-fca7247ad068

Theo dự báo mới nhất của OPEC, tăng trưởng nhu cầu dầu toàn cầu năm 2025 thay đổi bao nhiêu triệu thùng/ngày so với năm 2024?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(1.6; 1.61)`
- Model: `subtract(1.6; 1.61)`

## Dòng 12 — cec8dcff-3fa4-5ca6-8e4c-5e0165982140

Chênh lệch tuyệt đối giữa giá mục tiêu và giá hiện tại tại ngày 1/31/2024 của cổ phiếu VCB là bao nhiêu VND?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(104000; 88500)`
- Model: `subtract(1300; 127.8)`
- #0 arg0: '104000' -> '1300'
- #0 arg1: '88500' -> '127.8'

## Dòng 13 — 9ee8c9d7-e6aa-5279-bb41-56adac7b882c

Tỷ lệ giữa lợi nhuận gộp và doanh thu của mảng Thủy điện trong năm 2023 là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(370; 532)`
- Model: `divide(532; 100)`
- #0 arg0: '370' -> '532'
- #0 arg1: '532' -> '100'

## Dòng 14 — ddfd9968-2114-5f51-b8e5-0ec8f99efc74

Khi giá điện tăng 3%, mức tác động gián tiếp làm tăng CPI được ước tính là bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(0.17; 0.105)`
- Model: `multiply(0.4; 0.175)`
- #0: operator subtract -> multiply
- #0 arg0: '0.17' -> '0.4'
- #0 arg1: '0.105' -> '0.175'

## Dòng 15 — 56719970-a89f-5792-9469-3852c782b6c2

Khoảng chênh lệch giữa mức thay đổi cao nhất và thấp nhất của các phân ngành trong giai đoạn điều chỉnh là bao nhiêu phần trăm?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; Điều chỉnh; none; none); table_min(Table 1; Điều chỉnh; none; none); subtract(#0; #1)`
- Model: `chart_max(Table 1; T12; none; none); chart_min(Table 1; T12; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0: operator table_max -> chart_max
- #0 arg1: 'Điều chỉnh' -> 'T12'
- #1: operator table_min -> chart_min
- #1 arg1: 'Điều chỉnh' -> 'T12'

## Dòng 16 — 99c4d9c9-942e-595d-bbe6-a18dfb93d44c

Mức tăng trưởng huy động từ đầu năm trung bình trong quý 1 (từ tháng 1 đến tháng 3) của năm 2022 là bao nhiêu phần trăm?

- Nhãn: invalid_source_type, non_exact, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_average(Image 1; 2022; Jan; Mar)`
- Model: `chart_average(Table 2; Tăng trưởng huy động theo tháng; Jan-Mar 2022; none)`
- Vi phạm kiểm tra: source_type@0:Table 2
- #0 arg0: 'Image 1' -> 'Table 2'
- #0 arg1: '2022' -> 'Tăng trưởng huy động theo tháng'
- #0 arg2: 'Jan' -> 'Jan-Mar 2022'
- #0 arg3: 'Mar' -> 'none'

## Dòng 17 — 9b1dd460-d98c-57c1-a0b2-04824c5c7e8c

Dòng vốn đầu tư vào thị trường US đã thay đổi bao nhiêu phần trăm từ tháng 12/2024 sang tháng 1/2025?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(46495; 68999); divide(#0; 68999); multiply(#1; 100)`
- Model: `subtract(46.5; -45.5); divide(#0; -45.5)`
- #0 arg0: '46495' -> '46.5'
- #0 arg1: '68999' -> '-45.5'
- #1 arg1: '68999' -> '-45.5'
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 18 — c9e613ba-a5b4-5dcc-8843-0cacc7f54311

Mức tăng trưởng huy động từ đầu năm tại thời điểm tháng 12 năm 2023 cao hơn bao nhiêu phần trăm so với tháng 12 năm 2022?

- Nhãn: invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; 2023; Dec; none); chart_at(Image 1; 2022; Dec; none); subtract(#0; #1)`
- Model: `divide(100; 100); subtract(#0; 1); multiply(#1; #2); subtract(#3; 1)`
- Vi phạm kiểm tra: reference@2:#2; reference@3:#3
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '100'
- #0 arg1: '2023' -> '100'
- #0 arg2: 'Dec' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> subtract
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: '2022' -> '1'
- #1 arg2: 'Dec' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '#2'
- #3: extra predicted step #3: subtract(#3; 1)

## Dòng 19 — bb2cfae7-45c4-5402-8c46-e7a1164df2e9

Dựa trên giả định biên lợi nhuận gộp của mảng FMCG và các dự phóng doanh thu năm 2026, lợi nhuận gộp ước tính của mảng FMCG tương đương bao nhiêu phần của tổng lợi nhuận gộp năm 2026 của Nova Consumer?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `multiply(2022; 38); chart_at(Image 1; Doanh thu; 2026; none); chart_at(Image 1; Biên lợi nhuận gộp; 2026; none); multiply(#1; #2); divide(#0; #3)`
- Model: `divide(700; 2200); divide(13.6; 100); multiply(#0; #1); multiply(#2; 100)`
- #0: operator multiply -> divide
- #0 arg0: '2022' -> '700'
- #0 arg1: '38' -> '2200'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '13.6'
- #1 arg1: 'Doanh thu' -> '100'
- #1 arg2: '2026' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator chart_at -> multiply
- #2 arg0: 'Image 1' -> '#0'
- #2 arg1: 'Biên lợi nhuận gộp' -> '#1'
- #2 arg2: '2026' -> '<absent>'
- #2 arg3: 'none' -> '<absent>'
- #3 arg0: '#1' -> '#2'
- #3 arg1: '#2' -> '100'
- #4: missing gold step #4: divide(#0; #3)

## Dòng 20 — fc144adb-28b4-5a18-bd29-7720b4702d70

Nếu lấy trung điểm của vùng mua hợp lý làm giá mua tham chiếu, tiềm năng tăng giá của MWG đến giá mục tiêu cơ bản là bao nhiêu phần trăm?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `add(52.3; 53); divide(#0; 2); subtract(61.5; #1); divide(#2; #1); multiply(#3; 100)`
- Model: `divide(67.5; 100)`
- #0: operator add -> divide
- #0 arg0: '52.3' -> '67.5'
- #0 arg1: '53' -> '100'
- #1: missing gold step #1: divide(#0; 2)
- #2: missing gold step #2: subtract(61.5; #1)
- #3: missing gold step #3: divide(#2; #1)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 21 — 4b5fd7f8-890c-5f01-9873-f61069b70efa

Trong tháng 9/2022, nếu lấy lợi suất trung bình của Tiện ích và Y tế trừ lợi suất của VN-Index thì được bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, invalid_arity, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `table_average(Table 1; Tiện ích; T9/2022; T9/2022); table_average(Table 1; Y tế; T9/2022; T9/2022); add(#0; #1); divide(#2; 2); table_average(Table 1; VN-Index; T9/2022; T9/2022); subtract(#3; #4)`
- Model: `chart_average(Image 1; 9/1/2022; 9/30/2022)`
- Vi phạm kiểm tra: arity@0:3!=4
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Tiện ích' -> '9/1/2022'
- #0 arg2: 'T9/2022' -> '9/30/2022'
- #0 arg3: 'T9/2022' -> '<absent>'
- #1: missing gold step #1: table_average(Table 1; Y tế; T9/2022; T9/2022)
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: divide(#2; 2)
- #4: missing gold step #4: table_average(Table 1; VN-Index; T9/2022; T9/2022)
- #5: missing gold step #5: subtract(#3; #4)

## Dòng 22 — 32f5441b-ff47-5181-bf01-8172989b3a64

Trong nhóm cổ phiếu khuyến nghị tháng 8/2022, chênh lệch giữa mức thay đổi giá hiện tại so với ngày ra báo cáo cao nhất và thấp nhất là bao nhiêu điểm phần trăm?

- Nhãn: missing_source_id, non_exact, same_ops_argument_diff, strict_invalid
- Ground truth: `table_max(Table 1; % thay đổi giá hiện tại so với ngày ra báo cáo; none; none); table_min(Table 1; % thay đổi giá hiện tại so với ngày ra báo cáo; none; none); subtract(#0; #1)`
- Model: `table_max(Table 3; Thay đổi giá hiện tại so với ngày ra báo cáo; none; none); table_min(Table 3; Thay đổi giá hiện tại so với ngày ra báo cáo; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_missing@0:Table 3; source_missing@1:Table 3
- #0 arg0: 'Table 1' -> 'Table 3'
- #0 arg1: '% thay đổi giá hiện tại so với ngày ra báo cáo' -> 'Thay đổi giá hiện tại so với ngày ra báo cáo'
- #1 arg0: 'Table 1' -> 'Table 3'
- #1 arg1: '% thay đổi giá hiện tại so với ngày ra báo cáo' -> 'Thay đổi giá hiện tại so với ngày ra báo cáo'

## Dòng 23 — 01e1e905-4875-5222-aa9f-14dfb117c8e2

Thu nhập lãi thuần (NII) của 9 ngân hàng trong nhóm theo dõi thay đổi bao nhiêu phần trăm từ năm 2019 đến 3Q24 (TTM)?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NII; 2019; none); chart_at(Image 1; NII; 3Q24 (TTM); none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(158; 69); divide(#0; 69); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '158'
- #0 arg1: 'NII' -> '69'
- #0 arg2: '2019' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'NII' -> '69'
- #1 arg2: '3Q24 (TTM)' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 24 — 8a552027-d461-5ec3-97c4-209013720331

Biên độ dao động (chênh lệch giữa mức cao nhất và mức thấp nhất theo tháng) của dòng vốn đầu tư vào thị trường Trung Quốc trong năm 2024 là bao nhiêu?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; China; Jan-24; Dec-24); table_min(Table 1; China; Jan-24; Dec-24); subtract(#0; #1)`
- Model: `chart_max(Table 1; China; none; none); chart_min(Table 1; China; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0: operator table_max -> chart_max
- #0 arg2: 'Jan-24' -> 'none'
- #0 arg3: 'Dec-24' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg2: 'Jan-24' -> 'none'
- #1 arg3: 'Dec-24' -> 'none'

## Dòng 25 — d10f5eb2-3009-5e9d-be8b-554a6ab040f2

Tổng số điểm đóng góp vào chỉ số VNIndex của ba cổ phiếu có tác động tích cực nhất (VCB, BCM và MWG) trong tháng 8 là bao nhiêu?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 3; VNIndex; VCB; none); chart_at(Image 3; VNIndex; BCM; none); chart_at(Image 3; VNIndex; MWG; none); add(#0; #1); add(#3; #2)`
- Model: `add(100; 100); add(#1; 100); add(#2; 100)`
- Vi phạm kiểm tra: reference@1:#1; reference@2:#2
- #0: operator chart_at -> add
- #0 arg0: 'Image 3' -> '100'
- #0 arg1: 'VNIndex' -> '100'
- #0 arg2: 'VCB' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> add
- #1 arg0: 'Image 3' -> '#1'
- #1 arg1: 'VNIndex' -> '100'
- #1 arg2: 'BCM' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator chart_at -> add
- #2 arg0: 'Image 3' -> '#2'
- #2 arg1: 'VNIndex' -> '100'
- #2 arg2: 'MWG' -> '<absent>'
- #2 arg3: 'none' -> '<absent>'
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 26 — 9088b59a-9d69-5606-b27b-bc166d2e2438

Trong ba phiên 24/10/2022, 25/10/2022 và 26/10/2022, VNIndex trung bình thấp hơn mốc tâm lý mà chỉ số đã xuyên thủng bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 24/10/2022; none); chart_at(Image 1; VNIndex; 25/10/2022; none); chart_at(Image 1; VNIndex; 26/10/2022; none); add(#0; #1); add(#3; #2); divide(#4; 3); subtract(1000; #5)`
- Model: `subtract(1000; 1.02794)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1000'
- #0 arg1: 'VNIndex' -> '1.02794'
- #0 arg2: '24/10/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; VNIndex; 25/10/2022; none)
- #2: missing gold step #2: chart_at(Image 1; VNIndex; 26/10/2022; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)
- #5: missing gold step #5: divide(#4; 3)
- #6: missing gold step #6: subtract(1000; #5)

## Dòng 27 — a65347bd-e76f-557c-99d3-c647b5ad8cbd

Mức chênh lệch hệ số P/B giữa hai ngân hàng duy nhất ghi nhận tăng trưởng tích cực về thu nhập thuần từ dịch vụ trong kỳ là bao nhiêu lần?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `subtract(2.7; 1.1)`
- Model: `chart_max(Image 1; none; 100; none); chart_min(Image 1; none; 100; none); subtract(#0; #1)`
- #0: operator subtract -> chart_max
- #0 arg0: '2.7' -> 'Image 1'
- #0 arg1: '1.1' -> 'none'
- #0 arg2: '<absent>' -> '100'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: chart_min(Image 1; none; 100; none)
- #2: extra predicted step #2: subtract(#0; #1)

## Dòng 28 — 769eee4a-8297-5c89-8b97-9d44323ec6bd

Tính đến 31/10/2022, chênh lệch hiệu suất lũy kế giữa VNIndex và DJIA (Mỹ) là bao nhiêu điểm phần trăm?

- Nhãn: invalid_reference, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_at(Image 2; VNIndex; 31/10/2022; none); chart_at(Image 2; DJIA (Mỹ); 31/10/2022; none); subtract(#0; #1)`
- Model: `chart_at(Image 2; VNIndex; 31/10/2022; none); chart_at(Image 2; DJIA (Mỹ); 31/10/2022; none); subtract(#1; #2)`
- Vi phạm kiểm tra: reference@2:#2
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '#2'

## Dòng 29 — 425157f4-3411-5a21-8831-3143e6c15678

Mức chênh lệch giữa giá trị vốn hóa free float cao nhất và thấp nhất trong số các thị trường là bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 1; Free float market cap; none; none); chart_min(Image 1; Free float market cap; none; none); subtract(#0; #1)`
- Model: `subtract(35; 10)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 1' -> '35'
- #0 arg1: 'Free float market cap' -> '10'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 1; Free float market cap; none; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 30 — 0fae53ec-ddac-597f-9286-a186987659dc

Tỷ lệ giữa tổng thu nhập lãi thuần (NII) của nhóm ngân hàng theo dõi trong kỳ 3Q24 (TTM) và vốn hóa thị trường của ngân hàng VCB là bao nhiêu?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `chart_at(Image 1; NII; 3Q24 (TTM); none); multiply(#0; 1000); divide(#1; 495752)`
- Model: `divide(158; 53); divide(390; 100); multiply(#0; #1)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '158'
- #0 arg1: 'NII' -> '53'
- #0 arg2: '3Q24 (TTM)' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator multiply -> divide
- #1 arg0: '#0' -> '390'
- #1 arg1: '1000' -> '100'
- #2: operator divide -> multiply
- #2 arg0: '#1' -> '#0'
- #2 arg1: '495752' -> '#1'

## Dòng 31 — 4609ef0b-bda1-5dcb-ae1f-b1ddb5ef62fb

Tổng sản lượng dự báo từ các lưu vực khí Cửu Long, Nam Côn Sơn 1, Nam Côn Sơn 2 và PM3 trong năm 2026F là bao nhiêu tỷ m3/năm?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 2; Cửu Long; 2026F; none); chart_at(Image 2; Nam Côn Sơn 1; 2026F; none); chart_at(Image 2; Nam Côn Sơn 2; 2026F; none); chart_at(Image 2; PM3; 2026F; none); add(#0; #1); add(#4;#2); add(#5;#3)`
- Model: `table_sum(Table 1; Lưới; none; none)`
- #0: operator chart_at -> table_sum
- #0 arg0: 'Image 2' -> 'Table 1'
- #0 arg1: 'Cửu Long' -> 'Lưới'
- #0 arg2: '2026F' -> 'none'
- #1: missing gold step #1: chart_at(Image 2; Nam Côn Sơn 1; 2026F; none)
- #2: missing gold step #2: chart_at(Image 2; Nam Côn Sơn 2; 2026F; none)
- #3: missing gold step #3: chart_at(Image 2; PM3; 2026F; none)
- #4: missing gold step #4: add(#0; #1)
- #5: missing gold step #5: add(#4; #2)
- #6: missing gold step #6: add(#5; #3)

## Dòng 32 — 27a1ac01-62b5-5982-8469-affdb168bc96

Mức tác động phần trăm trung bình lên LNTT của các ngành Giấy, Thép, Xi măng và Hóa chất là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_average(Image 2; %LNTT; none; none)`
- Model: `table_average(Table 1; LNTT; none; none)`
- #0: operator chart_average -> table_average
- #0 arg0: 'Image 2' -> 'Table 1'
- #0 arg1: '%LNTT' -> 'LNTT'

## Dòng 33 — d137719c-8207-5970-8d7b-a051cba55d66

Mức diễn biến cao nhất mà chỉ số VNIndex đạt được trong chu kỳ năm 2023 là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; VNIndex; none; none)`
- Model: `chart_max(Image 1; VNIndex; none; Dec-22; Nov-23)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0 arg3: 'none' -> 'Dec-22'
- #0 arg4: '<absent>' -> 'Nov-23'

## Dòng 34 — 2481009b-3fef-58e9-86cc-c22eebe6c28f

Tổng tỷ lệ sở hữu của Hyundai Elevator Co., Ltd và Quỹ KIM là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_sum(Image 1; Hyundai Elevator Co., Ltd; none; none); chart_sum(Image 1; Quỹ KIM; none; none); add(#0; #1)`
- Model: `add(11; 5)`
- #0: operator chart_sum -> add
- #0 arg0: 'Image 1' -> '11'
- #0 arg1: 'Hyundai Elevator Co., Ltd' -> '5'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_sum(Image 1; Quỹ KIM; none; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 35 — d84447ce-43ac-565f-ba8a-0c0a5fef785b

Trong năm 2023, nhóm cổ phiếu ngành Y Tế vượt VNIndex bao nhiêu điểm phần trăm về mức tăng?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(29; 12)`
- Model: `subtract(29; 12)`

## Dòng 36 — af418e60-8643-5f92-b870-382f860f6326

Trung bình tỷ lệ thay đổi giá tại ngày 06/09/2022 so với ngày ra báo cáo 05/08/2022 của toàn bộ các cổ phiếu khuyến nghị là bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_average(Table 1; % thay đổi giá hiện tại so với ngày ra báo cáo; BCM; NLG)`
- Model: `table_average(Table 2; Tỷ lệ thay đổi giá tại ngày 06/09/2022; none; Tỷ lệ thay đổi giá tại ngày ra báo cáo 05/08/2022)`
- #0 arg0: 'Table 1' -> 'Table 2'
- #0 arg1: '% thay đổi giá hiện tại so với ngày ra báo cáo' -> 'Tỷ lệ thay đổi giá tại ngày 06/09/2022'
- #0 arg2: 'BCM' -> 'none'
- #0 arg3: 'NLG' -> 'Tỷ lệ thay đổi giá tại ngày ra báo cáo 05/08/2022'

## Dòng 37 — 18ac0acb-1795-5522-a13a-aa1c3eb4a43b

Trong kỳ theo dõi, giá cao nhất của cổ phiếu BCM có vượt mức giá PTKT của mã này không?

- Nhãn: invalid_source_type, lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `greater(92000; 85000)`
- Model: `chart_max(Table 2; BCM; none; none); greater(#0; 100)`
- Vi phạm kiểm tra: source_type@0:Table 2
- #0: operator greater -> chart_max
- #0 arg0: '92000' -> 'Table 2'
- #0 arg1: '85000' -> 'BCM'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: greater(#0; 100)

## Dòng 38 — 76e56e04-9a67-5b48-b050-ff4c74edf2c4

Biên độ dòng vốn đầu tư hàng tháng vào Việt Nam trong giai đoạn từ Jan-24 đến Jan-25 là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Vietnam; Jan-24; Jan-25); table_min(Table 1; Vietnam; Jan-24; Jan-25); subtract(#0; #1)`
- Model: `table_max(Table 1; Jan-24; none; none); table_min(Table 1; Jan-25; none; none); subtract(#0; #1)`
- #0 arg1: 'Vietnam' -> 'Jan-24'
- #0 arg2: 'Jan-24' -> 'none'
- #0 arg3: 'Jan-25' -> 'none'
- #1 arg1: 'Vietnam' -> 'Jan-25'
- #1 arg2: 'Jan-24' -> 'none'
- #1 arg3: 'Jan-25' -> 'none'

## Dòng 39 — e3a52ab6-f4ab-5268-b3ea-6e8e2aa283c1

Lãi suất cho vay mua nhà của CTG sau thời gian ưu đãi gấp bao nhiêu lần lãi suất ưu đãi cho kỳ hạn 12 tháng?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(9; 6)`
- Model: `divide(10.1; 9.7)`
- #0 arg0: '9' -> '10.1'
- #0 arg1: '6' -> '9.7'

## Dòng 40 — de61aa84-1fe9-5c76-b929-32ba356d7f17

Dựa vào các dự phóng về lợi nhuận ròng, tỷ suất sinh lời trên vốn chủ sở hữu (ROE) và tỷ lệ nợ trên vốn chủ sở hữu, mức tổng nợ dự kiến của Nova Consumer vào năm 2025 là bao nhiêu tỷ đồng?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 3; Lợi nhuận ròng; 2025; none); chart_at(Image 2; ROE; 2025; none); divide(#1; 100); divide(#0; #2); chart_at(Image 4; Nợ/ Vốn chủ sở hữu; 2025; none); multiply(#3; #4)`
- Model: `divide(904.2; 100); multiply(#0; 13.1); divide(#1; 100); multiply(#2; #3)`
- Vi phạm kiểm tra: reference@3:#3
- #0: operator chart_at -> divide
- #0 arg0: 'Image 3' -> '904.2'
- #0 arg1: 'Lợi nhuận ròng' -> '100'
- #0 arg2: '2025' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> multiply
- #1 arg0: 'Image 2' -> '#0'
- #1 arg1: 'ROE' -> '13.1'
- #1 arg2: '2025' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #3: operator divide -> multiply
- #3 arg0: '#0' -> '#2'
- #3 arg1: '#2' -> '#3'
- #4: missing gold step #4: chart_at(Image 4; Nợ/ Vốn chủ sở hữu; 2025; none)
- #5: missing gold step #5: multiply(#3; #4)

## Dòng 41 — 8233c19c-097f-58cd-9e63-c1ab4b5ba5a9

Trong tháng 1/2025, dòng vốn đầu tư vào Trung Quốc có cao hơn Đài Loan không?

- Nhãn: both_math_only, invalid_arity, invalid_math_argument, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `greater(3.444; 1.958)`
- Model: `greater(Table 1#Jan-25#China#Taiwan; none; none)`
- Vi phạm kiểm tra: arity@0:3!=2; math_type@0:Table 1#Jan-25#China#Taiwan; math_type@0:none
- #0 arg0: '3.444' -> 'Table 1#Jan-25#China#Taiwan'
- #0 arg1: '1.958' -> 'none'
- #0 arg2: '<absent>' -> 'none'

## Dòng 42 — 260c3976-4957-51fb-8cf4-361367bc00b1

Mức chênh lệch giữa dự báo của OPEC và IEA về tăng trưởng nhu cầu dầu toàn cầu trong năm 2025 là bao nhiêu triệu thùng/ngày?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(1.6; 1.1)`
- Model: `subtract(1.6; 1.1)`

## Dòng 43 — ba5c818c-b578-5c3f-9c61-f188a3f48a12

Tổng dòng vốn đầu tư vào Trung Quốc và Đài Loan trong tháng 1/2025 là bao nhiêu?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `add(3444; 1958)`
- Model: `table_sum(Table 1; Trung Quốc; Jan-25; none; Đài Loan)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator add -> table_sum
- #0 arg0: '3444' -> 'Table 1'
- #0 arg1: '1958' -> 'Trung Quốc'
- #0 arg2: '<absent>' -> 'Jan-25'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> 'Đài Loan'

## Dòng 44 — 5c18faa5-9796-5d39-a85b-70630e533f46

Chênh lệch giữa tỷ lệ tăng trưởng lợi nhuận ròng và tỷ lệ tăng trưởng NPATMI dự phóng năm 2024 của IMP là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(14.5; 14.4)`
- Model: `subtract(14.4; 6)`
- #0 arg0: '14.5' -> '14.4'
- #0 arg1: '14.4' -> '6'

## Dòng 45 — 651d2f9e-184d-5d62-9cf1-f694a3a694bd

Chênh lệch giữa cận trên và cận dưới của vùng mua hợp lý khuyến nghị cho CII là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(22; 21.5)`
- Model: `subtract(1.180; 1.140)`
- #0 arg0: '22' -> '1.180'
- #0 arg1: '21.5' -> '1.140'

## Dòng 46 — b5005882-dc9e-54c6-b7ea-5a2130f78832

Chênh lệch giữa P/E dự phóng hiện nay của ngành dầu khí và mức trung bình 5 năm, tính theo P/E hiện nay trừ P/E trung bình 5 năm, là bao nhiêu lần?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(12.5; 13.5)`
- Model: `subtract(12.5; 13.5)`

## Dòng 47 — 212fc8b8-f141-5492-b6e6-b9d5dd8bb114

Mức thay đổi của hiệu suất lũy kế S&P 500 (Mỹ) từ 30/9/2022 đến 31/10/2022 là bao nhiêu điểm phần trăm?

- Nhãn: exact, repo_equivalent
- Ground truth: `chart_at(Image 2; S&P 500 (Mỹ); 30/9/2022; none); chart_at(Image 2; S&P 500 (Mỹ); 31/10/2022; none); subtract(#1; #0)`
- Model: `chart_at(Image 2; S&P 500 (Mỹ); 30/9/2022; none); chart_at(Image 2; S&P 500 (Mỹ); 31/10/2022; none); subtract(#1; #0)`

## Dòng 48 — 75942c41-9dfa-5dde-9606-65f893287648

Trong Q124, mảng Xây dựng mang lại doanh thu tuyệt đối là bao nhiêu tỷ đồng cho công ty?

- Nhãn: both_math_only, non_exact, pred_math_only, same_math_value_non_exact, same_ops_argument_diff
- Ground truth: `divide(64; 100); multiply(425; #0)`
- Model: `divide(425; 100); multiply(#0; 64)`
- #0 arg0: '64' -> '425'
- #1 arg0: '425' -> '#0'
- #1 arg1: '#0' -> '64'

## Dòng 49 — 8e576d65-e368-5424-8c4b-17786acd1154

Giá cổ phiếu FPT đã thay đổi bao nhiêu phần trăm từ ngày 05/08/2022 đến ngày 06/09/2022?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `subtract(85800; 84813); divide(#0; 84813); multiply(#1; 100)`
- Model: `chart_at(Image 1; FPT; none; 05/08/2022; none); chart_at(Image 1; FPT; none; 06/09/2022; none); divide(#1; #0); subtract(#2; 100); multiply(#3; 100)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0: operator subtract -> chart_at
- #0 arg0: '85800' -> 'Image 1'
- #0 arg1: '84813' -> 'FPT'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> '05/08/2022'
- #0 arg4: '<absent>' -> 'none'
- #1: operator divide -> chart_at
- #1 arg0: '#0' -> 'Image 1'
- #1 arg1: '84813' -> 'FPT'
- #1 arg2: '<absent>' -> 'none'
- #1 arg3: '<absent>' -> '06/09/2022'
- #1 arg4: '<absent>' -> 'none'
- #2: operator multiply -> divide
- #2 arg1: '100' -> '#0'
- #3: extra predicted step #3: subtract(#2; 100)
- #4: extra predicted step #4: multiply(#3; 100)

## Dòng 50 — c3ee700f-5906-5eb6-9ed3-4294e4a1deb4

Tỷ lệ giữa tổng dự phòng so với quy mô nợ xấu và nợ tái cơ cấu của ngân hàng VPB là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 11; Tổng dự phòng; VPB; none); chart_at(Image 11; Nợ xấu, nợ tái cơ cấu; VPB; none); divide(#0; #1)`
- Model: `divide(100; 1.5)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 11' -> '100'
- #0 arg1: 'Tổng dự phòng' -> '1.5'
- #0 arg2: 'VPB' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 11; Nợ xấu, nợ tái cơ cấu; VPB; none)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 51 — c452a6f2-747d-575a-a654-e6e1a0f68509

P/E dự phóng 2024 của ngành Công nghệ Thông tin bằng bao nhiêu lần mức P/E dự phóng 2024 của Tổng/ Trung bình?

- Nhãn: both_math_only, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `divide(15.4; 10.6)`
- Model: `divide(#1; #0)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#0
- #0 arg0: '15.4' -> '#1'
- #0 arg1: '10.6' -> '#0'

## Dòng 52 — f95efc97-8871-5161-a8c7-d5e28f255df7

Giá mục tiêu 1 năm của cổ phiếu FPT có cao hơn giá mục tiêu 1 năm của cổ phiếu VCB hay không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `greater(109200; 104000)`
- Model: `chart_at(Image 1; Giá mục tiêu 1 năm; FPT; none); chart_at(Image 1; Giá mục tiêu 1 năm; VCB; none); greater(#0; #1)`
- #0: operator greater -> chart_at
- #0 arg0: '109200' -> 'Image 1'
- #0 arg1: '104000' -> 'Giá mục tiêu 1 năm'
- #0 arg2: '<absent>' -> 'FPT'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: chart_at(Image 1; Giá mục tiêu 1 năm; VCB; none)
- #2: extra predicted step #2: greater(#0; #1)

## Dòng 53 — 1ad3c036-bb48-5028-ba6c-18652f00d5e4

Mức sinh lời của nhóm Y Tế vào tháng 11/2023 thay đổi bao nhiêu điểm phần trăm so với tháng 7/2023?

- Nhãn: invalid_math_argument, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, strict_invalid
- Ground truth: `chart_at(Image 1; Nhóm Y Tế; Jul-23; none); chart_at(Image 1; Nhóm Y Tế; Nov-23; none); subtract(#1; #0)`
- Model: `subtract(100; none); divide(#0; none); multiply(#1; 100)`
- Vi phạm kiểm tra: math_type@0:none; math_type@1:none
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '100'
- #0 arg1: 'Nhóm Y Tế' -> 'none'
- #0 arg2: 'Jul-23' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Nhóm Y Tế' -> 'none'
- #1 arg2: 'Nov-23' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'

## Dòng 54 — 1c9490f5-d4fc-508c-afd4-4eadd8930650

Trong tháng 1/2025, tổng dòng vốn đầu tư vào các tài sản tài chính gồm cổ phiếu, trái phiếu và tiền tệ là bao nhiêu tỷ USD?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_total(Image 1; Jan-25; none; none)`
- Model: `divide(86; 100); add(#0; 67.2); add(#1; 64.7)`
- #0: operator chart_total -> divide
- #0 arg0: 'Image 1' -> '86'
- #0 arg1: 'Jan-25' -> '100'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: extra predicted step #1: add(#0; 67.2)
- #2: extra predicted step #2: add(#1; 64.7)

## Dòng 55 — fd842717-8f50-5c7a-bbbb-6e2eeb3b4f32

Vào tháng 11 năm 2024, mức chênh lệch giữa chỉ số của FPT VN và chỉ số VN-Index là bao nhiêu phần trăm?

- Nhãn: invalid_reference, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; FPT VN; Nov 24; none); chart_at(Image 1; VN-Index; Nov 24; none); subtract(#0; #1)`
- Model: `chart_at(Image 1; VN-Index; Nov 24; none); chart_at(Image 1; FPT VN; Nov 24; none); subtract(#1; #2); divide(#3; #2); multiply(#4; 100)`
- Vi phạm kiểm tra: reference@2:#2; reference@3:#3; reference@4:#4
- #0 arg1: 'FPT VN' -> 'VN-Index'
- #1 arg1: 'VN-Index' -> 'FPT VN'
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '#2'
- #3: extra predicted step #3: divide(#3; #2)
- #4: extra predicted step #4: multiply(#4; 100)

## Dòng 56 — 23ed2a6a-cd30-5a3a-ab11-f51f9e8e9653

Trong giai đoạn 6 tháng (6M), mức chênh lệch giữa thay đổi giá cổ phiếu tuyệt đối và tương đối là bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, invalid_source_type, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `subtract(32.5; 24.1)`
- Model: `chart_average(Table 1; 6M; Change in price; none; none)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 1
- #0: operator subtract -> chart_average
- #0 arg0: '32.5' -> 'Table 1'
- #0 arg1: '24.1' -> '6M'
- #0 arg2: '<absent>' -> 'Change in price'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> 'none'

## Dòng 57 — 850ad259-bf30-5f17-9316-2adb3c7888cd

ROE bình quân của HBC trong ba năm tài chính 2017, 2018 và 2019 là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 1; ROE (%); FY 2017; FY2019)`
- Model: `chart_average(Image 1; ROE (LHS); 2017; 2019)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'ROE (%)' -> 'ROE (LHS)'
- #0 arg2: 'FY 2017' -> '2017'
- #0 arg3: 'FY2019' -> '2019'

## Dòng 58 — 6f6b25cd-4e55-5356-8ba5-331012f6f130

Đối với DPG, hệ số P/E forward năm 2024 hàm ý khi lấy mức giá mục tiêu được nâng lên chia cho EPS dự phóng 2024 là bao nhiêu lần?

- Nhãn: both_math_only, non_exact, pred_math_only, same_math_value_non_exact, same_ops_argument_diff
- Ground truth: `divide(52102; 3351)`
- Model: `divide(52.102; 3.351)`
- #0 arg0: '52102' -> '52.102'
- #0 arg1: '3351' -> '3.351'

## Dòng 59 — 747ede2a-9e1d-5aa6-a055-79d4db280cd1

Tổng giá trị dòng tiền vào ròng của Quỹ cổ phiếu toàn cầu và Quỹ thị trường tiền tệ trong tháng 1 đạt bao nhiêu tỷ USD?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `add(64.7; 86)`
- Model: `add(64.7; 86)`

## Dòng 60 — b998db1a-0f39-5b70-aa2f-3d179c7b3d60

Chênh lệch giữa P/E 2025F trung bình của GAS, PVS, PVD, PLX và BSR với P/E dự phóng hiện nay của ngành dầu khí là bao nhiêu lần?

- Nhãn: invalid_reference, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_average(Table 1; P/E@2025F; GAS; BSR); subtract(#0; 12.5)`
- Model: `table_average(Table 1; P/E 2025F; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: reference@1:#1
- #0 arg1: 'P/E@2025F' -> 'P/E 2025F'
- #0 arg2: 'GAS' -> 'none'
- #0 arg3: 'BSR' -> 'none'
- #1 arg1: '12.5' -> '#1'

## Dòng 61 — 42523de0-d558-5aba-a87c-21a24feb9939

Giá mục tiêu của DPG đã được điều chỉnh tăng bao nhiêu phần trăm so với mức giá mục tiêu trước đó?

- Nhãn: both_math_only, non_exact, pred_math_only, same_math_value_non_exact, same_ops_argument_diff
- Ground truth: `subtract(52102; 44733); divide(#0; 44733); multiply(#1; 100)`
- Model: `subtract(52.102; 44.733); divide(#0; 44.733); multiply(#1; 100)`
- #0 arg0: '52102' -> '52.102'
- #0 arg1: '44733' -> '44.733'
- #1 arg1: '44733' -> '44.733'

## Dòng 62 — 3969e23b-bc01-5b42-bfc2-dfe0c1888b8b

Giá trị giao dịch ròng của khối ngoại đối với cổ phiếu DGC trong năm 2023, nếu loại trừ tháng 10, là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; 2023; DGC; none); chart_at(Image 3; T10/2023; DGC; none); subtract(#0; #1)`
- Model: `subtract(300; 500)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 3' -> '300'
- #0 arg1: '2023' -> '500'
- #0 arg2: 'DGC' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; T10/2023; DGC; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 63 — f9be0492-5c5f-597f-a224-12e04f0f81cc

Mức đóng góp điểm trung bình vào VNIndex của nhóm cổ phiếu tạo tác động tích cực mạnh nhất lên thị trường trong tháng 8 là bao nhiêu điểm?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_average(Image 3; VNIndex; none; none)`
- Model: `divide(1280.51; 1206.33); multiply(#0; 6.15)`
- #0: operator chart_average -> divide
- #0 arg0: 'Image 3' -> '1280.51'
- #0 arg1: 'VNIndex' -> '1206.33'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: extra predicted step #1: multiply(#0; 6.15)

## Dòng 64 — b322a100-8e2d-5af8-8610-1a43b57b9674

Mức giá trị bán ra hàng tuần cao nhất của nhà đầu tư nước ngoài (NĐTNN Bán) trong tháng 9 là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 5; NĐTNN Bán; 9/5; 9/26)`
- Model: `chart_max(Image 6; GTGD ròng NĐTNN; none; none)`
- #0 arg0: 'Image 5' -> 'Image 6'
- #0 arg1: 'NĐTNN Bán' -> 'GTGD ròng NĐTNN'
- #0 arg2: '9/5' -> 'none'
- #0 arg3: '9/26' -> 'none'

## Dòng 65 — 3e804f1a-dbe8-5ca2-a9d8-f7db1645aa83

Dựa vào các dự phóng, lợi nhuận gộp của mảng kinh doanh FMCG dự kiến chiếm tỷ trọng bao nhiêu trong tổng lợi nhuận gộp của toàn bộ doanh nghiệp vào năm 2026?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(38; 100); multiply(2022; #0); chart_at(Image 1; Biên lợi nhuận gộp; 2026; none); divide(#2; 100); multiply(17133.3; #3); divide(#1; #4)`
- Model: `divide(2000; 1000); divide(1200; 1.1); add(#0; #1)`
- #0 arg0: '38' -> '2000'
- #0 arg1: '100' -> '1000'
- #1: operator multiply -> divide
- #1 arg0: '2022' -> '1200'
- #1 arg1: '#0' -> '1.1'
- #2: operator chart_at -> add
- #2 arg0: 'Image 1' -> '#0'
- #2 arg1: 'Biên lợi nhuận gộp' -> '#1'
- #2 arg2: '2026' -> '<absent>'
- #2 arg3: 'none' -> '<absent>'
- #3: missing gold step #3: divide(#2; 100)
- #4: missing gold step #4: multiply(17133.3; #3)
- #5: missing gold step #5: divide(#1; #4)

## Dòng 66 — 5f4713b5-bb6a-5b16-addf-2fafc4b1ef3f

Tính đến tháng 11/2024, lãi suất ưu đãi cho vay mua nhà kỳ hạn 12 tháng của VPB có cao hơn của CTG không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff
- Ground truth: `greater(7.2; 6.0)`
- Model: `table_max(Table 1; VPB; Nov-24; CTG)`
- #0: operator greater -> table_max
- #0 arg0: '7.2' -> 'Table 1'
- #0 arg1: '6.0' -> 'VPB'
- #0 arg2: '<absent>' -> 'Nov-24'
- #0 arg3: '<absent>' -> 'CTG'

## Dòng 67 — 1be02ac8-8f77-56b4-a7d9-5de24c4ff081

Suất sinh lợi theo tháng của ngành Năng lượng đã thay đổi bao nhiêu điểm phần trăm từ tháng 8/2022 sang tháng 9/2022?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(-12.3; 15.5)`
- Model: `subtract(-12.3; -12.3)`
- #0 arg1: '15.5' -> '-12.3'

## Dòng 68 — 78e89c74-e725-5196-9a0e-54586f83ad40

Sự chênh lệch của P/E ước tính cho năm tài chính hiện tại giữa thời điểm 1/2/2020 và 5/2/2020 là bao nhiêu?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2020; none); chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 5/2/2020; none); subtract(#0; #1)`
- Model: `subtract(#1; #2)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#2
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '#1'
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> '#2'
- #0 arg2: '1/2/2020' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 5/2/2020; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 69 — cb3871b3-a0a2-5a0a-b1c3-189e8a0956c0

Trong giai đoạn từ tháng 1/2020 đến tháng 1/2025, lượng vốn lũy kế cao nhất chảy vào các quỹ cổ phiếu của thị trường Việt Nam là bao nhiêu tỷ USD?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_max(Image 3; Việt Nam; Jan-20; Jan-25)`
- Model: `table_sum(Table 1; Việt Nam; Jan-20; Jan-25)`
- #0: operator chart_max -> table_sum
- #0 arg0: 'Image 3' -> 'Table 1'

## Dòng 70 — 506a3d61-3cc3-57e6-86a1-d83411abe879

Trong tháng 1/2025, dòng vốn vào thị trường Mỹ chiếm bao nhiêu phần của tổng dòng vốn vào quỹ cổ phiếu thị trường phát triển (DM)?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; Phát triển (DM); Jan-25; none); divide(46.495; #0)`
- Model: `divide(46.5; 3)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '46.5'
- #0 arg1: 'Phát triển (DM)' -> '3'
- #0 arg2: 'Jan-25' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: divide(46.495; #0)

## Dòng 71 — bd34fd01-9f9a-5a5f-9461-0da564ef493c

Mức giá trung bình của vùng cắt lỗ đối với các mã cổ phiếu được khuyến nghị là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_average(Table 1; Vùng cắt lỗ; none; none)`
- Model: `table_average(Table 1; Tỷ lệ giữa mức giá hiện tại và mức giá hợp lý; none; none)`
- #0 arg1: 'Vùng cắt lỗ' -> 'Tỷ lệ giữa mức giá hiện tại và mức giá hợp lý'

## Dòng 72 — 7d48988e-48d6-55fb-97e1-580e9575fdbd

Trong năm 2023, lợi nhuận gộp của mảng Thủy điện đã sụt giảm một lượng tuyệt đối là bao nhiêu so với năm trước?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(503; 370)`
- Model: `subtract(503; 657)`
- #0 arg1: '370' -> '657'

## Dòng 73 — e28cfc75-fbcd-5011-b7cf-ff3ee43dcbd4

P/E ước tính cho năm tài chính hiện tại đã thay đổi bao nhiêu phần trăm từ ngày 1/2/2022 đến 9/2/2023?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2022; none); chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 9/2/2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 1; P/E; Jan-22; none); chart_at(Image 1; P/E; Sep-23; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #0 arg2: '1/2/2022' -> 'Jan-22'
- #1 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #1 arg2: '9/2/2023' -> 'Sep-23'

## Dòng 74 — 56ff49bd-8f8f-5c14-8d0e-c9cde7ad527b

Mức đóng góp doanh thu hằng năm tối đa được dự báo cho mảng FMCG cao hơn doanh thu năm 2025 của Công ty FMCG bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(2200; 2185)`
- Model: `subtract(2200; 1786)`
- #0 arg1: '2185' -> '1786'

## Dòng 75 — f39ab262-420c-5910-bcf7-3be4918f35df

Dựa vào mức vốn hóa của HBC tại ngày 15/06/2020 và tỷ lệ tương đương của mức vốn hóa này so với tài sản còn lại, tổng giá trị tài sản còn lại của doanh nghiệp được ước tính là bao nhiêu tỷ đồng?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(2893; 65); multiply(#0; 100)`
- Model: `divide(2893; 65)`
- #1: missing gold step #1: multiply(#0; 100)

## Dòng 76 — bcedd388-55fb-5f81-a4bd-1d6969757b05

Đối với BID, tỷ lệ LLR gấp bao nhiêu lần tỷ lệ NPL?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(180.9; 1.3)`
- Model: `divide(1.5; 0.5)`
- #0 arg0: '180.9' -> '1.5'
- #0 arg1: '1.3' -> '0.5'

## Dòng 77 — 0479a43e-f63c-59d3-8157-0b89e76c4f6a

Tại tháng 11/2024, ngành Ngân hàng vượt trội hơn VNIndex bao nhiêu điểm phần trăm về hiệu suất?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Ngân hàng; Nov-24; none); chart_at(Image 1; VNIndex; Nov-24; none); subtract(#0; #1)`
- Model: `subtract(23.0; 12.1)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '23.0'
- #0 arg1: 'Ngân hàng' -> '12.1'
- #0 arg2: 'Nov-24' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; VNIndex; Nov-24; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 78 — ed790b80-c43b-5221-a3f1-e7c554db79e1

Chênh lệch giữa mức tăng giá hàm ý từ giá mục tiêu và giá hiện tại của FMC với mức % tăng giá 1 năm của chính cổ phiếu này là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(55500; 44600); divide(#0; 44600); multiply(#1; 100); subtract(#2; 24.4)`
- Model: `divide(1300; 100); divide(1000; 100); subtract(#0; #1); multiply(#2; 100)`
- #0: operator subtract -> divide
- #0 arg0: '55500' -> '1300'
- #0 arg1: '44600' -> '100'
- #1 arg0: '#0' -> '1000'
- #1 arg1: '44600' -> '100'
- #2: operator multiply -> subtract
- #2 arg0: '#1' -> '#0'
- #2 arg1: '100' -> '#1'
- #3: operator subtract -> multiply
- #3 arg1: '24.4' -> '100'

## Dòng 79 — 6dd0a0ec-b8ed-5498-a6d7-78838130100e

Trong ngày 31/10/2022, chênh lệch giữa giá trị mua và giá trị bán của nhà đầu tư nước ngoài là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 6; NĐTNN Mua; 31/10/2022; none); chart_at(Image 6; NĐTNN Bán; 31/10/2022; none); subtract(#0; #1)`
- Model: `subtract(0; 0)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 6' -> '0'
- #0 arg1: 'NĐTNN Mua' -> '0'
- #0 arg2: '31/10/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 6; NĐTNN Bán; 31/10/2022; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 80 — f79444d0-596c-5093-a751-658dbb28eae1

P/E 2024F hàm ý từ giá hiện tại của cổ phiếu IMP thấp hơn bao nhiêu lần so với mức P/E trung bình lịch sử của cổ phiếu này?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(61100; 4863); subtract(20.08; #0)`
- Model: `divide(12.5; 20)`
- #0 arg0: '61100' -> '12.5'
- #0 arg1: '4863' -> '20'
- #1: missing gold step #1: subtract(20.08; #0)

## Dòng 81 — 8e40bd59-76de-5a62-b7da-0d7542a00238

Tỷ trọng của Malaysia trong chỉ số FTSE EM có lớn hơn tỷ trọng của Philippines hay không?

- Nhãn: fewer_steps, invalid_math_argument, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; Weight in FTSE EM Index; Malaysia; none); chart_at(Image 1; Weight in FTSE EM Index; Philippines; none); greater(#0; #1)`
- Model: `greater(#1; Table_average(Table 1#none#Philippines#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none))`
- Vi phạm kiểm tra: reference@0:#1; math_type@0:Table_average(Table 1#none#Philippines#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none)
- #0: operator chart_at -> greater
- #0 arg0: 'Image 1' -> '#1'
- #0 arg1: 'Weight in FTSE EM Index' -> 'Table_average(Table 1#none#Philippines#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none#none)'
- #0 arg2: 'Malaysia' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Weight in FTSE EM Index; Philippines; none)
- #2: missing gold step #2: greater(#0; #1)

## Dòng 82 — 213ef250-ffa3-54c4-a808-f542e213fbc0

Mức giá mục tiêu của cổ phiếu GAS cao hơn bao nhiêu phần trăm so với mức giá hiện tại?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(79000; 68100); divide(#0; 68100); multiply(#1; 100)`
- Model: `subtract(30; 100); divide(#0; 100); add(1; #1)`
- #0 arg0: '79000' -> '30'
- #0 arg1: '68100' -> '100'
- #1 arg1: '68100' -> '100'
- #2: operator multiply -> add
- #2 arg0: '#1' -> '1'
- #2 arg1: '100' -> '#1'

## Dòng 83 — f109158c-02e5-566e-90ce-5b7a625b35a8

Tỷ lệ biên lãi thuần (NIM) trung bình của nhóm NHTM tư nhân Mirae theo dõi cao hơn nhóm NHTM quốc doanh bao nhiêu phần trăm?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `subtract(4.5; 2.9)`
- Model: `chart_at(Image 1; NIM; none; none; 2024Q3); chart_at(Image 1; NIM; none; none; 2024Q3); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0: operator subtract -> chart_at
- #0 arg0: '4.5' -> 'Image 1'
- #0 arg1: '2.9' -> 'NIM'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> '2024Q3'
- #1: extra predicted step #1: chart_at(Image 1; NIM; none; none; 2024Q3)
- #2: extra predicted step #2: subtract(#0; #1)

## Dòng 84 — f6284e8d-e29b-5706-9e8c-49472cb364b1

Trong tháng 1, mức giải ngân của quỹ trái phiếu thị trường phát triển bằng bao nhiêu phần của tổng giá trị vào ròng của quỹ trái phiếu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(67.1; 67.2)`
- Model: `divide(67.2; 100)`
- #0 arg0: '67.1' -> '67.2'
- #0 arg1: '67.2' -> '100'

## Dòng 85 — 73460d23-850d-5ef2-90e0-7ff0e282dab4

Với giả định doanh nghiệp không thể chuyển phần chi phí điện tăng thêm sang người tiêu dùng và giá điện tăng 3%, mức giảm LNTT trung bình của 4 ngành Thép, Giấy, Xi măng và Hóa chất gấp bao nhiêu lần mức tăng GVHB trung bình của chính 4 ngành này?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `add(15; 2); add(13; 1); add(#0; #1); divide(#2; 4); table_average(Table 1; Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%; none; none); divide(#3; #4)`
- Model: `table_average(Table 1; %GVHB; none; none); table_average(Table 1; %LNTT; none; none); divide(#0; #1)`
- #0: operator add -> table_average
- #0 arg0: '15' -> 'Table 1'
- #0 arg1: '2' -> '%GVHB'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: operator add -> table_average
- #1 arg0: '13' -> 'Table 1'
- #1 arg1: '1' -> '%LNTT'
- #1 arg2: '<absent>' -> 'none'
- #1 arg3: '<absent>' -> 'none'
- #2: operator add -> divide
- #3: missing gold step #3: divide(#2; 4)
- #4: missing gold step #4: table_average(Table 1; Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%; none; none)
- #5: missing gold step #5: divide(#3; #4)

## Dòng 86 — fca24ba1-5414-5f79-b20c-7b6235865fa9

Đến tháng 10/2023, lũy kế dòng tiền vào các quỹ cổ phiếu của Ấn Độ, Indonesia, Thái Lan và Việt Nam trung bình là bao nhiêu tỷ USD?

- Nhãn: fewer_steps, invalid_arity, missing_source_id, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 4; Ấn Độ; Oct-23; none); chart_at(Image 4; Indonesia; Oct-23; none); chart_at(Image 4; Thái Lan; Oct-23; none); chart_at(Image 4; Việt Nam; Oct-23; none); add(#0; #1); add(#4; #2); add(#5; #3); divide(#6; 4)`
- Model: `table_average(Table 4; India; none; Indonesia; none; Thailand; none; Vietnam; none)`
- Vi phạm kiểm tra: arity@0:9!=4; source_missing@0:Table 4
- #0: operator chart_at -> table_average
- #0 arg0: 'Image 4' -> 'Table 4'
- #0 arg1: 'Ấn Độ' -> 'India'
- #0 arg2: 'Oct-23' -> 'none'
- #0 arg3: 'none' -> 'Indonesia'
- #0 arg4: '<absent>' -> 'none'
- #0 arg5: '<absent>' -> 'Thailand'
- #0 arg6: '<absent>' -> 'none'
- #0 arg7: '<absent>' -> 'Vietnam'
- #0 arg8: '<absent>' -> 'none'
- #1: missing gold step #1: chart_at(Image 4; Indonesia; Oct-23; none)
- #2: missing gold step #2: chart_at(Image 4; Thái Lan; Oct-23; none)
- #3: missing gold step #3: chart_at(Image 4; Việt Nam; Oct-23; none)
- #4: missing gold step #4: add(#0; #1)
- #5: missing gold step #5: add(#4; #2)
- #6: missing gold step #6: add(#5; #3)
- #7: missing gold step #7: divide(#6; 4)

## Dòng 87 — 8a7bb4b7-4dc8-5e2c-bedc-c3b91bfb627f

Trong 3 quý đầu năm 2024, giá trị nợ xấu đã xử lý của VPB chiếm bao nhiêu phần trong tổng giá trị nợ xấu đã xử lý của các ngân hàng được nghiên cứu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(19.4; 73.3)`
- Model: `divide(65.7; 100)`
- #0 arg0: '19.4' -> '65.7'
- #0 arg1: '73.3' -> '100'

## Dòng 88 — 35885d57-09b6-5e71-8a45-41bac74eaa2e

Năm 2026, doanh thu dự phóng của nước tăng lực bình quân trên mỗi nghìn điểm bán là bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(782; 100)`
- Model: `divide(2200; 1000); divide(#0; 100)`
- #0 arg0: '782' -> '2200'
- #0 arg1: '100' -> '1000'
- #1: extra predicted step #1: divide(#0; 100)

## Dòng 89 — 71864677-3847-5f46-b314-90f360367e49

Giá cổ phiếu hàm ý của ACB theo công thức EPS 12T nhân với hệ số P/E là bao nhiêu?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `multiply(3558; 6.5)`
- Model: `chart_at(Image 1; ACB; none; EPS 12T; none)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator multiply -> chart_at
- #0 arg0: '3558' -> 'Image 1'
- #0 arg1: '6.5' -> 'ACB'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'EPS 12T'
- #0 arg4: '<absent>' -> 'none'

## Dòng 90 — 2356c4a7-57df-5e54-aea5-fe424aa737da

Chênh lệch giữa tỷ trọng dòng vốn vào Mỹ trong tổng dòng vốn quỹ cổ phiếu thị trường phát triển khi tính theo cặp số gần đúng của tháng 1 và tỷ trọng tương ứng khi tính theo số liệu Jan-25 là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(46.5; 66); chart_at(Image 2; Phát triển (DM); Jan-25; none); divide(46.495; #1); subtract(#0; #2)`
- Model: `divide(6; 100); divide(100; 100); subtract(#0; #1)`
- #0 arg0: '46.5' -> '6'
- #0 arg1: '66' -> '100'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 2' -> '100'
- #1 arg1: 'Phát triển (DM)' -> '100'
- #1 arg2: 'Jan-25' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator divide -> subtract
- #2 arg0: '46.495' -> '#0'
- #3: missing gold step #3: subtract(#0; #2)

## Dòng 91 — ddc0f6eb-a2f6-5c96-b141-0510884ba500

Tổng giá trị mua vào của khối ngoại trong các phiên giao dịch được thống kê của tháng 10 là bao nhiêu?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `chart_sum(Image 6; NĐTNN Mua; none; none)`
- Model: `chart_total(Table 6; GTGD ròng NDTNN; none; none)`
- Vi phạm kiểm tra: source_type@0:Table 6
- #0: operator chart_sum -> chart_total
- #0 arg0: 'Image 6' -> 'Table 6'
- #0 arg1: 'NĐTNN Mua' -> 'GTGD ròng NDTNN'

## Dòng 92 — bc2bd1ef-a214-5f60-89ea-223068203f1d

Chênh lệch giữa tăng trưởng tín dụng và tăng trưởng huy động dự phóng cho năm 2025 là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; Tăng trưởng tín dụng; 2025F; none); chart_at(Image 2; Tăng trưởng huy động; 2025F; none); subtract(#0; #1)`
- Model: `subtract(16.0; 8.0)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '16.0'
- #0 arg1: 'Tăng trưởng tín dụng' -> '8.0'
- #0 arg2: '2025F' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; Tăng trưởng huy động; 2025F; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 93 — bc5b0ee5-ebe1-5bed-a53b-93effb92928f

Mức P/E FY2020(F) của HBC cao hơn bao nhiêu lần so với P/E mục tiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(21.6; 12.66)`
- Model: `subtract(12.66; 10)`
- #0 arg0: '21.6' -> '12.66'
- #0 arg1: '12.66' -> '10'

## Dòng 94 — 06683677-cc1c-5c43-b036-5ccfd49bf8ad

Lấy P/E ước tính cho năm tài chính hiện tại trung bình từ 1/2/2023 đến 9/2/2023 trừ mức TB năm của 2023, chênh lệch là bao nhiêu điểm P/E?

- Nhãn: fewer_steps, invalid_arity, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_average(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2023; 9/2/2023); chart_at(Image 1; TB năm; 1/2/2023; none); subtract(#0; #1)`
- Model: `chart_average(Image 1; P/E; 1/2/2023; 9/2/2023; none; none`
- Vi phạm kiểm tra: unbalanced_parentheses; unknown_operator@0:INVALID; arity@0:1!=4
- #0: operator chart_average -> INVALID
- #0 arg0: 'Image 1' -> 'chart_average(Image 1; P/E; 1/2/2023; 9/2/2023; none; none'
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> '<absent>'
- #0 arg2: '1/2/2023' -> '<absent>'
- #0 arg3: '9/2/2023' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; TB năm; 1/2/2023; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 95 — ddf0814e-1c4a-5af0-b9b4-232b491ba035

Biên lợi nhuận gộp dự phóng của Nova Consumer trong giai đoạn 2022-2026 chênh lệch bao nhiêu điểm phần trăm giữa mức cao nhất và thấp nhất?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 1; Biên lợi nhuận gộp; 2022; 2026); chart_min(Image 1; Biên lợi nhuận gộp; 2022; 2026); subtract(#0; #1)`
- Model: `subtract(38; 35)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 1' -> '38'
- #0 arg1: 'Biên lợi nhuận gộp' -> '35'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: '2026' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 1; Biên lợi nhuận gộp; 2022; 2026)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 96 — b4825aa5-f9c4-51f7-bc1d-2f643c979577

Lãi suất tiền gửi 12 tháng của nhóm NH TMCP Tư nhân đã thay đổi bao nhiêu phần trăm từ thời điểm 1-Apr-24 đến 1-Sep-24?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 6; NH TMCP Tư nhân; 1-Apr-24; none); chart_at(Image 6; NH TMCP Tư nhân; 1-Sep-24; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 6; LHS; Apr-24; none); chart_at(Image 6; LHS; Sep-24; none); subtract(#1; #0)`
- #0 arg1: 'NH TMCP Tư nhân' -> 'LHS'
- #0 arg2: '1-Apr-24' -> 'Apr-24'
- #1 arg1: 'NH TMCP Tư nhân' -> 'LHS'
- #1 arg2: '1-Sep-24' -> 'Sep-24'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 97 — f3b687ed-17d3-57e6-8244-615717340d75

Mức P/E ước tính trung bình trong các kỳ quan sát năm 2024 từ 1/2/2024 đến 11/2/2024 là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_average(Image 1; P/E ước tính 2024; 1/2/2024; 11/2/2024)`
- Model: `chart_average(Image 1; P/E; Jan-24; Nov-24)`
- #0 arg1: 'P/E ước tính 2024' -> 'P/E'
- #0 arg2: '1/2/2024' -> 'Jan-24'
- #0 arg3: '11/2/2024' -> 'Nov-24'

## Dòng 98 — 8763b48d-5349-5062-879a-8db49ed88c8f

Tổng lãi gộp của HBC trong ba năm tài chính FY2017, FY2018 và FY2019 là bao nhiêu?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_sum(Table 1; Lãi gộp (Vbn); FY 2017; FY2019)`
- Model: `chart_sum(Image 1; Lãi gộp; none; 2017; none; 2019)`
- Vi phạm kiểm tra: arity@0:6!=4
- #0: operator table_sum -> chart_sum
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Lãi gộp (Vbn)' -> 'Lãi gộp'
- #0 arg2: 'FY 2017' -> 'none'
- #0 arg3: 'FY2019' -> '2017'
- #0 arg4: '<absent>' -> 'none'
- #0 arg5: '<absent>' -> '2019'

## Dòng 99 — 63f835e7-cef9-595a-b63f-417d4f231101

Trong số các ngành được đánh giá, mức dự báo tăng trưởng doanh thu cao nhất cho năm 2024 là bao nhiêu phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 1; Tăng trưởng doanh thu@2024F; none; none)`
- Model: `chart_max(Image 1; Tăng trưởng doanh thu 2024; none; none)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Tăng trưởng doanh thu@2024F' -> 'Tăng trưởng doanh thu 2024'

## Dòng 100 — cbced019-3325-55a8-96cf-220f9d77ae59

Tỷ suất ROE dự phóng năm 2024 của PLX có cao hơn so với PVS hay không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `greater(12.0; 7.6)`
- Model: `chart_average(Image 1; ROE (post-tax). 2024F; PLX; none); chart_average(Image 1; ROE (post-tax). 2024F; PVS; none); greater(#0; #1)`
- #0: operator greater -> chart_average
- #0 arg0: '12.0' -> 'Image 1'
- #0 arg1: '7.6' -> 'ROE (post-tax). 2024F'
- #0 arg2: '<absent>' -> 'PLX'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: chart_average(Image 1; ROE (post-tax). 2024F; PVS; none)
- #2: extra predicted step #2: greater(#0; #1)

## Dòng 101 — ce5a837b-8bc1-5ac0-9c2f-dd38b48426c8

Giả sử quy mô thu nhập lãi thuần (NII) trong năm 2023 tăng trưởng theo đúng tốc độ tăng của chỉ tiêu này trong 9 tháng đầu năm 2024, thì mức tăng thêm tuyệt đối sẽ là bao nhiêu nghìn tỷ đồng?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `chart_at(Image 1; NII; 2023; none); divide(14.1; 100); multiply(#0; #1)`
- Model: `multiply(14.9; 14.1); divide(#0; 100); subtract(#1; 14.9)`
- #0: operator chart_at -> multiply
- #0 arg0: 'Image 1' -> '14.9'
- #0 arg1: 'NII' -> '14.1'
- #0 arg2: '2023' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1 arg0: '14.1' -> '#0'
- #2: operator multiply -> subtract
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '14.9'

## Dòng 102 — bc315c29-ef1b-5b5d-ac4b-5b64f419af69

Mức thay đổi trung bình của ba chỉ số VN30, VNMidcap và VNSmallcap trong tháng 9/2022 là bao nhiêu phần trăm?

- Nhãn: invalid_arity, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_average(Table 1; T9/2022; VN30; VNSmallcap)`
- Model: `chart_average(VN30#0; VNMidcap#0; VNSmallcap#0)`
- Vi phạm kiểm tra: arity@0:3!=4; source_type@0:VN30#0
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'VN30#0'
- #0 arg1: 'T9/2022' -> 'VNMidcap#0'
- #0 arg2: 'VN30' -> 'VNSmallcap#0'
- #0 arg3: 'VNSmallcap' -> '<absent>'

## Dòng 103 — 85a837e5-5c6a-5d4f-a729-67f31c596690

Lợi nhuận sau thuế dự phóng trung bình của DPG trong giai đoạn 2024F-2026F là bao nhiêu tỷ đồng?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_average(Table 2; Lợi nhuận sau thuế (tỷđồng); 2024F; 2026F)`
- Model: `chart_average(Table 2; LNST sau thuế; 2024F; 2026F)`
- Vi phạm kiểm tra: source_type@0:Table 2
- #0: operator table_average -> chart_average
- #0 arg1: 'Lợi nhuận sau thuế (tỷđồng)' -> 'LNST sau thuế'

## Dòng 104 — 4f4cf0dd-0dba-50fc-b989-6b52cc7b59d7

Chênh lệch mức sinh lời ở giai đoạn hồi phục giữa ngành Dịch vụ tài chính và Dầu khí là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `subtract(29.7; 8.27)`
- Model: `subtract(69.4; #1)`
- Vi phạm kiểm tra: reference@0:#1
- #0 arg0: '29.7' -> '69.4'
- #0 arg1: '8.27' -> '#1'

## Dòng 105 — c48cb615-4f74-518c-a940-3273b9042e9a

Tỷ suất lợi nhuận trên vốn chủ sở hữu (ROE) trung bình của các ngân hàng ghi nhận tăng trưởng thu nhập thuần từ dịch vụ (NSI) tích cực nhờ thế mạnh trong mảng xuất nhập khẩu và chứng khoán là bao nhiêu phần trăm?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `add(20.0; 16.6); divide(#0; 2)`
- Model: `divide(390; 53)`
- #0: operator add -> divide
- #0 arg0: '20.0' -> '390'
- #0 arg1: '16.6' -> '53'
- #1: missing gold step #1: divide(#0; 2)

## Dòng 106 — d480d3f1-50c0-58f1-802c-3181a3a31786

Giá trị bán của nhà đầu tư nước ngoài (NĐTNN Bán) tại thời điểm 9/26 có lớn hơn mức bán tại thời điểm 9/5 hay không?

- Nhãn: fewer_steps, invalid_arity, invalid_math_argument, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 5; NĐTNN Bán; 9/26; none); chart_at(Image 5; NĐTNN Bán; 9/5; none); greater(#0; #1)`
- Model: `greater(#0; #1; #2; none; #3)`
- Vi phạm kiểm tra: arity@0:5!=2; reference@0:#0; reference@0:#1; reference@0:#2; math_type@0:none; reference@0:#3
- #0: operator chart_at -> greater
- #0 arg0: 'Image 5' -> '#0'
- #0 arg1: 'NĐTNN Bán' -> '#1'
- #0 arg2: '9/26' -> '#2'
- #0 arg4: '<absent>' -> '#3'
- #1: missing gold step #1: chart_at(Image 5; NĐTNN Bán; 9/5; none)
- #2: missing gold step #2: greater(#0; #1)

## Dòng 107 — dd881b5b-986b-553c-9db1-038d164758a5

Tổng số điểm đóng góp của nhóm cổ phiếu tác động tích cực nhất đến thị trường trong tháng có lớn hơn độ lớn tổng số điểm kéo giảm của nhóm cổ phiếu tác động tiêu cực nhất trong tháng hay không?

- Nhãn: fewer_steps, invalid_math_argument, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff, strict_invalid
- Ground truth: `chart_sum(Image 1; Index; none; none); chart_sum(Image 2; Index; none; none); subtract(0; #1); greater(#0; #2)`
- Model: `greater(Table 1#%+/-; -7); greater(#0; -6)`
- Vi phạm kiểm tra: math_type@0:Table 1#%+/-
- #0: operator chart_sum -> greater
- #0 arg0: 'Image 1' -> 'Table 1#%+/-'
- #0 arg1: 'Index' -> '-7'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_sum -> greater
- #1 arg0: 'Image 2' -> '#0'
- #1 arg1: 'Index' -> '-6'
- #1 arg2: 'none' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(0; #1)
- #3: missing gold step #3: greater(#0; #2)

## Dòng 108 — ff8db97f-0b3c-5fb4-be98-6bd660732c6f

Mức tối thiểu của lượng vốn dự kiến Việt Nam có thể thu hút được ngay lập tức khi quyết định nâng hạng có hiệu lực lớn hơn tổng ước tính dòng vốn từ các quỹ lớn mô phỏng theo chỉ số của FTSE Russell là bao nhiêu triệu USD?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `multiply(1.7; 1000); subtract(#0; 1687.5)`
- Model: `subtract(1.7; 2.5)`
- #0: operator multiply -> subtract
- #0 arg1: '1000' -> '2.5'
- #1: missing gold step #1: subtract(#0; 1687.5)

## Dòng 109 — 14f7878f-c487-5455-97d5-ed918bef7701

Trung bình tỷ suất lợi nhuận trên vốn chủ sở hữu (ROE) trong giai đoạn từ năm 2021H đến 2023H là bao nhiêu phần trăm?

- Nhãn: invalid_arity, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_average(Table 2; ROE (%); 2021H; 2023H)`
- Model: `chart_average(Table 2; ROE; none; 2021H; 2023H)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 2
- #0: operator table_average -> chart_average
- #0 arg1: 'ROE (%)' -> 'ROE'
- #0 arg2: '2021H' -> 'none'
- #0 arg3: '2023H' -> '2021H'
- #0 arg4: '<absent>' -> '2023H'

## Dòng 110 — 33e650dc-1631-56d3-a2d4-96131d3abfd6

Tổng doanh thu từ mảng Xây dựng và mảng Thủy điện trong năm 2023 là bao nhiêu?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `add(2875; 532)`
- Model: `add(2875; 532)`

## Dòng 111 — 722c8a6f-c093-50a8-9937-988805f4fc40

Mức chênh lệch giữa tỷ lệ tăng trưởng lợi nhuận ước tính năm 2024 của nhóm VN30 so với mức tăng trưởng của 83 cổ phiếu trong phạm vi nghiên cứu của SSI Research là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(16.2; 15.3)`
- Model: `subtract(15.3; -5.6)`
- #0 arg0: '16.2' -> '15.3'
- #0 arg1: '15.3' -> '-5.6'

## Dòng 112 — 1c24e063-55f0-5613-a0f2-c4f8d024dc4f

Chênh lệch giữa mức hiệu suất cao nhất và thấp nhất trong năm 2022 của các chỉ số và nhóm ngành là bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 2; Năm 2022; none; none); table_min(Table 2; Năm 2022; none; none); subtract(#0; #1)`
- Model: `table_max(Table 2; 2022; none; none); table_min(Table 2; 2022; none; none); subtract(#0; #1)`
- #0 arg1: 'Năm 2022' -> '2022'
- #1 arg1: 'Năm 2022' -> '2022'

## Dòng 113 — 9ec10d7d-aa63-5195-a355-f70454304a12

Tỷ trọng chi phí điện trên giá vốn hàng bán (GVHB) trung bình của bốn ngành: thép, hóa chất, xi măng và giấy là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_average(Table 1; Tỷ trọng Chi phí điện/GVHB; none; none)`
- Model: `table_average(Table 1; %GVHB; Thép; Hóa Chất; Xi măng)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0 arg1: 'Tỷ trọng Chi phí điện/GVHB' -> '%GVHB'
- #0 arg2: 'none' -> 'Thép'
- #0 arg3: 'none' -> 'Hóa Chất'
- #0 arg4: '<absent>' -> 'Xi măng'

## Dòng 114 — 55a0af38-23ac-58b3-8ca0-b20d564f95d2

Trong 3 phiên từ 05–09/06/2020, tỷ lệ cổ phần HBC được giao dịch so với vốn điều lệ tương đương bao nhiêu lần tỷ lệ sở hữu của nhóm cổ đông "Khác"?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `chart_at(Image 1; Khác; Hình 1: Cơ cấu cổ đông; none); divide(16; #0)`
- Model: `divide(37; 100); divide(#0; 59)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '37'
- #0 arg1: 'Khác' -> '100'
- #0 arg2: 'Hình 1: Cơ cấu cổ đông' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1 arg0: '16' -> '#0'
- #1 arg1: '#0' -> '59'

## Dòng 115 — a6dd6881-6830-5132-80fc-54e06b3e8ec5

Mức biến động trung bình trong năm 2022 của ba chỉ số VN30, VNMidcap và VNSmallcap là bao nhiêu phần trăm?

- Nhãn: missing_source_id, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `table_average(Table 1; Năm 2022; VN30; VNSmallcap)`
- Model: `table_average(Table 3; VN30; none; none); table_average(Table 3; VNMidcap; none; none); table_average(Table 3; VNSmallcap; none; none); add(#0; #1); add(#2; #3)`
- Vi phạm kiểm tra: source_missing@0:Table 3; source_missing@1:Table 3; source_missing@2:Table 3
- #0 arg0: 'Table 1' -> 'Table 3'
- #0 arg1: 'Năm 2022' -> 'VN30'
- #0 arg2: 'VN30' -> 'none'
- #0 arg3: 'VNSmallcap' -> 'none'
- #1: extra predicted step #1: table_average(Table 3; VNMidcap; none; none)
- #2: extra predicted step #2: table_average(Table 3; VNSmallcap; none; none)
- #3: extra predicted step #3: add(#0; #1)
- #4: extra predicted step #4: add(#2; #3)

## Dòng 116 — 065fbb02-99b8-54b4-b495-c99c47a3a452

Mức tăng trưởng lợi nhuận của các ngân hàng niêm yết trong quý 2 năm 2024 cao hơn quý 1 cùng năm bao nhiêu phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(22.6; 9.5)`
- Model: `subtract(22.6; 9.5)`

## Dòng 117 — a10d8533-2502-5b88-a3da-28e4fbb09c1a

Tỷ trọng ước tính của Việt Nam trong Schwab Emerging Markets Equity ETF có cao hơn tỷ trọng ước tính của Việt Nam trong Vanguard FTSE Emerging Markets ETF không?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `greater(0.73; 0.70)`
- Model: `divide(3.5; 100)`
- #0: operator greater -> divide
- #0 arg0: '0.73' -> '3.5'
- #0 arg1: '0.70' -> '100'

## Dòng 118 — 0b7d1e61-d33e-5266-bdfb-97d22970220f

Mức giá điện cao nhất được ghi nhận trong giai đoạn từ năm 2009 đến năm 2023 là bao nhiêu VND/kWh?

- Nhãn: invalid_source_type, non_exact, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; Giá điện; none; none)`
- Model: `chart_max(1920; 1864; none; none)`
- Vi phạm kiểm tra: source_type@0:1920
- #0 arg0: 'Image 1' -> '1920'
- #0 arg1: 'Giá điện' -> '1864'

## Dòng 119 — 72ae11f8-8e8e-5c90-b88e-96282be7f2b1

Lợi suất bình quân trong tháng 10/2022 của ba chỉ số vốn hóa VN30, VNMidcap và VNSmallcap là bao nhiêu?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff
- Ground truth: `add(-10.9; -11.9); add(#0; -15.8); divide(#1; 3)`
- Model: `chart_average(Image 3; VN30; none; none); chart_average(Image 3; VNMidcap; none; none); chart_average(Image 3; VNSmallcap; none; none)`
- #0: operator add -> chart_average
- #0 arg0: '-10.9' -> 'Image 3'
- #0 arg1: '-11.9' -> 'VN30'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: operator add -> chart_average
- #1 arg0: '#0' -> 'Image 3'
- #1 arg1: '-15.8' -> 'VNMidcap'
- #1 arg2: '<absent>' -> 'none'
- #1 arg3: '<absent>' -> 'none'
- #2: operator divide -> chart_average
- #2 arg0: '#1' -> 'Image 3'
- #2 arg1: '3' -> 'VNSmallcap'
- #2 arg2: '<absent>' -> 'none'
- #2 arg3: '<absent>' -> 'none'

## Dòng 120 — 88b08555-76e0-5fde-aa86-71750137ab29

Trong T8/2022, mức sinh lời của ngành Năng lượng chênh lệch bao nhiêu điểm phần trăm so với VN-Index?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(15.5; 6.1)`
- Model: `subtract(15.5; 6.15)`
- #0 arg1: '6.1' -> '6.15'

## Dòng 121 — 25b630eb-1156-5678-9f2c-5006e60a178e

Tổng giá trị mua ròng của khối ngoại trong tháng 10/2023 đối với nhóm cổ phiếu nằm trong top được mua ròng trong tháng là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_sum(Image 3; T10/2023; none; none)`
- Model: `chart_sum(Image 3; Top CP Nước ngoài mua ròng trong tháng 10; none; none)`
- #0 arg1: 'T10/2023' -> 'Top CP Nước ngoài mua ròng trong tháng 10'

## Dòng 122 — 71429458-7919-5664-b80f-49364856302e

Tổng thu nhập thuần từ dịch vụ (NSI) và thu nhập khác (NOI) của 9 ngân hàng trong nhóm theo dõi trong năm 2023 đạt bao nhiêu nghìn tỷ đồng?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NSI; 2023; none); chart_at(Image 1; NOI; 2023; none); add(#0; #1)`
- Model: `add(354; 51)`
- #0: operator chart_at -> add
- #0 arg0: 'Image 1' -> '354'
- #0 arg1: 'NSI' -> '51'
- #0 arg2: '2023' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; NOI; 2023; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 123 — 503bf24e-6e8d-5bca-97f5-4e4df7fce562

Chênh lệch giữa mức thay đổi của VN-Index tính cho “Năm 2022” và hiệu suất lũy kế của VNIndex tại ngày 31/10/2022 là bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, invalid_reference, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; VNIndex; 31/10/2022; none); subtract(-31.4; #0)`
- Model: `chart_at(Image 2; VNIndex; none; 2022; none); chart_at(Image 2; VNIndex; none; 31/10/2022; none); subtract(#1; #2); divide(#3; #1); multiply(#4; 100)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4; reference@2:#2; reference@3:#3; reference@4:#4
- #0 arg2: '31/10/2022' -> 'none'
- #0 arg3: 'none' -> '2022'
- #0 arg4: '<absent>' -> 'none'
- #1: operator subtract -> chart_at
- #1 arg0: '-31.4' -> 'Image 2'
- #1 arg1: '#0' -> 'VNIndex'
- #1 arg2: '<absent>' -> 'none'
- #1 arg3: '<absent>' -> '31/10/2022'
- #1 arg4: '<absent>' -> 'none'
- #2: extra predicted step #2: subtract(#1; #2)
- #3: extra predicted step #3: divide(#3; #1)
- #4: extra predicted step #4: multiply(#4; 100)

## Dòng 124 — 6e7c66c4-d186-535f-82aa-941c5444f912

Trong tháng 10, tổng mức tác động tích cực của ba cổ phiếu VNM, CTG và EIB lên chỉ số thị trường là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 4; Index; VNM; none); chart_at(Image 4; Index; CTG; none); chart_at(Image 4; Index; EIB; none); add(#0; #1); add(#3; #2)`
- Model: `add(3.5; 1.5); add(#0; 0.5)`
- #0: operator chart_at -> add
- #0 arg0: 'Image 4' -> '3.5'
- #0 arg1: 'Index' -> '1.5'
- #0 arg2: 'VNM' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> add
- #1 arg0: 'Image 4' -> '#0'
- #1 arg1: 'Index' -> '0.5'
- #1 arg2: 'CTG' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: chart_at(Image 4; Index; EIB; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 125 — 5310f137-46f9-5cc5-b93d-c6e1dda8a27b

Trong tháng 9/2022, mức sinh lời của nhóm Công nghiệp chênh lệch bao nhiêu điểm phần trăm so với VN-Index?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(-14.5; -11.6)`
- Model: `subtract(-12.3; 1132.11)`
- #0 arg0: '-14.5' -> '-12.3'
- #0 arg1: '-11.6' -> '1132.11'

## Dòng 126 — 214ca05b-1621-5d07-a2d3-f4420a81cbb6

Trung bình mỗi tháng trong 10 tháng đầu năm 2022, tỷ suất sinh lời của nhóm ngành Năng lượng là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_average(Table 1; Năng lượng; T1/2022; T10/2022)`
- Model: `chart_average(Image 3; Năng lượng; none; Jan-22; Oct-22)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 3'
- #0 arg2: 'T1/2022' -> 'none'
- #0 arg3: 'T10/2022' -> 'Jan-22'
- #0 arg4: '<absent>' -> 'Oct-22'

## Dòng 127 — d3ae532c-ed89-536e-befe-2bd1c7942c53

Biên độ giữa giá trị lũy kế cao nhất và thấp nhất của dòng tiền vào các quỹ cổ phiếu tại Thái Lan trong giai đoạn từ Jan-20 đến Jan-25 là bao nhiêu tỷ USD?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_max(Image 3; Thái Lan; Jan-20; Jan-25); chart_min(Image 3; Thái Lan; Jan-20; Jan-25); subtract(#0; #1)`
- Model: `table_max(Table 1; Thái Lan; Jan-20; Jan-25); table_min(Table 1; Thái Lan; Jan-20; Jan-25); subtract(#0; #1)`
- #0: operator chart_max -> table_max
- #0 arg0: 'Image 3' -> 'Table 1'
- #1: operator chart_min -> table_min
- #1 arg0: 'Image 3' -> 'Table 1'

## Dòng 128 — 0db75e38-1c10-5bcb-8bbf-81a49f3b0e30

Khoảng chênh lệch giữa mức thay đổi giá cao nhất và thấp nhất của các nhóm ngành trong năm 2023 là bao nhiêu điểm phần trăm?

- Nhãn: invalid_source_type, non_exact, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; 2023; none; none); chart_min(Image 1; 2023; none; none); subtract(#0; #1)`
- Model: `chart_max(Table 1; 2023; none; none); chart_min(Table 1; 2023; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0 arg0: 'Image 1' -> 'Table 1'
- #1 arg0: 'Image 1' -> 'Table 1'

## Dòng 129 — 2ffb1418-9cfa-546a-ae05-5ee0d04bb897

Tổng NII, NSI và NOI của 9 ngân hàng trong nhóm theo dõi tại 3Q24 (TTM) là bao nhiêu nghìn tỷ?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; NII; 3Q24 (TTM); none); chart_at(Image 1; NSI; 3Q24 (TTM); none); chart_at(Image 1; NOI; 3Q24 (TTM); none); add(#0; #1); add(#3; #2)`
- Model: `multiply(53; 390); add(#0; 158); multiply(#1; #2)`
- Vi phạm kiểm tra: reference@2:#2
- #0: operator chart_at -> multiply
- #0 arg0: 'Image 1' -> '53'
- #0 arg1: 'NII' -> '390'
- #0 arg2: '3Q24 (TTM)' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> add
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'NSI' -> '158'
- #1 arg2: '3Q24 (TTM)' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator chart_at -> multiply
- #2 arg0: 'Image 1' -> '#1'
- #2 arg1: 'NOI' -> '#2'
- #2 arg2: '3Q24 (TTM)' -> '<absent>'
- #2 arg3: 'none' -> '<absent>'
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 130 — 400bc221-29e5-55aa-8f60-b0e2f29ee394

Chênh lệch giữa giá mục tiêu cơ bản và vùng cắt lỗ của cổ phiếu MWG là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(61.5; 48)`
- Model: `subtract(43.5; 37.5)`
- #0 arg0: '61.5' -> '43.5'
- #0 arg1: '48' -> '37.5'

## Dòng 131 — f586104f-e262-5eda-aae2-fdf6f92af861

Chênh lệch giữa mức tăng/giảm giá trung bình trong tháng của nhóm cổ phiếu tác động tích cực nhất đến thị trường và nhóm cổ phiếu tác động tiêu cực nhất đến thị trường là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_average(Image 1; % +/-; none; none); chart_average(Image 2; % +/-; none; none); subtract(#0; #1)`
- Model: `multiply(0.5; -7)`
- #0: operator chart_average -> multiply
- #0 arg0: 'Image 1' -> '0.5'
- #0 arg1: '% +/-' -> '-7'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_average(Image 2; % +/-; none; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 132 — df06fd16-43d5-58c0-aef8-e22c36d5a404

Nếu chi phí điện tăng 3% và doanh nghiệp không thể chuyển phần chi phí tăng thêm sang người tiêu dùng, mức giảm tối đa LNTT ước tính trung bình của các ngành Thép, Giấy, Xi măng và Hóa chất là bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `add(15; 2); add(13; 1); add(#0; #1); divide(#2; 4)`
- Model: `divide(15; 1); divide(-1; 1); divide(2; 1); add(#0; #1); add(#2; #3)`
- #0: operator add -> divide
- #0 arg1: '2' -> '1'
- #1: operator add -> divide
- #1 arg0: '13' -> '-1'
- #2: operator add -> divide
- #2 arg0: '#0' -> '2'
- #2 arg1: '#1' -> '1'
- #3: operator divide -> add
- #3 arg0: '#2' -> '#0'
- #3 arg1: '4' -> '#1'
- #4: extra predicted step #4: add(#2; #3)

## Dòng 133 — e64ef0cf-ebf4-504c-b5f9-f509198e9328

Biên độ dao động (khoảng cách giữa mức thay đổi cao nhất và thấp nhất) theo tháng của VN-Index trong 10 tháng đầu năm 2023 là bao nhiêu phần trăm?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; VN-Index; Jan-23; Oct-23); table_min(Table 1; VN-Index; Jan-23; Oct-23); subtract(#0; #1)`
- Model: `chart_max(Table 1; VN-Index; none; none); chart_min(Table 1; VN-Index; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0: operator table_max -> chart_max
- #0 arg2: 'Jan-23' -> 'none'
- #0 arg3: 'Oct-23' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg2: 'Jan-23' -> 'none'
- #1 arg3: 'Oct-23' -> 'none'

## Dòng 134 — ac178077-3aad-521d-95bb-9c0100d5e2ed

Chênh lệch giữa định giá P/E trung bình 5 năm và P/E ước tính cho năm tài chính hiện tại tại thời điểm 1/2/2023 là bao nhiêu?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2023; none); chart_at(Image 1; TB 5 năm; 1/2/2023; none); subtract(#1; #0)`
- Model: `chart_average(Image 1; P/E; 1/2/2023; none)`
- #0: operator chart_at -> chart_average
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #1: missing gold step #1: chart_at(Image 1; TB 5 năm; 1/2/2023; none)
- #2: missing gold step #2: subtract(#1; #0)

## Dòng 135 — 2ddfba1e-dbcf-54c6-bfcb-603021520501

Thanh khoản của nhóm VN30 trong tháng 8/2022 đã thay đổi bao nhiêu phần trăm so với tháng 7/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; VN30; T7/2022; none); chart_at(Image 2; VN30; T8/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `divide(7.2; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '7.2'
- #0 arg1: 'VN30' -> '100'
- #0 arg2: 'T7/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; VN30; T8/2022; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 136 — e6d47c78-4a96-560c-bae8-fddcb05eb927

Tổng tài sản ròng trung bình của các quỹ lớn mô phỏng theo các chỉ số của FTSE Russell là bao nhiêu tỷ USD?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 1; Tổng tài sản ròng (tỷ USD); Vanguard Total International Stock Index Fund; Schwab Emerging Markets Equity ETF)`
- Model: `chart_average(Image 1; Tổng tài sản ròng (Tỷ USD); Jan-24; Dec-23)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Tổng tài sản ròng (tỷ USD)' -> 'Tổng tài sản ròng (Tỷ USD)'
- #0 arg2: 'Vanguard Total International Stock Index Fund' -> 'Jan-24'
- #0 arg3: 'Schwab Emerging Markets Equity ETF' -> 'Dec-23'

## Dòng 137 — 3d783ce3-baa3-59fb-80cb-3b7e4d5bce08

Dựa trên kết quả thực hiện 9 tháng đầu năm, FPT cần ghi nhận thêm bao nhiêu tỷ đồng doanh thu để đạt được mức dự phóng cho toàn bộ năm 2024?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(61880; 45241)`
- Model: `subtract(61880; 45241)`

## Dòng 138 — 54d75952-642d-532b-aedf-24b2a95dca6e

Trong năm 2023, lợi nhuận gộp của mảng Thủy điện chiếm tỷ trọng bao nhiêu so với tổng lợi nhuận gộp của công ty?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(370; 585)`
- Model: `divide(532; 503); multiply(#0; 100)`
- #0 arg0: '370' -> '532'
- #0 arg1: '585' -> '503'
- #1: extra predicted step #1: multiply(#0; 100)

## Dòng 139 — 5a358982-e953-5f2b-b16c-cde530ce5e10

Trong giai đoạn 05–09/06/2020, dựa trên khối lượng giao dịch của HBC và tỷ lệ khối lượng này so với vốn điều lệ, có thể suy ra tổng số cổ phần tương ứng với vốn điều lệ của công ty là khoảng bao nhiêu cổ phần?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(16; 100); divide(37000000; #0)`
- Model: `divide(37; 100); divide(38.88; 100); multiply(#0; #1); add(#2; 1)`
- #0 arg0: '16' -> '37'
- #1 arg0: '37000000' -> '38.88'
- #1 arg1: '#0' -> '100'
- #2: extra predicted step #2: multiply(#0; #1)
- #3: extra predicted step #3: add(#2; 1)

## Dòng 140 — dae192c6-b0f5-5fcb-a97e-cdbd8647d16a

Tốc độ tăng trưởng của cổ phiếu FPT VN có cao hơn mức tăng trưởng của chỉ số VN-Index trong giai đoạn từ Nov 23 đến Nov 24 hay không?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 1; FPT VN; Nov 23; none); chart_at(Image 1; FPT VN; Nov 24; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); chart_at(Image 1; VN-Index; Nov 23; none); chart_at(Image 1; VN-Index; Nov 24; none); subtract(#6; #5); divide(#7; #5); multiply(#8; 100); greater(#4; #9)`
- Model: `chart_at(Image 1; VN-Index; Nov 23; none); chart_at(Image 1; VN-Index; Nov 24; none); subtract(#1; #0); divide(#2; #0); greater(#3; 1)`
- #0 arg1: 'FPT VN' -> 'VN-Index'
- #1 arg1: 'FPT VN' -> 'VN-Index'
- #4: operator multiply -> greater
- #4 arg1: '100' -> '1'
- #5: missing gold step #5: chart_at(Image 1; VN-Index; Nov 23; none)
- #6: missing gold step #6: chart_at(Image 1; VN-Index; Nov 24; none)
- #7: missing gold step #7: subtract(#6; #5)
- #8: missing gold step #8: divide(#7; #5)
- #9: missing gold step #9: multiply(#8; 100)
- #10: missing gold step #10: greater(#4; #9)

## Dòng 141 — 3c0fa5ae-8acb-5778-8306-db5ea12a6e8f

Trong 3Q23, mức thay đổi giá của nhóm Công nghệ thông tin cao hơn VN-Index bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `subtract(24.4; 3.0)`
- Model: `table_average(Table 1; Công nghệ thông tin; 3Q23; none; VN-Index)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator subtract -> table_average
- #0 arg0: '24.4' -> 'Table 1'
- #0 arg1: '3.0' -> 'Công nghệ thông tin'
- #0 arg2: '<absent>' -> '3Q23'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> 'VN-Index'

## Dòng 142 — 8fe89d79-48b6-5077-9004-7dccc8142adb

Mức cao nhất của biên lợi nhuận gộp được dự phóng cho công ty trong giai đoạn từ năm 2022 đến năm 2026 là bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 1; Biên lợi nhuận gộp; 2022; 2026)`
- Model: `chart_max(Image 1; Biên Lợi Nhuận Gồm; none; none)`
- #0 arg1: 'Biên lợi nhuận gộp' -> 'Biên Lợi Nhuận Gồm'
- #0 arg2: '2022' -> 'none'
- #0 arg3: '2026' -> 'none'

## Dòng 143 — 60dbae1b-2cbf-58d9-9e55-e0cca1ec1388

Mức chênh lệch giữa hiệu suất cao nhất và thấp nhất theo tháng của ngành Ngân hàng trong năm 2024 là bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 1; Ngân hàng; Jan-24; Nov-24); chart_min(Image 1; Ngân hàng; Jan-24; Nov-24); subtract(#0; #1)`
- Model: `chart_max(Image 1; Năm 2024; none; none); chart_min(Image 1; Năm 2024; none; none); subtract(#0; #1)`
- #0 arg1: 'Ngân hàng' -> 'Năm 2024'
- #0 arg2: 'Jan-24' -> 'none'
- #0 arg3: 'Nov-24' -> 'none'
- #1 arg1: 'Ngân hàng' -> 'Năm 2024'
- #1 arg2: 'Jan-24' -> 'none'
- #1 arg3: 'Nov-24' -> 'none'

## Dòng 144 — ecc21dfc-a89e-51d1-8cc8-5d6ff8176476

Nếu lấy mức sinh lời vượt trội của DPG so với VN-Index trong giai đoạn từ cuối tháng 12/2023 đến cuối tháng 6/2024 trừ đi mức thay đổi giá tương đối 6 tháng của DPG, chênh lệch là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, invalid_arity, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; DPG VN; Dec 23; none); chart_at(Image 1; DPG VN; Jun 24; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); chart_at(Image 1; VN-Index; Dec 23; none); chart_at(Image 1; VN-Index; Jun 24; none); subtract(#6; #5); divide(#7; #5); multiply(#8; 100); subtract(#4; #9); subtract(#10; 24.1)`
- Model: `chart_max(Image 1; VN-Index; Jun 22; Dec 23); chart_max(Image 1; DPG VN; Jun 22; none); chart_max(Image 1; DPG VN; Jun 22; Jun 24); chart_total(#1; #2; #3); chart_total(#1; #4; #5); subtract(#6; #7; #8); subtract(#9; #10; #11); subtract(#12; #13; #14)`
- Vi phạm kiểm tra: arity@3:3!=4; reference@3:#3; source_type@3:#1; arity@4:3!=4; reference@4:#4; reference@4:#5; source_type@4:#1; arity@5:3!=2; reference@5:#6; reference@5:#7; reference@5:#8; arity@6:3!=2; reference@6:#9; reference@6:#10; reference@6:#11; arity@7:3!=2; reference@7:#12; reference@7:#13; reference@7:#14
- #0: operator chart_at -> chart_max
- #0 arg1: 'DPG VN' -> 'VN-Index'
- #0 arg2: 'Dec 23' -> 'Jun 22'
- #0 arg3: 'none' -> 'Dec 23'
- #1: operator chart_at -> chart_max
- #1 arg2: 'Jun 24' -> 'Jun 22'
- #2: operator subtract -> chart_max
- #2 arg0: '#1' -> 'Image 1'
- #2 arg1: '#0' -> 'DPG VN'
- #2 arg2: '<absent>' -> 'Jun 22'
- #2 arg3: '<absent>' -> 'Jun 24'
- #3: operator divide -> chart_total
- #3 arg0: '#2' -> '#1'
- #3 arg1: '#0' -> '#2'
- #3 arg2: '<absent>' -> '#3'
- #4: operator multiply -> chart_total
- #4 arg0: '#3' -> '#1'
- #4 arg1: '100' -> '#4'
- #4 arg2: '<absent>' -> '#5'
- #5: operator chart_at -> subtract
- #5 arg0: 'Image 1' -> '#6'
- #5 arg1: 'VN-Index' -> '#7'
- #5 arg2: 'Dec 23' -> '#8'
- #5 arg3: 'none' -> '<absent>'
- #6: operator chart_at -> subtract
- #6 arg0: 'Image 1' -> '#9'
- #6 arg1: 'VN-Index' -> '#10'
- #6 arg2: 'Jun 24' -> '#11'
- #6 arg3: 'none' -> '<absent>'
- #7 arg0: '#6' -> '#12'
- #7 arg1: '#5' -> '#13'
- #7 arg2: '<absent>' -> '#14'
- #8: missing gold step #8: divide(#7; #5)
- #9: missing gold step #9: multiply(#8; 100)
- #10: missing gold step #10: subtract(#4; #9)
- #11: missing gold step #11: subtract(#10; 24.1)

## Dòng 145 — 60db1ebe-cc00-532f-9b26-faa205fb84e7

Tại quý 3/2024, chi phí tín dụng có lớn hơn tỷ lệ nợ xấu mới hình thành hay không?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 9; Chi phí tín dụng; 3Q24; none); chart_at(Image 9; Tỷ lệ nợ xấu mới hình thành; 3Q24; none); greater(#0; #1)`
- Model: `greater(1.22; 1.28)`
- #0: operator chart_at -> greater
- #0 arg0: 'Image 9' -> '1.22'
- #0 arg1: 'Chi phí tín dụng' -> '1.28'
- #0 arg2: '3Q24' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 9; Tỷ lệ nợ xấu mới hình thành; 3Q24; none)
- #2: missing gold step #2: greater(#0; #1)

## Dòng 146 — 9e1128e4-ddb1-5e5e-89dc-69895eeaba16

Trong tháng 1/2025, dòng vốn vào quỹ cổ phiếu thị trường phát triển cao hơn quỹ cổ phiếu thị trường đang phát triển bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; Phát triển (DM); Jan-25; none); chart_at(Image 2; Đang phát triển (EM); Jan-25; none); subtract(#0; #1)`
- Model: `subtract(66.5; -1.1)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '66.5'
- #0 arg1: 'Phát triển (DM)' -> '-1.1'
- #0 arg2: 'Jan-25' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; Đang phát triển (EM); Jan-25; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 147 — 121939cc-fc09-5acf-89f7-a0697309d2cd

VNIndex đã thay đổi bao nhiêu phần trăm từ ngày 29/7/2022 đến ngày 31/8/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 29/7/2022; none); chart_at(Image 1; VNIndex; 31/8/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(1280.51; 1200); divide(#0; 1200); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1280.51'
- #0 arg1: 'VNIndex' -> '1200'
- #0 arg2: '29/7/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'VNIndex' -> '1200'
- #1 arg2: '31/8/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 148 — 16d8a36b-4aa2-5687-b9e4-d24d939c3457

Suất sinh lời theo tháng của nhóm Năng lượng đã thay đổi bao nhiêu điểm phần trăm từ tháng 9/2022 sang tháng 10/2022?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(-14.3; -12.3)`
- Model: `subtract(-14.3; -14.1)`
- #0 arg1: '-12.3' -> '-14.1'

## Dòng 149 — 532ca091-9dfe-5ac6-8581-e5103dcfb335

Mức thay đổi phần trăm trung bình của các cổ phiếu tác động tiêu cực nhất lên thị trường trong tháng 10 là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_average(Image 5; % +/-; none; none)`
- Model: `table_average(Table 1; Đả giảm; -26; none)`
- #0: operator chart_average -> table_average
- #0 arg0: 'Image 5' -> 'Table 1'
- #0 arg1: '% +/-' -> 'Đả giảm'
- #0 arg2: 'none' -> '-26'

## Dòng 150 — 0e4c653c-7cf8-5197-a11d-dd008a56f7da

Liệu hệ số P/E dự phóng năm 2024 của cổ phiếu IMP có cao hơn mức định giá P/E thấp nhất của cổ phiếu này trong giai đoạn 2019-2023 hay không?

- Nhãn: invalid_arity, invalid_source_type, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `greater(12.5; 13.23)`
- Model: `chart_min(Table 3; P/E 2024 (left); none; none); 12.5#none`
- Vi phạm kiểm tra: source_type@0:Table 3; unknown_operator@1:INVALID; arity@1:1!=4
- #0: operator greater -> chart_min
- #0 arg0: '12.5' -> 'Table 3'
- #0 arg1: '13.23' -> 'P/E 2024 (left)'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: INVALID(12.5#none)

## Dòng 151 — a00efea0-6d07-523f-b227-545fcba3c8e0

Tính theo mức điểm VNIndex tại ngày 31/8/2022 và 30/9/2022, chỉ số đã thay đổi bao nhiêu phần trăm trong tháng 9/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 31/8/2022; none); chart_at(Image 1; VNIndex; 30/9/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(1300; 1100); divide(#0; 1300); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1300'
- #0 arg1: 'VNIndex' -> '1100'
- #0 arg2: '31/8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'VNIndex' -> '1300'
- #1 arg2: '30/9/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 152 — 0002d3f2-7d30-533e-80bb-dc3a05ca6770

Trung bình mỗi tháng dòng vốn đầu tư chảy vào thị trường Việt Nam trong giai đoạn từ tháng 1/2024 đến tháng 1/2025 là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_average(Table 1; Vietnam; Jan-24; Jan-25)`
- Model: `table_average(Table 1; Việt Nam; Jan-24; Jan-25)`
- #0 arg1: 'Vietnam' -> 'Việt Nam'

## Dòng 153 — c1ea1492-1dfc-5d4c-a43c-dbd5309a15e6

Sản lượng tiêu thụ của BSR thay đổi bao nhiêu phần trăm từ 2024E sang 2025?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; Dầu khí - BSR; 2024E; none); chart_at(Image 3; Dầu khí - BSR; 2025; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `divide(3.1; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 3' -> '3.1'
- #0 arg1: 'Dầu khí - BSR' -> '100'
- #0 arg2: '2024E' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; Dầu khí - BSR; 2025; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 154 — 0edb77c7-efa4-5a50-a7ba-c8570d9cfeac

Tốc độ tăng trưởng lợi nhuận của các NHNY trong Q3/2024 chênh lệch bao nhiêu điểm phần trăm so với quý 2?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(17.7; 22.6)`
- Model: `subtract(17.7; 22.6)`

## Dòng 155 — 0b2bee3f-9aee-58c9-856b-21b4984a5d5c

Mức ROE dự phóng trung bình năm 2024 của các cổ phiếu y tế được phân tích là bao nhiêu phần trăm?

- Nhãn: invalid_reference, invalid_source_type, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_average(Table 2; ROE@2024F; none; none)`
- Model: `table_average(#1; ROE (post-tax); none; none)`
- Vi phạm kiểm tra: reference@0:#1; source_type@0:#1
- #0 arg0: 'Table 2' -> '#1'
- #0 arg1: 'ROE@2024F' -> 'ROE (post-tax)'

## Dòng 156 — cf650a58-551a-5244-a91f-02b912f431de

Mức chênh lệch giữa P/E 2025F cao nhất và thấp nhất của các cổ phiếu GAS, PVS, PVD, PLX và BSR là bao nhiêu lần?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 1; P/E@2025F; none; none); table_min(Table 1; P/E@2025F; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; P/E 2025F; none; none); chart_min(Image 1; P/E 2025F; none; none); subtract(#0; #1)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'P/E@2025F' -> 'P/E 2025F'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Image 1'
- #1 arg1: 'P/E@2025F' -> 'P/E 2025F'

## Dòng 157 — 77495d85-7c39-5aa9-a37b-3171b4b74b88

Trong tháng 10, mức % thay đổi thấp nhất của nhóm cổ phiếu tác động tiêu cực nhất lên thị trường là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_min(Image 5; % +/-; none; none)`
- Model: `table_min(Table 1; % +/-%; none; none)`
- #0: operator chart_min -> table_min
- #0 arg0: 'Image 5' -> 'Table 1'
- #0 arg1: '% +/-' -> '% +/-%'

## Dòng 158 — 03c0267b-0adc-58cf-9632-c39ee2bf6eac

Tăng trưởng NPATMI của NLG trong 2024F có lớn hơn mức của năm 2023 không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `greater(114.0; -13.0)`
- Model: `table_average(Table 2; NLG; 2023; none); table_average(Table 2; NLG; 2023; 2024F)`
- #0: operator greater -> table_average
- #0 arg0: '114.0' -> 'Table 2'
- #0 arg1: '-13.0' -> 'NLG'
- #0 arg2: '<absent>' -> '2023'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: table_average(Table 2; NLG; 2023; 2024F)

## Dòng 159 — 6a7c39db-9369-5550-8bd5-069d5f9e4b72

Mức biên lợi nhuận gộp cao nhất được dự phóng trong giai đoạn từ năm 2024 đến năm 2026 là bao nhiêu phần trăm?

- Nhãn: invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `table_max(Table 2; Biên lợi nhuận gộp (%); 2024F; 2026F)`
- Model: `subtract(#0; 7); divide(#1; 7); add(7; #2)`
- Vi phạm kiểm tra: reference@0:#0; reference@1:#1; reference@2:#2
- #0: operator table_max -> subtract
- #0 arg0: 'Table 2' -> '#0'
- #0 arg1: 'Biên lợi nhuận gộp (%)' -> '7'
- #0 arg2: '2024F' -> '<absent>'
- #0 arg3: '2026F' -> '<absent>'
- #1: extra predicted step #1: divide(#1; 7)
- #2: extra predicted step #2: add(7; #2)

## Dòng 160 — 891e8826-809a-54a0-b7cb-c6e9d9d096db

Chênh lệch giữa tỷ suất cổ tức 2024F cao nhất và thấp nhất trong nhóm các mã cổ phiếu được nêu là bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_max(Table 2; Tỷ suất cổ tức (%)@2024F; none; none); table_min(Table 2; Tỷ suất cổ tức (%)@2024F; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; Tỷ suất cổ tức (2024F; none; none); none); chart_min(Image 1; Tỷ suất cổ tức (2024F; none; none); none); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:3!=4; arity@1:3!=4
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 2' -> 'Image 1'
- #0 arg1: 'Tỷ suất cổ tức (%)@2024F' -> 'Tỷ suất cổ tức (2024F; none; none)'
- #0 arg3: 'none' -> '<absent>'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 2' -> 'Image 1'
- #1 arg1: 'Tỷ suất cổ tức (%)@2024F' -> 'Tỷ suất cổ tức (2024F; none; none)'
- #1 arg3: 'none' -> '<absent>'

## Dòng 161 — 3dc9bd3f-10d0-5374-899c-30932ca68f34

Với giả định doanh nghiệp không thể chuyển chi phí điện tăng thêm sang người tiêu dùng, mức giảm tối đa của tổng lợi nhuận trước thuế gấp bao nhiêu lần mức tăng giá vốn hàng bán của ngành Thép khi chi phí điện tăng 3%?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(15; 0.3)`
- Model: `divide(15; 100)`
- #0 arg1: '0.3' -> '100'

## Dòng 162 — e55302ea-d372-5528-986a-a0702b64dd46

Năm 2025, doanh thu dự phóng của Công ty FMCG chiếm bao nhiêu phần trăm tổng doanh thu dự phóng?

- Nhãn: both_math_only, invalid_reference, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, strict_invalid
- Ground truth: `divide(2185; 13600.9); multiply(#0; 100)`
- Model: `divide(904.2; 100); divide(#0; #2)`
- Vi phạm kiểm tra: reference@1:#2
- #0 arg0: '2185' -> '904.2'
- #0 arg1: '13600.9' -> '100'
- #1: operator multiply -> divide
- #1 arg1: '100' -> '#2'

## Dòng 163 — 8cc1c9e2-e8f2-506c-8790-759032f17147

Trong nhóm ngân hàng quốc doanh, ROE của VCB cao hơn BID bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `subtract(20.0; 19.1)`
- Model: `chart_at(Image 1; ROE; VN; none; 100); subtract(#0; 100); divide(#1; 100); multiply(#2; 100)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator subtract -> chart_at
- #0 arg0: '20.0' -> 'Image 1'
- #0 arg1: '19.1' -> 'ROE'
- #0 arg2: '<absent>' -> 'VN'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> '100'
- #1: extra predicted step #1: subtract(#0; 100)
- #2: extra predicted step #2: divide(#1; 100)
- #3: extra predicted step #3: multiply(#2; 100)

## Dòng 164 — 8d829101-30ce-504a-8f1d-9c4299018ae3

Mức giá mục tiêu trung bình trong 1 năm của các cổ phiếu dầu khí được phân tích là bao nhiêu đồng?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_average(Table 1; Giá mục tiêu (đồng)@Trong 1 năm; none; none)`
- Model: `table_average(Table 1; Giá mục tiêu 1 năm; none; none)`
- #0 arg1: 'Giá mục tiêu (đồng)@Trong 1 năm' -> 'Giá mục tiêu 1 năm'

## Dòng 165 — ad9115dc-b52c-5bd2-89ea-6433b9a46538

Trong năm 2023, doanh thu từ mảng Bất động sản chiếm tỷ lệ bao nhiêu so với tổng doanh thu của DPG?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(26; 3450)`
- Model: `divide(26; 345)`
- #0 arg1: '3450' -> '345'

## Dòng 166 — 1ae1f424-e901-5b8a-923a-cc4ca2e93a8a

Chênh lệch giữa mức tác động lên %GVHB cao nhất và thấp nhất của các ngành thép, hóa chất, xi măng và giấy khi giá điện tăng 3% là bao nhiêu điểm phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_max(Image 2; %GVHB; none; none); chart_min(Image 2; %GVHB; none; none); subtract(#0; #1)`
- Model: `table_max(Table 1; %GVHB; Thép; Xi măng); table_min(Table 1; %GVHB; Thép; Xi măng); subtract(#0; #1)`
- #0: operator chart_max -> table_max
- #0 arg0: 'Image 2' -> 'Table 1'
- #0 arg2: 'none' -> 'Thép'
- #0 arg3: 'none' -> 'Xi măng'
- #1: operator chart_min -> table_min
- #1 arg0: 'Image 2' -> 'Table 1'
- #1 arg2: 'none' -> 'Thép'
- #1 arg3: 'none' -> 'Xi măng'

## Dòng 167 — 6c8ddd9c-3901-5d52-b2f5-e6240c8cd30f

Năm 2026, chênh lệch giữa biên lợi nhuận ròng của Nova Consumer được tính từ lợi nhuận ròng chia cho doanh thu và biên lợi nhuận ròng được báo cáo là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Doanh thu; 2026; none); chart_at(Image 3; Lợi nhuận ròng; 2026; none); divide(#1; #0); multiply(#2; 100); chart_at(Image 3; Biên lợi nhuận ròng; 2026; none); subtract(#3; #4)`
- Model: `subtract(7.14; 5.8)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '7.14'
- #0 arg1: 'Doanh thu' -> '5.8'
- #0 arg2: '2026' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; Lợi nhuận ròng; 2026; none)
- #2: missing gold step #2: divide(#1; #0)
- #3: missing gold step #3: multiply(#2; 100)
- #4: missing gold step #4: chart_at(Image 3; Biên lợi nhuận ròng; 2026; none)
- #5: missing gold step #5: subtract(#3; #4)

## Dòng 168 — 9a618d93-3814-5a14-9f7e-6d8df7788ffa

Độ chênh lệch giữa mức tăng trưởng hàng tháng cao nhất và thấp nhất của chỉ số VN-Index trong 9 tháng đầu năm 2022 là bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; VN-Index; T1/2022; T9/2022); table_min(Table 1; VN-Index; T1/2022; T9/2022); subtract(#0; #1)`
- Model: `table_max(Table 1; Tăng trưởng HĐTM; none; none); table_min(Table 1; Tăng trưởng HĐTM; none; none); subtract(#0; #1)`
- #0 arg1: 'VN-Index' -> 'Tăng trưởng HĐTM'
- #0 arg2: 'T1/2022' -> 'none'
- #0 arg3: 'T9/2022' -> 'none'
- #1 arg1: 'VN-Index' -> 'Tăng trưởng HĐTM'
- #1 arg2: 'T1/2022' -> 'none'
- #1 arg3: 'T9/2022' -> 'none'

## Dòng 169 — 0ffc6b47-7493-59ad-b0a7-78247c657723

Khi giá bán lẻ điện bình quân tăng 3%, mức thay đổi tỷ lệ giá vốn hàng bán (%GVHB) của ngành Xi măng cao hơn ngành Thép bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; %GVHB; Xi măng; none); chart_at(Image 2; %GVHB; Thép; none); subtract(#0; #1)`
- Model: `subtract(-13; -15)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '-13'
- #0 arg1: '%GVHB' -> '-15'
- #0 arg2: 'Xi măng' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; %GVHB; Thép; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 170 — 4ca15f1a-7c66-5173-82ce-1f8459572e19

Tăng trưởng NPATMI dự phóng năm 2025 của PVD có cao hơn PVS không?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `greater(50.1; 22.8)`
- Model: `chart_average(Image 1; 2025; none; none`
- Vi phạm kiểm tra: unbalanced_parentheses; unknown_operator@0:INVALID; arity@0:1!=4
- #0: operator greater -> INVALID
- #0 arg0: '50.1' -> 'chart_average(Image 1; 2025; none; none'
- #0 arg1: '22.8' -> '<absent>'

## Dòng 171 — c16ef52b-ff9f-52b4-807c-669a4983a82c

Trung bình mức thay đổi giá của nhóm ngành Tài chính trong 3 quý đầu năm 2023 là bao nhiêu phần trăm?

- Nhãn: invalid_arity, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_average(Table 1; Tài chính; 1Q23; 3Q23)`
- Model: `chart_average(Table 1; Tài chính; Q1/23; none; Q3/23)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 1
- #0: operator table_average -> chart_average
- #0 arg2: '1Q23' -> 'Q1/23'
- #0 arg3: '3Q23' -> 'none'
- #0 arg4: '<absent>' -> 'Q3/23'

## Dòng 172 — 57cb44d1-cc2a-589d-844a-52343018e682

Khi giá điện tăng 3%, mức tăng giá vốn hàng bán trung bình của bốn ngành thép, hóa chất, xi măng và giấy là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_average(Table 1; Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%; none; none)`
- Model: `table_average(Table 1; %GVHB; Thép; Hóa Chất; Xi măng)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0 arg1: 'Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%' -> '%GVHB'
- #0 arg2: 'none' -> 'Thép'
- #0 arg3: 'none' -> 'Hóa Chất'
- #0 arg4: '<absent>' -> 'Xi măng'

## Dòng 173 — 16630d77-0f27-526b-85c6-5ccb5a90a26e

Mức biên lãi gộp cao nhất mà doanh nghiệp ghi nhận trong giai đoạn từ năm tài chính 2015 đến 2020 là bao nhiêu phần trăm?

- Nhãn: invalid_arity, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_max(Table 1; Biên lãi gộp (%); FY 2015; FY2020(F))`
- Model: `chart_max(#1; none; none; 2015; 2020)`
- Vi phạm kiểm tra: arity@0:5!=4; reference@0:#1; source_type@0:#1
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> '#1'
- #0 arg1: 'Biên lãi gộp (%)' -> 'none'
- #0 arg2: 'FY 2015' -> 'none'
- #0 arg3: 'FY2020(F)' -> '2015'
- #0 arg4: '<absent>' -> '2020'

## Dòng 174 — 6374e09d-27e7-5d3c-b83e-168bf9321aeb

Dòng vốn đầu tư vào thị trường Ấn Độ trong tháng 8/2023 đã thay đổi bao nhiêu phần trăm so với tháng 7/2023?

- Nhãn: both_math_only, invalid_reference, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, strict_invalid
- Ground truth: `subtract(1.751; 2.821); divide(#0; 2.821); multiply(#1; 100)`
- Model: `divide(#1; 0.5); subtract(#0; 1); multiply(#1; 100)`
- Vi phạm kiểm tra: reference@0:#1
- #0: operator subtract -> divide
- #0 arg0: '1.751' -> '#1'
- #0 arg1: '2.821' -> '0.5'
- #1: operator divide -> subtract
- #1 arg1: '2.821' -> '1'

## Dòng 175 — ecc0e965-2d46-5ecc-aa2a-f4ceb76cd47e

Trong danh sách các cổ phiếu được khuyến nghị, mức giá mục tiêu cơ bản cao nhất là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Giá mục tiêu cơ bản; none; none)`
- Model: `table_max(Table 1; Mức giá mục tiêu cơ bản; none; none)`
- #0 arg1: 'Giá mục tiêu cơ bản' -> 'Mức giá mục tiêu cơ bản'

## Dòng 176 — 70c37cdb-414c-5e81-93c9-8d815e19ab87

Trong giai đoạn được thống kê, mức chênh lệch giữa giá trị lũy kế cao nhất và thấp nhất của dòng tiền vào các quỹ cổ phiếu tại thị trường Việt Nam là bao nhiêu tỷ USD?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 4; Việt Nam; none; none); chart_min(Image 4; Việt Nam; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 4; TRỤC Y - Tr. USD; none; none); chart_min(Image 5; DM Equity; none; none); subtract(#0; #1)`
- #0 arg1: 'Việt Nam' -> 'TRỤC Y - Tr. USD'
- #1 arg0: 'Image 4' -> 'Image 5'
- #1 arg1: 'Việt Nam' -> 'DM Equity'

## Dòng 177 — f83eb72a-8395-59ed-8563-859275237988

Trong giai đoạn bứt phá, mức sinh lời của ngành Bán lẻ có cao hơn Dịch vụ tài chính không?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `greater(36.78; 34.41)`
- Model: `multiply(11.4; 100)`
- #0: operator greater -> multiply
- #0 arg0: '36.78' -> '11.4'
- #0 arg1: '34.41' -> '100'

## Dòng 178 — 72a604ca-774a-534f-aa88-2afbcee1fcce

Trong tháng 8/2022, tổng thanh khoản của ba nhóm VN30, VNMidcap và VNSmallcap là bao nhiêu?

- Nhãn: fewer_steps, invalid_math_argument, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; VN30; T8/2022; none); chart_at(Image 2; VNMidcap; T8/2022; none); chart_at(Image 2; VNSmallcap; T8/2022; none); add(#0; #1); add(#3; #2)`
- Model: `add(VN30; VNMidcap); add(#0; VNSmallcap)`
- Vi phạm kiểm tra: math_type@0:VN30; math_type@0:VNMidcap; math_type@1:VNSmallcap
- #0: operator chart_at -> add
- #0 arg0: 'Image 2' -> 'VN30'
- #0 arg1: 'VN30' -> 'VNMidcap'
- #0 arg2: 'T8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> add
- #1 arg0: 'Image 2' -> '#0'
- #1 arg1: 'VNMidcap' -> 'VNSmallcap'
- #1 arg2: 'T8/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: chart_at(Image 2; VNSmallcap; T8/2022; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 179 — c3685869-6e02-5034-a125-d8f8a5da1f70

Trong tháng 1/2025, dòng vốn vào quỹ cổ phiếu tại các thị trường phát triển ngoài Mỹ tương đương bao nhiêu phần của tổng dòng vốn vào quỹ cổ phiếu toàn cầu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; Phát triển (DM); Jan-25; none); subtract(#0; 46.495); chart_at(Image 1; Cổ phiếu; Jan-25; none); divide(#1; #2)`
- Model: `divide(6; 100); multiply(#0; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '6'
- #0 arg1: 'Phát triển (DM)' -> '100'
- #0 arg2: 'Jan-25' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator subtract -> multiply
- #1 arg1: '46.495' -> '100'
- #2: missing gold step #2: chart_at(Image 1; Cổ phiếu; Jan-25; none)
- #3: missing gold step #3: divide(#1; #2)

## Dòng 180 — 36cf6f60-9d24-5872-b074-c147675d7a8e

Mức thay đổi giá trung bình trong tháng 12 của ba nhóm ngành Bán lẻ, Thực phẩm và đồ uống, và Du lịch và Giải trí là bao nhiêu phần trăm?

- Nhãn: fewer_steps, invalid_arity, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; T12; Bán lẻ; none); chart_at(Image 1; T12; Thực phẩm và đồ uống; none); chart_at(Image 1; T12; Du lịch và Giải trí; none); add(#0; #1); add(#3; #2); divide(#4; 3)`
- Model: `chart_average(Table 1; Bán lẻ; none; Thực phẩm đồ uống; Du lịch giải trí)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 1
- #0: operator chart_at -> chart_average
- #0 arg0: 'Image 1' -> 'Table 1'
- #0 arg1: 'T12' -> 'Bán lẻ'
- #0 arg2: 'Bán lẻ' -> 'none'
- #0 arg3: 'none' -> 'Thực phẩm đồ uống'
- #0 arg4: '<absent>' -> 'Du lịch giải trí'
- #1: missing gold step #1: chart_at(Image 1; T12; Thực phẩm và đồ uống; none)
- #2: missing gold step #2: chart_at(Image 1; T12; Du lịch và Giải trí; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)
- #5: missing gold step #5: divide(#4; 3)

## Dòng 181 — b95428d9-e2a1-5042-bc19-31254034184e

Giá trị giao dịch bình quân phiên trên sàn HOSE trong tháng 10 thấp hơn bao nhiêu nghìn tỷ đồng so với mức bình quân của 9 tháng đầu năm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(14.9; 14.4)`
- Model: `subtract(14.9; 14.4)`

## Dòng 182 — fbc74d91-1edb-5af7-aac2-da69cab23a26

Dựa trên kế hoạch LNST năm 2020 và tỷ lệ hoàn thành sau 3 tháng đầu năm của HBC, công ty ước đã thực hiện được bao nhiêu tỷ đồng LNST trong 3 tháng đầu năm 2020?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `multiply(125; 0.04)`
- Model: `divide(125; 4)`
- #0: operator multiply -> divide
- #0 arg1: '0.04' -> '4'

## Dòng 183 — dd392d85-1c2c-597f-85f1-d0b4de549ce9

Khoảng chênh lệch giữa mức doanh thu dự phóng cao nhất và thấp nhất của mảng heo hơi trong giai đoạn 2022-2026 là bao nhiêu tỷ đồng?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_max(Table 1; Heo hơi; 2022; 2026); table_min(Table 1; Heo hơi; 2022; 2026); subtract(#0; #1)`
- Model: `table_max(Table 1; Heo; none; 2022; 2026); table_min(Table 1; Heo; none; 2022; 2026); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0 arg1: 'Heo hơi' -> 'Heo'
- #0 arg2: '2022' -> 'none'
- #0 arg3: '2026' -> '2022'
- #0 arg4: '<absent>' -> '2026'
- #1 arg1: 'Heo hơi' -> 'Heo'
- #1 arg2: '2022' -> 'none'
- #1 arg3: '2026' -> '2022'
- #1 arg4: '<absent>' -> '2026'

## Dòng 184 — b1b311e9-864a-5cc4-8a92-a71057aec326

Tỷ lệ giữa chi phí dự phòng (Prov.) và chi phí hoạt động (OPEX) của 9 ngân hàng trong nhóm theo dõi vào năm 2023 là bao nhiêu?

- Nhãn: fewer_steps, invalid_source_type, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; Prov.; 2023; none); chart_at(Image 1; OPEX; 2023; none); divide(#0; #1)`
- Model: `chart_average(Table 1; Prov; OPEX; none)`
- Vi phạm kiểm tra: source_type@0:Table 1
- #0: operator chart_at -> chart_average
- #0 arg0: 'Image 1' -> 'Table 1'
- #0 arg1: 'Prov.' -> 'Prov'
- #0 arg2: '2023' -> 'OPEX'
- #1: missing gold step #1: chart_at(Image 1; OPEX; 2023; none)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 185 — 18edb297-4a99-597d-be14-b6373e9cb94e

Dựa trên mức vào ròng tháng 10 của quỹ tiền tệ và tỷ lệ thấp hơn so với tháng trước, dòng vốn vào quỹ tiền tệ của tháng trước được hàm ý là bao nhiêu tỷ USD?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `multiply(6.1; 10)`
- Model: `divide(6.1; 100)`
- #0: operator multiply -> divide
- #0 arg1: '10' -> '100'

## Dòng 186 — cdd6a41c-564a-5146-845a-dd729fd0c4af

Tỷ lệ giữa lợi nhuận trên mỗi cổ phiếu (EPS) dự phóng năm 2024 và giá hiện tại của cổ phiếu IMP là bao nhiêu?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(4863; 61100)`
- Model: `divide(14.4; 100); divide(#0; 61000)`
- #0 arg0: '4863' -> '14.4'
- #0 arg1: '61100' -> '100'
- #1: extra predicted step #1: divide(#0; 61000)

## Dòng 187 — 3268ef4f-6cf3-57d8-9b21-9ad8cd22c3d7

Tỷ lệ Nợ/EBITDA dự phóng năm 2022 có lớn hơn tỷ lệ Nợ/EBITDA dự phóng năm 2026 không?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 4; Nợ/ EBITDA; 2022; none); chart_at(Image 4; Nợ/ EBITDA; 2026; none); greater(#0; #1)`
- Model: `greater(0.38; 0.18)`
- #0: operator chart_at -> greater
- #0 arg0: 'Image 4' -> '0.38'
- #0 arg1: 'Nợ/ EBITDA' -> '0.18'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 4; Nợ/ EBITDA; 2026; none)
- #2: missing gold step #2: greater(#0; #1)

## Dòng 188 — 95039a40-3e8a-5dc7-890c-e1472903f136

P/E ước tính cho năm tài chính hiện tại tại thời điểm 1/2/2022 đã thay đổi bao nhiêu phần trăm so với thời điểm 1/2/2021?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2021; none); chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `divide(13; 11)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '13'
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> '11'
- #0 arg2: '1/2/2021' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2022; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 189 — 21bbe424-7022-525c-b415-077330433d10

Năm 2023, thu nhập lãi thuần (NII) của 9 ngân hàng trong nhóm theo dõi cao hơn chi phí hoạt động (OPEX) bao nhiêu nghìn tỷ đồng?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NII; 2023; none); chart_at(Image 1; OPEX; 2023; none); subtract(#0; #1)`
- Model: `subtract(52; 30)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '52'
- #0 arg1: 'NII' -> '30'
- #0 arg2: '2023' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; OPEX; 2023; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 190 — fb615f16-7dcd-5ab0-9e4a-14f3cda842d8

Tỷ lệ thanh khoản của nhóm VN30 so với tổng thanh khoản của chỉ số VNIndex trong tháng 8/2022 là bao nhiêu?

- Nhãn: fewer_steps, invalid_math_argument, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; VN30; T8/2022; none); chart_at(Image 2; VNIndex; T8/2022; none); divide(#0; #1)`
- Model: `divide(14; 1.206.33); multiply(#0; 100)`
- Vi phạm kiểm tra: math_type@0:1.206.33
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '14'
- #0 arg1: 'VN30' -> '1.206.33'
- #0 arg2: 'T8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> multiply
- #1 arg0: 'Image 2' -> '#0'
- #1 arg1: 'VNIndex' -> '100'
- #1 arg2: 'T8/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: divide(#0; #1)

## Dòng 191 — f29449b3-dc21-58a6-9222-747718073537

Tốc độ tăng trưởng lợi nhuận của các NHNY trong Q3/2024 gấp bao nhiêu lần so với quý 1/2024?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `divide(17.7; 9.5)`
- Model: `divide(17.7; 9.5)`

## Dòng 192 — 39177476-f3d1-5398-820a-971b29972107

Tỷ lệ tăng trưởng dự phóng của lợi nhuận ròng từ năm 2022 đến năm 2026 là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; Lợi nhuận ròng; 2022; none); chart_at(Image 3; Lợi nhuận ròng; 2026; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(1224; 332.6); divide(#0; 332.6); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 3' -> '1224'
- #0 arg1: 'Lợi nhuận ròng' -> '332.6'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 3' -> '#0'
- #1 arg1: 'Lợi nhuận ròng' -> '332.6'
- #1 arg2: '2026' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 193 — 2112c88c-d9e5-5b8c-aacf-a2b9e00eb002

Tăng trưởng huy động từ đầu năm trung bình của năm 2023 trong ba tháng cuối năm là bao nhiêu phần trăm?

- Nhãn: invalid_arity, invalid_source_type, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_average(Image 1; 2023; Oct; Dec)`
- Model: `chart_average(Table 2; Tăng trưởng huy động; none; Dec-23; Sep-23)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 2
- #0 arg0: 'Image 1' -> 'Table 2'
- #0 arg1: '2023' -> 'Tăng trưởng huy động'
- #0 arg2: 'Oct' -> 'none'
- #0 arg3: 'Dec' -> 'Dec-23'
- #0 arg4: '<absent>' -> 'Sep-23'

## Dòng 194 — 9b627d6d-4266-5e18-8704-d33b8e236c0a

Nếu dùng tỷ lệ tăng của giá điện bình quân từ 2022 sang 2023 làm cùng một cú sốc đầu vào, thì tác động bình quân lên GVHB của 4 ngành Thép, Hóa chất, Xi măng và Giấy cao hơn tác động trực tiếp lên CPI theo tỷ trọng điện trong rổ CPI bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Giá điện; 2022; none); chart_at(Image 1; Giá điện; 2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); multiply(#4; 3.5); divide(#5; 100); table_average(Table 1; Tỷ trọng Chi phí điện/GVHB; none; none); multiply(#4; #7); divide(#8; 100); subtract(#9; #6)`
- Model: `divide(1920; 1864)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '1920'
- #0 arg1: 'Giá điện' -> '1864'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Giá điện; 2023; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: multiply(#4; 3.5)
- #6: missing gold step #6: divide(#5; 100)
- #7: missing gold step #7: table_average(Table 1; Tỷ trọng Chi phí điện/GVHB; none; none)
- #8: missing gold step #8: multiply(#4; #7)
- #9: missing gold step #9: divide(#8; 100)
- #10: missing gold step #10: subtract(#9; #6)

## Dòng 195 — e24d7dc4-55df-51d0-91ea-22f04eb4ee1e

Tổng tác động ròng lên VNIndex của nhóm cổ phiếu tác động tích cực nhất và nhóm cổ phiếu tác động tiêu cực nhất trong tháng 8 là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_sum(Image 3; VNIndex; none; none); chart_sum(Image 4; VNIndex; none; none); add(#0; #1)`
- Model: `subtract(12.4; -3.6)`
- #0: operator chart_sum -> subtract
- #0 arg0: 'Image 3' -> '12.4'
- #0 arg1: 'VNIndex' -> '-3.6'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_sum(Image 4; VNIndex; none; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 196 — c17a6aee-5e61-5902-9636-784a15cc8532

Mức thay đổi giá cổ phiếu tương đối trung bình của DPG trong các kỳ 1 tháng, 6 tháng và 12 tháng là bao nhiêu phần trăm?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_average(Table 1; Tương đối; 1M; 12M)`
- Model: `chart_average(Table 1; Change; none; none)`
- Vi phạm kiểm tra: source_type@0:Table 1
- #0: operator table_average -> chart_average
- #0 arg1: 'Tương đối' -> 'Change'
- #0 arg2: '1M' -> 'none'
- #0 arg3: '12M' -> 'none'

## Dòng 197 — 33017547-48e2-500d-9451-06b2441ab1d1

Trong dòng vốn đầu tư vào các tài sản tài chính theo tháng, dòng vốn vào cổ phiếu thay đổi bao nhiêu phần trăm từ tháng 12/2024 sang tháng 1/2025?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Cổ phiếu; Dec-24; none); chart_at(Image 1; Cổ phiếu; Jan-25; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `divide(64.7; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '64.7'
- #0 arg1: 'Cổ phiếu' -> '100'
- #0 arg2: 'Dec-24' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Cổ phiếu; Jan-25; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 198 — af7524c6-5e6e-554c-978b-32f19bf2c364

Trong năm 2020, mức P/E ước tính cho năm tài chính hiện tại đạt giá trị cao nhất là bao nhiêu?

- Nhãn: invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_max(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2020; 11/2/2020)`
- Model: `table_max(#1; 2020; none; none)`
- Vi phạm kiểm tra: reference@0:#1; source_type@0:#1
- #0: operator chart_max -> table_max
- #0 arg0: 'Image 1' -> '#1'
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> '2020'
- #0 arg2: '1/2/2020' -> 'none'
- #0 arg3: '11/2/2020' -> 'none'

## Dòng 199 — a573cd27-521f-59ba-ac20-dbeaeca396b5

Mức thay đổi giá của nhóm ngành Công nghệ thông tin vượt trội hơn bao nhiêu phần trăm so với mức thay đổi của chỉ số VN-Index trong năm 2023?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff
- Ground truth: `subtract(23.5; 2.1)`
- Model: `table_average(Table 1; Công nghệ thông tin; none; none)`
- #0: operator subtract -> table_average
- #0 arg0: '23.5' -> 'Table 1'
- #0 arg1: '2.1' -> 'Công nghệ thông tin'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'

## Dòng 200 — 17deebd3-b46f-5ead-987d-218326e01bcd

Mức chênh lệch giữa sản lượng cao nhất và thấp nhất của lưu vực khí Nam Côn Sơn 2 trong toàn bộ giai đoạn được thống kê và dự báo là bao nhiêu tỷ m3/năm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 2; Nam Côn Sơn 2; none; none); chart_min(Image 2; Nam Côn Sơn 2; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 3; Nam Côn Sơn 2; none; none); chart_min(Image 3; Nam Côn Sơn 2; none; none); subtract(#0; #1)`
- #0 arg0: 'Image 2' -> 'Image 3'
- #1 arg0: 'Image 2' -> 'Image 3'

## Dòng 201 — 5a3e25ed-019d-5506-9973-1dac72317fc9

Công suất dự kiến của dự án LNG Sơn Mỹ trong giai đoạn 2 lớn hơn bao nhiêu triệu tấn so với giai đoạn đầu tiên?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(6; 3.6)`
- Model: `subtract(6; 3.6)`

## Dòng 202 — f58484f7-b57c-5e11-b659-0f8b48482df9

Chênh lệch lợi suất năm 2023 giữa nhóm Dịch vụ tài chính và Dầu khí là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(69.4; 36)`
- Model: `subtract(69.4; 36)`

## Dòng 203 — 31c60903-c8c2-5ac9-a1b7-86722d03ac00

Trong nhóm các cổ phiếu tác động tích cực nhất đến thị trường trong tháng, mức đóng góp điểm số vào Index của mã SSB lớn gấp bao nhiêu lần so với mã LPB?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Index; SSB; none); chart_at(Image 1; Index; LPB; none); divide(#0; #1)`
- Model: `divide(0.5; 0.4)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '0.5'
- #0 arg1: 'Index' -> '0.4'
- #0 arg2: 'SSB' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Index; LPB; none)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 204 — 26286d85-62c0-5ae6-89e7-5dd2f949b498

Mức thay đổi theo điểm phần trăm của tăng trưởng NPATMI ngành Bất động sản từ năm 2023 sang 2024F là bao nhiêu?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `subtract(10.9; -0.5)`
- Model: `table_average(Table 2; NPATMI; none; 2023; 2024F)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator subtract -> table_average
- #0 arg0: '10.9' -> 'Table 2'
- #0 arg1: '-0.5' -> 'NPATMI'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> '2023'
- #0 arg4: '<absent>' -> '2024F'

## Dòng 205 — a09d5735-8ea4-59a2-a208-c1aaa471dedf

Khoảng chênh lệch giữa mức cao nhất và thấp nhất của chỉ số P/E ước tính cho năm tài chính hiện tại trong năm 2022 là bao nhiêu?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_max(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2022; 11/2/2022); chart_min(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2022; 11/2/2022); subtract(#0; #1)`
- Model: `subtract(#1; #0)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#0
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 1' -> '#1'
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> '#0'
- #0 arg2: '1/2/2022' -> '<absent>'
- #0 arg3: '11/2/2022' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2022; 11/2/2022)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 206 — 53ee3099-ed36-50be-a8af-5c06b827f9ba

Tính đến tháng 1 năm 2025, lũy kế dòng tiền vào các quỹ cổ phiếu tại thị trường Ấn Độ chênh lệch bao nhiêu tỷ USD so với thị trường Thái Lan?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_at(Image 3; Ấn Độ; Jan-25; none); chart_at(Image 3; Thái Lan; Jan-25; none); subtract(#0; #1)`
- Model: `table_sum(Table 1; India; Jan-25; none); table_sum(Table 1; Thailand; Jan-25; none); subtract(#0; #1)`
- #0: operator chart_at -> table_sum
- #0 arg0: 'Image 3' -> 'Table 1'
- #0 arg1: 'Ấn Độ' -> 'India'
- #1: operator chart_at -> table_sum
- #1 arg0: 'Image 3' -> 'Table 1'
- #1 arg1: 'Thái Lan' -> 'Thailand'

## Dòng 207 — e9e428c0-ed05-58a9-a959-a21762ee77c0

Dựa trên doanh thu dự phóng năm 2026, biên EBITDA năm 2026 và tỷ lệ Nợ/EBITDA năm 2026, mức nợ ước tính của Nova Consumer trong năm 2026 là bao nhiêu tỷ đồng?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Doanh thu; 2026; none); chart_at(Image 1; Biên EBITDA; 2026; none); multiply(#0; #1); divide(#2; 100); chart_at(Image 4; Nợ/ EBITDA; 2026; none); multiply(#3; #4)`
- Model: `divide(1224; 11.61); multiply(#0; 100); divide(#1; 0.18)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '1224'
- #0 arg1: 'Doanh thu' -> '11.61'
- #0 arg2: '2026' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> multiply
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Biên EBITDA' -> '100'
- #1 arg2: '2026' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator multiply -> divide
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '0.18'
- #3: missing gold step #3: divide(#2; 100)
- #4: missing gold step #4: chart_at(Image 4; Nợ/ EBITDA; 2026; none)
- #5: missing gold step #5: multiply(#3; #4)

## Dòng 208 — ebe9aa65-55be-58ca-ab9c-c9162488d824

Năm 2022, sản lượng tiêu thụ khí khô (bao gồm LNG) của GAS tương đương bao nhiêu lần tổng sản lượng từ bốn lưu vực khí chính Cửu Long, Nam Côn Sơn 1, Nam Côn Sơn 2 và PM3 sau khi quy đổi về cùng đơn vị?

- Nhãn: fewer_steps, invalid_arity, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; Cửu Long; 2022; none); chart_at(Image 2; Nam Côn Sơn 1; 2022; none); add(#0; #1); chart_at(Image 2; Nam Côn Sơn 2; 2022; none); add(#2; #3); chart_at(Image 2; PM3; 2022; none); add(#4; #5); chart_at(Image 3; Khí khô (bao gồm LNG) - GAS; 2022; none); multiply(#6; 1000); divide(#7; #8)`
- Model: `chart_average(Image 2; Cổ phiếu khí; 2022; none; none`
- Vi phạm kiểm tra: unbalanced_parentheses; unknown_operator@0:INVALID; arity@0:1!=4
- #0: operator chart_at -> INVALID
- #0 arg0: 'Image 2' -> 'chart_average(Image 2; Cổ phiếu khí; 2022; none; none'
- #0 arg1: 'Cửu Long' -> '<absent>'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; Nam Côn Sơn 1; 2022; none)
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: chart_at(Image 2; Nam Côn Sơn 2; 2022; none)
- #4: missing gold step #4: add(#2; #3)
- #5: missing gold step #5: chart_at(Image 2; PM3; 2022; none)
- #6: missing gold step #6: add(#4; #5)
- #7: missing gold step #7: chart_at(Image 3; Khí khô (bao gồm LNG) - GAS; 2022; none)
- #8: missing gold step #8: multiply(#6; 1000)
- #9: missing gold step #9: divide(#7; #8)

## Dòng 209 — 921dc32d-c40f-5e33-89f2-72adb3e61f24

Tổng giá trị giao dịch ròng của nhà đầu tư nước ngoài tại ba cổ phiếu HPG, PVD và DGC là bao nhiêu tỷ đồng?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 6; GTGD ròng NĐTNN; HPG; none); chart_at(Image 6; GTGD ròng NĐTNN; PVD; none); chart_at(Image 6; GTGD ròng NĐTNN; DGC; none); add(#0; #1); add(#3; #2)`
- Model: `add(600; 400); add(#0; 300)`
- #0: operator chart_at -> add
- #0 arg0: 'Image 6' -> '600'
- #0 arg1: 'GTGD ròng NĐTNN' -> '400'
- #0 arg2: 'HPG' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> add
- #1 arg0: 'Image 6' -> '#0'
- #1 arg1: 'GTGD ròng NĐTNN' -> '300'
- #1 arg2: 'PVD' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: chart_at(Image 6; GTGD ròng NĐTNN; DGC; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 210 — ba0292f4-30a0-5a33-883e-7c96eee77430

Trong năm 2023, mức tăng trưởng huy động từ đầu năm cao nhất theo tháng là bao nhiêu phần trăm?

- Nhãn: invalid_arity, invalid_reference, invalid_source_type, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; 2023; Jan; Dec)`
- Model: `chart_max(#1; Tăng trưởng huy động theo tháng; none; Jan-23; none)`
- Vi phạm kiểm tra: arity@0:5!=4; reference@0:#1; source_type@0:#1
- #0 arg0: 'Image 1' -> '#1'
- #0 arg1: '2023' -> 'Tăng trưởng huy động theo tháng'
- #0 arg2: 'Jan' -> 'none'
- #0 arg3: 'Dec' -> 'Jan-23'
- #0 arg4: '<absent>' -> 'none'

## Dòng 211 — 10876bf5-a133-5d02-a563-fd29992fcccb

Trong giai đoạn 2022-2026, tỷ lệ Nợ/Vốn chủ sở hữu dự phóng thấp nhất là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_min(Image 4; Nợ/ Vốn chủ sở hữu; 2022; 2026)`
- Model: `chart_min(Image 4; Nợ/Vốn chủ sở hữu; 2022; 2026)`
- #0 arg1: 'Nợ/ Vốn chủ sở hữu' -> 'Nợ/Vốn chủ sở hữu'

## Dòng 212 — 6b0cfb1c-18fb-56a9-a9fd-75978f962cd3

Giá bán lẻ điện bình quân từ năm 2009 đến năm 2023 đã tăng bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Giá điện; 2009; none); chart_at(Image 1; Giá điện; 2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(1920; 100); divide(#0; 100); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1920'
- #0 arg1: 'Giá điện' -> '100'
- #0 arg2: '2009' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Giá điện' -> '100'
- #1 arg2: '2023' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 213 — 713a60fb-050c-5404-8a2e-aad42a43292f

Doanh thu dự phóng của Nova Consumer tăng bao nhiêu phần trăm từ năm 2022 đến năm 2026?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Doanh thu; 2022; none); chart_at(Image 1; Doanh thu; 2026; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(1224; 332.6); divide(#0; 332.6); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1224'
- #0 arg1: 'Doanh thu' -> '332.6'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Doanh thu' -> '332.6'
- #1 arg2: '2026' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 214 — 1329c396-d5e8-5b57-bcf9-1f5a4f9a70c6

Giá trị dòng tiền trung bình của VNIndex qua toàn bộ các giai đoạn được thống kê là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_average(Image 3; VNIndex; none; none)`
- Model: `chart_average(Image 1; VNIndex; none; none)`
- #0 arg0: 'Image 3' -> 'Image 1'

## Dòng 215 — 92b845ce-5fc5-5e46-a539-1b7c48f40486

Chênh lệch giữa mức thay đổi của ngành Bán lẻ trong tháng 12 và mức thay đổi của ngành này ở giai đoạn hồi phục là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; T12; Bán lẻ; none); subtract(#0; 14.2)`
- Model: `divide(11.4; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '11.4'
- #0 arg1: 'T12' -> '100'
- #0 arg2: 'Bán lẻ' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: subtract(#0; 14.2)

## Dòng 216 — 07893d87-be07-5109-b499-9fff1e5283dc

NIM hàm ý của ngành ngân hàng trong Q2/2024 là bao nhiêu trước khi giảm theo quý trong Q3/2024?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(22; 100); add(3.47; #0)`
- Model: `subtract(3.62; 3.47)`
- #0: operator divide -> subtract
- #0 arg0: '22' -> '3.62'
- #0 arg1: '100' -> '3.47'
- #1: missing gold step #1: add(3.47; #0)

## Dòng 217 — 5eee0e5f-2e41-5c46-bec5-9b0000cde084

Tổng thu nhập hoạt động (TOI) ước tính của các ngân hàng trong năm 2023 là bao nhiêu nghìn tỷ đồng, dựa trên khoản thu nhập từ giao dịch trái phiếu chính phủ và tỷ trọng của khoản này trong TOI cùng năm?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `divide(2.4; 100); divide(12.1; #0)`
- Model: `divide(50; 2.4); multiply(#0; 100)`
- #0 arg0: '2.4' -> '50'
- #0 arg1: '100' -> '2.4'
- #1: operator divide -> multiply
- #1 arg0: '12.1' -> '#0'
- #1 arg1: '#0' -> '100'

## Dòng 218 — 2fa6c18b-8d9d-5f37-a4b0-7eaaa852622b

Trong năm 2022, mức chênh lệch giữa tổng sản lượng từ các lưu vực khí chính và sản lượng tiêu thụ khí khô (bao gồm LNG) của GAS là bao nhiêu tỷ m3?

- Nhãn: fewer_steps, invalid_arity, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; Cửu Long; 2022; none); chart_at(Image 2; Nam Côn Sơn 1; 2022; none); add(#0; #1); chart_at(Image 2; Nam Côn Sơn 2; 2022; none); add(#2; #3); chart_at(Image 2; PM3; 2022; none); add(#4; #5); chart_at(Image 3; Khí khô (bao gồm LNG) - GAS; 2022; none); divide(#7; 1000); subtract(#6; #8)`
- Model: `chart_sum(Table 1; Tổng sản lượng khí; none; 2022; none)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 1
- #0: operator chart_at -> chart_sum
- #0 arg0: 'Image 2' -> 'Table 1'
- #0 arg1: 'Cửu Long' -> 'Tổng sản lượng khí'
- #0 arg2: '2022' -> 'none'
- #0 arg3: 'none' -> '2022'
- #0 arg4: '<absent>' -> 'none'
- #1: missing gold step #1: chart_at(Image 2; Nam Côn Sơn 1; 2022; none)
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: chart_at(Image 2; Nam Côn Sơn 2; 2022; none)
- #4: missing gold step #4: add(#2; #3)
- #5: missing gold step #5: chart_at(Image 2; PM3; 2022; none)
- #6: missing gold step #6: add(#4; #5)
- #7: missing gold step #7: chart_at(Image 3; Khí khô (bao gồm LNG) - GAS; 2022; none)
- #8: missing gold step #8: divide(#7; 1000)
- #9: missing gold step #9: subtract(#6; #8)

## Dòng 219 — 20166cec-fd05-5886-8ea7-af0f875d8c50

Từ 1/2/2024 đến 11/2/2024, giá dầu Brent thay đổi bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_at(Image 1; Giá dầu Brent; 1/2/2024; none); chart_at(Image 1; Giá dầu Brent; 11/2/2024; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 1; Brent; 1/2/2024; none); chart_at(Image 1; Brent; 11/2/2024; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- #0 arg1: 'Giá dầu Brent' -> 'Brent'
- #1 arg1: 'Giá dầu Brent' -> 'Brent'

## Dòng 220 — 8a40402b-410b-5163-b4bf-913c3960929c

P/E dự phóng năm 2024 của IMP đang thấp hơn bao nhiêu lần so với mức P/E trung bình lịch sử giai đoạn 2019-2023?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(20.08; 12.5)`
- Model: `divide(12.5; 20)`
- #0: operator subtract -> divide
- #0 arg0: '20.08' -> '12.5'
- #0 arg1: '12.5' -> '20'

## Dòng 221 — 2b29cd19-b308-5b1c-aa23-88544992c084

Tỷ lệ giữa chỉ số định giá P/E dự phóng năm 2024 của cổ phiếu PVS so với cổ phiếu GAS là bao nhiêu lần?

- Nhãn: both_math_only, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `divide(24.2; 14.8)`
- Model: `divide(#1; #3)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#3
- #0 arg0: '24.2' -> '#1'
- #0 arg1: '14.8' -> '#3'

## Dòng 222 — 169b8dba-e60b-5e77-8bac-42fe72ee90cd

Mức sinh lời của ngành Hóa chất đã thay đổi bao nhiêu phần trăm từ giai đoạn Đi ngang sang giai đoạn Bứt phá?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(23.02; 13.31); divide(#0; 13.31); multiply(#1; 100)`
- Model: `subtract(37.6; 15); divide(#0; 15); multiply(#1; 100)`
- #0 arg0: '23.02' -> '37.6'
- #0 arg1: '13.31' -> '15'
- #1 arg1: '13.31' -> '15'

## Dòng 223 — 867bd255-373b-5257-9a4c-2ce02fd39f8a

Đối với 9 ngân hàng trong nhóm theo dõi, liệu thu nhập lãi thuần (NII) của giai đoạn 3Q24 (TTM) có lớn hơn mức của cả năm 2023 hay không?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_at(Image 1; NII; 3Q24 (TTM); none); chart_at(Image 1; NII; 2023; none); greater(#0; #1)`
- Model: `chart_max(Image 1; NII; none; 2023; none); chart_at(Image 1; NII; none; 3Q24 (TTM); none); greater(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0: operator chart_at -> chart_max
- #0 arg2: '3Q24 (TTM)' -> 'none'
- #0 arg3: 'none' -> '2023'
- #0 arg4: '<absent>' -> 'none'
- #1 arg2: '2023' -> 'none'
- #1 arg3: 'none' -> '3Q24 (TTM)'
- #1 arg4: '<absent>' -> 'none'

## Dòng 224 — 7ef22981-672f-539c-aeaa-7eaa51284ab9

Trong tháng 10, giá trị thực hiện qua kênh khớp lệnh của khối ngoại tương đương bao nhiêu lần quy mô bán ròng của khối ngoại?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(4; 2.7)`
- Model: `divide(400; 3900)`
- #0 arg0: '4' -> '400'
- #0 arg1: '2.7' -> '3900'

## Dòng 225 — 03e2cefb-0caf-53a1-9469-ae6d3fc3529f

Mức chênh lệch (điểm phần trăm) khi lấy mức thay đổi phần trăm của VN-Index trong tháng 10 (từ dữ liệu thống kê qua các tháng) trừ đi mức thay đổi phần trăm được tính toán dựa trên các điểm chỉ số vào ngày 30/9 và 31/10 là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_sum(Image 1; VNIndex; 31/10/2022; 31/10/2022); chart_sum(Image 1; VNIndex; 30/9/2022; 30/9/2022); subtract(#0; #1); divide(#2; #1); multiply(#3; 100); subtract(-9.2; #4)`
- Model: `subtract(-9.2; -9.1)`
- #0: operator chart_sum -> subtract
- #0 arg0: 'Image 1' -> '-9.2'
- #0 arg1: 'VNIndex' -> '-9.1'
- #0 arg2: '31/10/2022' -> '<absent>'
- #0 arg3: '31/10/2022' -> '<absent>'
- #1: missing gold step #1: chart_sum(Image 1; VNIndex; 30/9/2022; 30/9/2022)
- #2: missing gold step #2: subtract(#0; #1)
- #3: missing gold step #3: divide(#2; #1)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: subtract(-9.2; #4)

## Dòng 226 — fdafa460-e8e7-5d37-8434-b4ed171faca0

Tỷ trọng trung bình trong chỉ số FTSE EM của Thái Lan, Indonesia, Malaysia, Thổ Nhĩ Kỳ, Kuwait và Philippines là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_average(Image 1; Weight in FTSE EM Index; Thailand; Philippines)`
- Model: `chart_average(Image 1; none; none; none)`
- #0 arg1: 'Weight in FTSE EM Index' -> 'none'
- #0 arg2: 'Thailand' -> 'none'
- #0 arg3: 'Philippines' -> 'none'

## Dòng 227 — c5ce9fbb-1648-5e24-8e23-2f46a264ebeb

Mức sinh lời trung bình của VNIndex trong quý 2/2023, tính từ tháng 4 đến tháng 6/2023, là bao nhiêu %?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_average(Image 1; VNIndex; Apr-23; Jun-23)`
- Model: `chart_average(Image 1; VNIndex; none; Apr-23; Jun-23; none)`
- Vi phạm kiểm tra: arity@0:6!=4
- #0 arg2: 'Apr-23' -> 'none'
- #0 arg3: 'Jun-23' -> 'Apr-23'
- #0 arg4: '<absent>' -> 'Jun-23'
- #0 arg5: '<absent>' -> 'none'

## Dòng 228 — 222e3efe-0bbc-5bbb-aade-879ee5adbffb

Tổng vốn hóa thị trường của ba ngân hàng quốc doanh VCB, BID và CTG là bao nhiêu tỷ đồng?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_sum(Table 1; Vốn hóa (tỷ); VCB; CTG)`
- Model: `chart_at(Image 1; Vốn hóa thị trường; 3Q24; none; none)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator table_sum -> chart_at
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Vốn hóa (tỷ)' -> 'Vốn hóa thị trường'
- #0 arg2: 'VCB' -> '3Q24'
- #0 arg3: 'CTG' -> 'none'
- #0 arg4: '<absent>' -> 'none'

## Dòng 229 — 4d4d4f25-caec-5470-91e5-5dcd827ece7b

Trong các ngành thép, hóa chất, xi măng và giấy, mức chênh lệch giữa tỷ trọng chi phí điện trên giá vốn hàng bán cao nhất và thấp nhất là bao nhiêu điểm phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Tỷ trọng Chi phí điện/GVHB; none; none); table_min(Table 1; Tỷ trọng Chi phí điện/GVHB; none; none); subtract(#0; #1)`
- Model: `table_max(Table 1; Chi phí điện trên GVHB; none; none); table_min(Table 1; Chi phí điện trên GVHB; none; none); subtract(#0; #1)`
- #0 arg1: 'Tỷ trọng Chi phí điện/GVHB' -> 'Chi phí điện trên GVHB'
- #1 arg1: 'Tỷ trọng Chi phí điện/GVHB' -> 'Chi phí điện trên GVHB'

## Dòng 230 — d566c99c-6738-5b56-a010-786236282bf0

Giá của STB tại ngày 06/09/2022 gấp bao nhiêu lần mức giá cắt lỗ?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(24700; 22100)`
- Model: `divide(100; 100)`
- #0 arg0: '24700' -> '100'
- #0 arg1: '22100' -> '100'

## Dòng 231 — 798be3b6-202e-57ab-9b9b-21bcbf875cd0

Thanh khoản của VNIndex trong tháng 8/2022 thay đổi bao nhiêu phần trăm so với tháng 7/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; VNIndex; T7/2022; none); chart_at(Image 2; VNIndex; T8/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `divide(14; 13.4)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '14'
- #0 arg1: 'VNIndex' -> '13.4'
- #0 arg2: 'T7/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; VNIndex; T8/2022; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 232 — 9491e29c-d9bd-59c3-9e32-d907c6331128

Trong 9T2024, chênh lệch giữa tốc độ tăng trưởng thu nhập lãi thuần (NII) và thu nhập khác (NOI) là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(14.1; 2.1)`
- Model: `subtract(14.1; 2.1)`

## Dòng 233 — 7dfa2845-f9a0-5f55-8437-64251e01a506

Dòng vốn lũy kế vào quỹ cổ phiếu từ đầu năm 2023 tại tháng 10/2023 đã thay đổi bao nhiêu phần trăm so với mức tại tháng 1/2023?

- Nhãn: invalid_reference, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_at(Image 2; Cổ phiếu; Jan-23; none); chart_at(Image 2; Cổ phiếu; Oct-23; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 4; Trụ Y - Lũy kế dòng vốn; Jan-23; none); chart_at(Image 4; Trụ Y - Lũy kế dòng vốn; Oct-23; none); divide(#1; #2); subtract(#3; 1); multiply(#4; 100)`
- Vi phạm kiểm tra: reference@2:#2; reference@3:#3; reference@4:#4
- #0 arg0: 'Image 2' -> 'Image 4'
- #0 arg1: 'Cổ phiếu' -> 'Trụ Y - Lũy kế dòng vốn'
- #1 arg0: 'Image 2' -> 'Image 4'
- #1 arg1: 'Cổ phiếu' -> 'Trụ Y - Lũy kế dòng vốn'
- #2: operator subtract -> divide
- #2 arg1: '#0' -> '#2'
- #3: operator divide -> subtract
- #3 arg0: '#2' -> '#3'
- #3 arg1: '#0' -> '1'
- #4 arg0: '#3' -> '#4'

## Dòng 234 — 300f6285-c3d4-5e9e-9942-56de9c0082ca

Mức chênh lệch giữa chỉ số P/E hiện tại và P/E dự phóng năm 2024 của cổ phiếu IMP là bao nhiêu?

- Nhãn: both_math_only, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `subtract(16.0; 12.5)`
- Model: `subtract(#1; #0)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#0
- #0 arg0: '16.0' -> '#1'
- #0 arg1: '12.5' -> '#0'

## Dòng 235 — efde61b6-3875-51f1-85b2-618a7fd0578c

Biên độ giữa mức giá dầu Brent cao nhất và thấp nhất trong các kỳ quan sát năm 2024 là bao nhiêu USD/thùng?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; Giá dầu Brent; 1/2/2024; 11/2/2024); chart_min(Image 1; Giá dầu Brent; 1/2/2024; 11/2/2024); subtract(#0; #1)`
- Model: `chart_max(Image 1; Brent; none; Jan-24; Dec-24); chart_min(Image 1; Brent; none; Jan-24; Dec-24); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0 arg1: 'Giá dầu Brent' -> 'Brent'
- #0 arg2: '1/2/2024' -> 'none'
- #0 arg3: '11/2/2024' -> 'Jan-24'
- #0 arg4: '<absent>' -> 'Dec-24'
- #1 arg1: 'Giá dầu Brent' -> 'Brent'
- #1 arg2: '1/2/2024' -> 'none'
- #1 arg3: '11/2/2024' -> 'Jan-24'
- #1 arg4: '<absent>' -> 'Dec-24'

## Dòng 236 — 5836d71e-238a-513f-a689-e1b965210082

Mức trung bình phần trăm thay đổi giá hiện tại so với ngày ra báo cáo của các cổ phiếu được khuyến nghị là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 1; % thay đổi giá hiện tại so với ngày ra báo cáo; none; none)`
- Model: `chart_average(Image 1; % thay đổi giá hiện tại so với ngày ra báo cáo; none; none)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'

## Dòng 237 — a6e61bfc-ca92-587d-8f7d-c2a9fb10f94d

Doanh thu quý 1/2024 của DPG chiếm bao nhiêu phần trong dự báo doanh thu cả năm 2024 của công ty?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `divide(425; 4142)`
- Model: `divide(425; 4142)`

## Dòng 238 — 3d95c22e-79c3-56dd-8835-9d16841226c1

Tổng tỷ lệ sở hữu của ông Lê Viết Hải và các bên liên quan trong cơ cấu cổ đông là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Lê Viết Hải; Hình 1: Cơ cấu cổ đông; none); chart_at(Image 1; Liên quan Ông Lê Viết Hải; Hình 1: Cơ cấu cổ đông; none); add(#0; #1)`
- Model: `add(21; 5)`
- #0: operator chart_at -> add
- #0 arg0: 'Image 1' -> '21'
- #0 arg1: 'Lê Viết Hải' -> '5'
- #0 arg2: 'Hình 1: Cơ cấu cổ đông' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Liên quan Ông Lê Viết Hải; Hình 1: Cơ cấu cổ đông; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 239 — 619fe5f8-cf61-5829-a683-72c429026f20

Tăng trưởng lợi nhuận của các ngân hàng trong Q3/2024 có cao hơn mức tăng trưởng lợi nhuận lũy kế 9T2024 hay không?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `greater(17.7; 16.4)`
- Model: `greater(17.7; 16.4)`

## Dòng 240 — b110f00a-d5d7-5b7c-a581-a8966ceac78e

Trong tháng 10/2023, mức thay đổi giá của cổ phiếu VHM chênh lệch bao nhiêu phần trăm so với mức thay đổi của nhóm ngành Bất động sản?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; % +/-; VHM; none); subtract(#0; -13.4)`
- Model: `divide(-7; -6)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '-7'
- #0 arg1: '% +/-' -> '-6'
- #0 arg2: 'VHM' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: subtract(#0; -13.4)

## Dòng 241 — b35ef64d-8f57-58f3-ae38-3da45c677795

Chênh lệch giữa tỷ trọng trung bình của Indonesia, Turkey và Kuwait trong chỉ số FTSE Emerging Markets với tỷ trọng trung bình của cùng ba quốc gia này trong Schwab Emerging Markets Equity ETF là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; Weight in FTSE EM Index; Indonesia; none); chart_at(Image 1; Weight in FTSE EM Index; Turkey; none); chart_at(Image 1; Weight in FTSE EM Index; Kuwait; none); add(#0; #1); add(#3; #2); divide(#4; 3); add(2.28; 1.39); add(#6; 0.92); divide(#7; 3); subtract(#5; #8)`
- Model: ``
- Vi phạm kiểm tra: empty
- #0: missing gold step #0: chart_at(Image 1; Weight in FTSE EM Index; Indonesia; none)
- #1: missing gold step #1: chart_at(Image 1; Weight in FTSE EM Index; Turkey; none)
- #2: missing gold step #2: chart_at(Image 1; Weight in FTSE EM Index; Kuwait; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)
- #5: missing gold step #5: divide(#4; 3)
- #6: missing gold step #6: add(2.28; 1.39)
- #7: missing gold step #7: add(#6; 0.92)
- #8: missing gold step #8: divide(#7; 3)
- #9: missing gold step #9: subtract(#5; #8)

## Dòng 242 — ef4ec7da-bcae-55c8-8c53-2cb347ed5ed7

Trong 9T24, doanh thu của mảng Viễn thông ước tính đạt khoảng bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(28.3; 100); multiply(45241; #0)`
- Model: `divide(45241; 100); multiply(#0; 28.5); divide(#1; 100)`
- #0 arg0: '28.3' -> '45241'
- #1 arg0: '45241' -> '#0'
- #1 arg1: '#0' -> '28.5'
- #2: extra predicted step #2: divide(#1; 100)

## Dòng 243 — a30c9a64-12f4-5f40-b405-0714326887f9

Dòng vốn vào các quỹ cổ phiếu EM trong tháng 10/2023 đã thay đổi bao nhiêu phần trăm so với tháng 10/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; EM Equity; Oct-22; none); chart_at(Image 3; EM Equity; Oct-23; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `divide(-100; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 3' -> '-100'
- #0 arg1: 'EM Equity' -> '100'
- #0 arg2: 'Oct-22' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; EM Equity; Oct-23; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 244 — 7322474a-92ff-5c09-9b4e-41ff58e72433

Khoảng chênh lệch giữa mức tăng trưởng NPATMI 2024F cao nhất và thấp nhất của các ngành là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `table_max(Table 1; Tăng trưởng NPATMI@2024F; Hàng tiêu dùng không thiết yếu; Dịch vụ tiện ích); table_min(Table 1; Tăng trưởng NPATMI@2024F; Hàng tiêu dùng không thiết yếu; Dịch vụ tiện ích); subtract(#0; #1)`
- Model: `subtract(#1; #2)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#2
- #0: operator table_max -> subtract
- #0 arg0: 'Table 1' -> '#1'
- #0 arg1: 'Tăng trưởng NPATMI@2024F' -> '#2'
- #0 arg2: 'Hàng tiêu dùng không thiết yếu' -> '<absent>'
- #0 arg3: 'Dịch vụ tiện ích' -> '<absent>'
- #1: missing gold step #1: table_min(Table 1; Tăng trưởng NPATMI@2024F; Hàng tiêu dùng không thiết yếu; Dịch vụ tiện ích)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 245 — cee418df-bf3e-58bd-af67-4701af20b4bb

Tăng trưởng NPATMI dự phóng trung bình năm 2024F của bốn cổ phiếu DBD, IMP, TNH và TRA là bao nhiêu?

- Nhãn: invalid_arity, invalid_source_type, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_average(Table 2; Tăng trưởng NPATMI@2024F; DBD; TRA)`
- Model: `table_average(Table 2#NPATMI (svck); 4)`
- Vi phạm kiểm tra: arity@0:2!=4; source_type@0:Table 2#NPATMI (svck)
- #0 arg0: 'Table 2' -> 'Table 2#NPATMI (svck)'
- #0 arg1: 'Tăng trưởng NPATMI@2024F' -> '4'
- #0 arg2: 'DBD' -> '<absent>'
- #0 arg3: 'TRA' -> '<absent>'

## Dòng 246 — 7ae928fc-e97f-545d-8bf4-bd35bea7be9a

Tỷ suất cổ tức trung bình hàng năm của FPT trong giai đoạn từ FY21 đến FY26F là bao nhiêu phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 1; Dividend yield (%); FY21; FY26F)`
- Model: `chart_average(Image 1; Cổ tức EPS (VNĐ)*; none; none)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Dividend yield (%)' -> 'Cổ tức EPS (VNĐ)*'
- #0 arg2: 'FY21' -> 'none'
- #0 arg3: 'FY26F' -> 'none'

## Dòng 247 — 7fbaa616-e621-55cf-b49b-68e77e052e39

Biên độ định giá lịch sử của P/E ước tính cho năm tài chính hiện tại trong giai đoạn từ 1/2/2018 đến 9/2/2023 là bao nhiêu lần, tính bằng chênh lệch giữa mức cao nhất và thấp nhất?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2018; 9/2/2023); chart_min(Image 1; P/E ước tính cho năm tài chính hiện tại; 1/2/2018; 9/2/2023); subtract(#0; #1)`
- Model: `chart_max(Image 1; P/E; none; 12/2018; 1/9/2023); chart_min(Image 1; P/E; none; 12/2018; 1/9/2023); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #0 arg2: '1/2/2018' -> 'none'
- #0 arg3: '9/2/2023' -> '12/2018'
- #0 arg4: '<absent>' -> '1/9/2023'
- #1 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #1 arg2: '1/2/2018' -> 'none'
- #1 arg3: '9/2/2023' -> '12/2018'
- #1 arg4: '<absent>' -> '1/9/2023'

## Dòng 248 — bd870cf6-8c39-5ed1-82e9-3c9c2608d3a9

Tỷ lệ biến động của ngành Tài chính chênh lệch bao nhiêu điểm phần trăm so với ngành Bất động sản trong tháng 9/2022?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(-13.3; -11.1)`
- Model: `subtract(-13.3; 11.5)`
- #0 arg1: '-11.1' -> '11.5'

## Dòng 249 — 5a9e813f-37fb-5733-8f9f-49cc752f7a49

Tỷ suất sinh lời của ngành Công nghệ Thông tin trong giai đoạn bứt phá gấp bao nhiêu lần so với giai đoạn đi ngang?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(36.15; 8.08)`
- Model: `divide(43.23; 30)`
- #0 arg0: '36.15' -> '43.23'
- #0 arg1: '8.08' -> '30'

## Dòng 250 — 1cd59ae1-2b0b-5ed1-9c0b-4c0d154fcaf0

Tỷ lệ dòng vốn ước tính của quỹ Vanguard FTSE Emerging Markets ETF so với quỹ Vanguard Emerging Markets Stock Index Fund là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(496.5; 178.6)`
- Model: `divide(1.8; 1.3)`
- #0 arg0: '496.5' -> '1.8'
- #0 arg1: '178.6' -> '1.3'

## Dòng 251 — 7a497d6b-de1a-5fe5-ab48-4f21cb095bf8

Mức tăng giá bán lẻ điện bình quân hằng năm được nêu cho giai đoạn 2009–2019 cao hơn bao nhiêu điểm phần trăm so với mức tăng trung bình mỗi năm nếu tính đơn giản từ giá điện năm 2009 đến năm 2019?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Giá điện; 2009; none); chart_at(Image 1; Giá điện; 2019; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); divide(#4; 10); subtract(10; #5)`
- Model: `divide(10; 100); multiply(#0; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '10'
- #0 arg1: 'Giá điện' -> '100'
- #0 arg2: '2009' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> multiply
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Giá điện' -> '100'
- #1 arg2: '2019' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: divide(#4; 10)
- #6: missing gold step #6: subtract(10; #5)

## Dòng 252 — 42412944-92f5-592a-a2da-988433d012f4

Trong số các cổ phiếu được liệt kê, mức P/E dự phóng thấp nhất cho năm 2024 là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_min(Table 1; P/E@2024F;  none;  none)`
- Model: `table_min(Table 1; P/E 2024 (x); none; none)`
- #0 arg1: 'P/E@2024F' -> 'P/E 2024 (x)'

## Dòng 253 — 5f87ca46-3542-5ee6-b915-609d6de00ce5

Mức % tăng giá 1 năm bình quân của các mã FMC, VNM, STB, PLX, VCB, SCS, FPT, CTR, IDC, PVD, DPM, HPG, PVT, ACB, BID, NLG, PNJ và HSG là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 2; % Tăng giá@1 năm; none; none)`
- Model: `chart_average(Image 1; 100; none; none)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 2' -> 'Image 1'
- #0 arg1: '% Tăng giá@1 năm' -> '100'

## Dòng 254 — 4006843d-3883-5d12-bb2f-35c32cce57d4

Vào tháng 7 năm 2023, mức tăng trưởng của Nhóm Y Tế vượt trội hơn bao nhiêu điểm phần trăm so với chỉ số VNIndex?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Nhóm Y Tế; Jul-23; none); chart_at(Image 1; VNIndex; Jul-23; none); subtract(#0; #1)`
- Model: `subtract(29; 12)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '29'
- #0 arg1: 'Nhóm Y Tế' -> '12'
- #0 arg2: 'Jul-23' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; VNIndex; Jul-23; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 255 — eb61a9c5-dac8-5da2-8ac4-36d04539a3b8

Trong tháng 1 năm 2025, dòng vốn đầu tư vào thị trường Mỹ chiếm bao nhiêu phần trăm so với tổng dòng vốn vào các quỹ cổ phiếu thuộc thị trường phát triển (DM)?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(46495; 1000); chart_at(Image 2; Phát triển (DM); Jan-25; none); divide(#0; #1); multiply(#2; 100)`
- Model: `divide(46.5; 100)`
- #0 arg0: '46495' -> '46.5'
- #0 arg1: '1000' -> '100'
- #1: missing gold step #1: chart_at(Image 2; Phát triển (DM); Jan-25; none)
- #2: missing gold step #2: divide(#0; #1)
- #3: missing gold step #3: multiply(#2; 100)

## Dòng 256 — 0a17b9f0-ee04-5a6b-9c1f-c2b4bd2594a2

Thu nhập lãi thuần (NII) bình quân hằng năm của 9 ngân hàng trong nhóm theo dõi giai đoạn 2019–2023 là bao nhiêu nghìn tỷ?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_average(Image 1; NII; 2019; 2023)`
- Model: `table_average(Table 1; NII; none; none)`
- #0: operator chart_average -> table_average
- #0 arg0: 'Image 1' -> 'Table 1'
- #0 arg2: '2019' -> 'none'
- #0 arg3: '2023' -> 'none'

## Dòng 257 — 7c2ea565-7042-5a47-8be5-4a70ed91d672

Mức chênh lệch giữa giá trị lãi gộp cao nhất và thấp nhất trong các năm tài chính từ 2015 đến 2020 là bao nhiêu tỷ đồng?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 1; Lãi gộp (Vbn); none; none); table_min(Table 1; Lãi gộp (Vbn); none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; Lãi gộp; none; none); chart_min(Image 1; Lãi gộp; none; none); subtract(#0; #1)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Lãi gộp (Vbn)' -> 'Lãi gộp'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Image 1'
- #1 arg1: 'Lãi gộp (Vbn)' -> 'Lãi gộp'

## Dòng 258 — b829a517-ff99-5746-a972-9f386ec2e0fb

Tại 3Q24, chênh lệch giữa lợi suất tài sản trung bình và chi phí vốn trung bình là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, invalid_math_argument, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 5; Lợi suất tài sản trung bình; 3Q24; none); chart_at(Image 5; Chi phí vốn trung bình; 3Q24; none); subtract(#0; #1)`
- Model: `chart_at(Image 5; NIM - RHS; none; none); subtract(#0; none)`
- Vi phạm kiểm tra: math_type@1:none
- #0 arg1: 'Lợi suất tài sản trung bình' -> 'NIM - RHS'
- #0 arg2: '3Q24' -> 'none'
- #1: operator chart_at -> subtract
- #1 arg0: 'Image 5' -> '#0'
- #1 arg1: 'Chi phí vốn trung bình' -> 'none'
- #1 arg2: '3Q24' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 259 — e47f0211-a1b6-508d-80a6-dbcef4e02232

Biên độ chênh lệch giữa mức tăng trưởng huy động từ đầu năm cao nhất và thấp nhất theo tháng trong năm 2023 là bao nhiêu điểm phần trăm?

- Nhãn: invalid_source_type, non_exact, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; 2023; Jan; Dec); chart_min(Image 1; 2023; Jan; Dec); subtract(#0; #1)`
- Model: `chart_max(Table 2; Tăng trưởng huy động theo tháng; none; none); chart_min(Table 2; Tăng trưởng huy động theo tháng; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 2; source_type@1:Table 2
- #0 arg0: 'Image 1' -> 'Table 2'
- #0 arg1: '2023' -> 'Tăng trưởng huy động theo tháng'
- #0 arg2: 'Jan' -> 'none'
- #0 arg3: 'Dec' -> 'none'
- #1 arg0: 'Image 1' -> 'Table 2'
- #1 arg1: '2023' -> 'Tăng trưởng huy động theo tháng'
- #1 arg2: 'Jan' -> 'none'
- #1 arg3: 'Dec' -> 'none'

## Dòng 260 — 963a03d5-01f5-53e3-ac70-d16843b82b57

Theo SSI Research, tăng trưởng NPATMI ước tính của các công ty trong danh sách năm 2024 thay đổi bao nhiêu điểm phần trăm so với ước tính cho cả năm 2023?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(6; 16)`
- Model: `subtract(6; 8.4)`
- #0 arg1: '16' -> '8.4'

## Dòng 261 — 4ceb6838-9bf0-5213-b537-6c600ccd2763

Tỷ lệ LNST trên doanh thu năm 2019 của HBC là bao nhiêu?

- Nhãn: both_math_only, invalid_reference, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `divide(417; 18610)`
- Model: `divide(417; 100); divide(#0; #2)`
- Vi phạm kiểm tra: reference@1:#2
- #0 arg1: '18610' -> '100'
- #1: extra predicted step #1: divide(#0; #2)

## Dòng 262 — 439f019d-18ee-5182-bf22-404eda962774

Trong quý 3 năm 2023, mức thay đổi giá của nhóm ngành Tài chính có tích cực hơn so với nhóm Bất động sản hay không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `greater(5.7; -2.1)`
- Model: `table_average(Table 1; Tài chính; Q3/23; none); table_average(Table 1; Bất động sản; Q3/23; none); greater(#0; #1)`
- #0: operator greater -> table_average
- #0 arg0: '5.7' -> 'Table 1'
- #0 arg1: '-2.1' -> 'Tài chính'
- #0 arg2: '<absent>' -> 'Q3/23'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: table_average(Table 1; Bất động sản; Q3/23; none)
- #2: extra predicted step #2: greater(#0; #1)

## Dòng 263 — 2a4f4298-b500-5af3-bc21-b1eee20640d5

Dự báo tăng trưởng NPATMI 2024F của ngành Nguyên vật liệu vượt ngưỡng tăng trưởng lợi nhuận được xem là mức phục hồi đáng kể cho một số ngành trong năm 2024 bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(51.2; 30)`
- Model: `subtract(30.5; 15.3)`
- #0 arg0: '51.2' -> '30.5'
- #0 arg1: '30' -> '15.3'

## Dòng 264 — d43ed3ab-58b3-5388-bccb-5db7c6f98779

Mức vốn hóa lớn nhất của một ngân hàng trong số các ngân hàng được thống kê là bao nhiêu tỷ đồng?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Vốn hóa (tỷ); none; none)`
- Model: `table_max(Table 1; Vốn hóa; none; none)`
- #0 arg1: 'Vốn hóa (tỷ)' -> 'Vốn hóa'

## Dòng 265 — c22ca584-8a9f-52f1-a85b-330c034513c8

Mức biến động giá theo phần trăm trung bình của các cổ phiếu có tác động tích cực nhất lên thị trường trong tháng 10 là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_average(Image 4; % +/-; none; none)`
- Model: `table_average(Table 1; % +/-%; 100; none)`
- #0: operator chart_average -> table_average
- #0 arg0: 'Image 4' -> 'Table 1'
- #0 arg1: '% +/-' -> '% +/-%'
- #0 arg2: 'none' -> '100'

## Dòng 266 — 583adc96-a4b6-5124-8869-c5823958490e

Trong tháng 10, tỷ lệ giữa tổng giá trị giao dịch ròng của nhà đầu tư nước ngoài đối với mã cổ phiếu VNM so với độ lớn tổng giá trị bán ròng của khối ngoại trên toàn sàn HOSE là bao nhiêu?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_sum(Image 7; GTGD ròng NĐTNN; VNM; VNM); multiply(1.5; 1000); divide(#0; #1)`
- Model: `divide(#1; #0)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#0
- #0: operator chart_sum -> divide
- #0 arg0: 'Image 7' -> '#1'
- #0 arg1: 'GTGD ròng NĐTNN' -> '#0'
- #0 arg2: 'VNM' -> '<absent>'
- #0 arg3: 'VNM' -> '<absent>'
- #1: missing gold step #1: multiply(1.5; 1000)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 267 — bd7bef26-007a-5095-9e5b-0e1589272e5b

Mức chênh lệch giữa tốc độ tăng trưởng sản lượng tiêu thụ dự kiến năm 2025 của BSR so với năm 2024 (tính từ các số liệu quy mô sản lượng) và tỷ lệ phục hồi sản lượng kỳ vọng của doanh nghiệp này sau đợt bảo trì năm 2024 là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; Dầu khí - BSR; 2024E; none); chart_at(Image 3; Dầu khí - BSR; 2025; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); subtract(#4; 15)`
- Model: `subtract(15; 73)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 3' -> '15'
- #0 arg1: 'Dầu khí - BSR' -> '73'
- #0 arg2: '2024E' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; Dầu khí - BSR; 2025; none)
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: subtract(#4; 15)

## Dòng 268 — efbe8932-40c7-5250-ae6e-eb6cc21d96e3

Trong năm 2023, nếu lấy tổng NII, NSI và NOI trừ đi tổng OPEX và chi phí dự phòng của nhóm 9 ngân hàng theo dõi, kết quả là bao nhiêu nghìn tỷ?

- Nhãn: fewer_steps, invalid_source_type, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; NII; 2023; none); chart_at(Image 1; NSI; 2023; none); add(#0; #1); chart_at(Image 1; NOI; 2023; none); add(#2; #3); chart_at(Image 1; OPEX; 2023; none); chart_at(Image 1; Prov.; 2023; none); add(#5; #6); subtract(#4; #7)`
- Model: `chart_sum(Table 1; OPEX; none; none); chart_sum(Table 1; NII; 3Q24 (TTM); none); chart_sum(Table 1; NSI; 3Q24 (TTM); none); chart_sum(Table 1; NOI; 3Q24 (TTM); none); subtract(#3; #1); subtract(#4; #2); subtract(#5; #3); subtract(#6; #4)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1; source_type@2:Table 1; source_type@3:Table 1
- #0: operator chart_at -> chart_sum
- #0 arg0: 'Image 1' -> 'Table 1'
- #0 arg1: 'NII' -> 'OPEX'
- #0 arg2: '2023' -> 'none'
- #1: operator chart_at -> chart_sum
- #1 arg0: 'Image 1' -> 'Table 1'
- #1 arg1: 'NSI' -> 'NII'
- #1 arg2: '2023' -> '3Q24 (TTM)'
- #2: operator add -> chart_sum
- #2 arg0: '#0' -> 'Table 1'
- #2 arg1: '#1' -> 'NSI'
- #2 arg2: '<absent>' -> '3Q24 (TTM)'
- #2 arg3: '<absent>' -> 'none'
- #3: operator chart_at -> chart_sum
- #3 arg0: 'Image 1' -> 'Table 1'
- #3 arg2: '2023' -> '3Q24 (TTM)'
- #4: operator add -> subtract
- #4 arg0: '#2' -> '#3'
- #4 arg1: '#3' -> '#1'
- #5: operator chart_at -> subtract
- #5 arg0: 'Image 1' -> '#4'
- #5 arg1: 'OPEX' -> '#2'
- #5 arg2: '2023' -> '<absent>'
- #5 arg3: 'none' -> '<absent>'
- #6: operator chart_at -> subtract
- #6 arg0: 'Image 1' -> '#5'
- #6 arg1: 'Prov.' -> '#3'
- #6 arg2: '2023' -> '<absent>'
- #6 arg3: 'none' -> '<absent>'
- #7: operator add -> subtract
- #7 arg0: '#5' -> '#6'
- #7 arg1: '#6' -> '#4'
- #8: missing gold step #8: subtract(#4; #7)

## Dòng 269 — 3c40b517-d714-5c5e-bfe3-f91211368ee3

Trong giai đoạn từ 31/8/2022 đến 30/9/2022, chênh lệch giữa mức VNIndex cao nhất và thấp nhất là bao nhiêu điểm?

- Nhãn: exact, repo_equivalent
- Ground truth: `chart_max(Image 1; VNIndex; none; none); chart_min(Image 1; VNIndex; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; VNIndex; none; none); chart_min(Image 1; VNIndex; none; none); subtract(#0; #1)`

## Dòng 270 — 827e6005-5e9e-5c95-ae9a-1baa9d0d7e0e

Tăng trưởng NPATMI dự phóng năm 2025 trung bình của 5 cổ phiếu dầu khí GAS, PVS, PVD, PLX và BSR là bao nhiêu phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 1; Tăng trưởng NPATMI@2025F; none; none)`
- Model: `chart_average(Image 1; 2025F; none; none)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Tăng trưởng NPATMI@2025F' -> '2025F'

## Dòng 271 — 3c46d896-8490-5e9c-9169-cb4d3de9feef

Chênh lệch giữa mức tăng trung bình năm 2023 và mức tăng trung bình trong giai đoạn bứt phá của bốn nhóm ngành Dịch vụ tài chính, Tài nguyên Cơ bản, Hóa chất và Dầu khí là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, invalid_source_type, lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `add(69.4; 42.9); add(#0; 37.6); add(#1; 36); divide(#2; 4); add(34.41; 25.25); add(#4; 23.02); add(#5; 15.02); divide(#6; 4); subtract(#3; #7)`
- Model: `chart_average(Table 1; Dịch vụ tài chính; none; none); chart_average(Table 1; Tài nguyên Cơ bản; none; none); chart_average(Table 1; Hóa chất; none; none); chart_average(Table 1; Dầu khí; none; none); subtract(#0; #1); subtract(#2; #3); subtract(#4; #5)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1; source_type@2:Table 1; source_type@3:Table 1
- #0: operator add -> chart_average
- #0 arg0: '69.4' -> 'Table 1'
- #0 arg1: '42.9' -> 'Dịch vụ tài chính'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: operator add -> chart_average
- #1 arg0: '#0' -> 'Table 1'
- #1 arg1: '37.6' -> 'Tài nguyên Cơ bản'
- #1 arg2: '<absent>' -> 'none'
- #1 arg3: '<absent>' -> 'none'
- #2: operator add -> chart_average
- #2 arg0: '#1' -> 'Table 1'
- #2 arg1: '36' -> 'Hóa chất'
- #2 arg2: '<absent>' -> 'none'
- #2 arg3: '<absent>' -> 'none'
- #3: operator divide -> chart_average
- #3 arg0: '#2' -> 'Table 1'
- #3 arg1: '4' -> 'Dầu khí'
- #3 arg2: '<absent>' -> 'none'
- #3 arg3: '<absent>' -> 'none'
- #4: operator add -> subtract
- #4 arg0: '34.41' -> '#0'
- #4 arg1: '25.25' -> '#1'
- #5: operator add -> subtract
- #5 arg0: '#4' -> '#2'
- #5 arg1: '23.02' -> '#3'
- #6: operator add -> subtract
- #6 arg0: '#5' -> '#4'
- #6 arg1: '15.02' -> '#5'
- #7: missing gold step #7: divide(#6; 4)
- #8: missing gold step #8: subtract(#3; #7)

## Dòng 272 — 0b5c5933-6f47-5baf-8b74-dea4cea10aae

Mức chênh lệch giữa giá trị trung bình của các số liệu phần trăm tăng trưởng chỉ số VN-Index tháng 8 được nêu trực tiếp và mức tăng trưởng phần trăm tính từ sự thay đổi điểm số giữa ngày 31/8 và ngày 29/7 là bao nhiêu?

- Nhãn: fewer_steps, invalid_source_type, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `add(6.15; 6.1); divide(#0; 2); chart_at(Image 1; VNIndex; 29/7/2022; none); chart_at(Image 1; VNIndex; 31/8/2022; none); subtract(#3; #2); divide(#4; #2); multiply(#5; 100); subtract(#1; #6)`
- Model: `chart_average(Table 2#Tăng trưởng từ 29/7#none; 2021; 2021; none)`
- Vi phạm kiểm tra: source_type@0:Table 2#Tăng trưởng từ 29/7#none
- #0: operator add -> chart_average
- #0 arg0: '6.15' -> 'Table 2#Tăng trưởng từ 29/7#none'
- #0 arg1: '6.1' -> '2021'
- #0 arg2: '<absent>' -> '2021'
- #0 arg3: '<absent>' -> 'none'
- #1: missing gold step #1: divide(#0; 2)
- #2: missing gold step #2: chart_at(Image 1; VNIndex; 29/7/2022; none)
- #3: missing gold step #3: chart_at(Image 1; VNIndex; 31/8/2022; none)
- #4: missing gold step #4: subtract(#3; #2)
- #5: missing gold step #5: divide(#4; #2)
- #6: missing gold step #6: multiply(#5; 100)
- #7: missing gold step #7: subtract(#1; #6)

## Dòng 273 — cbdf2226-d316-58f6-8248-af53c906b30f

Chênh lệch giữa mức tăng/giảm trung bình trong tháng 12 và mức tăng/giảm trung bình ở giai đoạn hồi phục của ba nhóm Bán lẻ, Thực phẩm và đồ uống, và Du lịch và Giải trí là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; T12; Bán lẻ; none); chart_at(Image 1; T12; Thực phẩm và đồ uống; none); add(#0; #1); chart_at(Image 1; T12; Du lịch và Giải trí; none); add(#2; #3); divide(#4; 3); add(14.2; 9.03); add(#6; 14.44); divide(#7; 3); subtract(#5; #8)`
- Model: `subtract(-5.2; -11.4); divide(#0; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '-5.2'
- #0 arg1: 'T12' -> '-11.4'
- #0 arg2: 'Bán lẻ' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'T12' -> '100'
- #1 arg2: 'Thực phẩm và đồ uống' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: chart_at(Image 1; T12; Du lịch và Giải trí; none)
- #4: missing gold step #4: add(#2; #3)
- #5: missing gold step #5: divide(#4; 3)
- #6: missing gold step #6: add(14.2; 9.03)
- #7: missing gold step #7: add(#6; 14.44)
- #8: missing gold step #8: divide(#7; 3)
- #9: missing gold step #9: subtract(#5; #8)

## Dòng 274 — 970a46c7-0fbb-5106-bcc7-06a6721741de

Tốc độ tăng trưởng tín dụng bình quân hằng năm trong giai đoạn 2017–2023 là bao nhiêu?

- Nhãn: invalid_arity, missing_source_id, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_average(Image 2; Tăng trưởng tín dụng; 2017; 2023)`
- Model: `table_average(Table 2; Tăng trưởng tín dụng và huy động; none; 2017; 2023)`
- Vi phạm kiểm tra: arity@0:5!=4; source_missing@0:Table 2
- #0: operator chart_average -> table_average
- #0 arg0: 'Image 2' -> 'Table 2'
- #0 arg1: 'Tăng trưởng tín dụng' -> 'Tăng trưởng tín dụng và huy động'
- #0 arg2: '2017' -> 'none'
- #0 arg3: '2023' -> '2017'
- #0 arg4: '<absent>' -> '2023'

## Dòng 275 — a864c036-da82-55c7-a66f-95c656a8ba8d

Tại mức vốn hóa của HBC vào ngày 15/06/2020, vốn hóa này gấp bao nhiêu lần lợi nhuận sau thuế năm 2019 của công ty?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `divide(2893; 417)`
- Model: `divide(2893; 417)`

## Dòng 276 — 17ca622e-1bdf-5da4-b2ed-749d84c88dd8

Trong 9T24, tốc độ tăng trưởng lợi nhuận trước thuế (LNTT) so với cùng kỳ của mảng CNTT toàn cầu cao hơn mảng CNTT trong nước bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(25.6; -21)`
- Model: `subtract(19.8; 21.0)`
- #0 arg0: '25.6' -> '19.8'
- #0 arg1: '-21' -> '21.0'

## Dòng 277 — 0a2b115b-251c-576b-ad21-06c081550eaa

Mức sinh lời trung bình trong tháng 8/2022 của ba chỉ số vốn hóa VN30, VNMidcap và VNSmallcap là bao nhiêu phần trăm?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `table_average(Table 2; VN30; T8/2022; T8/2022); table_average(Table 2; VNMidcap; T8/2022; T8/2022); table_average(Table 2; VNSmallcap; T8/2022; T8/2022); add(#0; #1); add(#3; #2); divide(#4; 3)`
- Model: `table_average(Table 1; VN30; none; VNSmallcap)`
- #0 arg0: 'Table 2' -> 'Table 1'
- #0 arg2: 'T8/2022' -> 'none'
- #0 arg3: 'T8/2022' -> 'VNSmallcap'
- #1: missing gold step #1: table_average(Table 2; VNMidcap; T8/2022; T8/2022)
- #2: missing gold step #2: table_average(Table 2; VNSmallcap; T8/2022; T8/2022)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)
- #5: missing gold step #5: divide(#4; 3)

## Dòng 278 — f18ebc7f-32d8-532f-a621-d6041e1072cc

Từ 2019 đến 3Q24 (TTM), biên độ giữa mức chi phí dự phòng cao nhất và thấp nhất của 9 ngân hàng trong nhóm theo dõi là bao nhiêu nghìn tỷ?

- Nhãn: invalid_source_type, non_exact, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; Prov.; none; none); chart_min(Image 1; Prov.; none; none); subtract(#0; #1)`
- Model: `chart_max(Table 1#Prov; none; none; none); chart_min(Table 1#Prov; none; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1#Prov; source_type@1:Table 1#Prov
- #0 arg0: 'Image 1' -> 'Table 1#Prov'
- #0 arg1: 'Prov.' -> 'none'
- #1 arg0: 'Image 1' -> 'Table 1#Prov'
- #1 arg1: 'Prov.' -> 'none'

## Dòng 279 — bbe8da9a-a189-5ab8-8a92-b7442e7f305c

Trong tháng 1, sau khi loại phần vốn vào thị trường Mỹ, dòng vốn vào các quỹ cổ phiếu thị trường phát triển còn lại là bao nhiêu tỷ USD?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(66; 46.5)`
- Model: `subtract(64.7; 46.5)`
- #0 arg0: '66' -> '64.7'

## Dòng 280 — ad73db55-32ee-5334-8e73-d7e95348801e

Khoảng chênh lệch tuyệt đối giữa giá mục tiêu của BCM và giá của cổ phiếu này tại ngày ra báo cáo 05/08/2022 là bao nhiêu?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(82500; 78000)`
- Model: `subtract(100; 80); subtract(100; 80); subtract(#0; #1)`
- #0 arg0: '82500' -> '100'
- #0 arg1: '78000' -> '80'
- #1: extra predicted step #1: subtract(100; 80)
- #2: extra predicted step #2: subtract(#0; #1)

## Dòng 281 — 9729849a-5c86-5f16-b845-44eea1a7c438

Dựa trên tổng doanh thu quý 1/2024 và tỷ trọng đóng góp của mảng Xây dựng, doanh thu ước tính từ mảng Xây dựng của DPG là bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `multiply(425; 0.64)`
- Model: `divide(425; 64); multiply(#0; 2875)`
- #0: operator multiply -> divide
- #0 arg1: '0.64' -> '64'
- #1: extra predicted step #1: multiply(#0; 2875)

## Dòng 282 — 426be3a5-607b-5f0a-b456-7373f6cad449

Vào tháng 6 năm 2024, mức chênh lệch giữa DPG VN và chỉ số VN-Index là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_at(Image 1; DPG VN; Jun 24; none); chart_at(Image 1; VN-Index; Jun 24; none); subtract(#0; #1)`
- Model: `chart_at(Image 1; Jun 24; VN-Index; none; 100); subtract(#0; 100); divide(#1; 100)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0 arg1: 'DPG VN' -> 'Jun 24'
- #0 arg2: 'Jun 24' -> 'VN-Index'
- #0 arg4: '<absent>' -> '100'
- #1: operator chart_at -> subtract
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'VN-Index' -> '100'
- #1 arg2: 'Jun 24' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> divide
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '100'

## Dòng 283 — 9c561eeb-7e02-591f-9cf8-20233d1cc8f7

Nếu lấy PE 2024 của thị trường tại ngày 6/2/2024 trừ đi P/E 2024F của Tổng/ Trung bình, chênh lệch là bao nhiêu lần?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(10.6; 10.6)`
- Model: `subtract(10.6; 10.6)`

## Dòng 284 — 5b6284a2-7c74-5017-bd61-b39c8a80b45c

Tổng doanh thu dự phóng năm 2023 của Nova Consumer, AFF(Mặt Trời Mọc) và Công ty FMCG là bao nhiêu tỷ VND?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `table_sum(Table 1; Nova Consumer; 2023; 2023); table_sum(Table 1; AFF(Mặt Trời Mọc); 2023; 2023); table_sum(Table 1; Công ty FMCG; 2023; 2023); add(#0; #1); add(#3; #2)`
- Model: `add(11000; 1000); add(#0; 100); add(#1; 1000)`
- #0: operator table_sum -> add
- #0 arg0: 'Table 1' -> '11000'
- #0 arg1: 'Nova Consumer' -> '1000'
- #0 arg2: '2023' -> '<absent>'
- #0 arg3: '2023' -> '<absent>'
- #1: operator table_sum -> add
- #1 arg0: 'Table 1' -> '#0'
- #1 arg1: 'AFF(Mặt Trời Mọc)' -> '100'
- #1 arg2: '2023' -> '<absent>'
- #1 arg3: '2023' -> '<absent>'
- #2: operator table_sum -> add
- #2 arg0: 'Table 1' -> '#1'
- #2 arg1: 'Công ty FMCG' -> '1000'
- #2 arg2: '2023' -> '<absent>'
- #2 arg3: '2023' -> '<absent>'
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 285 — b4b323f9-d82a-51e6-91b5-3cfddd7f4d92

Khoảng chênh lệch giữa tỷ lệ sở hữu cao nhất và thấp nhất trong cơ cấu cổ đông của HBC là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 1; Khác; none; none); chart_min(Image 1; PYN Elite Fund; none; none); subtract(#0; #1)`
- Model: `subtract(59; 5)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 1' -> '59'
- #0 arg1: 'Khác' -> '5'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 1; PYN Elite Fund; none; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 286 — 13cc59d1-174a-5f9b-9d93-6bb90c262ee1

Giá trị giao dịch bình quân phiên trên sàn HOSE trong tháng 10 thay đổi bao nhiêu phần trăm so với mức bình quân của 9 tháng đầu năm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(14.4; 14.9); divide(#0; 14.9); multiply(#1; 100)`
- Model: `subtract(14.4; 14.9); divide(#0; 14.9); multiply(#1; 100)`

## Dòng 287 — 46c4f0af-27f5-50e7-b25b-a9bee97bd9ad

Trong giai đoạn từ Jun 22 đến Jun 24, chênh lệch giữa mức cao nhất và thấp nhất của VN-Index theo chỉ số hiệu suất là bao nhiêu điểm %?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 1; VN-Index; none; none); chart_min(Image 1; VN-Index; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; VN-Index; Jun 22; none); chart_min(Image 1; VN-Index; Jun 22; none); subtract(#0; #1)`
- #0 arg2: 'none' -> 'Jun 22'
- #1 arg2: 'none' -> 'Jun 22'

## Dòng 288 — 582d1c49-ba6e-57e1-ac6c-7b2c646ee89c

Lãi suất ưu đãi cho vay mua nhà kỳ hạn 12 tháng bình quân của các ngân hàng nằm trong danh sách cổ phiếu ưa thích là bao nhiêu?

- Nhãn: fewer_steps, invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `add(5.7; 6); add(#0; 7); add(#1; 6.7); divide(#2; 4)`
- Model: `table_average(Table 1; Cổ phiếu ưa thích; 12 tháng; none; none)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator add -> table_average
- #0 arg0: '5.7' -> 'Table 1'
- #0 arg1: '6' -> 'Cổ phiếu ưa thích'
- #0 arg2: '<absent>' -> '12 tháng'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> 'none'
- #1: missing gold step #1: add(#0; 7)
- #2: missing gold step #2: add(#1; 6.7)
- #3: missing gold step #3: divide(#2; 4)

## Dòng 289 — d2783f93-e1b0-59aa-9b1e-b1440615beb1

Trong tháng 10/2022, mức sinh lời của nhóm Vật liệu chênh lệch bao nhiêu điểm phần trăm so với VN-Index?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(-22.4; -9.2)`
- Model: `subtract(-22.4; 1027.94)`
- #0 arg1: '-9.2' -> '1027.94'

## Dòng 290 — af382dc9-8700-5567-86ea-483e6c51e919

Biên độ chênh lệch tỷ lệ nợ xấu (NPL) giữa mức cao nhất và thấp nhất trong ba ngân hàng quốc doanh VCB, BID và CTG là bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_max(Table 1; NPL (%); VCB; CTG); table_min(Table 1; NPL (%); VCB; CTG); subtract(#0; #1)`
- Model: `chart_max(Image 1; NPL; none; CTG; BID; VCB); chart_min(Image 1; NPL; none; CTG; BID; VCB); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:6!=4; arity@1:6!=4
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'NPL (%)' -> 'NPL'
- #0 arg2: 'VCB' -> 'none'
- #0 arg4: '<absent>' -> 'BID'
- #0 arg5: '<absent>' -> 'VCB'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Image 1'
- #1 arg1: 'NPL (%)' -> 'NPL'
- #1 arg2: 'VCB' -> 'none'
- #1 arg4: '<absent>' -> 'BID'
- #1 arg5: '<absent>' -> 'VCB'

## Dòng 291 — 3f548843-c848-50cd-8b98-48bb9e1cc198

Tỷ lệ giữa chỉ số P/E dự phóng năm 2024 và P/E năm 2023 của ngành Bất động sản là bao nhiêu?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `divide(10.8; 12.2)`
- Model: `chart_divide(Chart 2#P/E 2024#none#P/E 2023#Bất động sản; Chart 2#P/E 2023#none#P/E 2023#Bất động sản)`
- Vi phạm kiểm tra: unknown_operator@0:chart_divide; arity@0:2!=4
- #0: operator divide -> chart_divide
- #0 arg0: '10.8' -> 'Chart 2#P/E 2024#none#P/E 2023#Bất động sản'
- #0 arg1: '12.2' -> 'Chart 2#P/E 2023#none#P/E 2023#Bất động sản'

## Dòng 292 — db168906-e1e6-52c4-9933-eb1aa9750c02

Mức tăng trưởng thu nhập lãi thuần (NII) trong 9T2024 chênh lệch bao nhiêu điểm phần trăm so với mức thay đổi NII khi so sánh giá trị năm 2023 với 3Q24 (TTM) của nhóm 9 ngân hàng theo dõi?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NII; 2023; none); chart_at(Image 1; NII; 3Q24 (TTM); none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); subtract(14.1; #4)`
- Model: `subtract(14.1; 100); divide(#0; 100); multiply(#1; 15.8)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '14.1'
- #0 arg1: 'NII' -> '100'
- #0 arg2: '2023' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'NII' -> '100'
- #1 arg2: '3Q24 (TTM)' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '15.8'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: subtract(14.1; #4)

## Dòng 293 — 54acedeb-33d0-5c30-b51b-c8318c6f44ba

Tăng trưởng NPATMI dự phóng năm 2024F của IMP có cao hơn mức tăng trưởng NPATMI ước tính cho năm 2024 của các công ty trong danh sách SSI Research hay không?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `greater(14.4; 6)`
- Model: `multiply(14.4; 6)`
- #0: operator greater -> multiply

## Dòng 294 — b9fd03b8-ce68-5251-89b1-24f9ff6d1259

Chênh lệch giữa giá mục tiêu và giá tại ngày 06/09/2022 của cổ phiếu BCM là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(82500; 88900)`
- Model: `subtract(100; 97.5)`
- #0 arg0: '82500' -> '100'
- #0 arg1: '88900' -> '97.5'

## Dòng 295 — 9bffa4c6-f92f-5987-b5fd-d29e201807dd

Trong 10 tháng, dòng tiền vào quỹ trái phiếu ở thị trường phát triển cao hơn bao nhiêu tỷ USD so với tổng dòng tiền vào các quỹ trái phiếu?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(277; 244)`
- Model: `subtract(277; 244)`

## Dòng 296 — 64c63430-7ee9-50e2-930f-25c4f4da3bc4

Chênh lệch giữa ước tính tăng trưởng lợi nhuận năm 2024 của 83 cổ phiếu trong phạm vi nghiên cứu SSI Research và mức tăng trưởng NPATMI 2024F của nhóm Tổng/ Trung bình là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(15.3; 15.3)`
- Model: `subtract(15.3; -5.6)`
- #0 arg1: '15.3' -> '-5.6'

## Dòng 297 — 648c0465-0a34-5ef8-bcf5-57759f395717

Nếu mức tăng giá điện được nâng từ 3% lên 5%, tác động trực tiếp lên CPI tăng thêm bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(0.175; 0.105)`
- Model: `subtract(0.175; 0.105)`

## Dòng 298 — f5e10586-f916-5ec2-8b36-12532321c97a

Tại ngày 9/2/2023, nếu lấy P/E ước tính cho năm tài chính hiện tại trừ đi mức P/E trung bình 5 năm, kết quả là bao nhiêu?

- Nhãn: aligned_noncommutative_swap, invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 9/2/2023; none); chart_at(Image 1; TB 5 năm; 9/2/2023; none); subtract(#0; #1)`
- Model: `chart_average(Image 1; P/E; none; 2023; none; 2024); chart_at(Image 1; P/E; none; 2024; Jan; none); subtract(#1; #0)`
- Vi phạm kiểm tra: arity@0:6!=4; arity@1:6!=4
- #0: operator chart_at -> chart_average
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #0 arg2: '9/2/2023' -> 'none'
- #0 arg3: 'none' -> '2023'
- #0 arg4: '<absent>' -> 'none'
- #0 arg5: '<absent>' -> '2024'
- #1 arg1: 'TB 5 năm' -> 'P/E'
- #1 arg2: '9/2/2023' -> 'none'
- #1 arg3: 'none' -> '2024'
- #1 arg4: '<absent>' -> 'Jan'
- #1 arg5: '<absent>' -> 'none'
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '#0'

## Dòng 299 — 1f32ada5-2e99-5cc3-9df4-0d4f460f432c

Tính đến tháng 10/2023, dòng vốn lũy kế vào quỹ tiền tệ còn cách mốc tổng giải ngân 10 tháng đầu năm được nhắc tới cho nhóm tài sản này bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `multiply(1; 1000); chart_at(Image 2; Tiền tệ; Oct-23; none); subtract(#0; #1)`
- Model: `subtract(100; 10)`
- #0: operator multiply -> subtract
- #0 arg0: '1' -> '100'
- #0 arg1: '1000' -> '10'
- #1: missing gold step #1: chart_at(Image 2; Tiền tệ; Oct-23; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 300 — ba360249-e5c9-5114-b230-6ce0db2a2546

Giá mục tiêu cơ bản của DCM có cao hơn giá mục tiêu kỹ thuật của mã này không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `greater(37.3; 37)`
- Model: `table_max(Table 1; DCM; none; none); greater(#0; 100.0)`
- #0: operator greater -> table_max
- #0 arg0: '37.3' -> 'Table 1'
- #0 arg1: '37' -> 'DCM'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: greater(#0; 100.0)

## Dòng 301 — 94d3b55e-4cf1-503d-9baa-18b08d9c9d10

Dự kiến sản lượng tiêu thụ của BSR trong năm 2025 sẽ thay đổi bao nhiêu phần trăm so với năm 2023?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; Dầu khí - BSR; 2025; none); chart_at(Image 3; Dầu khí - BSR; 2023; none); subtract(#0; #1); divide(#2; #1); multiply(#3; 100)`
- Model: `divide(115; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 3' -> '115'
- #0 arg1: 'Dầu khí - BSR' -> '100'
- #0 arg2: '2025' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; Dầu khí - BSR; 2023; none)
- #2: missing gold step #2: subtract(#0; #1)
- #3: missing gold step #3: divide(#2; #1)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 302 — ff18af6d-67a9-5b8a-959c-8bd805aaa462

Mức giá mục tiêu cơ bản của cổ phiếu CII cao hơn vùng cắt lỗ bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(25.8; 18); divide(#0; 18); multiply(#1; 100)`
- Model: `divide(40; 35); subtract(#0; 1); multiply(#1; 100)`
- #0: operator subtract -> divide
- #0 arg0: '25.8' -> '40'
- #0 arg1: '18' -> '35'
- #1: operator divide -> subtract
- #1 arg1: '18' -> '1'

## Dòng 303 — 0e5bd9e6-e40b-5c8d-b0aa-b9846b26c91f

Mức chênh lệch giữa tỷ lệ thay đổi theo tháng cao nhất và thấp nhất của chỉ số VN-Index trong 10 tháng đầu năm 2022 là bao nhiêu điểm phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 1; VN-Index; T1/2022; T10/2022); table_min(Table 1; VN-Index; T1/2022; T10/2022); subtract(#0; #1)`
- Model: `chart_max(Image 1; Tỷ lệ thay đổi theo tháng; none; none); chart_min(Image 1; Tỷ lệ thay đổi theo tháng; none; none); subtract(#0; #1)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'VN-Index' -> 'Tỷ lệ thay đổi theo tháng'
- #0 arg2: 'T1/2022' -> 'none'
- #0 arg3: 'T10/2022' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Image 1'
- #1 arg1: 'VN-Index' -> 'Tỷ lệ thay đổi theo tháng'
- #1 arg2: 'T1/2022' -> 'none'
- #1 arg3: 'T10/2022' -> 'none'

## Dòng 304 — 01fcbeb9-eb77-557c-872c-9f20a514320f

Chỉ số VNIndex đã thay đổi bao nhiêu phần trăm từ ngày 29/7/2022 đến ngày 31/8/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 31/8/2022; none); chart_at(Image 1; VNIndex; 29/7/2022; none); subtract(#0; #1); divide(#2; #1); multiply(#3; 100)`
- Model: `subtract(1280.51; 1200); divide(#0; 1200); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1280.51'
- #0 arg1: 'VNIndex' -> '1200'
- #0 arg2: '31/8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'VNIndex' -> '1200'
- #1 arg2: '29/7/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '100'
- #3: missing gold step #3: divide(#2; #1)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 305 — 96c33c73-e974-52ef-8159-ddd20aa624f5

Tỷ lệ lợi nhuận sau thuế trên doanh thu dự phóng năm 2024F của DPG là bao nhiêu?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `divide(211; 4142)`
- Model: `divide(211; 4142)`

## Dòng 306 — ea808364-14ea-5829-a796-63623e24f15e

Từ mức ước tính thấp đến mức ước tính cao của tỷ trọng Việt Nam trong chỉ số FTSE EM, mức tăng tương đối là bao nhiêu phần trăm?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff, strict_invalid
- Ground truth: `subtract(1.0; 0.7); divide(#0; 0.7); multiply(#1; 100)`
- Model: `divide(100; 0)`
- Vi phạm kiểm tra: division_zero@0
- #0: operator subtract -> divide
- #0 arg0: '1.0' -> '100'
- #0 arg1: '0.7' -> '0'
- #1: missing gold step #1: divide(#0; 0.7)
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 307 — 38280bd2-b4ca-5e3d-ba8c-9f4cee95862d

Mức giá mục tiêu mới của cổ phiếu DPG đã được nâng lên cao hơn bao nhiêu đồng so với mức giá mục tiêu cũ?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(52102; 44733)`
- Model: `subtract(52.102; 44.733)`
- #0 arg0: '52102' -> '52.102'
- #0 arg1: '44733' -> '44.733'

## Dòng 308 — ae969e3e-5c2e-55d7-b4c9-ddaaa2e3f410

Mức chi phí OPEX của 9 ngân hàng trong nhóm theo dõi năm 2023 đã thay đổi bao nhiêu phần trăm so với năm 2022?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `chart_at(Image 1; OPEX; 2022; none); chart_at(Image 1; OPEX; 2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_average(Table 1; OPEX; 2022; none); chart_average(Table 1; OPEX; 2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0: operator chart_at -> chart_average
- #0 arg0: 'Image 1' -> 'Table 1'
- #1: operator chart_at -> chart_average
- #1 arg0: 'Image 1' -> 'Table 1'

## Dòng 309 — a9f5ce5a-1905-5dbf-aed4-72d75dd2a555

Công suất của giai đoạn 2 của dự án LNG Sơn Mỹ lớn gấp bao nhiêu lần công suất của giai đoạn đầu tiên?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `divide(6; 3.6)`
- Model: `divide(6; 3.6)`

## Dòng 310 — 1aaa76a8-7f57-5893-8727-d8ebef8d61b5

Sau khi được mua lại và đầu tư trong năm 2022, công suất sản xuất xúc xích hằng năm của AFF tăng bao nhiêu phần trăm so với trước đầu tư?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(11200; 8400); divide(#0; 8400); multiply(#1; 100)`
- Model: `subtract(11200; 8400)`
- #1: missing gold step #1: divide(#0; 8400)
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 311 — f727669a-4bdd-50af-8ef8-b4023f42f9c9

Trong kế hoạch giai đoạn 2023-2026, khoản đầu tư Capex dự kiến chiếm bao nhiêu phần trăm số vốn Nova Consumer dự kiến tăng thêm?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(500; 1000); multiply(#0; 100)`
- Model: `divide(2000; 100)`
- #0 arg0: '500' -> '2000'
- #0 arg1: '1000' -> '100'
- #1: missing gold step #1: multiply(#0; 100)

## Dòng 312 — dda3614b-843a-543c-8f9d-dfc1e19c1b7b

Trong tháng 9/2022, mức biến động phần trăm thấp nhất được ghi nhận trong số các nhóm ngành là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_min(Table 1; T9/2022; none; none)`
- Model: `table_min(Table 1; Biến động % trong tháng; none; none)`
- #0 arg1: 'T9/2022' -> 'Biến động % trong tháng'

## Dòng 313 — 9f40e599-82ae-5246-b2bb-838bad6f350e

Dựa trên giá mục tiêu mới được cập nhật, hệ số P/E ngụ ý (implied P/E) của cổ phiếu FPT là bao nhiêu lần nếu tính theo EPS dự phóng của năm tài chính 2024?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(150640; 4798)`
- Model: `divide(150.64; 100)`
- #0 arg0: '150640' -> '150.64'
- #0 arg1: '4798' -> '100'

## Dòng 314 — 543a1ab6-5209-585b-9e14-604f8dc57e64

Giá mục tiêu cơ bản của PLX cao hơn bao nhiêu so với mức trung bình của vùng giá mục tiêu kỹ thuật?

- Nhãn: fewer_steps, invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `add(43.5; 44.6); divide(#0; 2); subtract(44; #1)`
- Model: `table_average(Table 1; PLX; none; 100; 100)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator add -> table_average
- #0 arg0: '43.5' -> 'Table 1'
- #0 arg1: '44.6' -> 'PLX'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> '100'
- #0 arg4: '<absent>' -> '100'
- #1: missing gold step #1: divide(#0; 2)
- #2: missing gold step #2: subtract(44; #1)

## Dòng 315 — 5f54a119-afff-5d80-8aae-96af849bab76

Trung bình mỗi cổ phiếu trong nhóm tác động tích cực nhất đến thị trường trong tháng đóng góp bao nhiêu điểm vào chỉ số?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `chart_average(Image 1; Index; none; none)`
- Model: `divide(0.5; 100)`
- #0: operator chart_average -> divide
- #0 arg0: 'Image 1' -> '0.5'
- #0 arg1: 'Index' -> '100'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'

## Dòng 316 — 03c489f4-728f-556a-8f3c-f4061be9c2cb

Mức cải thiện theo điểm phần trăm của tăng trưởng lợi nhuận năm 2024 so với mức giảm của năm trước đối với 83 cổ phiếu trong phạm vi nghiên cứu của SSI Research là bao nhiêu?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(15.3; -5.6)`
- Model: `divide(15.3; -5.6)`
- #0: operator subtract -> divide

## Dòng 317 — 5112e3c2-c2d6-5908-925b-29b99d18fb65

Mức điểm VNIndex đã thay đổi bao nhiêu phần trăm từ ngày 30/9/2022 đến ngày 31/10/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 30/9/2022; none); chart_at(Image 1; VNIndex; 31/10/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(100; 1027.94); divide(#0; 1000); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '100'
- #0 arg1: 'VNIndex' -> '1027.94'
- #0 arg2: '30/9/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'VNIndex' -> '1000'
- #1 arg2: '31/10/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 318 — 570e9b5d-37fb-5afe-bdd6-59a070ed28f0

Trong số các cổ phiếu có tác động tiêu cực nhất lên thị trường trong tháng 8, mức điểm tác động thấp nhất lên chỉ số VNIndex là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_min(Image 4; VNIndex; none; none)`
- Model: `table_min(Table 2; Điểm tác động; none; VNIndex)`
- #0: operator chart_min -> table_min
- #0 arg0: 'Image 4' -> 'Table 2'
- #0 arg1: 'VNIndex' -> 'Điểm tác động'
- #0 arg3: 'none' -> 'VNIndex'

## Dòng 319 — e84b465f-769b-5c49-afd0-ff4ef81cad23

Lũy kế giá trị mua/bán ròng của khối ngoại qua bốn tuần 5/9, 12/9, 19/9 và 26/9 là bao nhiêu?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 5; Giá trị mua/bán ròng; 9/5; none); chart_at(Image 5; Giá trị mua/bán ròng; 9/12; none); chart_at(Image 5; Giá trị mua/bán ròng; 9/19; none); chart_at(Image 5; Giá trị mua/bán ròng; 9/26; none); add(#0; #1); add(#4; #2); add(#5; #3)`
- Model: `chart_sum(Image 5; GTGD ròng NĐTNN; none; none)`
- #0: operator chart_at -> chart_sum
- #0 arg1: 'Giá trị mua/bán ròng' -> 'GTGD ròng NĐTNN'
- #0 arg2: '9/5' -> 'none'
- #1: missing gold step #1: chart_at(Image 5; Giá trị mua/bán ròng; 9/12; none)
- #2: missing gold step #2: chart_at(Image 5; Giá trị mua/bán ròng; 9/19; none)
- #3: missing gold step #3: chart_at(Image 5; Giá trị mua/bán ròng; 9/26; none)
- #4: missing gold step #4: add(#0; #1)
- #5: missing gold step #5: add(#4; #2)
- #6: missing gold step #6: add(#5; #3)

## Dòng 320 — e8d0c58d-5e8a-5011-bb1a-2147af343b9b

Tại 3Q24 (TTM), thu nhập lãi thuần gấp bao nhiêu lần chi phí hoạt động của 9 ngân hàng trong nhóm theo dõi?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NII; 3Q24 (TTM); none); chart_at(Image 1; OPEX; 3Q24 (TTM); none); divide(#0; #1)`
- Model: `divide(158; 158)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '158'
- #0 arg1: 'NII' -> '158'
- #0 arg2: '3Q24 (TTM)' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; OPEX; 3Q24 (TTM); none)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 321 — 9ba29d9a-08ec-5a58-81f4-4599b83842f9

Tổng thu nhập trên mỗi cổ phần trong 12 tháng (EPS 12T) của các ngân hàng thuộc nhóm NHTM quốc doanh là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_sum(Table 1; EPS 12T; VCB; CTG)`
- Model: `table_average(Table 1; EPS 12T; none; none)`
- #0: operator table_sum -> table_average
- #0 arg2: 'VCB' -> 'none'
- #0 arg3: 'CTG' -> 'none'

## Dòng 322 — 5298a46e-53af-5a2c-9b8d-e38a46797825

Tổng GTGD ròng của nhà đầu tư nước ngoài trên toàn bộ các mã thuộc nhóm cổ phiếu mua ròng/bán ròng nhiều nhất là bao nhiêu?

- Nhãn: missing_source_id, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `chart_sum(Image 7; GTGD ròng NĐTNN; none; none)`
- Model: `table_sum(Table 6; GTGD ròng NDTNN; none; none)`
- Vi phạm kiểm tra: source_missing@0:Table 6
- #0: operator chart_sum -> table_sum
- #0 arg0: 'Image 7' -> 'Table 6'
- #0 arg1: 'GTGD ròng NĐTNN' -> 'GTGD ròng NDTNN'

## Dòng 323 — dbe4e294-56e9-51ea-baf0-b0d195001de4

Tổng lợi nhuận ròng của IMP trong giai đoạn 2022-2024F là bao nhiêu tỷ đồng?

- Nhãn: invalid_arity, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_sum(Table 3; Lợi nhuận ròng; 2022; 2024F)`
- Model: `chart_sum(#0; LNR; none; 2022; 2024F)`
- Vi phạm kiểm tra: arity@0:5!=4; reference@0:#0; source_type@0:#0
- #0: operator table_sum -> chart_sum
- #0 arg0: 'Table 3' -> '#0'
- #0 arg1: 'Lợi nhuận ròng' -> 'LNR'
- #0 arg2: '2022' -> 'none'
- #0 arg3: '2024F' -> '2022'
- #0 arg4: '<absent>' -> '2024F'

## Dòng 324 — c3536c58-9312-526e-bda9-2872841ea97b

Mức giá mục tiêu cao nhất trong số các cổ phiếu dầu khí được đánh giá là bao nhiêu đồng?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Giá mục tiêu (đồng)@Trong 1 năm; none; none)`
- Model: `table_max(Table 1; none; Giá mục tiêu (VND/CP); none)`
- #0 arg1: 'Giá mục tiêu (đồng)@Trong 1 năm' -> 'none'
- #0 arg2: 'none' -> 'Giá mục tiêu (VND/CP)'

## Dòng 325 — 78df809f-a379-501a-a4b7-8bf20e611227

ROA dự phóng trung bình của Nova Consumer trong giai đoạn 2022-2026 là bao nhiêu?

- Nhãn: exact, repo_equivalent
- Ground truth: `chart_average(Image 2; ROA; 2022; 2026)`
- Model: `chart_average(Image 2; ROA; 2022; 2026)`

## Dòng 326 — ffa0ab78-f342-553f-a2f7-1c0f25831ee0

Trong 9T24, các mảng hoạt động CNTT toàn cầu, Viễn thông và Giáo dục đóng góp tổng cộng bao nhiêu phần trăm vào lợi nhuận trước thuế của tập đoàn?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `add(45; 33); add(#0; 20)`
- Model: `add(50; 45); add(#0; 10)`
- #0 arg0: '45' -> '50'
- #0 arg1: '33' -> '45'
- #1 arg1: '20' -> '10'

## Dòng 327 — 26e337d3-ccc2-5a00-94b5-479f0d0ac11c

Chênh lệch giữa tỷ lệ thay đổi giá vốn hàng bán (GVHB) lớn nhất và nhỏ nhất của các ngành được thống kê khi giá điện tăng 3% là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `table_max(Table 1; Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%; none; none); table_min(Table 1; Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%; none; none); subtract(#0; #1)`
- Model: `table_max(Table 1; %GVHB; none; Giày; Thép); table_min(Table 1; %GVHB; none; Giày; Thép); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; arity@1:5!=4
- #0 arg1: 'Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%' -> '%GVHB'
- #0 arg3: 'none' -> 'Giày'
- #0 arg4: '<absent>' -> 'Thép'
- #1 arg1: 'Thay đổi giá vốn hàng bán (GVHB) sau khi tăng giá điện 3%' -> '%GVHB'
- #1 arg3: 'none' -> 'Giày'
- #1 arg4: '<absent>' -> 'Thép'

## Dòng 328 — 73d1865d-8165-5c5b-8eea-9cd48b0ddf3c

Doanh thu dự kiến trong năm tài chính 2024 (FY24F) tăng trưởng bao nhiêu phần trăm so với năm tài chính 2023 (FY23)?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(61880; 52618); divide(#0; 52618); multiply(#1; 100)`
- Model: `subtract(61880; 59350); divide(#0; 59350); multiply(#1; 100)`
- #0 arg1: '52618' -> '59350'
- #1 arg1: '52618' -> '59350'

## Dòng 329 — 98c4dda8-3d15-5945-b21d-d742575d0f51

Tỷ trọng ước tính trung bình dành cho Việt Nam của các quỹ riêng lẻ mô phỏng theo chỉ số FTSE Russell là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_average(Table 1; Vietnam (ƯT); Vanguard Total International Stock Index Fund; Schwab Emerging Markets Equity ETF)`
- Model: `table_average(Table 1; Tỷ trọng (%); none; none)`
- #0 arg1: 'Vietnam (ƯT)' -> 'Tỷ trọng (%)'
- #0 arg2: 'Vanguard Total International Stock Index Fund' -> 'none'
- #0 arg3: 'Schwab Emerging Markets Equity ETF' -> 'none'

## Dòng 330 — 2b769b31-01a0-56d3-b2e8-6d725cca86fc

Biên độ chênh lệch giữa mức thay đổi giá cổ phiếu tuyệt đối cao nhất và thấp nhất trong các kỳ 1 tháng, 6 tháng và 12 tháng là bao nhiêu điểm phần trăm?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; Tuyệt đối; 1M; 12M); table_min(Table 1; Tuyệt đối; 1M; 12M); subtract(#0; #1)`
- Model: `chart_max(Table 1; Change; none; none); chart_min(Table 1; Change; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0: operator table_max -> chart_max
- #0 arg1: 'Tuyệt đối' -> 'Change'
- #0 arg2: '1M' -> 'none'
- #0 arg3: '12M' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg1: 'Tuyệt đối' -> 'Change'
- #1 arg2: '1M' -> 'none'
- #1 arg3: '12M' -> 'none'

## Dòng 331 — 83f22f63-3439-5a46-b513-882a75a4cc76

Tổng tác động ròng lên chỉ số thị trường của nhóm cổ phiếu tác động tích cực nhất và nhóm cổ phiếu tác động tiêu cực nhất trong tháng là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_sum(Image 1; Index; none; none); chart_sum(Image 2; Index; none; none); add(#0; #1)`
- Model: `multiply(0.5; -7)`
- #0: operator chart_sum -> multiply
- #0 arg0: 'Image 1' -> '0.5'
- #0 arg1: 'Index' -> '-7'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_sum(Image 2; Index; none; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 332 — 87a7802f-f47e-50eb-9aef-30ff9489502e

Khoảng chênh lệch giữa mức thấp nhất và cao nhất của ước tính dòng vốn Việt Nam có thể thu hút ngay khi quyết định nâng hạng có hiệu lực là bao nhiêu tỷ USD?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(2.5; 1.7)`
- Model: `subtract(2.5; 1.7)`

## Dòng 333 — cfc7c28b-208b-5afc-97f0-3900c75c80b1

Trong tháng 10 năm 2023, dòng vốn đầu tư vào thị trường Taiwan có lớn hơn thị trường Korea hay không?

- Nhãn: both_math_only, invalid_arity, invalid_math_argument, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `greater(1.989; 1.703)`
- Model: `greater(Table 1#Taiwan#none)`
- Vi phạm kiểm tra: arity@0:1!=2; math_type@0:Table 1#Taiwan#none
- #0 arg0: '1.989' -> 'Table 1#Taiwan#none'
- #0 arg1: '1.703' -> '<absent>'

## Dòng 334 — 35f534be-c810-506b-84c2-639aa9e525af

Tỷ lệ giữa giá mục tiêu cơ bản của cổ phiếu BCM so với cổ phiếu MWG là bao nhiêu?

- Nhãn: invalid_arity, invalid_reference, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `divide(88.7; 61.5)`
- Model: `table_divide(#1; 100)`
- Vi phạm kiểm tra: unknown_operator@0:table_divide; arity@0:2!=4; reference@0:#1
- #0: operator divide -> table_divide
- #0 arg0: '88.7' -> '#1'
- #0 arg1: '61.5' -> '100'

## Dòng 335 — 85621d0b-995f-563d-8128-ea0e650b2373

Tổng giá trị mua ròng của khối ngoại đối với các mã VNM, MSN, FRT, DGC, IDC, DCM, VCB và DPM trong tháng 10 là bao nhiêu tỷ đồng?

- Nhãn: fewer_steps, invalid_arity, lookup_added_to_math_gold, missing_source_id, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `add(881; 694); add(#0; 364); add(#1; 354); add(#2; 325); add(#3; 255); add(#4; 239); add(#5; 214)`
- Model: `table_sum(Table 6; GTGD ròng NDTNN; none; VNM; none)`
- Vi phạm kiểm tra: arity@0:5!=4; source_missing@0:Table 6
- #0: operator add -> table_sum
- #0 arg0: '881' -> 'Table 6'
- #0 arg1: '694' -> 'GTGD ròng NDTNN'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'VNM'
- #0 arg4: '<absent>' -> 'none'
- #1: missing gold step #1: add(#0; 364)
- #2: missing gold step #2: add(#1; 354)
- #3: missing gold step #3: add(#2; 325)
- #4: missing gold step #4: add(#3; 255)
- #5: missing gold step #5: add(#4; 239)
- #6: missing gold step #6: add(#5; 214)

## Dòng 336 — 7899eac3-f8ee-5884-88c8-5eef80673dac

Mức tăng trưởng lợi nhuận bình quân so với cùng kỳ của các NHNY trong quý 1, quý 2 và Q3/2024 là bao nhiêu?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `add(9.5; 22.6); add(#0; 17.7); divide(#1; 3)`
- Model: `add(9.5; 22.6); add(#0; 17.7); divide(#1; 3)`

## Dòng 337 — 8ef58221-ea1c-5203-b942-816e6dd98690

Tại thời điểm tháng 11/2023, nhóm Y Tế vượt VNIndex bao nhiêu điểm phần trăm về mức sinh lời?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Nhóm Y Tế; Nov-23; none); chart_at(Image 1; VNIndex; Nov-23; none); subtract(#0; #1)`
- Model: `subtract(29; 12)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '29'
- #0 arg1: 'Nhóm Y Tế' -> '12'
- #0 arg2: 'Nov-23' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; VNIndex; Nov-23; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 338 — 946992bf-c5ca-50cf-a341-f1808f0bea54

Chênh lệch giữa ROE và ROA dự phóng trong năm 2026 là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; ROE; 2026; none); chart_at(Image 2; ROA; 2026; none); subtract(#0; #1)`
- Model: `subtract(13.6; 12.4)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '13.6'
- #0 arg1: 'ROE' -> '12.4'
- #0 arg2: '2026' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; ROA; 2026; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 339 — 01277405-12bc-5d63-a98f-241f5f156577

Thu nhập khác (NOI) của 9 ngân hàng trong nhóm theo dõi tại 3Q24 (TTM) có vượt mức năm 2023 hay không?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NOI; 3Q24 (TTM); none); chart_at(Image 1; NOI; 2023; none); greater(#0; #1)`
- Model: `greater(53; 52)`
- #0: operator chart_at -> greater
- #0 arg0: 'Image 1' -> '53'
- #0 arg1: 'NOI' -> '52'
- #0 arg2: '3Q24 (TTM)' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; NOI; 2023; none)
- #2: missing gold step #2: greater(#0; #1)

## Dòng 340 — c6122971-780d-562f-8fa4-43a6933013e0

Doanh thu thuần của IMP năm 2023 đã tăng bao nhiêu phần trăm so với năm 2019?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(1835; 1402); divide(#0; 1402); multiply(#1; 100)`
- Model: `divide(37387; 33554)`
- #0: operator subtract -> divide
- #0 arg0: '1835' -> '37387'
- #0 arg1: '1402' -> '33554'
- #1: missing gold step #1: divide(#0; 1402)
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 341 — 70a9e9cc-5dfd-5ead-a16c-2e7d50879bca

Mức tăng của nhóm cổ phiếu ngành Y Tế vào tháng 6/2023 cao hơn bao nhiêu điểm phần trăm so với mức tăng của cả nhóm trong năm 2023?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 1; Nhóm Y Tế; Jun-23; none); subtract(#0; 29)`
- Model: `chart_average(Image 1; none; none; none)`
- #0: operator chart_at -> chart_average
- #0 arg1: 'Nhóm Y Tế' -> 'none'
- #0 arg2: 'Jun-23' -> 'none'
- #1: missing gold step #1: subtract(#0; 29)

## Dòng 342 — 95866f50-fc97-51c1-9bef-0dba476ada95

Tính đến tháng 10 năm 2023, tổng dòng vốn lũy kế từ đầu năm vào ba nhóm tài sản tài chính gồm cổ phiếu, trái phiếu và tiền tệ là bao nhiêu tỷ USD?

- Nhãn: fewer_steps, invalid_source_type, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; Cổ phiếu; Oct-23; none); chart_at(Image 2; Trái phiếu; Oct-23; none); chart_at(Image 2; Tiền tệ; Oct-23; none); add(#0; #1); add(#3; #2)`
- Model: `chart_total(Table 4; Dòng vốn lũy kế từ đầu năm; Oct-23; Oct-23)`
- Vi phạm kiểm tra: source_type@0:Table 4
- #0: operator chart_at -> chart_total
- #0 arg0: 'Image 2' -> 'Table 4'
- #0 arg1: 'Cổ phiếu' -> 'Dòng vốn lũy kế từ đầu năm'
- #0 arg3: 'none' -> 'Oct-23'
- #1: missing gold step #1: chart_at(Image 2; Trái phiếu; Oct-23; none)
- #2: missing gold step #2: chart_at(Image 2; Tiền tệ; Oct-23; none)
- #3: missing gold step #3: add(#0; #1)
- #4: missing gold step #4: add(#3; #2)

## Dòng 343 — 5726e52f-00cc-52d5-b27d-1e1162086cc2

Tại Mar 24, giá trị chỉ số hóa của DPG VN có cao hơn VN-Index không?

- Nhãn: fewer_steps, invalid_math_argument, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 1; DPG VN; Mar 24; none); chart_at(Image 1; VN-Index; Mar 24; none); greater(#0; #1)`
- Model: `greater(Table 2@Mar 24; Table 2@VN-Index)`
- Vi phạm kiểm tra: math_type@0:Table 2@Mar 24; math_type@0:Table 2@VN-Index
- #0: operator chart_at -> greater
- #0 arg0: 'Image 1' -> 'Table 2@Mar 24'
- #0 arg1: 'DPG VN' -> 'Table 2@VN-Index'
- #0 arg2: 'Mar 24' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; VN-Index; Mar 24; none)
- #2: missing gold step #2: greater(#0; #1)

## Dòng 344 — cc50fda9-20ae-5e1b-8249-204ae462dfeb

Trong năm 2023, chênh lệch bao nhiêu điểm phần trăm giữa mức thay đổi trung bình của 5 nhóm ngành Dịch vụ tài chính, Tài nguyên cơ bản, Hóa chất, Dầu khí và CNTT so với mức thay đổi trung bình của 3 nhóm Bán lẻ, Thực phẩm đồ uống và Du lịch giải trí?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `add(69.4; 42.9); add(#0; 37.6); add(#1; 36); add(#2; 43.2); divide(#3; 5); add(11.4; -4.5); add(#5; -5.2); divide(#6; 3); subtract(#4; #7)`
- Model: `divide(69.4; 100); divide(43.2; 100); divide(37.6; 100); divide(36; 100); divide(43.2; 100); add(#0; #1); add(#2; #3); add(#4; #5); add(#6; #7); divide(83.8; 5); divide(7.3; 3); subtract(#9; #10)`
- #0: operator add -> divide
- #0 arg1: '42.9' -> '100'
- #1: operator add -> divide
- #1 arg0: '#0' -> '43.2'
- #1 arg1: '37.6' -> '100'
- #2: operator add -> divide
- #2 arg0: '#1' -> '37.6'
- #2 arg1: '36' -> '100'
- #3: operator add -> divide
- #3 arg0: '#2' -> '36'
- #3 arg1: '43.2' -> '100'
- #4 arg0: '#3' -> '43.2'
- #4 arg1: '5' -> '100'
- #5 arg0: '11.4' -> '#0'
- #5 arg1: '-4.5' -> '#1'
- #6 arg0: '#5' -> '#2'
- #6 arg1: '-5.2' -> '#3'
- #7: operator divide -> add
- #7 arg0: '#6' -> '#4'
- #7 arg1: '3' -> '#5'
- #8: operator subtract -> add
- #8 arg0: '#4' -> '#6'
- #9: extra predicted step #9: divide(83.8; 5)
- #10: extra predicted step #10: divide(7.3; 3)
- #11: extra predicted step #11: subtract(#9; #10)

## Dòng 345 — 7d088730-dd28-56f3-a938-20f6f3e69498

Trong 10 nhóm ngành, khoảng chênh lệch giữa mức sinh lời lũy kế từ đầu năm 2022 cao nhất và thấp nhất là bao nhiêu điểm phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Năm 2022; Tài chính; Y tế); table_min(Table 1; Năm 2022; Tài chính; Y tế); subtract(#0; #1)`
- Model: `table_max(Table 1; Lợi nhuận lũy kế từ đầu năm; none; none); table_min(Table 1; Lợi nhuận lũy kế từ đầu năm; none; none); subtract(#0; #1)`
- #0 arg1: 'Năm 2022' -> 'Lợi nhuận lũy kế từ đầu năm'
- #0 arg2: 'Tài chính' -> 'none'
- #0 arg3: 'Y tế' -> 'none'
- #1 arg1: 'Năm 2022' -> 'Lợi nhuận lũy kế từ đầu năm'
- #1 arg2: 'Tài chính' -> 'none'
- #1 arg3: 'Y tế' -> 'none'

## Dòng 346 — 4de3f754-d893-571d-86af-c874c05ac836

Liệu ước tính dòng vốn của Vanguard Total International Stock Index Fund có lớn hơn tổng mức ước tính dòng vốn của Vanguard Institutional Total International Stock Market Index Trust II và Vanguard Total World Stock ETF hay không?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `add(317.4; 20.6); greater(565.8; #0)`
- Model: `divide(1.7; 2.5)`
- #0: operator add -> divide
- #0 arg0: '317.4' -> '1.7'
- #0 arg1: '20.6' -> '2.5'
- #1: missing gold step #1: greater(565.8; #0)

## Dòng 347 — 3b60d761-8dd7-5be3-bcb5-edb83266029d

Dự phóng mức chênh lệch giữa tỷ suất sinh lời trên vốn chủ sở hữu (ROE) và tỷ suất sinh lời trên tổng tài sản (ROA) của Nova Consumer trong năm 2025 là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; ROE; 2025; none); chart_at(Image 2; ROA; 2025; none); subtract(#0; #1)`
- Model: `subtract(7.14; 6.65)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '7.14'
- #0 arg1: 'ROE' -> '6.65'
- #0 arg2: '2025' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; ROA; 2025; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 348 — 44fb96f7-457f-54af-8f0f-edaa98af36c8

Trong 9T2024, tổng tỷ trọng của hai cấu phần thu nhập từ kinh doanh ngoại hối và chứng khoán đầu tư là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 13; Kinh doanh ngoại hối; 9M24; none); chart_at(Image 13; Chứng khoán đầu tư; 9M24; none); add(#0; #1)`
- Model: `add(24; 7)`
- #0: operator chart_at -> add
- #0 arg0: 'Image 13' -> '24'
- #0 arg1: 'Kinh doanh ngoại hối' -> '7'
- #0 arg2: '9M24' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 13; Chứng khoán đầu tư; 9M24; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 349 — 452c4562-24b6-59b3-b79d-55a527d5f121

Trung bình mỗi tháng, dòng vốn đầu tư vào thị trường Mỹ trong giai đoạn từ tháng 8/2023 đến tháng 10/2023 là bao nhiêu?

- Nhãn: invalid_arity, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_average(Table 1; US; Aug-23; Oct-23)`
- Model: `chart_average(Table 1; DM Equity; Aug-23; Oct-23; none)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 1
- #0: operator table_average -> chart_average
- #0 arg1: 'US' -> 'DM Equity'
- #0 arg4: '<absent>' -> 'none'

## Dòng 350 — bd6ee8ee-935d-51b5-901a-f82ad0653bcb

Trong T12, mức thay đổi giá cao nhất trong số các nhóm ngành đạt bao nhiêu phần trăm?

- Nhãn: exact, repo_equivalent
- Ground truth: `chart_max(Image 1; T12; none; none)`
- Model: `chart_max(Image 1; T12; none; none)`

## Dòng 351 — c787fa68-0742-5e59-91cb-5bec6f27bd77

Chênh lệch giữa tỷ lệ thay đổi của VNIndex suy ra từ mức điểm ngày 29/7/2022 và 31/8/2022 với mức sinh lời của VN-Index trong tháng 8/2022 là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 29/7/2022; none); chart_at(Image 1; VNIndex; 31/8/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); subtract(#4; 6.1)`
- Model: `subtract(1280.51; 1200); divide(#0; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1280.51'
- #0 arg1: 'VNIndex' -> '1200'
- #0 arg2: '29/7/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'VNIndex' -> '100'
- #1 arg2: '31/8/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: subtract(#4; 6.1)

## Dòng 352 — be9da4e2-31c6-5322-b71a-ff2271cd4f73

Dòng vốn đầu tư vào nhóm tài sản trái phiếu trong tháng 1 năm 2025 đã tăng trưởng bao nhiêu phần trăm so với tháng 12 năm 2024?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Trái phiếu; Dec-24; none); chart_at(Image 1; Trái phiếu; Jan-25; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `multiply(67.2; 64.7); divide(#0; 100)`
- #0: operator chart_at -> multiply
- #0 arg0: 'Image 1' -> '67.2'
- #0 arg1: 'Trái phiếu' -> '64.7'
- #0 arg2: 'Dec-24' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Trái phiếu' -> '100'
- #1 arg2: 'Jan-25' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 353 — da6c7685-ffa5-5847-aa25-2d0815a8f8cc

Doanh thu thuần của IMP dự phóng năm 2024F tăng bao nhiêu phần trăm so với năm 2023?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(2113; 1835); divide(#0; 1835); multiply(#1; 100)`
- Model: `subtract(114; 100); divide(#0; 100)`
- #0 arg0: '2113' -> '114'
- #0 arg1: '1835' -> '100'
- #1 arg1: '1835' -> '100'
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 354 — b8488d06-8871-58f6-8b36-464f78cb0384

Mức biến động theo tháng của VN-Index đã thay đổi bao nhiêu điểm phần trăm từ tháng 9/2023 sang tháng 10/2023?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(-10.9; -5.7)`
- Model: `subtract(-7; -6)`
- #0 arg0: '-10.9' -> '-7'
- #0 arg1: '-5.7' -> '-6'

## Dòng 355 — 106fa713-c784-582d-b05b-dc7901931320

Từ Jun 22 đến Jun 24, chỉ số hiệu suất của DPG VN đã thay đổi bao nhiêu phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_at(Image 1; DPG VN; Jun 22; none); chart_at(Image 1; DPG VN; Jun 24; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 1; Jun 22; none; 100); chart_at(Image 1; Jun 24; none; 100); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- #0 arg1: 'DPG VN' -> 'Jun 22'
- #0 arg2: 'Jun 22' -> 'none'
- #0 arg3: 'none' -> '100'
- #1 arg1: 'DPG VN' -> 'Jun 24'
- #1 arg2: 'Jun 24' -> 'none'
- #1 arg3: 'none' -> '100'

## Dòng 356 — 53198c36-6daa-5653-a34f-b9e0cf2891fa

Tỷ lệ lợi nhuận gộp trên doanh thu thuần năm 2024F của IMP là bao nhiêu?

- Nhãn: both_math_only, invalid_math_argument, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `divide(897; 2113)`
- Model: `divide(#1; Table 3#Doanh thu thuần 2024F#none#none)`
- Vi phạm kiểm tra: reference@0:#1; math_type@0:Table 3#Doanh thu thuần 2024F#none#none
- #0 arg0: '897' -> '#1'
- #0 arg1: '2113' -> 'Table 3#Doanh thu thuần 2024F#none#none'

## Dòng 357 — 88ae9b5f-eac4-5d3f-b635-cd6e2cd2ba8a

Chênh lệch giữa dòng vốn vào quỹ cổ phiếu trong tháng 9/2023 ghi nhận theo tháng và dòng vốn tháng 9/2023 suy ra từ biến động mức lũy kế từ đầu năm giữa tháng 8 và tháng 9 là bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Cổ phiếu; Sep-23; none); chart_at(Image 2; Cổ phiếu; Aug-23; none); chart_at(Image 2; Cổ phiếu; Sep-23; none); subtract(#2; #1); subtract(#0; #3)`
- Model: `subtract(150; 150)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '150'
- #0 arg1: 'Cổ phiếu' -> '150'
- #0 arg2: 'Sep-23' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; Cổ phiếu; Aug-23; none)
- #2: missing gold step #2: chart_at(Image 2; Cổ phiếu; Sep-23; none)
- #3: missing gold step #3: subtract(#2; #1)
- #4: missing gold step #4: subtract(#0; #3)

## Dòng 358 — 5747b97e-10a7-5f02-87dc-b910b545c788

Trong số các quỹ lớn mô phỏng theo các chỉ số của FTSE Russell, mức ước tính dòng vốn cao nhất là bao nhiêu triệu USD?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Ước tính dòng vốn (triệu USD); Vanguard Total International Stock Index Fund; Schwab Emerging Markets Equity ETF)`
- Model: `table_max(Table 1; Dòng vốn vào VN (triệu USD); none; none)`
- #0 arg1: 'Ước tính dòng vốn (triệu USD)' -> 'Dòng vốn vào VN (triệu USD)'
- #0 arg2: 'Vanguard Total International Stock Index Fund' -> 'none'
- #0 arg3: 'Schwab Emerging Markets Equity ETF' -> 'none'

## Dòng 359 — bc5630fa-3c65-5643-bc50-d4981ae0291c

Dòng vốn đầu tư bình quân mỗi tháng vào thị trường Ấn Độ trong giai đoạn từ Jan-23 đến Oct-23 là bao nhiêu tỷ USD?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_average(Table 1; India; Jan-23; Oct-23)`
- Model: `table_average(Table 1; India; none; Oct-23)`
- #0 arg2: 'Jan-23' -> 'none'

## Dòng 360 — d5e9007e-4905-5d8b-a119-9fb384b39287

Độ rộng của khoảng dự báo tăng trưởng lợi nhuận ròng năm 2025 là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(20; 15)`
- Model: `subtract(20; 15)`

## Dòng 361 — 8151ba4d-ca53-544d-afa7-d8d688e9f85b

Tổng sản lượng dự phóng năm 2027 của bốn lưu vực khí chính gồm Cửu Long, Nam Côn Sơn 1, Nam Côn Sơn 2 và PM3 là bao nhiêu tỷ m3/năm?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 2; Cửu Long; 2027F; none); chart_at(Image 2; Nam Côn Sơn 1; 2027F; none); chart_at(Image 2; Nam Côn Sơn 2; 2027F; none); chart_at(Image 2; PM3; 2027F; none); add(#0; #1); add(#2; #3); add(#4; #5)`
- Model: `chart_sum(Image 3; Lưu lượng khí dự phóng năm 2027; none; none)`
- #0: operator chart_at -> chart_sum
- #0 arg0: 'Image 2' -> 'Image 3'
- #0 arg1: 'Cửu Long' -> 'Lưu lượng khí dự phóng năm 2027'
- #0 arg2: '2027F' -> 'none'
- #1: missing gold step #1: chart_at(Image 2; Nam Côn Sơn 1; 2027F; none)
- #2: missing gold step #2: chart_at(Image 2; Nam Côn Sơn 2; 2027F; none)
- #3: missing gold step #3: chart_at(Image 2; PM3; 2027F; none)
- #4: missing gold step #4: add(#0; #1)
- #5: missing gold step #5: add(#2; #3)
- #6: missing gold step #6: add(#4; #5)

## Dòng 362 — 0b7b5473-0a3d-564a-9b96-29bfcd0a429b

Nếu lấy dòng vốn quỹ cổ phiếu toàn cầu tháng 10/2023 được suy ra từ biến động mức lũy kế đầu năm 2023 giữa cuối tháng 9 và cuối tháng 10, rồi trừ đi tổng dòng vốn vào DM equity và EM equity trong cùng tháng, chênh lệch là bao nhiêu tỷ USD?

- Nhãn: aligned_noncommutative_swap, fewer_steps, invalid_arity, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 2; Cổ phiếu; Sep-23; none); chart_at(Image 2; Cổ phiếu; Oct-23; none); subtract(#1; #0); subtract(-9853; -7081); subtract(#2; #3)`
- Model: `chart_at(Image 4; Dòng vốn lũy kế đầu năm 2023; Oct-23; none); chart_at(Image 4; Dòng vốn lũy kế đầu năm 2023; Sep-23; none); subtract(#0; #1); chart_total(#3; DM equity; EM equity)`
- Vi phạm kiểm tra: arity@3:3!=4; reference@3:#3; source_type@3:#3
- #0 arg0: 'Image 2' -> 'Image 4'
- #0 arg1: 'Cổ phiếu' -> 'Dòng vốn lũy kế đầu năm 2023'
- #0 arg2: 'Sep-23' -> 'Oct-23'
- #1 arg0: 'Image 2' -> 'Image 4'
- #1 arg1: 'Cổ phiếu' -> 'Dòng vốn lũy kế đầu năm 2023'
- #1 arg2: 'Oct-23' -> 'Sep-23'
- #2 arg0: '#1' -> '#0'
- #2 arg1: '#0' -> '#1'
- #3: operator subtract -> chart_total
- #3 arg0: '-9853' -> '#3'
- #3 arg1: '-7081' -> 'DM equity'
- #3 arg2: '<absent>' -> 'EM equity'
- #4: missing gold step #4: subtract(#2; #3)

## Dòng 363 — 7d91e260-af71-5018-8d57-ca7690a85187

Trong năm 2023, chênh lệch doanh thu giữa mảng Xây dựng và mảng Bất động sản của DPG là bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(2875; 26)`
- Model: `subtract(3450; 26)`
- #0 arg0: '2875' -> '3450'

## Dòng 364 — 2ae0ac58-eb7d-58b4-9453-821335a5c7e1

Tổng tỷ suất cổ tức năm 2023 của hai mã cổ phiếu VEA và PNJ là bao nhiêu phần trăm?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `add(13; 2.3)`
- Model: `table_average(Table 2; Tỷ suất cổ tức theo năm; none; 2023; VEA; none); table_average(Table 2; Tỷ suất cổ tức theo năm; none; 2023; PNJ; none); add(#0; #1)`
- Vi phạm kiểm tra: arity@0:6!=4; arity@1:6!=4
- #0: operator add -> table_average
- #0 arg0: '13' -> 'Table 2'
- #0 arg1: '2.3' -> 'Tỷ suất cổ tức theo năm'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> '2023'
- #0 arg4: '<absent>' -> 'VEA'
- #0 arg5: '<absent>' -> 'none'
- #1: extra predicted step #1: table_average(Table 2; Tỷ suất cổ tức theo năm; none; 2023; PNJ; none)
- #2: extra predicted step #2: add(#0; #1)

## Dòng 365 — b7e011af-a5aa-5146-98e0-02ab520a283b

Tổng sản lượng của bốn lưu vực khí chính Cửu Long, Nam Côn Sơn 1, Nam Côn Sơn 2 và PM3 thay đổi bao nhiêu phần trăm từ năm 2021 đến mức dự phóng 2030F?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 2; Cửu Long; 2021; none); chart_at(Image 2; Nam Côn Sơn 1; 2021; none); add(#0; #1); chart_at(Image 2; Nam Côn Sơn 2; 2021; none); add(#2; #3); chart_at(Image 2; PM3; 2021; none); add(#4; #5); chart_at(Image 2; Cửu Long; 2030F; none); chart_at(Image 2; Nam Côn Sơn 1; 2030F; none); add(#7; #8); chart_at(Image 2; Nam Côn Sơn 2; 2030F; none); add(#9; #10); chart_at(Image 2; PM3; 2030F; none); add(#11; #12); subtract(#13; #6); divide(#14; #6); multiply(#15; 100)`
- Model: `chart_average(Image 1; Cửu Long; 2021; 2030F)`
- #0: operator chart_at -> chart_average
- #0 arg0: 'Image 2' -> 'Image 1'
- #0 arg3: 'none' -> '2030F'
- #1: missing gold step #1: chart_at(Image 2; Nam Côn Sơn 1; 2021; none)
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: chart_at(Image 2; Nam Côn Sơn 2; 2021; none)
- #4: missing gold step #4: add(#2; #3)
- #5: missing gold step #5: chart_at(Image 2; PM3; 2021; none)
- #6: missing gold step #6: add(#4; #5)
- #7: missing gold step #7: chart_at(Image 2; Cửu Long; 2030F; none)
- #8: missing gold step #8: chart_at(Image 2; Nam Côn Sơn 1; 2030F; none)
- #9: missing gold step #9: add(#7; #8)
- #10: missing gold step #10: chart_at(Image 2; Nam Côn Sơn 2; 2030F; none)
- #11: missing gold step #11: add(#9; #10)
- #12: missing gold step #12: chart_at(Image 2; PM3; 2030F; none)
- #13: missing gold step #13: add(#11; #12)
- #14: missing gold step #14: subtract(#13; #6)
- #15: missing gold step #15: divide(#14; #6)
- #16: missing gold step #16: multiply(#15; 100)

## Dòng 366 — 3de72dc8-c9c0-58db-93c3-375c25ad601c

Trung bình tỷ suất lợi nhuận trên vốn chủ sở hữu (ROE) của HBC trong giai đoạn từ năm tài chính 2015 đến năm 2020 (bao gồm cả năm dự phóng) là bao nhiêu phần trăm?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_average(Table 1; ROE (%); FY 2015; FY2020(F))`
- Model: `chart_average(Image 1; ROE; none)`
- Vi phạm kiểm tra: arity@0:3!=4
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'ROE (%)' -> 'ROE'
- #0 arg2: 'FY 2015' -> 'none'
- #0 arg3: 'FY2020(F)' -> '<absent>'

## Dòng 367 — 0ff675b0-f61e-59e7-bea2-16173d0a5661

Tính từ đầu năm 2022, mức sinh lời của ngành Công nghệ thông tin có cao hơn mức sinh lời của VN-Index không?

- Nhãn: lookup_added_to_math_gold, non_exact, operator_sequence_diff
- Ground truth: `greater(2.8; -24.4)`
- Model: `table_average(Table 1; Công nghệ thông tin; none; none)`
- #0: operator greater -> table_average
- #0 arg0: '2.8' -> 'Table 1'
- #0 arg1: '-24.4' -> 'Công nghệ thông tin'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'

## Dòng 368 — c1158a75-9471-5259-85ef-71ad90450384

Trong giai đoạn từ năm 2019 đến năm 2024F, mức chênh lệch giữa giá trị lợi nhuận gộp cao nhất và thấp nhất của Imexpharm (IMP) là bao nhiêu tỷ đồng?

- Nhãn: invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_max(Table 3; Lợi nhuận gộp; 2019; 2024F); table_min(Table 3; Lợi nhuận gộp; 2019; 2024F); subtract(#0; #1)`
- Model: `chart_max(#1; none; 2019; 2024F); chart_min(#1; none; 2019; 2024F); subtract(#0; #1)`
- Vi phạm kiểm tra: reference@0:#1; source_type@0:#1; reference@1:#1; source_type@1:#1
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 3' -> '#1'
- #0 arg1: 'Lợi nhuận gộp' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 3' -> '#1'
- #1 arg1: 'Lợi nhuận gộp' -> 'none'

## Dòng 369 — f8ff0b92-f471-5b41-b62b-6313e39b9ada

Trung bình cộng của mục tiêu tăng trưởng lợi nhuận năm 2024 của DHG, mức dự phóng tăng trưởng NPATMI năm 2024 của TNH và mức dự phóng tăng trưởng lợi nhuận ròng năm 2024 của IMP là bao nhiêu phần trăm?

- Nhãn: fewer_steps, invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `add(-4; 4.7); add(#0; 14.5); divide(#1; 3)`
- Model: `table_average(Table 2; Lợi nhuận sau thuế; none; 2024F; none; 100)`
- Vi phạm kiểm tra: arity@0:6!=4
- #0: operator add -> table_average
- #0 arg0: '-4' -> 'Table 2'
- #0 arg1: '4.7' -> 'Lợi nhuận sau thuế'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> '2024F'
- #0 arg4: '<absent>' -> 'none'
- #0 arg5: '<absent>' -> '100'
- #1: missing gold step #1: add(#0; 14.5)
- #2: missing gold step #2: divide(#1; 3)

## Dòng 370 — b4af41df-d7be-552e-8e0e-78bb664ad037

Tổng mức tác động ròng (tính bằng điểm chỉ số) lên thị trường trong tháng của cổ phiếu có tác động tích cực nhất (SSB) và cổ phiếu có tác động tiêu cực nhất (VHM) là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Index; SSB; none); chart_at(Image 2; Index; VHM; none); add(#0; #1)`
- Model: `multiply(0.5; -7)`
- #0: operator chart_at -> multiply
- #0 arg0: 'Image 1' -> '0.5'
- #0 arg1: 'Index' -> '-7'
- #0 arg2: 'SSB' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; Index; VHM; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 371 — 398cd118-5eb8-56fd-a3ca-2b9c18df2353

Trong số các quỹ mô phỏng theo các chỉ số của FTSE Russell, chênh lệch giữa tỷ trọng phân bổ vào Indonesia cao nhất và thấp nhất là bao nhiêu điểm phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; Indonesia; Vanguard Total International Stock Index Fund; Schwab Emerging Markets Equity ETF); table_min(Table 1; Indonesia; Vanguard Total International Stock Index Fund; Schwab Emerging Markets Equity ETF); subtract(#0; #1)`
- Model: `table_max(Table 1; Indonesia; none; none); table_min(Table 1; Indonesia; none; none); subtract(#0; #1)`
- #0 arg2: 'Vanguard Total International Stock Index Fund' -> 'none'
- #0 arg3: 'Schwab Emerging Markets Equity ETF' -> 'none'
- #1 arg2: 'Vanguard Total International Stock Index Fund' -> 'none'
- #1 arg3: 'Schwab Emerging Markets Equity ETF' -> 'none'

## Dòng 372 — 53f8d20b-765f-58c5-ae1b-78364d9b6a2f

Trong nhóm cổ phiếu y tế DBD, DCL, DHG, DHT, DMC, DVM, IMP, PBC, TRA và VMD, chênh lệch giữa mức P/E hiện tại cao nhất và thấp nhất là bao nhiêu lần?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; Hiện tại; none; none); table_min(Table 1; Hiện tại; none; none); subtract(#0; #1)`
- Model: `chart_max(Table 3; P/E 2023; none; none); chart_min(Table 3; P/E 2023; none; none); divide(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 3; source_type@1:Table 3
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Table 3'
- #0 arg1: 'Hiện tại' -> 'P/E 2023'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Table 3'
- #1 arg1: 'Hiện tại' -> 'P/E 2023'
- #2: operator subtract -> divide

## Dòng 373 — e2563c70-ff3a-59bd-bc91-d197cb80dab7

Mức tăng trung bình trong năm 2023 của 5 nhóm ngành diễn biến tích cực nhất gồm Dịch vụ tài chính, Tài nguyên cơ bản, Hóa chất, Dầu khí và CNTT là bao nhiêu phần trăm?

- Nhãn: fewer_steps, invalid_arity, invalid_source_type, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `add(69.4; 42.9); add(#0; 37.6); add(#1; 36); add(#2; 43.2); divide(#3; 5)`
- Model: `chart_average(Table 1; Dịch vụ tài chính; Công nghệ thông tin; Du lịch giải trí; Dầu khí)`
- Vi phạm kiểm tra: arity@0:5!=4; source_type@0:Table 1
- #0: operator add -> chart_average
- #0 arg0: '69.4' -> 'Table 1'
- #0 arg1: '42.9' -> 'Dịch vụ tài chính'
- #0 arg2: '<absent>' -> 'Công nghệ thông tin'
- #0 arg3: '<absent>' -> 'Du lịch giải trí'
- #0 arg4: '<absent>' -> 'Dầu khí'
- #1: missing gold step #1: add(#0; 37.6)
- #2: missing gold step #2: add(#1; 36)
- #3: missing gold step #3: add(#2; 43.2)
- #4: missing gold step #4: divide(#3; 5)

## Dòng 374 — 64665cb1-161d-5f92-86b7-d823e02d5265

Trong tháng 1 năm 2025, mức chênh lệch giữa dòng vốn đầu tư vào tài sản cổ phiếu và dòng vốn rót vào các quỹ cổ phiếu tại thị trường phát triển (DM) là bao nhiêu tỷ USD?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_at(Image 1; Cổ phiếu; Jan-25; none); chart_at(Image 2; Phát triển (DM); Jan-25; none); subtract(#0; #1)`
- Model: `chart_at(Image 1; Cổ phiếu; Jan-25; none); divide(#0; 100)`
- #1: operator chart_at -> divide
- #1 arg0: 'Image 2' -> '#0'
- #1 arg1: 'Phát triển (DM)' -> '100'
- #1 arg2: 'Jan-25' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 375 — 87f99443-66bf-5f05-9dde-5fde098f0d51

Doanh thu tổng cộng dự phóng tăng bao nhiêu phần trăm từ năm 2023 lên năm 2026?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `subtract(17133.3; 8792.6); divide(#0; 8792.6); multiply(#1; 100)`
- Model: `divide(100; 100); divide(100; 100); add(#0; #1)`
- #0: operator subtract -> divide
- #0 arg0: '17133.3' -> '100'
- #0 arg1: '8792.6' -> '100'
- #1 arg0: '#0' -> '100'
- #1 arg1: '8792.6' -> '100'
- #2: operator multiply -> add
- #2 arg0: '#1' -> '#0'
- #2 arg1: '100' -> '#1'

## Dòng 376 — 7d3057ca-9abd-5e3a-8151-6c3bf18f78ea

Mức chênh lệch giữa tỷ lệ tăng trưởng huy động từ đầu năm cao nhất và thấp nhất được ghi nhận qua các tháng trong năm 2023 là bao nhiêu phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_max(Image 1; 2023; none; none); chart_min(Image 1; 2023; none; none); subtract(#0; #1)`
- Model: `table_max(Table 3; Tăng trưởng huy động từ đầu năm; none; none); table_min(Table 3; Tăng trưởng huy động từ đầu năm; none; none); subtract(#0; #1)`
- #0: operator chart_max -> table_max
- #0 arg0: 'Image 1' -> 'Table 3'
- #0 arg1: '2023' -> 'Tăng trưởng huy động từ đầu năm'
- #1: operator chart_min -> table_min
- #1 arg0: 'Image 1' -> 'Table 3'
- #1 arg1: '2023' -> 'Tăng trưởng huy động từ đầu năm'

## Dòng 377 — ab0086fc-52fc-5be2-b378-c3370d5e4697

Trong tháng 1/2025, chênh lệch giữa tổng dòng vốn vào quỹ cổ phiếu và tổng dòng vốn vào hai nhóm thị trường phát triển và đang phát triển là bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; Phát triển (DM); Jan-25; none); chart_at(Image 2; Đang phát triển (EM); Jan-25; none); add(#0; #1); chart_at(Image 1; Cổ phiếu; Jan-25; none); subtract(#3; #2)`
- Model: `subtract(64.7; -67.3)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '64.7'
- #0 arg1: 'Phát triển (DM)' -> '-67.3'
- #0 arg2: 'Jan-25' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; Đang phát triển (EM); Jan-25; none)
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: chart_at(Image 1; Cổ phiếu; Jan-25; none)
- #4: missing gold step #4: subtract(#3; #2)

## Dòng 378 — b4c64dd5-0920-54fb-99a0-d80d93f6a781

Tỷ lệ sở hữu gộp của ông Lê Viết Hải và những người có liên quan tại HBC chênh lệch bao nhiêu điểm phần trăm so với tổng tỷ lệ sở hữu tách riêng của hai nhóm "Lê Viết Hải" và "Liên quan Ông Lê Viết Hải"?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Lê Viết Hải; none; none); chart_at(Image 1; Liên quan Ông Lê Viết Hải; none; none); add(#0; #1); subtract(21; #2)`
- Model: `add(16; 5); subtract(21; #0)`
- #0: operator chart_at -> add
- #0 arg0: 'Image 1' -> '16'
- #0 arg1: 'Lê Viết Hải' -> '5'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> subtract
- #1 arg0: 'Image 1' -> '21'
- #1 arg1: 'Liên quan Ông Lê Viết Hải' -> '#0'
- #1 arg2: 'none' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: add(#0; #1)
- #3: missing gold step #3: subtract(21; #2)

## Dòng 379 — 0bc098fa-ec2f-57c8-ac1a-7c803191ecb0

Tỷ trọng chi phí điện trên GVHB của ngành Xi măng có cao hơn ngành Hóa chất không?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `greater(14; 9)`
- Model: `divide(15; 10)`
- #0: operator greater -> divide
- #0 arg0: '14' -> '15'
- #0 arg1: '9' -> '10'

## Dòng 380 — 4d00fac3-be0e-5a54-9c32-26a6db53e514

Khoảng chênh lệch giữa vùng cắt lỗ cao nhất và thấp nhất của các cổ phiếu trong danh sách khuyến nghị là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 1; Vùng cắt lỗ; none; none); table_min(Table 1; Vùng cắt lỗ; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; Tỷ lệ phần trăm giảm giá trong 1 năm; none; none); chart_min(Image 1; Tỷ lệ phần trăm giảm giá trong 1 năm; none; none); subtract(#0; #1)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Vùng cắt lỗ' -> 'Tỷ lệ phần trăm giảm giá trong 1 năm'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Image 1'
- #1 arg1: 'Vùng cắt lỗ' -> 'Tỷ lệ phần trăm giảm giá trong 1 năm'

## Dòng 381 — 1999e81e-d014-57c1-9f99-c39742d68ea7

Khoảng chênh lệch giữa giá mục tiêu cơ bản và vùng cắt lỗ của BCM là bao nhiêu?

- Nhãn: both_math_only, invalid_reference, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, strict_invalid
- Ground truth: `subtract(88.7; 66)`
- Model: `divide(#1; 100)`
- Vi phạm kiểm tra: reference@0:#1
- #0: operator subtract -> divide
- #0 arg0: '88.7' -> '#1'
- #0 arg1: '66' -> '100'

## Dòng 382 — 19df9c1c-94e9-513c-bcd9-e3325cfcf037

Khoảng cách điểm số giữa cổ phiếu có tác động tích cực lớn nhất và cổ phiếu có tác động tiêu cực mạnh nhất lên chỉ số trong tháng 9 là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 3; Index; none; none); chart_min(Image 4; Index; none; none); subtract(#0; #1)`
- Model: `subtract(0; 1)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 3' -> '0'
- #0 arg1: 'Index' -> '1'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 4; Index; none; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 383 — ca266b41-7619-551c-b7ff-ac09e7f6593e

Trong tháng 10/2023, mức biến động giá của VHM chênh lệch bao nhiêu điểm phần trăm so với VN-Index?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; % +/-; VHM; none); subtract(#0; -10.9)`
- Model: `divide(-7; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '-7'
- #0 arg1: '% +/-' -> '100'
- #0 arg2: 'VHM' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: subtract(#0; -10.9)

## Dòng 384 — 7250382a-39e4-5acf-a1b6-9b8b47d68d70

P/E ước tính thay đổi bao nhiêu phần trăm từ ngày 9/2/2023 đến ngày 11/2/2024?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_at(Image 1; P/E ước tính cho năm tài chính hiện tại; 9/2/2023; none); chart_at(Image 1; P/E ước tính 2024; 11/2/2024; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 1; P/E; Jan-23; none); chart_at(Image 1; P/E; Nov-24; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- #0 arg1: 'P/E ước tính cho năm tài chính hiện tại' -> 'P/E'
- #0 arg2: '9/2/2023' -> 'Jan-23'
- #1 arg1: 'P/E ước tính 2024' -> 'P/E'
- #1 arg2: '11/2/2024' -> 'Nov-24'

## Dòng 385 — 9a519c89-49c8-5992-b12a-b6cd451b8a23

Mức chi phí tín dụng trung bình của 3 quý đầu năm 2024 có lớn hơn mức dự báo của chỉ tiêu này cho cả năm 2024 hay không?

- Nhãn: invalid_arity, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_average(Image 9; Chi phí tín dụng; 1Q24; 3Q24); greater(#0; 1.28)`
- Model: `chart_average(#1; Chi phí tín dụng; none; 1Q24; 3Q24); 9.0; subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; reference@0:#1; source_type@0:#1; unknown_operator@1:INVALID; arity@1:1!=4
- #0 arg0: 'Image 9' -> '#1'
- #0 arg2: '1Q24' -> 'none'
- #0 arg3: '3Q24' -> '1Q24'
- #0 arg4: '<absent>' -> '3Q24'
- #1: operator greater -> INVALID
- #1 arg0: '#0' -> '9.0'
- #1 arg1: '1.28' -> '<absent>'
- #2: extra predicted step #2: subtract(#0; #1)

## Dòng 386 — f877b53f-eed0-5787-a299-34de9ad61bd3

Mức chênh lệch về tỷ lệ tăng trưởng giữa nhóm ngành Dịch vụ tài chính và nhóm ngành Tài nguyên cơ bản trong năm 2023 là bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(69.4; 42.9)`
- Model: `subtract(42.9; 37.6)`
- #0 arg0: '69.4' -> '42.9'
- #0 arg1: '42.9' -> '37.6'

## Dòng 387 — 2b68adc4-d9dc-5a8e-9a69-6e717ab2fd0e

Chênh lệch bao nhiêu điểm phần trăm giữa tỷ lệ nhu cầu sử dụng được đáp ứng bởi thuốc sản xuất trong nước hiện tại và mục tiêu đến năm 2030?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(80; 60)`
- Model: `subtract(80; 45)`
- #0 arg1: '60' -> '45'

## Dòng 388 — f2a9be01-bf01-50dd-ae6a-4cde845f9332

Vào ngày 25/8/2022, nếu lấy giá trị NĐTNN Mua trừ giá trị NĐTNN Bán rồi tiếp tục trừ giá trị mua/bán ròng, kết quả là bao nhiêu?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 5; NĐTNN Mua; 25/8/2022; none); chart_at(Image 5; NĐTNN Bán; 25/8/2022; none); subtract(#0; #1); chart_at(Image 5; Giá trị mua/bán ròng; 25/8/2022; none); subtract(#2; #3)`
- Model: `subtract(0; 0); subtract(#1; #2)`
- Vi phạm kiểm tra: reference@1:#1; reference@1:#2
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 5' -> '0'
- #0 arg1: 'NĐTNN Mua' -> '0'
- #0 arg2: '25/8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> subtract
- #1 arg0: 'Image 5' -> '#1'
- #1 arg1: 'NĐTNN Bán' -> '#2'
- #1 arg2: '25/8/2022' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#0; #1)
- #3: missing gold step #3: chart_at(Image 5; Giá trị mua/bán ròng; 25/8/2022; none)
- #4: missing gold step #4: subtract(#2; #3)

## Dòng 389 — b4e3a3fb-f025-56a0-a1a0-ff41bc612255

Trong tháng 9, tổng mức tác động ròng lên chỉ số VNIndex của hai cổ phiếu NVL và VCB là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; Index; NVL; none); chart_at(Image 4; Index; VCB; none); add(#0; #1)`
- Model: `subtract(-14.0; -8.0)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 3' -> '-14.0'
- #0 arg1: 'Index' -> '-8.0'
- #0 arg2: 'NVL' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 4; Index; VCB; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 390 — a187bde5-2327-5d0a-873e-d846e45ac785

Theo dự báo của IEA cho năm 2025, nguồn cung dầu toàn cầu dự kiến tương đương bao nhiêu lần nhu cầu dầu toàn cầu dự kiến?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `divide(104.8; 103.9)`
- Model: `divide(104.8; 103.9)`

## Dòng 391 — 84611c3f-23ac-5e0e-8aca-b74e9e765481

Mức chênh lệch giữa hệ số định giá P/E dự phóng năm 2024 của cổ phiếu FPT và chỉ số P/E trung bình cùng năm của ngành Công nghệ Thông tin là bao nhiêu?

- Nhãn: invalid_math_argument, lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff, strict_invalid
- Ground truth: `subtract(16.7; 15.4)`
- Model: `table_average(Table 3; P/E 2024; Công nghệ Thông tin; none); subtract(FPT#P/E 2024; #0)`
- Vi phạm kiểm tra: math_type@1:FPT#P/E 2024
- #0: operator subtract -> table_average
- #0 arg0: '16.7' -> 'Table 3'
- #0 arg1: '15.4' -> 'P/E 2024'
- #0 arg2: '<absent>' -> 'Công nghệ Thông tin'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: subtract(FPT#P/E 2024; #0)

## Dòng 392 — 6adc6bad-e270-572f-bb59-b5fb4034629b

Nếu lấy mức tăng trưởng doanh thu FY24 suy ra từ doanh thu 2023H và 2024F của DPG trừ đi mức tăng trưởng doanh thu FY24 được nêu ra, kết quả chênh lệch là bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(4142; 3450); divide(#0; 3450); multiply(#1; 100); subtract(#2; 20)`
- Model: `subtract(20; 4)`
- #0 arg0: '4142' -> '20'
- #0 arg1: '3450' -> '4'
- #1: missing gold step #1: divide(#0; 3450)
- #2: missing gold step #2: multiply(#1; 100)
- #3: missing gold step #3: subtract(#2; 20)

## Dòng 393 — 53711127-a34c-5e49-a319-23bd7dbf8a74

Trong tháng 1/2025, chênh lệch giữa dòng vốn vào quỹ cổ phiếu của khối thị trường đang phát triển (EM) và tổng dòng vốn vào các thị trường Trung Quốc, Ấn Độ, Indonesia, Hàn Quốc, Đài Loan, Thái Lan và Việt Nam là bao nhiêu tỷ USD?

- Nhãn: aligned_noncommutative_swap, non_exact, operator_sequence_diff
- Ground truth: `table_sum(Table 1; Jan-25; China; Vietnam); chart_at(Image 2; Đang phát triển (EM); Jan-25; none); subtract(#1; #0)`
- Model: `table_sum(Table 1; Dòng vốn đầu tư vào một số thị trường chính (tỷ USD); Trung Quốc; Đài Loan); table_sum(Table 1; Dòng vốn đầu tư vào một số thị trường chính (tỷ USD); Indonesia; Hàn Quốc); subtract(#0; #1)`
- #0 arg1: 'Jan-25' -> 'Dòng vốn đầu tư vào một số thị trường chính (tỷ USD)'
- #0 arg2: 'China' -> 'Trung Quốc'
- #0 arg3: 'Vietnam' -> 'Đài Loan'
- #1: operator chart_at -> table_sum
- #1 arg0: 'Image 2' -> 'Table 1'
- #1 arg1: 'Đang phát triển (EM)' -> 'Dòng vốn đầu tư vào một số thị trường chính (tỷ USD)'
- #1 arg2: 'Jan-25' -> 'Indonesia'
- #1 arg3: 'none' -> 'Hàn Quốc'
- #2 arg0: '#1' -> '#0'
- #2 arg1: '#0' -> '#1'

## Dòng 394 — 0b1b1093-ac9c-506e-8380-f8f4b49c172f

So với thời điểm đầu năm 2020, thị giá cổ phiếu khi chạm mức thấp nhất (tính theo cận dưới của vùng giá) trong cùng năm đã thay đổi bao nhiêu phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(5800; 11400); divide(#0; 11400); multiply(#1; 100)`
- Model: `subtract(5800; 11400); divide(#0; 11400); multiply(#1; 100)`

## Dòng 395 — 9031d0bd-4724-5bb3-a54a-e6da0fbfa9a9

Dựa trên EPS năm 2019, hệ số định giá P/E của doanh nghiệp sẽ là bao nhiêu lần nếu tính theo cận dưới của vùng giá thấp nhất được ghi nhận trong năm 2020?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `divide(5800; 1717)`
- Model: `divide(5800; 100); divide(#0; 18822)`
- #0 arg1: '1717' -> '100'
- #1: extra predicted step #1: divide(#0; 18822)

## Dòng 396 — a377ad50-b5ef-573c-b37a-7c295dce35f6

Tổng giá trị giải ngân cho vay trung và dài hạn trong 3 quý đầu năm 2024 là bao nhiêu nghìn tỷ đồng?

- Nhãn: lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_sum(Image 3; Cho vay trung và dài hạn; 1Q24; 3Q24)`
- Model: `add(171; 179); add(#0; 179); add(#1; 399)`
- #0: operator chart_sum -> add
- #0 arg0: 'Image 3' -> '171'
- #0 arg1: 'Cho vay trung và dài hạn' -> '179'
- #0 arg2: '1Q24' -> '<absent>'
- #0 arg3: '3Q24' -> '<absent>'
- #1: extra predicted step #1: add(#0; 179)
- #2: extra predicted step #2: add(#1; 399)

## Dòng 397 — 2ca9a337-b7ca-53c6-9501-2ee145396493

Trong giai đoạn 2021H đến 2026F, chênh lệch giữa ROE cao nhất và thấp nhất của DPG là bao nhiêu điểm phần trăm?

- Nhãn: invalid_arity, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `table_max(Table 2; ROE (%); 2021H; 2026F); table_min(Table 2; ROE (%); 2021H; 2026F); subtract(#0; #1)`
- Model: `chart_max(#1; ROE; none; 2021H; 2026F); chart_min(#1; ROE; none; 2021H; 2026F); subtract(#0; #1)`
- Vi phạm kiểm tra: arity@0:5!=4; reference@0:#1; source_type@0:#1; arity@1:5!=4; reference@1:#1; source_type@1:#1
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 2' -> '#1'
- #0 arg1: 'ROE (%)' -> 'ROE'
- #0 arg2: '2021H' -> 'none'
- #0 arg3: '2026F' -> '2021H'
- #0 arg4: '<absent>' -> '2026F'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 2' -> '#1'
- #1 arg1: 'ROE (%)' -> 'ROE'
- #1 arg2: '2021H' -> 'none'
- #1 arg3: '2026F' -> '2021H'
- #1 arg4: '<absent>' -> '2026F'

## Dòng 398 — d6ffe95d-93ad-54b5-b06c-27cfd58fd4bf

Trong tháng 9/2022, tỷ lệ thanh khoản của VN30 so với thanh khoản của VNIndex là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; VN30; T9/2022; none); chart_at(Image 2; VNIndex; T9/2022; none); divide(#0; #1)`
- Model: `divide(11.59; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 2' -> '11.59'
- #0 arg1: 'VN30' -> '100'
- #0 arg2: 'T9/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; VNIndex; T9/2022; none)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 399 — 8e8cab36-cbef-5c36-9e42-2ef03ee339bc

Doanh thu dự phóng năm 2026 của mảng FMCG có vượt qua mức đóng góp doanh thu tối đa hằng năm được kỳ vọng cho mảng này hay không?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `greater(2022; 2200)`
- Model: `greater(2200; 1786)`
- #0 arg0: '2022' -> '2200'
- #0 arg1: '2200' -> '1786'

## Dòng 400 — 6e899d6f-a5c4-5b1f-91c3-759852c9974e

Dòng tiền của VNIndex đã thay đổi bao nhiêu phần trăm từ tháng 7/2022 đến tháng 9/2022?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `chart_at(Image 3; VNIndex; T7/2022; none); chart_at(Image 3; VNIndex; T9/2022; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_average(Image 3; VNIndex; Jul-22; none); chart_average(Image 3; VNIndex; Sep-22; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- #0: operator chart_at -> chart_average
- #0 arg2: 'T7/2022' -> 'Jul-22'
- #1: operator chart_at -> chart_average
- #1 arg2: 'T9/2022' -> 'Sep-22'

## Dòng 401 — 713fcec6-809f-5148-a5c8-54aead79aee5

Tốc độ tăng trưởng của VN-Index từ tháng 12/2022 đến tháng 12/2023 là bao nhiêu phần trăm?

- Nhãn: exact, repo_equivalent
- Ground truth: `chart_at(Image 1; VN-Index; Dec 22; none); chart_at(Image 1; VN-Index; Dec 23; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `chart_at(Image 1; VN-Index; Dec 22; none); chart_at(Image 1; VN-Index; Dec 23; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`

## Dòng 402 — eefd4e0b-0767-5903-8a04-523ac0f80f2d

Mức chênh lệch giữa tỷ lệ nợ xấu (NPL) cao nhất và thấp nhất trong nhóm NHTM tư nhân Mirae theo dõi là bao nhiêu phần trăm?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 1; NPL (%); ACB; VPB); table_min(Table 1; NPL (%); ACB; VPB); subtract(#0; #1)`
- Model: `chart_max(Image 1; NPL; none; none); chart_min(Image 1; NPL; none; none); subtract(#0; #1)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'NPL (%)' -> 'NPL'
- #0 arg2: 'ACB' -> 'none'
- #0 arg3: 'VPB' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Image 1'
- #1 arg1: 'NPL (%)' -> 'NPL'
- #1 arg2: 'ACB' -> 'none'
- #1 arg3: 'VPB' -> 'none'

## Dòng 403 — f1c763d1-cde9-5c62-bf37-6c148f82b99a

Từ dự báo tổng mức tăng nguồn cung dầu toàn cầu và mức tăng từ các quốc gia không thuộc OPEC+ trong năm 2025, mức đóng góp ngầm định vào sự tăng trưởng nguồn cung từ các quốc gia OPEC+ là bao nhiêu triệu thùng/ngày?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(1.9; 1.5)`
- Model: `subtract(1.6; 1.9)`
- #0 arg0: '1.9' -> '1.6'
- #0 arg1: '1.5' -> '1.9'

## Dòng 404 — cae72f8a-b513-5215-8910-cfa1a128f9a4

Tỷ lệ giữa giá mục tiêu và giá cắt lỗ của cổ phiếu BCM là bao nhiêu?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(82500; 70000)`
- Model: `divide(25; 10)`
- #0 arg0: '82500' -> '25'
- #0 arg1: '70000' -> '10'

## Dòng 405 — 9dcacf50-b005-5ff0-b753-58b218a187a9

Mức chênh lệch giữa tỷ trọng ước tính của Việt Nam trong chỉ số FTSE Global và tỷ trọng ước tính của Việt Nam tại quỹ Vanguard Total World Stock ETF là bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(0.1; 0.07)`
- Model: `subtract(0.1; 0.7)`
- #0 arg1: '0.07' -> '0.7'

## Dòng 406 — a70f0b1f-07b9-56ae-be4d-3c26fcceedc7

Khoảng chênh lệch giữa mức lợi nhuận sau thuế cao nhất và thấp nhất của HBC trong giai đoạn năm tài chính 2015 đến 2020 dự phóng là bao nhiêu tỷ đồng?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `table_max(Table 1; LNST (VNDbn); FY 2015; FY2020(F)); table_min(Table 1; LNST (VNDbn); FY 2015; FY2020(F)); subtract(#0; #1)`
- Model: `subtract(859; 417)`
- #0: operator table_max -> subtract
- #0 arg0: 'Table 1' -> '859'
- #0 arg1: 'LNST (VNDbn)' -> '417'
- #0 arg2: 'FY 2015' -> '<absent>'
- #0 arg3: 'FY2020(F)' -> '<absent>'
- #1: missing gold step #1: table_min(Table 1; LNST (VNDbn); FY 2015; FY2020(F))
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 407 — f0d3b239-5e53-51b7-94dd-73d85d4645c8

Sự chênh lệch về giá trị dòng tiền vào ròng giữa Quỹ thị trường tiền tệ và Quỹ cổ phiếu toàn cầu trong tháng 1 là bao nhiêu tỷ USD?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(86; 64.7)`
- Model: `subtract(86; 64.7)`

## Dòng 408 — df4d14cd-3414-5a7e-873c-72f6764c4303

Tổng giá trị vào ròng của quỹ cổ phiếu toàn cầu trong tháng 1 cao hơn giá trị dòng vốn vào tài sản Cổ phiếu tại Jan-25 bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Cổ phiếu; Jan-25; none); subtract(64.7; #0)`
- Model: `subtract(64.7; 5.0)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '64.7'
- #0 arg1: 'Cổ phiếu' -> '5.0'
- #0 arg2: 'Jan-25' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: subtract(64.7; #0)

## Dòng 409 — 9d1e2066-d7a9-5475-8662-093004ba20a9

Tổng tác động ròng lên chỉ số của các cổ phiếu tác động tích cực nhất và các cổ phiếu tác động tiêu cực nhất trong tháng 9 là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_sum(Image 3; Index; none; none); chart_sum(Image 4; Index; none; none); add(#0; #1)`
- Model: `add(600; -200)`
- #0: operator chart_sum -> add
- #0 arg0: 'Image 3' -> '600'
- #0 arg1: 'Index' -> '-200'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_sum(Image 4; Index; none; none)
- #2: missing gold step #2: add(#0; #1)

## Dòng 410 — 6fe947ea-0288-5c4d-a89f-edaab925ccd1

Trong năm 2025, tổng doanh thu dự phóng của mảng thức ăn chăn nuôi và thuốc thú y là bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `add(4221; 1296)`
- Model: `multiply(100; 100)`
- #0: operator add -> multiply
- #0 arg0: '4221' -> '100'
- #0 arg1: '1296' -> '100'

## Dòng 411 — 241fb5fe-c2bc-52f8-bc9d-949274a7fdf2

Trong tháng 10/2023, tổng giá trị mua ròng của khối ngoại ở nhóm cổ phiếu được mua ròng nhiều nhất tương đương bao nhiêu lần giá trị thực hiện qua kênh khớp lệnh của khối ngoại trong cùng tháng?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `chart_sum(Image 3; T10/2023; none; none); multiply(4; 1000); divide(#0; #1)`
- Model: `chart_sum(Image 3; T10/2023; none; none)`
- #1: missing gold step #1: multiply(4; 1000)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 412 — 704fba48-a281-5a0d-ba98-039934e92941

Trong 10 tháng đầu năm 2023, chênh lệch giữa mức dòng vốn DM equity theo tháng cao nhất và thấp nhất là bao nhiêu tỷ USD?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `table_max(Table 1; DM equity; Jan-23; Oct-23); table_min(Table 1; DM equity; Jan-23; Oct-23); subtract(#0; #1)`
- Model: `table_max(Table 1; DM Equity; Jan-23; none); table_min(Table 1; DM Equity; Sep-23; none); subtract(#0; #1)`
- #0 arg1: 'DM equity' -> 'DM Equity'
- #0 arg3: 'Oct-23' -> 'none'
- #1 arg1: 'DM equity' -> 'DM Equity'
- #1 arg2: 'Jan-23' -> 'Sep-23'
- #1 arg3: 'Oct-23' -> 'none'

## Dòng 413 — 2348a26c-a114-566a-9f7c-7a27546c994f

Giá trị dòng vốn vào quỹ cổ phiếu thị trường phát triển (DM) trung bình tại các mốc Jan-24, May-24, Sep-24 và Jan-25 là bao nhiêu tỷ USD?

- Nhãn: invalid_arity, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_average(Image 2; Phát triển (DM); Jan-24; Jan-25)`
- Model: `table_average(Table 1; Cổ phiếu; Jan-24; none; Sep-24; May-24; Jan-25)`
- Vi phạm kiểm tra: arity@0:7!=4
- #0: operator chart_average -> table_average
- #0 arg0: 'Image 2' -> 'Table 1'
- #0 arg1: 'Phát triển (DM)' -> 'Cổ phiếu'
- #0 arg3: 'Jan-25' -> 'none'
- #0 arg4: '<absent>' -> 'Sep-24'
- #0 arg5: '<absent>' -> 'May-24'
- #0 arg6: '<absent>' -> 'Jan-25'

## Dòng 414 — 5a2ef8aa-ca89-593a-ab7b-e8e292989639

Sản lượng tiêu thụ trung bình của PLX trong giai đoạn từ năm 2019 đến năm 2025 là bao nhiêu?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_average(Image 3; Dầu khí - PLX; none; none)`
- Model: `chart_average(Image 1; 消费量(百万吨); 2019; 2025#1)`
- #0 arg0: 'Image 3' -> 'Image 1'
- #0 arg1: 'Dầu khí - PLX' -> '消费量(百万吨)'
- #0 arg2: 'none' -> '2019'
- #0 arg3: 'none' -> '2025#1'

## Dòng 415 — 7c2ec6d6-3053-5f7c-a774-cc2a183f5172

Tỷ lệ giữa mức thay đổi giá trong T12 và mức thay đổi giá của cả năm 2023 đối với nhóm ngành Dầu khí là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; T12; Dầu khí; none); chart_at(Image 1; 2023; Dầu khí; none); divide(#0; #1)`
- Model: `divide(10; 100)`
- #0: operator chart_at -> divide
- #0 arg0: 'Image 1' -> '10'
- #0 arg1: 'T12' -> '100'
- #0 arg2: 'Dầu khí' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; 2023; Dầu khí; none)
- #2: missing gold step #2: divide(#0; #1)

## Dòng 416 — d3dde7ea-1f80-5d51-b5c3-7f1097ec2442

Mức chênh lệch dự phóng tăng trưởng NPATMI năm 2024 giữa ngành Công nghệ Thông tin và ngành Công nghiệp là bao nhiêu phần trăm?

- Nhãn: invalid_arity, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `subtract(22.8; 11.2)`
- Model: `table_average(Table 3; Tăng trưởng NPATMI 2024; Công nghệ Thông tin; none; Công nghiệp)`
- Vi phạm kiểm tra: arity@0:5!=4
- #0: operator subtract -> table_average
- #0 arg0: '22.8' -> 'Table 3'
- #0 arg1: '11.2' -> 'Tăng trưởng NPATMI 2024'
- #0 arg2: '<absent>' -> 'Công nghệ Thông tin'
- #0 arg3: '<absent>' -> 'none'
- #0 arg4: '<absent>' -> 'Công nghiệp'

## Dòng 417 — 57967b08-5e32-55f8-bfe1-09a882b5ddc5

Giá trị ròng của khối ngoại đối với cổ phiếu STB trong tháng 10/2023 cao hơn giá trị ròng lũy kế năm 2023 bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 3; T10/2023; STB; none); chart_at(Image 3; 2023; STB; none); subtract(#0; #1)`
- Model: `subtract(700; 500)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 3' -> '700'
- #0 arg1: 'T10/2023' -> '500'
- #0 arg2: 'STB' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 3; 2023; STB; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 418 — f50aeb5a-fb16-5f80-b2a0-d99ec371b6bd

Trong tháng 1 năm 2025, dòng vốn đầu tư vào cổ phiếu có lớn hơn dòng vốn đầu tư vào trái phiếu hay không?

- Nhãn: exact, repo_equivalent
- Ground truth: `chart_at(Image 1; Cổ phiếu; Jan-25; none); chart_at(Image 1; Trái phiếu; Jan-25; none); greater(#0; #1)`
- Model: `chart_at(Image 1; Cổ phiếu; Jan-25; none); chart_at(Image 1; Trái phiếu; Jan-25; none); greater(#0; #1)`

## Dòng 419 — f5ce5f40-8089-566d-8ce7-a9ffc4d1617e

Trong các tháng Jan-23, Mar-23, May-23, Jul-23 và Sep-23, chênh lệch giữa mức dòng vốn theo tháng vào Tiền tệ cao nhất và thấp nhất là bao nhiêu tỷ USD?

- Nhãn: invalid_reference, invalid_source_type, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_max(Image 1; Tiền tệ; Jan-23; Sep-23); chart_min(Image 1; Tiền tệ; Jan-23; Sep-23); subtract(#0; #1)`
- Model: `chart_max(Table 1#Tiền tệ#Jan-23#Sep-23; none; none; none); chart_min(Table 1#Tiền tệ#Jan-23#Sep-23; none; none; none); subtract(#1; #2)`
- Vi phạm kiểm tra: source_type@0:Table 1#Tiền tệ#Jan-23#Sep-23; source_type@1:Table 1#Tiền tệ#Jan-23#Sep-23; reference@2:#2
- #0 arg0: 'Image 1' -> 'Table 1#Tiền tệ#Jan-23#Sep-23'
- #0 arg1: 'Tiền tệ' -> 'none'
- #0 arg2: 'Jan-23' -> 'none'
- #0 arg3: 'Sep-23' -> 'none'
- #1 arg0: 'Image 1' -> 'Table 1#Tiền tệ#Jan-23#Sep-23'
- #1 arg1: 'Tiền tệ' -> 'none'
- #1 arg2: 'Jan-23' -> 'none'
- #1 arg3: 'Sep-23' -> 'none'
- #2 arg0: '#0' -> '#1'
- #2 arg1: '#1' -> '#2'

## Dòng 420 — 408cde68-219c-5025-9406-f0e90f5e169c

Với IMP, nếu lấy mức giá hiện tại đi kèm với P/E 2024F và chia cho EPS 2024F dự phóng, thì P/E 2024F hàm ý cao hơn P/E 2024F được nêu cho công ty bao nhiêu lần?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `divide(61100; 4863); subtract(#0; 12.5)`
- Model: `divide(12.5; 10000); divide(76000; #0)`
- #0 arg0: '61100' -> '12.5'
- #0 arg1: '4863' -> '10000'
- #1: operator subtract -> divide
- #1 arg0: '#0' -> '76000'
- #1 arg1: '12.5' -> '#0'

## Dòng 421 — 3308ae21-c911-52e0-b8e7-a858be9267b6

Biên độ tăng giá kỳ vọng của cổ phiếu FMC từ mức giá hiện tại vào ngày 31/1/2024 đến mức giá mục tiêu 1 năm là bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(55500; 44600); divide(#0; 44600); multiply(#1; 100)`
- Model: `subtract(1300; 1000); divide(#0; 1000); multiply(#1; 100)`
- #0 arg0: '55500' -> '1300'
- #0 arg1: '44600' -> '1000'
- #1 arg1: '44600' -> '1000'

## Dòng 422 — ed0c6796-3a0e-52d8-a3f0-e2e14b8924bc

Giá mục tiêu cơ bản của cổ phiếu STB gấp bao nhiêu lần vùng cắt lỗ?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `divide(37.5; 28)`
- Model: `divide(20.5; 18.5)`
- #0 arg0: '37.5' -> '20.5'
- #0 arg1: '28' -> '18.5'

## Dòng 423 — 747334f2-ded3-52f7-8287-7e25e65549e6

Mức tăng trưởng NPATMI 2025F của PVD cao hơn dự báo tăng trưởng lợi nhuận năm 2025 của PVD bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(50.1; 50)`
- Model: `subtract(50; 20)`
- #0 arg0: '50.1' -> '50'
- #0 arg1: '50' -> '20'

## Dòng 424 — 12740dc4-0990-5d0c-8c3c-9750b8e6bb12

Chênh lệch giữa mức giá mục tiêu cao nhất và thấp nhất của các cổ phiếu được khuyến nghị trong báo cáo tháng 8/2022 là bao nhiêu?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; Giá mục tiêu; none; none); table_min(Table 1; Giá mục tiêu; none; none); subtract(#0; #1)`
- Model: `chart_max(Table 3; Giá mục tiêu cao nhất; none; none); chart_min(Table 3; Giá mục tiêu thấp nhất; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 3; source_type@1:Table 3
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 1' -> 'Table 3'
- #0 arg1: 'Giá mục tiêu' -> 'Giá mục tiêu cao nhất'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 1' -> 'Table 3'
- #1 arg1: 'Giá mục tiêu' -> 'Giá mục tiêu thấp nhất'

## Dòng 425 — 73e618af-72f3-565a-b49d-73fc518e041d

Mức tăng giá tiềm năng trung bình (%) của 7 cổ phiếu PLX, STB, HCM, MWG, DCM, BCM và CII là bao nhiêu nếu lấy giá mua là trung điểm của vùng mua hợp lý và so với giá mục tiêu cơ bản?

- Nhãn: fewer_steps, lookup_added_to_math_gold, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `add(37; 37.5); divide(#0; 2); subtract(44; #1); divide(#2; #1); multiply(#3; 100); add(31; 31.5); divide(#5; 2); subtract(37.5; #6); divide(#7; #6); multiply(#8; 100); add(32; 32.5); divide(#10; 2); subtract(36.4; #11); divide(#12; #11); multiply(#13; 100); add(52.3; 53); divide(#15; 2); subtract(61.5; #16); divide(#17; #16); multiply(#18; 100); add(31.5; 32); divide(#20; 2); subtract(37.3; #21); divide(#22; #21); multiply(#23; 100); add(69; 70); divide(#25; 2); subtract(88.7; #26); divide(#27; #26); multiply(#28; 100); add(21.5; 22); divide(#30; 2); subtract(25.8; #31); divide(#32; #31); multiply(#33; 100); add(#4; #9); add(#35; #14); add(#36; #19); add(#37; #24); add(#38; #29); add(#39; #34); divide(#40; 7)`
- Model: `table_average(Table 1; Tăng trưởng lợi nhuận 9T21; none; none)`
- #0: operator add -> table_average
- #0 arg0: '37' -> 'Table 1'
- #0 arg1: '37.5' -> 'Tăng trưởng lợi nhuận 9T21'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: missing gold step #1: divide(#0; 2)
- #2: missing gold step #2: subtract(44; #1)
- #3: missing gold step #3: divide(#2; #1)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: add(31; 31.5)
- #6: missing gold step #6: divide(#5; 2)
- #7: missing gold step #7: subtract(37.5; #6)
- #8: missing gold step #8: divide(#7; #6)
- #9: missing gold step #9: multiply(#8; 100)
- #10: missing gold step #10: add(32; 32.5)
- #11: missing gold step #11: divide(#10; 2)
- #12: missing gold step #12: subtract(36.4; #11)
- #13: missing gold step #13: divide(#12; #11)
- #14: missing gold step #14: multiply(#13; 100)
- #15: missing gold step #15: add(52.3; 53)
- #16: missing gold step #16: divide(#15; 2)
- #17: missing gold step #17: subtract(61.5; #16)
- #18: missing gold step #18: divide(#17; #16)
- #19: missing gold step #19: multiply(#18; 100)
- #20: missing gold step #20: add(31.5; 32)
- #21: missing gold step #21: divide(#20; 2)
- #22: missing gold step #22: subtract(37.3; #21)
- #23: missing gold step #23: divide(#22; #21)
- #24: missing gold step #24: multiply(#23; 100)
- #25: missing gold step #25: add(69; 70)
- #26: missing gold step #26: divide(#25; 2)
- #27: missing gold step #27: subtract(88.7; #26)
- #28: missing gold step #28: divide(#27; #26)
- #29: missing gold step #29: multiply(#28; 100)
- #30: missing gold step #30: add(21.5; 22)
- #31: missing gold step #31: divide(#30; 2)
- #32: missing gold step #32: subtract(25.8; #31)
- #33: missing gold step #33: divide(#32; #31)
- #34: missing gold step #34: multiply(#33; 100)
- #35: missing gold step #35: add(#4; #9)
- #36: missing gold step #36: add(#35; #14)
- #37: missing gold step #37: add(#36; #19)
- #38: missing gold step #38: add(#37; #24)
- #39: missing gold step #39: add(#38; #29)
- #40: missing gold step #40: add(#39; #34)
- #41: missing gold step #41: divide(#40; 7)

## Dòng 426 — 065423fc-5599-554f-a15e-d327e35d0b7d

Trong năm 2024, cổ phiếu ngân hàng có hiệu suất đầu tư vượt VNIndex bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, exact, pred_math_only, repo_equivalent
- Ground truth: `subtract(22; 12.1)`
- Model: `subtract(22; 12.1)`

## Dòng 427 — f440b0d5-7fd1-50ef-84cb-e23dcb6d7e69

Trong giai đoạn từ FY21 đến FY26F, mức chênh lệch giữa giá trị cao nhất và thấp nhất của hệ số định giá P/E là bao nhiêu?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_max(Table 1; P/E (x); FY21; FY26F); table_min(Table 1; P/E (x); FY21; FY26F); subtract(#0; #1)`
- Model: `chart_max(Table 1; P/E; none; none); chart_min(Table 1; P/E; none; none); subtract(#0; #1)`
- Vi phạm kiểm tra: source_type@0:Table 1; source_type@1:Table 1
- #0: operator table_max -> chart_max
- #0 arg1: 'P/E (x)' -> 'P/E'
- #0 arg2: 'FY21' -> 'none'
- #0 arg3: 'FY26F' -> 'none'
- #1: operator table_min -> chart_min
- #1 arg1: 'P/E (x)' -> 'P/E'
- #1 arg2: 'FY21' -> 'none'
- #1 arg3: 'FY26F' -> 'none'

## Dòng 428 — 1594e481-80b5-54d5-8b51-f6e7a7c8d540

Dựa trên mức tăng giá điện bình quân từ 2022 đến 2023 và tỷ trọng của điện trong rổ CPI, tác động trực tiếp ước tính lên CPI là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; Giá điện; 2022; none); chart_at(Image 1; Giá điện; 2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); divide(3.5; 100); multiply(#4; #5)`
- Model: `subtract(1920; 1864); divide(#0; 5.5)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1920'
- #0 arg1: 'Giá điện' -> '1864'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'Giá điện' -> '5.5'
- #1 arg2: '2023' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#1; #0)
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: divide(3.5; 100)
- #6: missing gold step #6: multiply(#4; #5)

## Dòng 429 — f240b1b1-1a4a-5b33-9844-2ae42ffc7e7d

Hiệu số giữa mức thay đổi giá trong T12 và trong giai đoạn điều chỉnh của phân ngành Ngân hàng là bao nhiêu phần trăm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; T12; Ngân hàng; none); subtract(#0; -11.01)`
- Model: `subtract(100; -10)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '100'
- #0 arg1: 'T12' -> '-10'
- #0 arg2: 'Ngân hàng' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: subtract(#0; -11.01)

## Dòng 430 — ac6b28c0-1a57-5406-bd5a-011174823cde

Trong giai đoạn 2009-2023, chênh lệch tuyệt đối giữa mức giá điện cao nhất và thấp nhất là bao nhiêu VND/kWh?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 1; Giá điện; none; none); chart_min(Image 1; Giá điện; none; none); subtract(#0; #1)`
- Model: `subtract(1920; 1864)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 1' -> '1920'
- #0 arg1: 'Giá điện' -> '1864'
- #0 arg2: 'none' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 1; Giá điện; none; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 431 — 167701a6-bb9a-5a5f-92f9-c3a53735dfcc

Dòng vốn vào DM Bond trong 10 tháng cao hơn EM Bond bao nhiêu tỷ USD?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 5; 10 Tháng; DM Bond; none); chart_at(Image 5; 10 Tháng; EM Bond; none); subtract(#0; #1)`
- Model: `subtract(100; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 5' -> '100'
- #0 arg1: '10 Tháng' -> '100'
- #0 arg2: 'DM Bond' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 5; 10 Tháng; EM Bond; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 432 — d9d19b61-3601-5c6d-b1c7-2dc73ad7fa58

Theo dự báo của IEA cho năm 2025, mức tăng nguồn cung dầu toàn cầu cao hơn mức tăng nhu cầu dầu toàn cầu bao nhiêu triệu thùng/ngày?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(1.9; 1.1)`
- Model: `subtract(1.9; 1.6)`
- #0 arg1: '1.1' -> '1.6'

## Dòng 433 — 9cceae18-b59f-5d17-ba70-2387956dce14

Trong giai đoạn từ Dec-22 đến Nov-23, biên độ giữa mức sinh lời cao nhất và thấp nhất của Nhóm Y Tế là bao nhiêu điểm phần trăm?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 1; Nhóm Y Tế; none; none); chart_min(Image 1; Nhóm Y Tế; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; Nhóm Y Tế; Dec-22; Nov-23); chart_min(Image 1; Nhóm Y Tế; Dec-22; Nov-23); subtract(#0; #1)`
- #0 arg2: 'none' -> 'Dec-22'
- #0 arg3: 'none' -> 'Nov-23'
- #1 arg2: 'none' -> 'Dec-22'
- #1 arg3: 'none' -> 'Nov-23'

## Dòng 434 — 90195875-0d6e-556b-a110-0da5ecb1c87f

Trong đại dự án Lô B – Ô Môn, tiến độ xây dựng của EPCI #2 cao hơn EPCI #1 bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `subtract(24.4; 12.8)`
- Model: `subtract(#1; #0)`
- Vi phạm kiểm tra: reference@0:#1; reference@0:#0
- #0 arg0: '24.4' -> '#1'
- #0 arg1: '12.8' -> '#0'

## Dòng 435 — 77f85190-4012-542d-92b3-21069cae602c

Tỷ suất cổ tức trung bình năm 2023 của danh sách các cổ phiếu có tỷ suất cổ tức cao là bao nhiêu?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_average(Table 3; Tỷ suất cổ tức (2023); none; none)`
- Model: `chart_average(Image 1; Tỷ suất cổ tức theo ngành; none; none)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 3' -> 'Image 1'
- #0 arg1: 'Tỷ suất cổ tức (2023)' -> 'Tỷ suất cổ tức theo ngành'

## Dòng 436 — b9789da3-9e1e-5e3d-890e-78758972b456

Khoảng chênh lệch giữa mức EPS cao nhất và thấp nhất trong giai đoạn từ năm 2021H đến năm 2026F là bao nhiêu đồng?

- Nhãn: non_exact, operator_sequence_diff
- Ground truth: `table_max(Table 2; EPS (VND/CP); 2021H; 2026F); table_min(Table 2; EPS (VND/CP); 2021H; 2026F); subtract(#0; #1)`
- Model: `chart_max(Image 1; EPS; 2021H; 2026F); chart_min(Image 1; EPS; 2021H; 2026F); subtract(#0; #1)`
- #0: operator table_max -> chart_max
- #0 arg0: 'Table 2' -> 'Image 1'
- #0 arg1: 'EPS (VND/CP)' -> 'EPS'
- #1: operator table_min -> chart_min
- #1 arg0: 'Table 2' -> 'Image 1'
- #1 arg1: 'EPS (VND/CP)' -> 'EPS'

## Dòng 437 — 69952714-4485-546b-af90-0ea2bd52db33

Trong năm 2022, mức tăng trưởng của ngành Công nghệ thông tin cao hơn ngành Tài chính bao nhiêu phần trăm?

- Nhãn: both_math_only, invalid_math_argument, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `subtract(10.5; -17.6)`
- Model: `subtract(#1; none)`
- Vi phạm kiểm tra: reference@0:#1; math_type@0:none
- #0 arg0: '10.5' -> '#1'
- #0 arg1: '-17.6' -> 'none'

## Dòng 438 — b86a8dc0-2fc5-5178-838e-a6106e1d6ad3

Mức thay đổi tuyệt đối của doanh thu công ty từ năm 2018 đến năm 2019 là bao nhiêu tỷ đồng?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(18610; 18299)`
- Model: `subtract(18822; 17337)`
- #0 arg0: '18610' -> '18822'
- #0 arg1: '18299' -> '17337'

## Dòng 439 — 6e0db2e8-201d-5c79-a9e9-0133aa1e52c1

Mức tăng trưởng thu nhập khác (NOI) so với cùng kỳ chênh lệch bao nhiêu điểm phần trăm so với tốc độ tăng trưởng của khoản mục này trong năm 2023 so với năm 2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; NOI; 2022; none); chart_at(Image 1; NOI; 2023; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100); subtract(2.1; #4)`
- Model: `multiply(2.1; 100); divide(#0; 51); subtract(#1; 100)`
- #0: operator chart_at -> multiply
- #0 arg0: 'Image 1' -> '2.1'
- #0 arg1: 'NOI' -> '100'
- #0 arg2: '2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'NOI' -> '51'
- #1 arg2: '2023' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)
- #5: missing gold step #5: subtract(2.1; #4)

## Dòng 440 — 04e3b943-5fb1-5ca3-b96a-813072456f4f

Mức tăng trong giai đoạn bứt phá của phân ngành Bán lẻ có lớn hơn so với phân ngành Công nghệ Thông tin hay không?

- Nhãn: both_math_only, invalid_math_argument, non_exact, operator_sequence_diff, pred_math_only, strict_invalid
- Ground truth: `greater(36.78; 36.15)`
- Model: `subtract(11.4; 43.23#0)`
- Vi phạm kiểm tra: math_type@0:43.23#0
- #0: operator greater -> subtract
- #0 arg0: '36.78' -> '11.4'
- #0 arg1: '36.15' -> '43.23#0'

## Dòng 441 — 0aa096c4-067c-5697-9824-3372cbe368f7

Trong giai đoạn đi ngang, mức thay đổi trung bình của tất cả các phân ngành là bao nhiêu phần trăm?

- Nhãn: invalid_source_type, non_exact, operator_sequence_diff, strict_invalid
- Ground truth: `table_average(Table 1; Đi ngang; none; none)`
- Model: `chart_average(Table 1; T12; none; none)`
- Vi phạm kiểm tra: source_type@0:Table 1
- #0: operator table_average -> chart_average
- #0 arg1: 'Đi ngang' -> 'T12'

## Dòng 442 — 1b705956-ae89-55b4-a29d-d1c021c0f310

Tại mốc 9/26, chênh lệch giữa giá trị mua/bán ròng của khối ngoại tự tính từ NĐTNN Mua trừ NĐTNN Bán và giá trị mua/bán ròng được ghi nhận là bao nhiêu?

- Nhãn: fewer_steps, invalid_reference, invalid_source_type, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `chart_at(Image 5; NĐTNN Mua; 9/26; none); chart_at(Image 5; NĐTNN Bán; 9/26; none); subtract(#0; #1); chart_at(Image 5; Giá trị mua/bán ròng; 9/26; none); subtract(#2; #3)`
- Model: `chart_at(#1; none; 9/26; none)`
- Vi phạm kiểm tra: reference@0:#1; source_type@0:#1
- #0 arg0: 'Image 5' -> '#1'
- #0 arg1: 'NĐTNN Mua' -> 'none'
- #1: missing gold step #1: chart_at(Image 5; NĐTNN Bán; 9/26; none)
- #2: missing gold step #2: subtract(#0; #1)
- #3: missing gold step #3: chart_at(Image 5; Giá trị mua/bán ròng; 9/26; none)
- #4: missing gold step #4: subtract(#2; #3)

## Dòng 443 — 04319977-5483-5631-81dd-d461782e72c7

Chênh lệch giữa giá trị mua và giá trị bán của nhà đầu tư nước ngoài trong ngày 15/8/2022 là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 5; NĐTNN Mua; 15/8/2022; none); chart_at(Image 5; NĐTNN Bán; 15/8/2022; none); subtract(#0; #1)`
- Model: `subtract(0; 0)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 5' -> '0'
- #0 arg1: 'NĐTNN Mua' -> '0'
- #0 arg2: '15/8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 5; NĐTNN Bán; 15/8/2022; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 444 — 94e256ae-64e8-5f42-a180-c8e98fd357af

Vào ngày 31/8/2022, VNIndex cao hơn mức tham chiếu của chỉ số này bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; VNIndex; 31/8/2022; none); chart_at(Image 1; Tham chiếu VNIndex; 31/8/2022; none); subtract(#0; #1)`
- Model: `subtract(1280.51; 1206.33)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '1280.51'
- #0 arg1: 'VNIndex' -> '1206.33'
- #0 arg2: '31/8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Tham chiếu VNIndex; 31/8/2022; none)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 445 — 91c5164c-4bb5-5e8c-b3ed-6910e5292bb7

Nếu lấy trung bình tất cả các mức giá điện được nêu trong giai đoạn 2009-2023, bao gồm cả các lần điều chỉnh trong cùng năm, thì giá điện bình quân là bao nhiêu VND/kWh?

- Nhãn: invalid_arity, invalid_source_type, non_exact, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `chart_average(Image 1; Giá điện; none; none)`
- Model: `chart_average(Table 1; (Lần 1)(Lần 2)(Lần 1)(Lần 2); none)`
- Vi phạm kiểm tra: arity@0:3!=4; source_type@0:Table 1
- #0 arg0: 'Image 1' -> 'Table 1'
- #0 arg1: 'Giá điện' -> '(Lần 1)(Lần 2)(Lần 1)(Lần 2)'
- #0 arg3: 'none' -> '<absent>'

## Dòng 446 — 444ff7f2-5747-511f-992d-6505a4a83610

Chỉ số FPT VN vào tháng 11 năm 2024 đã thay đổi bao nhiêu phần trăm so với thời điểm tháng 11 năm 2023?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 1; FPT VN; Nov 23; none); chart_at(Image 1; FPT VN; Nov 24; none); subtract(#1; #0); divide(#2; #0); multiply(#3; 100)`
- Model: `subtract(60; 40); divide(#0; 40); multiply(#1; 100)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 1' -> '60'
- #0 arg1: 'FPT VN' -> '40'
- #0 arg2: 'Nov 23' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: operator chart_at -> divide
- #1 arg0: 'Image 1' -> '#0'
- #1 arg1: 'FPT VN' -> '40'
- #1 arg2: 'Nov 24' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: operator subtract -> multiply
- #2 arg1: '#0' -> '100'
- #3: missing gold step #3: divide(#2; #0)
- #4: missing gold step #4: multiply(#3; 100)

## Dòng 447 — 582ec57b-7623-5f30-bc41-27ed817f5950

Thanh khoản của VNIndex trong T9/2022 thay đổi bao nhiêu so với T8/2022?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_at(Image 2; VNIndex; T8/2022; none); chart_at(Image 2; VNIndex; T9/2022; none); subtract(#1; #0)`
- Model: `subtract(11.8; 14.0)`
- #0: operator chart_at -> subtract
- #0 arg0: 'Image 2' -> '11.8'
- #0 arg1: 'VNIndex' -> '14.0'
- #0 arg2: 'T8/2022' -> '<absent>'
- #0 arg3: 'none' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 2; VNIndex; T9/2022; none)
- #2: missing gold step #2: subtract(#1; #0)

## Dòng 448 — 17ba1bbb-c2e0-58ab-975f-0648a565d2cb

Doanh thu của DPG dự kiến thay đổi bao nhiêu phần trăm từ 2023H sang 2024F?

- Nhãn: both_math_only, invalid_reference, non_exact, pred_math_only, repo_invalid, same_ops_argument_diff, strict_invalid
- Ground truth: `subtract(4142; 3450); divide(#0; 3450); multiply(#1; 100)`
- Model: `subtract(4.142; 3.450); divide(#1; 3.450); multiply(#2; 100)`
- Vi phạm kiểm tra: reference@1:#1; reference@2:#2
- #0 arg0: '4142' -> '4.142'
- #0 arg1: '3450' -> '3.450'
- #1 arg0: '#0' -> '#1'
- #1 arg1: '3450' -> '3.450'
- #2 arg0: '#1' -> '#2'

## Dòng 449 — 8dd222b9-27bd-5425-9ce6-9df5605eee6c

Mức chênh lệch giữa tổng dòng vốn lũy kế vào trái phiếu tính đến tháng 10/2023 và tổng dòng vốn vào trái phiếu thị trường phát triển (DM Bond) cùng trái phiếu thị trường mới nổi (EM Bond) trong 10 tháng đầu năm là bao nhiêu tỷ USD?

- Nhãn: invalid_arity, invalid_reference, non_exact, operator_sequence_diff, repo_invalid, strict_invalid
- Ground truth: `chart_at(Image 2; Trái phiếu; Oct-23; none); chart_at(Image 5; 10 Tháng; DM Bond; none); chart_at(Image 5; 10 Tháng; EM Bond; none); add(#1; #2); subtract(#0; #3)`
- Model: `chart_at(Image 4; Trụ Cực Y; none); chart_at(Image 5; EM Bond; none); chart_at(Image 5; DM Bond; none); subtract(#1; #2); subtract(#3; #4)`
- Vi phạm kiểm tra: arity@0:3!=4; arity@1:3!=4; arity@2:3!=4; reference@4:#4
- #0 arg0: 'Image 2' -> 'Image 4'
- #0 arg1: 'Trái phiếu' -> 'Trụ Cực Y'
- #0 arg2: 'Oct-23' -> 'none'
- #0 arg3: 'none' -> '<absent>'
- #1 arg1: '10 Tháng' -> 'EM Bond'
- #1 arg2: 'DM Bond' -> 'none'
- #1 arg3: 'none' -> '<absent>'
- #2 arg1: '10 Tháng' -> 'DM Bond'
- #2 arg2: 'EM Bond' -> 'none'
- #2 arg3: 'none' -> '<absent>'
- #3: operator add -> subtract
- #4 arg0: '#0' -> '#3'
- #4 arg1: '#3' -> '#4'

## Dòng 450 — eeb556da-51c3-51bb-8900-2162e2dbb775

Trong năm 2023, tỷ suất lợi nhuận trên vốn chủ sở hữu (ROE) của DBD có cao hơn so với IMP hay không?

- Nhãn: both_math_only, non_exact, operator_sequence_diff, pred_math_only
- Ground truth: `greater(18.8; 14.4)`
- Model: `divide(29; 14.4)`
- #0: operator greater -> divide
- #0 arg0: '18.8' -> '29'

## Dòng 451 — f94ea359-7307-55d9-a1e3-76047c3f67d7

Chênh lệch là bao nhiêu điểm phần trăm khi lấy trung bình của hai tỷ lệ giảm VNIndex trong tháng 9/2022 được nêu, rồi trừ đi tỷ lệ giảm suy ra từ mức VNIndex ngày 31/8/2022 và 30/9/2022?

- Nhãn: fewer_steps, invalid_reference, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `multiply(-11.6; -1); add(11.59; #0); divide(#1; 2); chart_at(Image 1; VNIndex; 31/8/2022; none); chart_at(Image 1; VNIndex; 30/9/2022; none); subtract(#3; #4); divide(#5; #3); multiply(#6; 100); subtract(#2; #7)`
- Model: `divide(#0; 2)`
- Vi phạm kiểm tra: reference@0:#0
- #0: operator multiply -> divide
- #0 arg0: '-11.6' -> '#0'
- #0 arg1: '-1' -> '2'
- #1: missing gold step #1: add(11.59; #0)
- #2: missing gold step #2: divide(#1; 2)
- #3: missing gold step #3: chart_at(Image 1; VNIndex; 31/8/2022; none)
- #4: missing gold step #4: chart_at(Image 1; VNIndex; 30/9/2022; none)
- #5: missing gold step #5: subtract(#3; #4)
- #6: missing gold step #6: divide(#5; #3)
- #7: missing gold step #7: multiply(#6; 100)
- #8: missing gold step #8: subtract(#2; #7)

## Dòng 452 — 0b73db0c-c89c-588e-9adb-5c8d49649228

Mức chênh lệch về tỷ suất cổ tức dự phóng năm 2025 giữa hai cổ phiếu PLX và GAS là bao nhiêu phần trăm?

- Nhãn: invalid_reference, lookup_added_to_math_gold, non_exact, operator_sequence_diff, repo_invalid, step_count_diff, strict_invalid
- Ground truth: `subtract(5.2; 4.4)`
- Model: `table_average(Table 1; Cổ tức dự phóng 2025 (LHS); none; none); subtract(#0; #1); divide(#2; #1); multiply(#3; 100)`
- Vi phạm kiểm tra: reference@1:#1; reference@2:#2; reference@3:#3
- #0: operator subtract -> table_average
- #0 arg0: '5.2' -> 'Table 1'
- #0 arg1: '4.4' -> 'Cổ tức dự phóng 2025 (LHS)'
- #0 arg2: '<absent>' -> 'none'
- #0 arg3: '<absent>' -> 'none'
- #1: extra predicted step #1: subtract(#0; #1)
- #2: extra predicted step #2: divide(#2; #1)
- #3: extra predicted step #3: multiply(#3; 100)

## Dòng 453 — 15a06da4-e3cd-5611-9b4f-36dc8c51d67b

GTGD khớp lệnh bình quân 1 phiên trên HOSE trong tháng 10/2022 đã thay đổi bao nhiêu phần trăm so với tháng trước?

- Nhãn: both_math_only, fewer_steps, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `subtract(9.2; 11.7); divide(#0; 11.7); multiply(#1; 100)`
- Model: `subtract(9.2; 11.7)`
- #1: missing gold step #1: divide(#0; 11.7)
- #2: missing gold step #2: multiply(#1; 100)

## Dòng 454 — c485bd4e-8a74-5ede-934b-eea3d386a9a0

Tổng mức thay đổi của ngành Công nghệ Thông tin trong hai giai đoạn bứt phá và hồi phục là bao nhiêu phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `add(36.15; 16.11)`
- Model: `add(30; 43.2)`
- #0 arg0: '36.15' -> '30'
- #0 arg1: '16.11' -> '43.2'

## Dòng 455 — d535a43d-a5d7-58fb-ad2c-0a74513fa670

Mức chênh lệch giữa tỷ suất sinh lời trung bình của các phân ngành trong giai đoạn bứt phá so với giai đoạn đi ngang là bao nhiêu điểm phần trăm?

- Nhãn: fewer_steps, non_exact, operator_sequence_diff, step_count_diff
- Ground truth: `table_average(Table 1; Bứt phá; none; none); table_average(Table 1; Đi ngang; none; none); subtract(#0; #1)`
- Model: `chart_average(Image 1; T12; none; none); subtract(#0; 43.23)`
- #0: operator table_average -> chart_average
- #0 arg0: 'Table 1' -> 'Image 1'
- #0 arg1: 'Bứt phá' -> 'T12'
- #1: operator table_average -> subtract
- #1 arg0: 'Table 1' -> '#0'
- #1 arg1: 'Đi ngang' -> '43.23'
- #1 arg2: 'none' -> '<absent>'
- #1 arg3: 'none' -> '<absent>'
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 456 — da8d8dbd-7aaa-55f5-9f35-213b9427b995

Sau khi quy đổi về cùng đơn vị triệu USD, tỷ lệ giữa tổng dòng vốn ước tính từ các quỹ lớn mô phỏng theo các chỉ số của FTSE Russell và vốn hóa free float của Việt Nam là bao nhiêu?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `table_sum(Table 1; Ước tính dòng vốn (triệu USD); Vanguard Total International Stock Index Fund; Schwab Emerging Markets Equity ETF); chart_at(Image 1; Free float market cap; Vietnam; none); multiply(#1; 1000); divide(#0; #2)`
- Model: `divide(2000; 1)`
- #0: operator table_sum -> divide
- #0 arg0: 'Table 1' -> '2000'
- #0 arg1: 'Ước tính dòng vốn (triệu USD)' -> '1'
- #0 arg2: 'Vanguard Total International Stock Index Fund' -> '<absent>'
- #0 arg3: 'Schwab Emerging Markets Equity ETF' -> '<absent>'
- #1: missing gold step #1: chart_at(Image 1; Free float market cap; Vietnam; none)
- #2: missing gold step #2: multiply(#1; 1000)
- #3: missing gold step #3: divide(#0; #2)

## Dòng 457 — 7b6b7542-6f03-5799-87a7-62d8e44b06d7

Khoảng chênh lệch giữa mức giá cao nhất và thấp nhất của dầu Brent trong giai đoạn được thống kê là bao nhiêu USD/thùng?

- Nhãn: non_exact, same_ops_argument_diff
- Ground truth: `chart_max(Image 1; Giá dầu Brent; none; none); chart_min(Image 1; Giá dầu Brent; none; none); subtract(#0; #1)`
- Model: `chart_max(Image 1; none; none; none); chart_min(Image 1; none; none; none); subtract(#0; #1)`
- #0 arg1: 'Giá dầu Brent' -> 'none'
- #1 arg1: 'Giá dầu Brent' -> 'none'

## Dòng 458 — 67859de1-7858-5a8e-9d29-048e477da8e7

Hiệu suất của ngành Hàng tiêu dùng không thiết yếu trong tháng 8/2022 cao hơn tháng 7/2022 bao nhiêu điểm phần trăm?

- Nhãn: both_math_only, non_exact, pred_math_only, same_ops_argument_diff
- Ground truth: `subtract(14.0; -12.5)`
- Model: `subtract(14; 7)`
- #0 arg0: '14.0' -> '14'
- #0 arg1: '-12.5' -> '7'

## Dòng 459 — dc36c5fe-7680-53b0-89b3-1d898557c88e

Biên độ điểm của VNIndex từ 30/9/2022 đến 31/10/2022, tính bằng mức cao nhất trừ mức thấp nhất trong giai đoạn này, là bao nhiêu điểm?

- Nhãn: fewer_steps, lookup_omitted_math_only, non_exact, operator_sequence_diff, pred_math_only, step_count_diff
- Ground truth: `chart_max(Image 1; VNIndex; 30/9/2022; 31/10/2022); chart_min(Image 1; VNIndex; 30/9/2022; 31/10/2022); subtract(#0; #1)`
- Model: `subtract(1100; 800)`
- #0: operator chart_max -> subtract
- #0 arg0: 'Image 1' -> '1100'
- #0 arg1: 'VNIndex' -> '800'
- #0 arg2: '30/9/2022' -> '<absent>'
- #0 arg3: '31/10/2022' -> '<absent>'
- #1: missing gold step #1: chart_min(Image 1; VNIndex; 30/9/2022; 31/10/2022)
- #2: missing gold step #2: subtract(#0; #1)

## Dòng 460 — 2252c63f-ec0e-5c67-95ce-8ec7cecd0297

ROE của HBC trong năm tài chính 2017 có cao hơn năm tài chính 2016 không?

- Nhãn: both_math_only, non_exact, pred_math_only, same_math_value_non_exact, same_ops_argument_diff
- Ground truth: `greater(40.0; 37.6)`
- Model: `greater(16.5; 15.1)`
- #0 arg0: '40.0' -> '16.5'
- #0 arg1: '37.6' -> '15.1'
