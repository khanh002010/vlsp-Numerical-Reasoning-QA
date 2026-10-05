# Rà soát ViNumQA và evaluation_report_v3

Ngày rà soát: 06/10/2026. Phạm vi: `page.html`, toàn bộ 459 dòng CSV, dữ liệu gốc/formatted và toàn bộ 24 file Python trong `vinumqa`, cùng `evaluate_shortcuts.py`.

## 1. Kết luận chính

Model đang sai chủ yếu ở **gắn bằng chứng với đúng nguồn/nhãn/vai trò và dựng chuỗi phép toán**, không chỉ sai hoán vị. Sửa prompt hoặc ép tên toán tử chưa đủ. Cần sửa dữ liệu huấn luyện, biểu diễn evidence, loss và kiểm tra cấu trúc program cùng nhau.

Ba vấn đề cần xử lý trước khi train lại:

1. **Dữ liệu formatted hiện có không chứa thông tin ảnh thực:** 1.725/1.725 mẫu train và 459/459 mẫu public đều có `[Chart: ... - extracted by CV Module]`; không mẫu nào có header `**Image ...**` với bảng CV thực. Nếu checkpoint dùng các file này, model phải đoán nhãn biểu đồ từ câu hỏi/văn bản và prior. Inference thực lại đưa bảng CV vào nên còn có chênh lệch phân phối.
2. **Quy tắc “cứ dữ liệu trong bảng là bắt buộc table_*” mâu thuẫn với nhãn:** ground truth có cả phép toán trực tiếp trên số lấy từ bảng. Câu đầu CSV là ví dụ rõ ràng. Không thể chữa shortcut bằng cách cấm toàn bộ program math-only.
3. **Hệ thống kiểm tra quá yếu:** decoder không kiểm tra toàn bộ tên toán tử/arity/reference; validator chấp nhận đối số sai kiểu; reflection gặp `NameError` ngay khi phải retry. Những lỗi này đã tái hiện offline.

Không có checkpoint, tokenizer Qwen cục bộ hay log v3 để xác nhận chính xác cấu hình đã tạo CSV. Các nguyên nhân về huấn luyện bên dưới là suy luận có điều kiện từ code và artifact đang có; lỗi trong CSV và các lỗi code tái hiện được được đánh dấu riêng. Không coi mọi lỗi hiện tại là nguyên nhân lịch sử đã được chứng minh.

## 2. Cuộc thi yêu cầu gì?

Theo bản lưu `page.html`, đầu ra là **reasoning program** của bài toán tài chính tiếng Việt kết hợp văn bản, bảng và biểu đồ. Tiêu chí là **Program Accuracy**, dùng script chính thức để so với program tham chiếu; chỉ trùng kết quả số không đủ. Bản lưu cũng nêu mỗi model thành phần không quá 8B tham số và phải khai báo dữ liệu ngoài.

Trong thư mục chưa thấy evaluator chính thức; `utils/metrics.py` và `evaluate_shortcuts.py` là metric nội bộ. Vì vậy 7,84% bên dưới là exact match quan sát được, **không tự khẳng định là điểm leaderboard**. Chưa biết evaluator chính thức xử lý các biểu thức tương đương hay hoán vị bước như thế nào.

## 3. Số liệu đối chiếu toàn bộ CSV

Đã join bằng QID: đủ 459 QID, không trùng/thiếu; tất cả `Ground_Truth` trong CSV khớp `public_test.json` sau strip hai đầu. Không dựa vào cột `Is_Shortcut` để phân loại lại.

