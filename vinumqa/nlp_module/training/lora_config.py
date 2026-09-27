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
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    max_steps: int = 1000  # or use num_train_epochs
    num_train_epochs: int = 3
    learning_rate: float = 2e-4
    fp16: bool = True
    logging_steps: int = 10
    output_dir: str = "./outputs/nlp_module"
    optim: str = "paged_adamw_32bit"
    max_seq_length: int = 2048
