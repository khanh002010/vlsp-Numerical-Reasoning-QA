# Giảm VRAM ở loss, giữ nguyên bài toán training

Mặc định `--loss-mode completion`. Toàn bộ input_ids/attention_mask/context vẫn đi qua
decoder Qwen2.5 như trước. Labels của prompt vốn đã là -100: các logits dự đoán chúng
không góp vào loss hoặc gradient. Trainer mới dùng `logits_to_keep` để bỏ phần prefix
này **trước lm_head**, giữ thêm một vị trí trước token đáp án đầu tiên cho causal shift.
Labels được thu hẹp tương ứng, không mất token đáp án/EOS. Với batch nhiều mẫu, chọn
prefix chung trước target đầu tiên của bất kỳ mẫu nào, giữ các vị trí mask/padding sau đó.

Hàm loss của model, cách chia loss theo số token, gradient accumulation, AMP, optimizer,
LoRA, checkpointing, train/validation data và sinh program đều giữ nguyên. Không dùng
sampled softmax, không giảm vocabulary, không truncate context/target, không giảm epoch.
Generation ngoài Trainer vẫn dùng model gốc. Chỉ hỗ trợ Qwen2/Qwen2.5 có logits_to_keep;
Trainer evaluation phải prediction_loss_only=True, như cấu hình hiện tại.

Nguồn API: [Qwen2ForCausalLM.forward](https://github.com/huggingface/transformers/blob/main/src/transformers/models/qwen2/modeling_qwen2.py).

Đo theo 1725 train + 459 public đã audit, microbatch=1 và padding bội 8:

| Tập | Vị trí logits cũ | Vị trí logits mới | Giảm |
|---|---:|---:|---:|
| Train | 4744376 | 244307 | 94,85% |
| Public validation loss | 1691480 | 75150 | 95,56% |

Đây là số vị trí lm_head/logits cộng trên dataset; không phải giảm tổng VRAM/thời gian
đã benchmark. Attention/decoder vẫn xử lý đủ context. Không cam kết hết OOM trên mọi
môi trường, hoặc điểm benchmark hoàn toàn giống bit-for-bit; phép nhân ma trận với
kích thước khác có thể gây khác biệt làm tròn số dấu phẩy động.

Giới hạn mặc định 7680 theo audit: train tối đa 6051, public tối đa 7487 token (7488 sau
padding). Không pad mọi mẫu lên 7680. Nếu resume checkpoint cũ, giữ max-seq-length cùng
giá trị trong manifest của checkpoint. loss-mode không đổi schema/weights/checkpoint.

Sau khi cập nhật code trên Kaggle, chạy trong subprocess mới:

```python
import subprocess
import sys

subprocess.run([
    sys.executable, "-u", "-m", "vinumqa.nlp_module.training.train_qlora",
    "--train-data", "/kaggle/working/prepared/train_structured.json",
    "--val-data", "/kaggle/working/prepared/public_test_structured.json",
    "--output-dir", "/kaggle/working/outputs/nlp_module",
    "--max-seq-length", "7680",
    "--loss-mode", "completion",
    "--max-train-hours", "10.5",
    "--save-steps", "50",
], cwd="/kaggle/working/vlsp-Numerical-Reasoning-QA", check=True)
```

Log `[Loss] context=... unchanged; LM-head logits=...` cho biết đã bật tối ưu. Chọn
`--loss-mode full` khi cần đối chiếu baseline (có thể OOM như cũ). Không cần OCR lại.

Kiểm thử dùng Qwen2 nhỏ khởi tạo ngẫu nhiên trên CPU, không tải trọng số 7B:

```bash
python -m unittest discover -s tests -p test_completion_logits.py
```

So sánh loss/gradient toàn model và LoRA, gradient checkpointing, accumulation có số
target khác nhau, training/evaluation qua Trainer thật, và greedy generation sau train.
Test này cần torch, transformers, accelerate, peft; nếu thiếu thư viện sẽ báo skip.


## OOM trong backward tr?n T4

Log OOM m?i x?y ra trong backward, d? ?? gi?m logits. M?t ???ng c? th? g?y l?i l?
SDPA native GQA r?i v? math kernel tr?n m?t s? phi?n b?n PyTorch/CUDA d?ng T4: kernel n?y c?n b? nh? b?c hai theo ??
d?i context. Traceback kh?ng ?? ?? x?c nh?n tensor g?y OOM; c?n ?o tr?n GPU.

Training hi?n ??ng k? `vinumqa_memory_sdpa`: m? r?ng KV heads r?i g?i SDPA g?c,
ch? cho ph?p efficient/flash CUDA kernels, kh?ng cho fallback sang math. ??ng k?
c? mask builder SDPA ?? gi? causal/padding mask. CPU v?n d?ng SDPA b?nh th??ng
cho ki?m th?. Kh?ng ??i context, target, s? m?u, LoRA, optimizer ho?c epoch.
Validation generation ch?y trong FP16 autocast, ph? h?p v?i QLoRA tr?n T4.

Tr??c khi n?p tr?ng s?, ch??ng tr?nh ki?m tra fused forward/backward tr?n t?ng GPU:
`[Attention] cuda:... fused SDPA forward/backward OK; math fallback disabled`.
N?u b? PyTorch/CUDA kh?ng h? tr? kernel, ch??ng tr?nh b?o l?i ngay. Ki?m tra nh?
n?y x?c nh?n backend ho?t ??ng, kh?ng ??m b?o to?n b? model lu?n ?? VRAM.

Sau `git pull`, ch?y l?i cell training c? b?ng subprocess m?i. Kh?ng c?n OCR l?i;
gi? `--max-seq-length` c? n?u resume checkpoint. Kh?ng ??i `prepared`.

Ki?m th? b? sung: `python -m unittest discover -s tests -p test_memory_attention.py`.
So s?nh logits/gradient, padding, checkpoint recomputation, causal prefix, generation
c? v? kh?ng c? KV cache. CPU parity kh?ng thay th? benchmark VRAM hay accuracy tr?n T4;
fused kernels c? th? kh?c sai s? l?m tr?n so v?i math kernel.

Ngu?n: [Hugging Face attention registry v? mask](https://huggingface.co/docs/transformers/main/en/attention_interface),
[PyTorch SDPA](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html).