| Chẩn đoán | Số câu | Tỷ lệ trên 459 |
|---|---:|---:|
| Khớp nguyên văn | 36 | 7,84% |
| Không khớp nguyên văn | 423 | 92,16% |
| Gold có lookup, prediction chỉ còn math | 116 | 25,27% |
| Gold chỉ math, prediction tự thêm lookup | 32 | 6,97% |
| Khác chuỗi tên toán tử | 298 | 64,92% |
| Cùng chuỗi toán tử nhưng khác đối số/biểu diễn | 125 | 27,23% |
| Khác số bước | 192 | 41,83% |
| Ít bước hơn gold | 158 | 34,42% |
| Không qua validator hiện có | 101 | 22,00% |
| Không qua kiểm tra bổ sung của audit | 136 | 29,63% |
| Có lỗi số lượng đối số | 64 | 13,94% |
| Có reference không hợp lệ | 47 | 10,24% |
| Có nguồn sai kiểu, như chart_*(Table...) | 47 | 10,24% |
| Có Image/Table ID đúng dạng nhưng không tồn tại | 6 | 1,31% |
| Có đối số math không phải số/reference hợp lệ | 14 | 3,05% |

Các nhóm lỗi chồng lấp, không cộng các hàng để ra tổng lỗi. Kiểm tra bổ sung kiểm tra arity, cân bằng ngoặc, reference, kiểu đối số math, source ID và chia trực tiếp cho 0. Nó chưa chứng minh nhãn đúng, phạm vi đúng hay suy luận đúng. Toàn bộ gold public qua các kiểm tra này.

| Nhóm theo toán tử trong gold | Tổng | Exact | Tỷ lệ |
|---|---:|---:|---:|
| Chỉ math | 182 | 30 | 16,48% |
| Có chart, không table | 199 | 6 | 3,02% |
| Có table, không chart | 75 | 0 | 0% |
| Có cả chart và table | 3 | 0 | 0% |

`chart_at`: **297 lần gold → 46 lần prediction**. `chart_average`: **21 → 51**. `add`: **136 → 45**. Đây là dấu hiệu bỏ lookup điểm, gom sai thành phép trung bình, và mất các chuỗi cộng; tần suất không phải precision/recall.

Script `evaluate_shortcuts.py` đánh dấu **263 program math-only** là shortcut. Trong số đó **147 có gold cũng math-only**, bao gồm 30 câu exact. Chỉ **116** là trường hợp gold có lookup nhưng prediction bỏ hết lookup. Đây vẫn là nhãn “bỏ lookup”, chưa phải chứng minh model tính tắt đúng kết quả.

## 4. Những kiểu sai cụ thể

### 4.1 Bỏ lookup và đôi khi sai cả dấu

QID `a8849fe2-cc8c-5a24-ae9e-4804fa503b8d`:

```text
Gold: chart_max(Image 2; % +/-; none; none); chart_min(Image 2; % +/-; none; none); subtract(#0; #1)
Pred: subtract(-7; -1)
```

Prediction mất nguồn và phạm vi. Với hai số model chọn, max trừ min phải là `-1 - (-7)`, không phải `-7 - (-1)`. Không thể chữa bằng cách thêm `chart_at` quanh hai số: bài yêu cầu tìm cực trị, không phải tùy ý chọn hai điểm.

QID `01e1e905-4875-5222-aa9f-14dfb117c8e2`: gold đọc NII năm 2019 và 3Q24 (TTM), rồi tính tăng trưởng; prediction thay hai lookup bằng `158` và `69`. Chuỗi tăng trưởng còn tương tự nhưng nguồn bằng chứng đã biến mất; chưa có output CV v3 để khẳng định hai số đó đúng.

### 4.2 Ép dùng lookup cũng sai

QID `bed4e850-a504-5677-9307-184caea40c71` hỏi trung bình lãi suất sau ưu đãi của VCB, CTG và Standard Charter. HTML có lần lượt `9,0%`, `9,0%`, `8,8%`.

```text
Gold: add(9; 9); add(#0; 8.8); divide(#1; 3)
Pred: table_average(Table 1; Lãi suất cho vay mua nhà; none; 3Q24)
```

