"""Generation telemetry without moving CUDA work into an abandoned thread."""
import threading
import time


def placement(device, cuda_available):
    """Single GPU by default; multi-GPU dispatch must be explicitly selected."""
    if device not in ('cpu', 'auto', 'cuda') and not (
        device.startswith('cuda:') and device[5:].isdigit()
    ):
        raise ValueError('device must be cpu, cuda, cuda:N or auto')
    if device == 'cpu' or not cuda_available:
        return 'cpu', 'cpu'
    if device == 'auto':
        return 'cuda', 'auto'
    selected = 'cuda:0' if device == 'cuda' else device
    return selected, {'': selected}


def eos_ids(generation_config, tokenizer):
    value = getattr(generation_config, 'eos_token_id', None)
    if value is None:
        value = tokenizer.eos_token_id
    return set(value if isinstance(value, (list, tuple)) else [value]) - {None}


class GenerationProgress:
    """HF stopping-criteria callback + CPU-only heartbeat, never stops generation.

    An unchanged token count means no decoding step has completed; it does not
    prove a deadlock. A stuck CUDA forward cannot be cancelled by this thread.
    """
    def __init__(self, prompt_tokens, interval=30, clock=time.monotonic, emit=None):
        if interval <= 0:
            raise ValueError('progress interval must be positive')
        self.prompt_tokens = prompt_tokens
        self.interval = interval
        self.clock = clock
        self.emit = emit or (lambda message: print(message, flush=True))
        self.generated_tokens = 0
        self.started = self.last_step = clock()
        self.phase = 'prefill/first token'
        self._stop = threading.Event()
        self._thread = None

    def __call__(self, input_ids, scores, **kwargs):
        self.generated_tokens = max(0, input_ids.shape[-1] - self.prompt_tokens)
        self.last_step = self.clock()
        self.phase = 'decode'
        return False

    def report(self):
        now = self.clock()
        self.emit(f'[NLP progress] phase={self.phase}; prompt_tokens={self.prompt_tokens}; '
                  f'generated_tokens={self.generated_tokens}; elapsed={now-self.started:.1f}s; '
                  f'last_token_step_ago={now-self.last_step:.1f}s')

    def _heartbeat(self):
        while not self._stop.wait(self.interval):
            self.report()

    def __enter__(self):
        self.started = self.last_step = self.clock()
        self._thread = threading.Thread(target=self._heartbeat, daemon=True, name='nlp-progress')
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join(timeout=1)
