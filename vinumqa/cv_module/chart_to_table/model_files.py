"""Resolve a complete local Qwen snapshot before constructing Transformers objects."""
import json
from pathlib import Path


def snapshot_complete(directory):
    root = Path(directory)
    def present(name):
        path = root / name
        return path.is_file() and path.stat().st_size > 0
    try:
        for name in ("config.json", "preprocessor_config.json", "tokenizer_config.json"):
            if not present(name): return False
            json.loads((root / name).read_text(encoding="utf-8"))
        if not (present("tokenizer.json") or (present("vocab.json") and present("merges.txt"))):
            return False
        tokenizer_config = json.loads((root / "tokenizer_config.json").read_text(encoding="utf-8"))
        if not (present("chat_template.json") or present("chat_template.jinja") or tokenizer_config.get("chat_template")):
            return False
        if present("model.safetensors.index.json"):
            index = json.loads((root / "model.safetensors.index.json").read_text(encoding="utf-8"))
            shards = set(index.get("weight_map", {}).values())
            return bool(shards) and all(present(name) for name in shards)
        return present("model.safetensors")
    except (OSError, ValueError, TypeError):
        return False


def resolve_model_directory(model_id, download=None):
    if Path(model_id).is_dir():
        if not snapshot_complete(model_id):
            raise RuntimeError(f"Incomplete local OCR model directory: {model_id}")
        return str(Path(model_id).resolve())
    if download is None:
        from huggingface_hub import snapshot_download
        download = snapshot_download
    options = {"repo_id": model_id, "allow_patterns": ["*.json", "*.safetensors", "*.txt", "*.jinja"]}
    try:
        cached = download(**options, local_files_only=True)
    except (OSError, ValueError):
        cached = None
    if cached and snapshot_complete(cached):
        print(f"OCR model: using cached local snapshot {cached}", flush=True)
        return str(Path(cached).resolve())
    print("OCR model cache incomplete; downloading missing snapshot files...", flush=True)
    try:
        directory = download(**options, max_workers=2)
    except Exception as error:
        raise RuntimeError(
            "Cannot download OCR model files. If Hugging Face reports HTTP 429, wait for its "
            "retry interval or configure HF_TOKEN, then rerun; keep the existing cache. "
            f"Details: {error}"
        ) from error
    if not snapshot_complete(directory):
        raise RuntimeError(f"OCR snapshot is missing required processor/tokenizer/weight files: {directory}")
    return str(Path(directory).resolve())
