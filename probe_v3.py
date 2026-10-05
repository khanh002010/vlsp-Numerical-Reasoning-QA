"""Small offline reproductions supporting the v3 audit, without loading models."""
import ast
import json
import re
import sys
from pathlib import Path
from statistics import median

from audit_v3 import ROOT, OUT, load
from vinumqa.utils.dsl_parser import parse_program, validate_program, resolve_arg
from vinumqa.utils.metrics import execution_accuracy


def definitions(path, names, env):
    module = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    # Test real functions/classes while avoiding heavyweight import-time model dependencies.
    module.body = [n for n in module.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(module, path, "exec"), env)
    return env


class FakeGenerator:
    def generate(self, *args):
        return {"program": "subtract(#1; #0)", "extracted_values": ""}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    result = {}
    env = definitions("vinumqa/nlp_module/critic/reflection_loop.py", {"ReflectionLoop"},
                      {"ProgramGenerator": object, "validate_program": validate_program})
    try:
        env["ReflectionLoop"](FakeGenerator()).generate_with_reflection("", "", "", "test")
    except Exception as e:
        result["reflection_retry"] = f"{type(e).__name__}: {e}"
    result["validator_examples"] = {s: validate_program(s) for s in [
        "add(VN30; VNMidcap)", "chart_max(Table 1; x; none; none)", "divide(100; 0)",
        "subtract(2; 1);add(#0; 3)"]}
    result["numeric_resolution"] = {s: resolve_arg(s, {}) for s in ["0.175", "0.105", "46.495", "52.102"]}
    result["execution_accuracy_missing_prediction"] = execution_accuracy([1, None], [1, 2])
    result["parsed_no_space"] = [repr(s) for s in parse_program("subtract(2; 1);add(#0; 3)")]
    data = load("data/public_test/public_test.json")
    rows = json.loads((OUT / "rows.json").read_text(encoding="utf-8"))
    result["swaps"] = [d for d in rows if "aligned_noncommutative_swap" in d["flags"]]
    result["same_math_value"] = [d for d in rows if "same_math_value_non_exact" in d["flags"]]
    result["formatted_checks"] = {}
    for raw_path, fmt_path in [("data/train/train.json", "train_formatted.json"), ("data/public_test/public_test.json", "public_test_formatted.json")]:
        raw, fmt = load(raw_path), load("vinumqa/data/" + fmt_path)
        lengths = [len(s["instruction"] + s["input"] + s["output"]) for s in fmt]
        def program(s):
            m = re.search(r"\| 2 \| (.*?) \|", s["output"])
            return m.group(1) if m else ""
        result["formatted_checks"][fmt_path] = {
            "program_mismatch_by_position": sum(s["qa"]["program"] != program(t) for s, t in zip(raw, fmt)),
            "median_chars": median(lengths), "max_chars": max(lengths),
            "over_16000_chars": sum(n > 16000 for n in lengths),
            "first_instruction": fmt[0]["instruction"],
            "program_mismatches": [{"qid": s["qid"], "raw": s["qa"]["program"], "formatted": program(t)} for s,t in zip(raw,fmt) if s["qa"]["program"] != program(t)],
        }
    qids = ["bed4e850-a504-5677-9307-184caea40c71", "b36cd841-19f1-544e-b95f-fb0234949122", "8d829101-30ce-504a-8f1d-9c4299018ae3", "42523de0-d558-5aba-a87c-21a24feb9939"]
    result["selected_sources"] = []
    fmt = load("vinumqa/data/public_test_formatted.json")
    for i, s in enumerate(data):
        if s["qid"] in qids:
            result["selected_sources"].append({"qid": s["qid"], "qa": s["qa"], "tables": s["tables"], "formatted_input": fmt[i]["input"]})
    result["split_overlap"] = {}
    a, b = load("vinumqa/data/train_split.json"), load("vinumqa/data/val_split.json")
    def images(samples): return {v for s in samples for v in s.get("images", {}).values()}
    result["split_overlap"] = {"train_samples": len(a), "val_samples": len(b), "shared_images": len(images(a) & images(b)), "val_images": len(images(b))}
    (OUT / "probes.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k != "selected_sources"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
