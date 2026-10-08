"""Real CPU Qwen/LoRA loss and gradient parity; no model download needed."""
import copy
import importlib.util
import tempfile
import unittest

AVAILABLE = all(importlib.util.find_spec(name) for name in ('torch','transformers','accelerate','peft'))
if AVAILABLE:
    import torch
    from transformers import Qwen2Config, Qwen2ForCausalLM, Trainer, TrainingArguments
    from peft import LoraConfig, get_peft_model
    from vinumqa.nlp_module.training.completion_logits import completion_loss_inputs, CompletionLogitsTrainer


@unittest.skipUnless(AVAILABLE, 'Requires CPU torch, transformers, accelerate and peft')
class CompletionLossTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(17)
        torch.set_num_threads(1)

    def model(self, lora=False):
        config = Qwen2Config(vocab_size=97, hidden_size=32, intermediate_size=64,
                            num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
                            max_position_embeddings=128, attention_dropout=0.0,
                            bos_token_id=1, eos_token_id=2, pad_token_id=0, use_cache=False)
        model = Qwen2ForCausalLM(config)
        if lora:
            model = get_peft_model(model, LoraConfig(r=4, lora_alpha=8, lora_dropout=0,
                target_modules=['q_proj', 'v_proj'], task_type='CAUSAL_LM'))
        return model

    def batch(self):
        ids = torch.randint(3, 97, (2, 24))
        labels = ids.clone()
        labels[0,:15] = -100
        labels[1,:19] = -100
        ids[0,21:] = 0
        labels[0,21:] = -100
        ids[0,20] = labels[0,20] = 2  # EOS must remain supervised.
        ids[1,23] = labels[1,23] = 2
        attention = ids.ne(0).long()
        return dict(input_ids=ids, labels=labels, attention_mask=attention)

    def assert_gradients(self, first, second):
        for (name,a),(other,b) in zip(first.named_parameters(), second.named_parameters()):
            self.assertEqual(name, other)
            if a.grad is None or b.grad is None:
                self.assertIs(a.grad, b.grad, name)
            else:
                torch.testing.assert_close(a.grad, b.grad, atol=2e-6, rtol=2e-5, msg=name)

    def test_full_context_eos_padding_and_shift_preserved(self):
        batch = self.batch()
        before = batch['labels'].clone()
        reduced = completion_loss_inputs(batch)
        self.assertIs(reduced['input_ids'], batch['input_ids'])
        self.assertIs(reduced['attention_mask'], batch['attention_mask'])
        self.assertEqual(reduced['logits_to_keep'], 10)  # first logit at 14 predicts label 15
        torch.testing.assert_close(batch['labels'], before)
        torch.testing.assert_close(reduced['labels'][:,1:].ne(-100).sum(), before[:,1:].ne(-100).sum())

    def test_dense_loss_and_all_gradients_match(self):
        for lora, checkpointing in ((False,False),(True,False),(True,True)):
            with self.subTest(lora=lora, checkpointing=checkpointing):
                reference = self.model(lora)
                optimized = copy.deepcopy(reference)
                if checkpointing:
                    for model in (reference, optimized):
                        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
                batch = self.batch()
                full = reference(**batch)
                reduced = optimized(**completion_loss_inputs(batch))
                self.assertEqual(full.logits.shape[1], 24)
                self.assertEqual(reduced.logits.shape[1], 10)
                torch.testing.assert_close(full.loss, reduced.loss, atol=1e-6, rtol=1e-6)
                full.loss.backward()
                reduced.loss.backward()
                self.assert_gradients(reference, optimized)

    def test_accumulated_token_denominator_matches_with_unequal_targets(self):
        reference = self.model(True)
        optimized = copy.deepcopy(reference)
        batches = [self.batch(), self.batch()]
        batches[1]['labels'][:,:21] = -100
        count = sum(b['labels'][:,1:].ne(-100).sum() for b in batches)
        total_a, total_b = 0, 0
        for batch in batches:
            a = reference(**batch, num_items_in_batch=count).loss
            b = optimized(**completion_loss_inputs(batch), num_items_in_batch=count).loss
            total_a += a.detach()
            total_b += b.detach()
            a.backward()
            b.backward()
        torch.testing.assert_close(total_a, total_b)
        self.assert_gradients(reference, optimized)

    def test_real_trainer_train_eval_and_generation_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference = self.model(True)
            optimized = copy.deepcopy(reference)
            batches = [self.batch(), self.batch()]
            samples = [{k:v[i] for k,v in b.items()} for b in batches for i in range(2)]
            # Unequal final accumulation window: 3 examples, 2 microbatches/step.
            samples = samples[:3]
            common = dict(use_cpu=True, per_device_train_batch_size=1, per_device_eval_batch_size=1,
                          gradient_accumulation_steps=2, num_train_epochs=1, learning_rate=1e-3,
                          save_strategy='no', report_to='none', disable_tqdm=True, seed=42,
                          prediction_loss_only=True, optim='adamw_torch', warmup_steps=0)
            trainers = []
            for name, cls, model in [('full', Trainer, reference), ('completion', CompletionLogitsTrainer, optimized)]:
                trainer = cls(model=model, args=TrainingArguments(output_dir=tmp+'/'+name, **common),
                              train_dataset=samples, eval_dataset=samples)
                trainer.train()
                trainers.append(trainer)
            for (name,a),(_,b) in zip(reference.named_parameters(), optimized.named_parameters()):
                torch.testing.assert_close(a,b,atol=2e-6,rtol=2e-5,msg=name)
            self.assertAlmostEqual(trainers[0].evaluate()['eval_loss'], trainers[1].evaluate()['eval_loss'], places=5)
            reference.eval()
            optimized.eval()
            with torch.no_grad():
                args = dict(input_ids=samples[0]['input_ids'][:8].unsqueeze(0), max_new_tokens=4, do_sample=False)
                torch.testing.assert_close(reference.generate(**args), optimized.generate(**args))

    def test_no_next_token_targets_is_rejected(self):
        batch = self.batch()
        batch['labels'][:] = -100
        batch['labels'][:,0] = 1
        with self.assertRaisesRegex(ValueError, 'No supervised'):
            completion_loss_inputs(batch)


if __name__ == '__main__': unittest.main()
