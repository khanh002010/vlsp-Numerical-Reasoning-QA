"""Full-context SDPA without native GQA's possible quadratic math fallback."""
from contextlib import nullcontext
import torch
from torch.nn.attention import SDPBackend, sdpa_kernel
from transformers import AttentionInterface
from transformers.masking_utils import AttentionMaskInterface, sdpa_mask
from transformers.integrations.sdpa_attention import repeat_kv, sdpa_attention_forward

BACKEND = "vinumqa_memory_sdpa"

class _ExpandedKV:
    """Delegate metadata without mutating the actual attention module."""
    num_key_value_groups = 1
    def __init__(self, module):
        self.module = module
    def __getattr__(self, name):
        return getattr(self.module, name)

def memory_attention(module, query, key, value, attention_mask, **kwargs):
    # Qwen updates its regular DynamicCache before entering this function.
    if kwargs.get("cache") is not None:
        raise ValueError("Memory SDPA supports regular Qwen caches, not paged attention")
    groups = query.shape[1] // key.shape[1]
    key, value = repeat_kv(key, groups), repeat_kv(value, groups)
    # Re-enter on checkpoint recomputation too; never silently use CUDA math.
    context = sdpa_kernel([SDPBackend.EFFICIENT_ATTENTION, SDPBackend.FLASH_ATTENTION]) if query.is_cuda else nullcontext()
    with context:
        return sdpa_attention_forward(_ExpandedKV(module), query, key, value,
                                      attention_mask, **kwargs)

def register_memory_attention():
    AttentionInterface.register(BACKEND, memory_attention)
    # Required to preserve causal/padding/sliding-window constraints.
    AttentionMaskInterface.register(BACKEND, sdpa_mask)
    return BACKEND

def check_cuda_attention():
    """Test forward/backward before weights load, on every visible GPU."""
    print(f"[Attention] torch={torch.__version__}; CUDA={torch.version.cuda}", flush=True)
    for index in range(torch.cuda.device_count()):
        with torch.cuda.device(index), torch.random.fork_rng(devices=[index]):
            q = torch.randn(1, 28, 32, 128, device=f"cuda:{index}", dtype=torch.float16, requires_grad=True)
            k = torch.randn(1, 4, 32, 128, device=q.device, dtype=q.dtype, requires_grad=True)
            v = torch.randn_like(k, requires_grad=True)
            output, _ = memory_attention(torch.nn.Identity(), q, k, v, None)
            output.float().square().mean().backward()
            torch.cuda.synchronize(index)
            print(f"[Attention] cuda:{index} {torch.cuda.get_device_name(index)}: fused SDPA forward/backward OK; math fallback disabled", flush=True)
            del q, k, v, output
    torch.cuda.empty_cache()
