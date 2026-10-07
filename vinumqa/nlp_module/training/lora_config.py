"""
LoRA and Training Configurations for NLP Module QLoRA Fine-tuning.
"""

from dataclasses import dataclass

@dataclass
class LoraConfig:
    r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    bias: str = "none"
    task_type: str = "CAUSAL_LM"
    target_modules: list = None
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
            
@dataclass
class TrainingConfig:
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 16
    warmup_steps: int = 100
    max_steps: int = -1  # Set to -1 to respect num_train_epochs
    num_train_epochs: int = 3
    learning_rate: float = 2e-4
    fp16: bool = True
    logging_steps: int = 10
    output_dir: str = "./outputs/nlp_module"
    optim: str = "paged_adamw_8bit"  # Chuyển state sang CPU khi đầy và dùng 8-bit để siêu tiết kiệm VRAM
    max_seq_length: int = 4096
    # Eval config: batch=1 + accumulate để tránh OOM khi logits.float() trên vocab Qwen 152k
    per_device_eval_batch_size: int = 1
    eval_accumulation_steps: int = 8