Ba ngân hàng là tập chọn rời rạc, không phải khoảng liên tục; `3Q24` không phải giới hạn đúng cho câu này. Quy tắc cứng tại `generate_program.py:159–162` khuyến khích output trái gold dù nguồn là bảng. Cần học chính sách annotation: khi nào dùng aggregate có phạm vi và khi nào chọn các số cụ thể rồi tính. DSL hiện không có `table_at`; không tự phát minh thêm toán tử nộp thi.

### 4.3 Đúng số nhưng sai toán tử / sai ý nghĩa phần trăm

QID `b36cd841-19f1-544e-b95f-fb0234949122`:

```text
Gold: subtract(39; 12.1)
Pred: divide(39; 12.1)
```

Chênh lệch giữa hai tỷ suất khác với tỷ số và khác tăng trưởng tương đối. Các mẫu contrastive phải phân biệt: chênh lệch `a-b`, gấp bao nhiêu lần `a/b`, tăng trưởng `(new-old)/old*100`, tỷ trọng `part/total*100`.

QID `f39ab262-420c-5910-bcf7-3be4918f35df`: prediction giữ `divide(2893; 65)` nhưng bỏ `multiply(#0; 100)`.

QID `9ba29d9a-08ec-5a58-81f4-4599b83842f9`: `table_sum(...EPS 12T; VCB; CTG)` bị thay bằng `table_average(...; none; none)`; sai cả phép tổng và phạm vi.

### 4.4 Hoán vị và đánh số bước là hai lỗi khác nhau

QID `769eee4a-8297-5c89-8b97-9d44323ec6bd`: hai lookup đúng hoàn toàn; bước cuối cần `subtract(#0; #1)` nhưng prediction là `subtract(#1; #2)`. Ở bước số 2, `#2` là tự tham chiếu, không phải hoán vị hợp lệ. Các câu chỉ có `divide(#1; #2)` cũng không phải đã “trích xuất ở Step 1” nên được phép dùng reference: `#N` chỉ đánh số operation trong program, không đánh số phần tử evidence.

Audit thấy 3 câu có cặp đối số của phép không giao hoán đảo khi so theo vị trí, nhưng **không được gọi cả 3 là lỗi đảo toán hạng thuần túy**. Ví dụ QID `0b7b5473-0a3d-564a-9b96-29bfcd0a429b` đổi thứ tự đọc Oct/Sep và đổi `subtract(#1; #0)` thành `subtract(#0; #1)`: hướng thời gian vẫn Oct trừ Sep. Program vẫn sai nguồn và các bước sau. Muốn chấm hoán vị phải resolve reference về evidence rồi so cây phụ thuộc.

Đổi thứ tự hai lookup độc lập có thể hợp lệ nếu remap tất cả reference. Không sắp xếp tùy ý đối số `subtract`, `divide`, `greater`, `exp`. `add`/`multiply` giao hoán nhưng vẫn phải giữ multiplicity: số 9 của VCB và số 9 của CTG là hai evidence khác nhau.

### 4.5 Sai nguồn, nhãn, mốc thời gian và cấu trúc bảng

- QID `56719970-a89f-5792-9469-3852c782b6c2`: `table_max/min(Table 1; Điều chỉnh; ...)` thành `chart_max/min(Table 1; T12; ...)`.
- QID `17deebd3-b46f-5ead-987d-218326e01bcd`: giữ Nam Côn Sơn 2 nhưng đổi Image 2 thành Image 3.
- QID `8d829101-30ce-504a-8f1d-9c4299018ae3`: `Giá mục tiêu (đồng)@Trong 1 năm` thành `Giá mục tiêu 1 năm`. HTML có header nhiều tầng; formatter chưa xây key chuẩn `cha@con`.
- QID `0002d3f2-7d30-533e-80bb-dc3a05ca6770`: `Vietnam` bị dịch thành `Việt Nam`. Nghĩa gần nhau không đảm bảo lookup/evaluator nhận cùng khóa.
- QID `e28cfc75-fbcd-5011-b7cf-ff3ee43dcbd4`: tên đầy đủ của series P/E bị rút thành `P/E`, mốc `1/2/2022`, `9/2/2023` đổi thành `Jan-22`, `Sep-23`. Không được tự suy diễn định dạng ngày rồi sửa nhãn nguồn.

