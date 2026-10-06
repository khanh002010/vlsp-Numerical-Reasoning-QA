"""Select an attention backend without requiring flash-attn on Turing GPUs."""

def select_attention_backend(capabilities, flash_available):
    # device_map=auto may place layers on any visible GPU.
    if capabilities and all(8 <= major <= 9 for major, minor in capabilities) and flash_available:
        return "flash_attention_2"
    return "sdpa"
