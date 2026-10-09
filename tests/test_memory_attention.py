"""Attention parity with full context, masks, backward and cached generation."""
import copy
import unittest
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM
from vinumqa.nlp_module.training.memory_attention import register_memory_attention

class MemoryAttentionTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(31)
        config = Qwen2Config(vocab_size=97, hidden_size=32, intermediate_size=64,
            num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
            max_position_embeddings=128, attention_dropout=0.0,
            bos_token_id=1, eos_token_id=2, pad_token_id=0)
        config._attn_implementation = "sdpa"
        self.reference = Qwen2ForCausalLM(config)
        self.optimized = copy.deepcopy(self.reference)
        self.optimized.set_attn_implementation(register_memory_attention())

    def test_loss_and_backward_with_padding_and_checkpointing(self):
        for padded in (False, True):
            for checkpointed in (False, True):
                with self.subTest(padded=padded, checkpointed=checkpointed):
                    ids = torch.randint(3, 97, (2, 24))
                    mask = torch.ones_like(ids)
                    if padded:
                        ids[0, 19:] = 0
                        mask[0, 19:] = 0
                    labels = ids.clone()
                    labels[:, :12] = -100
                    labels[mask == 0] = -100
                    outputs = []
                    for model in (self.reference, self.optimized):
                        model.zero_grad(set_to_none=True)
                        if checkpointed:
                            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
                        else:
                            model.gradient_checkpointing_disable()
                        output = model(input_ids=ids, attention_mask=mask, labels=labels, use_cache=False)
                        output.loss.backward()
                        outputs.append(output)
                    torch.testing.assert_close(outputs[0].logits, outputs[1].logits, atol=1e-6, rtol=1e-5)
                    for a, b in zip(self.reference.parameters(), self.optimized.parameters()):
                        torch.testing.assert_close(a.grad, b.grad, atol=2e-6, rtol=2e-5)

    def test_causal_prefix_and_cached_generation(self):
        ids = torch.randint(3, 97, (1, 16))
        changed = ids.clone()
        changed[:, 8:] = 3
        self.optimized.eval()
        self.reference.eval()
        with torch.no_grad():
            before = self.optimized(ids).logits[:, :8]
            after = self.optimized(changed).logits[:, :8]
            torch.testing.assert_close(before, after)
            for cache in (True, False):
                a = self.reference.generate(ids, max_new_tokens=5, do_sample=False, use_cache=cache)
                b = self.optimized.generate(ids, max_new_tokens=5, do_sample=False, use_cache=cache)
                torch.testing.assert_close(a, b)

if __name__ == "__main__":
    unittest.main()