Nên copy khóa từ schema nguồn; giữ raw label và normalized search label riêng. Tìm kiếm có thể dùng alias, nhưng output cần tên chuẩn theo annotation đã xác minh.

### 4.6 Sai số, scale và trùng kết quả tình cờ

QID `e55ef634-b777-5470-9d6a-75fe742d73e3`: dùng 61000 thay 61100; QID `9dcacf50-b005-5ff0-b753-58b218a187a9`: dùng 0.7 thay 0.07. Đây không phải lỗi hoán vị.

Có 4 câu non-exact cho cùng kết quả khi thực thi math bằng số hữu tỷ với dấu chấm là thập phân:

- `75942c41-9dfa-5dde-9606-65f893287648`: hai cách tính `425*64/100`, thực sự tương đương đại số.
- `6f6b25cd-4e55-5356-8ba5-331012f6f130`: `52102/3351` và `52.102/3.351`; scale chung triệt tiêu.
- `42523de0-d558-5aba-a87c-21a24feb9939`: scale chung triệt tiêu trong tỷ lệ tăng trưởng.
- `2252c63f-ec0e-5c67-95ce-8ec7cecd0297`: `greater(40.0; 37.6)` và `greater(16.5; 15.1)` đều true nhưng evidence sai hoàn toàn.

Vì vậy không dùng execution equality làm tiêu chuẩn sửa nhãn hay chọn program đúng. Bản thân gold có biểu diễn số cần giữ ngữ cảnh; không áp một heuristic dấu chấm/ngăn nghìn lên mọi literal.

## 5. Nguyên nhân trong code và cách sửa

### P0 — Sửa contract dữ liệu và huấn luyện

**A. Dùng cùng context builder và prompt cho train/val/inference.** Hiện `format_training_data.py` và `full_pipeline.py` lặp logic, còn `_build_prompt` thêm luật chỉ có ở inference. File public formatted đang lưu hint 14 toán tử, thiếu `exp`, `chart_total`, trong khi registry hiện có 16. Cần version/hash formatter, schema, prompt, tokenizer và model; tái tạo cache sau khi sửa. Formatter không được im lặng chuyển sang placeholder khi CV lỗi. Dùng cache extraction theo nội dung ảnh + cấu hình CV; mỗi nguồn giữ `Image N` gốc.

**B. Đổi Step 1 thành evidence có vai trò.** `extract_values_from_program` chỉ lấy literal từ target, bỏ mọi `#N`, rồi deduplicate và nối bằng `#`. Nó mất nguồn/vai trò/nhóm đối số, mất số lần xuất hiện, trộn label với số; không phải supervision trích xuất có grounding. Ví dụ hai số 9 trong câu trung bình chỉ còn một chuỗi `9`.

Đề xuất evidence nội bộ:

```json
{"eid":"e0","source":"Table 1","row":"VCB","column":"Lãi suất cho vay mua nhà sau thời gian ưu đãi","raw":"9,0%","value":"9","unit":"percent","role":"selected_member"}
```

Tạo e1 riêng cho CTG dù value cũng là 9. Với chart, giữ `{source, series, x_label, value, unit}`. Với literal không align được đáng tin, đánh dấu unresolved để sửa/loại khỏi supervision evidence; không suy ngược một tọa độ bịa từ đáp án. Reference evidence `e0` và reference operation `#0` phải tách biệt.

