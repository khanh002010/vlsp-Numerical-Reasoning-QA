"""Completion-only labels; fail on overflow instead of silently losing the target."""
def load_prepared_pair(train_path, val_path, skip_unready=False):
    """Load portable, self-contained JSON datasets without opening images or OCR cache."""
    import json
    from pathlib import Path
    from vinumqa.nlp_module.contracts import FORMAT_VERSION, INSTRUCTION
    datasets = []
    for path in (train_path, val_path):
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Prepared dataset not found: {path}. Run format_training_data once and copy its output JSON here.")
        rows = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(rows, dict) and rows.get("artifact_version") in {"vinumqa-prepared-v1", "vinumqa-prepared-structures-v1"}:
            records = rows["samples"]
            unready = [r for r in records if r["status"] != "ready"]
            if unready and not skip_unready:
                raise ValueError(f"{path}: {len(unready)} samples have failed/pending OCR or invalid labels. "
                                 "Finish/repair preparation or explicitly use --skip-unready to train/evaluate a subset.")
            if unready:
                print(f"{path}: excluding {len(unready)} unready samples; using a subset of this dataset.", flush=True)
            rows = [r["data"] for r in records if r["status"] == "ready"]
        if not isinstance(rows, list):
            raise ValueError(f"Prepared dataset must be a JSON list: {path}")
        datasets.append(rows)
    validate_dataset_pair(*datasets, FORMAT_VERSION, INSTRUCTION, allow_group_overlap=True)
    return tuple(datasets)

def validate_dataset_pair(train, val, format_version, instruction, allow_group_overlap=False):
    """Reject stale artifacts, overlapping document groups and duplicate question IDs."""
    from vinumqa.nlp_module.contracts import parse_response
    groups = []
    all_qids = set()
    profiles = {s.get('prompt_profile', 'legacy') for s in train + val}
    if len(profiles) != 1:
        raise ValueError('Train/validation prompt profiles differ; rebuild both with the same profile')
    for name, rows in [("train", train), ("val", val)]:
        if not rows: raise ValueError(f"Empty {name} dataset")
        keys = set()
        for s in rows:
            if s.get("format_version") != format_version or s.get("instruction") != instruction:
                raise ValueError("Stale dataset contract")
            if s.get("qid") in all_qids: raise ValueError("Duplicate/overlapping QID")
            all_qids.add(s.get("qid"))
            if not s.get("group_keys"): raise ValueError("Missing document group metadata")
            keys.update(s["group_keys"])
            if "extracted by CV Module" in s["input"]: raise ValueError("Placeholder CV input")
            if not parse_response(s["output"])["valid"]: raise ValueError("Invalid target program")
        groups.append(keys)
    if groups[0] & groups[1] and not allow_group_overlap: raise ValueError("Train/validation document or image overlap")


def augment_source_ids(rows):
    """Add a train-only permutation of Image/Table IDs, consistently in input/target.

    All source facts, values, ordering and questions are preserved up to source
    renaming. Single-source samples receive a non-1 ID to discourage source priors.
    """
    import copy
    import re
    from vinumqa.nlp_module.contracts import source_ids, parse_response
    augmented = []
    pattern = re.compile(r'\b(?:Image|Table) [1-9]\d*\b')
    for row in rows:
        ids = source_ids(row['input'])
        if not ids: continue
        mapping = {}
        for kind in ('Image', 'Table'):
            names = sorted((x for x in ids if x.startswith(kind+' ')), key=lambda x: int(x.split()[1]))
            if len(names) > 1:
                mapping.update(zip(names, names[1:] + names[:1]))
            elif names:
                mapping[names[0]] = f'{kind} {int(names[0].split()[1])+1}'
        remap = lambda text: pattern.sub(lambda m: mapping.get(m[0], m[0]), text)
        changed = copy.deepcopy(row)
        changed['qid'] = row['qid'] + ':source-permutation'
        changed['input'], changed['output'] = remap(row['input']), remap(row['output'])
        if 'charts' in row: changed['charts'] = {mapping.get(k,k): v for k,v in changed['charts'].items()}
        changed['augmentation'] = {'kind': 'source-id-permutation-v1', 'source_qid': row['qid'], 'mapping': mapping}
        if not parse_response(changed['output'])['valid']: raise ValueError('Invalid remapped target')
        augmented.append(changed)
    if {r['qid'] for r in rows} & {r['qid'] for r in augmented}:
        raise ValueError('Augmented QID collision')
    return rows + augmented

def pad_supervised(features, pad_id, multiple=8):
    n = max(len(f["input_ids"]) for f in features)
    n = ((n + multiple - 1) // multiple) * multiple
    return {k: [f[k] + [pad] * (n - len(f[k])) for f in features]
            for k, pad in [("input_ids", pad_id), ("attention_mask", 0), ("labels", -100)]}

def encode_supervised(tokenizer, prompt, completion, max_length):
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    target_ids = tokenizer.encode(completion, add_special_tokens=False)
    if not target_ids: raise ValueError("Empty completion")
    if tokenizer.eos_token_id is None: raise ValueError("Tokenizer must define EOS")
    target_ids.append(tokenizer.eos_token_id)
    if len(prompt_ids) + len(target_ids) > max_length:
        raise ValueError(f"Sequence overflow: prompt={len(prompt_ids)}, target={len(target_ids)}, budget={max_length}. Increase budget or reduce context before training; target was not truncated.")
    ids = prompt_ids + target_ids
    return {"input_ids": ids, "attention_mask": [1] * len(ids), "labels": [-100] * len(prompt_ids) + target_ids}

class CompletionCollator:
    def __init__(self, tokenizer, multiple=8):
        self.pad = tokenizer.pad_token_id
        self.multiple = multiple

    def __call__(self, features):
        import torch
        return {k: torch.tensor(v, dtype=torch.long) for k, v in pad_supervised(features, self.pad, self.multiple).items()}