**C. Tập trung loss vào response/program.** `train_qlora.py:113` đặt label bằng toàn bộ input IDs: model học tái tạo cả context dài. Cần labels prompt/padding = -100; giữ label response và EOS; dùng collator bảo toàn mask. Chỉ đổi labels ở tokenize nhưng vẫn dùng collator tự dựng lại labels có thể làm mất sửa đổi. Có thể giữ `Trainer` và viết collator nhỏ; nếu chuyển TRL phải pin version tương thích vì repo đang ghi `trl==0.9.4`, không chép API mới trực tiếp. Tài liệu [Hugging Face SFT](https://huggingface.co/docs/trl/sft_trainer) xác nhận hướng train completion-only; API cụ thể phải chọn theo phiên bản.

**D. Bảo vệ target trước truncation.** Hiện concat context/question/output rồi truncate 4096; response ở cuối dễ bị cắt. Cần đo tokenizer thực: số token prompt, target, số target token được giữ, số mẫu mất toàn bộ output; fail khi target bị cắt. Trích context liên quan bằng input/question, dự trù ngân sách target và EOS trước khi tokenize. Không dùng gold để chọn context lúc inference. Hiện chỉ đo được ký tự: train median 4.579/max 14.615; public median 6.339/max 16.986. **Chưa có tỷ lệ truncate bằng tokenizer Qwen**, không quy đổi ký tự thành số token để kết luận.

**E. Chuẩn hóa bảng có schema.** `dict_to_markdown_table` gọi `read_html` rồi `to_markdown`: nhiều artifact có header số `0,1,2,...`, tên thật nằm ở data row. Chưa có bước resolve rowspan/colspan thành đường dẫn header theo DSL. Tạo schema gồm source ID, nhãn hàng/cột, parent header, unit và giá trị raw/normalized; giữ thứ tự nguồn. Không tự dịch/rút gọn tên. Đối chiếu quy tắc `@` bằng train trước khi chuẩn hóa public.

### P0 — Sửa kiểm tra đầu ra trước khi chạy batch

**F. Reflection:** tái hiện `NameError: original_prompt is not defined` tại `reflection_loop.py:75`. Build prompt trước vòng retry. Sau mỗi lần sinh phải kiểm tra error và validate cả kết quả cuối cùng, kể cả khi hết retry. Tránh truy cập dict thiếu khóa hoặc trả invalid âm thầm.

Critic hiện không nhận question trong `_critique`, nên không kiểm tra ý nghĩa phép toán. Tìm literal bằng substring khiến `100` quy đổi bị báo thiếu, còn số xuất hiện ở sai hàng vẫn được chấp nhận. `"divide" in program and " 0" in program` báo nhầm với 0.x hoặc 0 ở tử số. Cần kiểm tra AST/evidence, hằng số cho phép và mẫu số đã resolve; không dựa substring.

**G. Validator/parser:** dùng parser kiểm tra cân bằng ngoặc và split dấu `;` ở depth 0 bất kể có khoảng trắng. Hiện `subtract(2; 1);add(#0; 3)` bị parse thành một operation. Kiểu literal số phải tách khỏi nhãn văn bản; validate full reference `#N`, chỉ lùi; math có 2 args, lookup có 4 args, source đúng modality/tồn tại, label/phạm vi tồn tại. Không cấm ngoặc bên trong label như `DJIA (Mỹ)` hoặc `FY2020(F)`.

Đã tái hiện validator hiện tại chấp nhận `add(VN30; VNMidcap)`, `chart_max(Table 1; x; none; none)` và `divide(100; 0)`. Audit bổ sung bắt thêm 35 câu ngoài 101 câu validator cũ phát hiện.

**H. Decoder:** `DSLLogitsProcessor` chỉ ép token đầu, cho cả token cấu trúc/số và thả tự do phần còn lại. Vì thế không ngăn được `chart_divide`/`table_divide` (đều có trong CSV), thiếu/thừa đối số, source sai kiểu, reference tới tương lai. Còn đọc chỉ 2.000 token cuối và lấy trạng thái hàng 0 áp cho toàn batch. Chưa thấy ảnh hưởng batch trong runner tuần tự, nhưng đây là lỗi khi mở rộng batch/beam.

Đề xuất decoder trạng thái cho phần program: danh sách đầy đủ operator, arity theo registry, reference chỉ `#0..#(i-1)`, kết thúc bước/response rõ ràng; source ID và label là candidate từ schema. Phải chỉ xét token sinh mới và reset giữa các lần generate/retry. Grammar chỉ đảm bảo cấu trúc, không tự quyết định subtract hay divide đúng câu hỏi.

`fsm_outlines.py` hiện không được pipeline gọi; regex cho math nhận chuỗi bất kỳ, không validate reference, đồng thời `[^;)]+` không hỗ trợ đúng label có ngoặc đóng. Không bật file này lên rồi coi vấn đề đã giải quyết. Nếu dùng thư viện grammar, kiểm tra API theo version đã pin và test label thực tế của train.

### P1 — Học kế hoạch phép toán và sinh reference bằng code

Tách **evidence selection → operation plan → compiler DSL**. Model dự đoán role như base/new, numerator/denominator, selected members, time range. Compiler đánh số node theo topo và sinh `#N` từ node ID; không để model tự đếm reference bằng văn bản.

Ví dụ evidence đúng cho NII:

```text
n0 = chart_at(Image 1; NII; 2019; none)
n1 = chart_at(Image 1; NII; 3Q24 (TTM); none)
n2 = subtract(n1; n0)
n3 = divide(n2; n0)
n4 = multiply(n3; 100)
```

Compiler xuất program giữ đúng thứ tự và 0-index. Không constant-fold lookup thành literal. Tên series và mốc thời gian copy từ schema. Thứ tự template chọn theo convention của train; không tùy tiện canonicalize mọi gold nếu evaluator chưa rõ.

Augment từ train bằng cặp tương phản: chênh lệch/tỷ lệ/tăng trưởng, đổi hướng A-B, tăng/giảm, phần trăm/điểm phần trăm, sum/average, giai đoạn/tập rời rạc, chart/table nguồn khác nhau. Mỗi mẫu có context và gold nhất quán. Augmentation hiện chủ yếu câu exp và label giả với context rỗng; không đánh trúng các lỗi chủ đạo. Dữ liệu tóm tắt có output dummy trong `multitask_mixing.py` không nên đưa vào training chính. Hai module này chưa được trainer gọi trực tiếp, nên chưa thể quy lỗi v3 cho chúng.

### P1 — Đánh giá và tái lập thí nghiệm

- Giữ exact string, normalized syntax, expression-tree equivalence, execution equality và validation rate là các cột riêng. `programs_equivalent` hiện chỉ zip từng bước và cho đảo add/multiply, không phải semantic equivalence tổng quát; hai chuỗi rỗng còn có thể được coi tương đương. `normalize_program` không làm đủ việc mà docstring nói và không được `program_accuracy` gọi.
- `execution_accuracy` bỏ qua prediction None: ví dụ pred `[1,None]`, gold `[1,2]` cho 100%. Nếu báo execution accuracy trên tập có gold, missing pred phải là sai; kèm coverage. Table/chart executor hiện luôn trả None dù có tham số tables/charts, nên chưa chấm end-to-end bằng execution được.
- Sửa number normalization theo **nguồn**. `resolve_arg('0.175') = 175`, `resolve_arg('0.105') = 105` là lỗi đã chạy lại; QID `648c0465-0a34-5ef8-bcf5-57759f395717` có program đúng nhưng executor sẽ tính 70 thay vì 0.07. DSL canonical dùng decimal độc lập locale; parser raw HTML/text có locale/unit riêng. Không xóa dấu chấm vì thấy đúng ba chữ số cuối.
- `prepare_dataset` tạo split theo step count, nhưng trainer không dùng split đó; dùng toàn bộ train và public làm eval. Split lưu hiện có 184/184 ảnh của val cũng xuất hiện ở train split. Dùng group theo tài liệu/ảnh (connected components nếu mẫu có nhiều ảnh), rồi cân bằng loại program giữa các group. Public đã được dùng chẩn đoán thì không còn là holdout độc lập cho chọn model.
- Lưu full generated text, parsed program, validator reasons, prompt/schema hash, adapter path/revision, tokenizer/dependency versions, CV cache key, số token và termination reason. Hiện raw output chỉ log 300 ký tự, batch chỉ lưu qid/program, không đủ phân biệt truncation, parse lỗi, CV lỗi và reasoning lỗi.

## 6. Kế hoạch triển khai và tiêu chí nghiệm thu

| Thứ tự | Thay đổi | Kiểm tra cần đạt |
|---|---|---|
| 1 | Sửa audit/metric, parser số, validator, retry crash | Các ca tái hiện trong `probes.json` xử lý đúng; invalid không được ghi như thành công |
| 2 | Context/schema/prompt dùng chung, cache CV thật, làm sạch train | Không còn placeholder giả trong cấu hình dùng CV; source/label/unit giữ được; toàn bộ target parse và serialize round-trip |
| 3 | Grouped split, response-only loss, bảo toàn target/EOS | Không chung tài liệu/ảnh train-val; prompt/pad bị mask; mọi mẫu còn đủ program label |
| 4 | Train lại SFT baseline và đo theo nhóm | Báo Program Accuracy trên val nội bộ cố định, lỗi nguồn/arity/reference/shortcut riêng |
| 5 | Evidence roles + compiler và augment tương phản | Compiler không sinh forward/self reference; giữ đúng hướng phép toán và quy ước gold |
| 6 | Grammar/validation + retry có giới hạn | Chạy được label có ngoặc/@/tiếng Việt; kiểm tra lần sinh cuối; đo mức cải thiện thực tế |

Nên làm ablation từng bước với cùng split và seed; tách kiểm tra NLP dùng schema đã xác minh khỏi end-to-end CV để biết điểm nghẽn. Chưa có cơ sở để hứa mức accuracy mới trước khi train/inference lại. Không dùng public gold làm lookup câu trả lời khi inference.

## 7. Checklist toàn bộ code đã đọc

| File trong vinumqa | Nhận xét/hành động |
|---|---|
| `__init__.py` | Chỉ docstring, không có logic gây sai |
| `utils/__init__.py` | Chỉ docstring |
| `utils/dsl_parser.py` | Split bước phụ thuộc khoảng trắng; thiếu type validation; sai locale số; lookup executor stub; equivalence hạn chế |
| `utils/metrics.py` | Metric nội bộ không phải official; missing prediction bị bỏ mẫu ở execution accuracy; operator F1 không bắt order và bỏ unknown operator khỏi tập tính |
| `data/prepare_dataset.py` | Path `vlsp-2026-ViTNumChart/train.json` không khớp layout hiện tại; split không group tài liệu; file split không được trainer sử dụng |
| `nlp_module/dsl_operators.py` | 16 operator nhưng docstring đầu ghi 14; registry nên là nguồn chung. Mô tả table chỉ “column” quá hẹp so với mẫu chọn chuỗi theo hàng |
| `nlp_module/data_prep/format_training_data.py` | Placeholder chart; Step 1 mất vai trò; table header chưa chuẩn; train/infer hint lệch; bỏ placeholder unmatched im lặng |
| `nlp_module/data_prep/augment_data.py` | Context rỗng, tập trung rare ops, không có grounding; chưa nối trực tiếp trainer |
| `nlp_module/data_prep/multitask_mixing.py` | Target tóm tắt dummy, không cải thiện supervision reasoning; chưa nối trực tiếp trainer |
| `nlp_module/training/lora_config.py` | 4096 token cần đo truncation; 3 epochs/r=16 không đủ bằng chứng để coi là nguyên nhân gốc |
| `nlp_module/training/train_qlora.py` | Full-sequence loss, right-truncation có nguy cơ mất target, public eval, thiếu lưu tokenizer/manifest và explicit EOS; không có generated Program Accuracy callback |
| `nlp_module/inference/generate_program.py` | Prompt mâu thuẫn gold bảng, không dùng chung formatter, regex response chỉ một dòng; không xác minh adapter thành công; lỗi load bị catch và có thể để model base đã nạp còn tồn tại; ngân sách 768 cần log kết thúc |
| `nlp_module/inference/constrained_decode.py` | Chỉ token đầu, không phải full grammar; cửa sổ 2000 token; trạng thái theo hàng 0 |
| `nlp_module/inference/fsm_outlines.py` | Chưa được gọi; regex không đủ type/ref và khó với ngoặc trong label; dependency không pin |
| `nlp_module/inference/symbolic_executor.py` | Không nhận context tables/charts để thực thi lookup; không được NLP pipeline thực thi |
| `nlp_module/critic/reflection_loop.py` | NameError retry; heuristic chia 0 và evidence substring yếu; không kiểm tra lần retry cuối |
| `nlp_module/pipeline.py` | Chỉ generator/reflection; docstring nói answer/executor nhưng không thực thi executor |
| `cv_module/chart_to_table/extract_table.py` | Text Markdown tự do; chưa schema hóa labels/units/axis; model failure trả bảng lỗi; 1024 token có thể thiếu bảng dài, chưa log; aspect ratio không xác nhận chart type |
| `cv_module/pipeline.py` | Cache RAM theo path, không persist/version; lưu cả output lỗi; verify không được gọi |
| `cv_module/chart_classifier/classify.py` | Không ở pipeline hiện tại; nếu không có weights thì classifier là ngẫu nhiên nhưng vẫn initialized=True |
| `cv_module/zoom_verify/verify_agent.py` | Không ở pipeline hiện tại; merge chỉ nối các bảng quadrant, không căn hàng/cột/legend |
| `cv_module/zoom_verify/zoom_tool.py` | Không ở pipeline hiện tại; crop có thể tách legend/trục khỏi dữ liệu và resize vuông méo tỷ lệ; không ưu tiên bật lại vô điều kiện |
| `pipeline/full_pipeline.py` | Có giữ header Image ở bản hiện tại; không quy lỗi mất header cho bản này; builder trùng formatter, drop unmatched, truyền CV output dạng text |
| `pipeline/batch_inference.py` | Không bắt lỗi theo mẫu để resume; chỉ ghi qid/program, không log evidence/validation; đường dẫn CLI mặc định không khớp data/public_test |

Đã AST-parse cả 24 file: đều hợp lệ cú pháp. Nhận xét sơ bộ về thụt lề CV đã được bác bỏ khi kiểm tra lại; không đưa vào danh sách lỗi.

Một mẫu train (`05a85e9c-7c27-529f-924b-466218915da3`) chứa newline giữa hai operation mà thiếu `;`. Nội dung đó được đưa vào output dạng bảng; regex một dòng không đọc được. Con số 1 trong probe “program_mismatch_by_position” là **lỗi định dạng/parsing target multiline**, không phải bằng chứng formatter thay đổi program gốc.

## 8. Artifact và tái lập

- `row_review.md`: từng câu, question, gold/pred, cờ kiểm tra và mọi khác biệt từng bước/đối số.
- `rows.json`: cùng chẩn đoán ở dạng máy đọc được.
- `summary.json`: số liệu tổng, phân bố toán tử, inventory code và thông tin artifact training.
- `probes.json`: tái hiện retry crash, parse số, validator, metric và các ca hoán vị/trùng giá trị.

Chạy từ project root: `python audit_v3.py`, rồi `python probe_v3.py`. Chỉ dùng thư viện chuẩn và các utility hiện có; không tải model. Audit này không chỉnh CSV nguồn, ground truth, model weights hay code sản xuất. Các hướng sửa ở trên cần triển khai và đánh giá lại trước khi kết luận cải thiện model.
