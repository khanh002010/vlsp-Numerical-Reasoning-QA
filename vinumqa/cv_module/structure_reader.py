"""GPU adapter for bounded structure reads and optional numerical evidence reads."""
import json
from pathlib import Path
from PIL import Image
from vinumqa.cv_module.structure import STRUCTURE_PROMPT, json_object, validate_structure, validate_box


class ChartStructureReader:
    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct"):
        from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor
        self.backend = ChartToTableExtractor(model_id=model_id)
        self.backend.generation_config.max_time = 120
        self.last_generation = {}

    def _read(self, path, prompt, box=None):
        self.last_generation = {"attempts": []}
        with Image.open(path) as opened:
            image = opened.convert("RGB")
        self.last_generation["original_size"] = list(image.size)
        self.last_generation["max_pixels"] = self.backend.max_pixels
        if box is not None:
            left, top, right, bottom = validate_box(box)
            bounds = (int(left * image.width), int(top * image.height),
                      int(right * image.width), int(bottom * image.height))
            if bounds[2] <= bounds[0] or bounds[3] <= bounds[1]: raise ValueError("Empty crop")
            image = image.crop(bounds)
        inputs, _ = self.backend.prepare_inputs(image, prompt)
        for budget in (1024, 2048):
            print(f"[Structure] {Path(path).name}: budget={budget}, crop={box is not None}", flush=True)
            result = self.backend.generate_once(inputs, budget)
            self.last_generation["attempts"].append({"budget": budget, **{k: result[k] for k in ("text", "tokens", "eos", "seconds", "stop_reason")}})
            print(f"[Structure] tokens={result['tokens']}, stop={result['stop_reason']}, seconds={result['seconds']}", flush=True)
            if result["stop_reason"] == "repetition": raise ValueError("Repetitive structure output")
            if result["eos"]: return json_object(result["text"])
            if len(result["token_ids"]) < budget: break  # Time limit; do not start another long retry.
        raise ValueError("Structure read incomplete at the bounded token/time limit")

    def read_structure(self, path):
        return validate_structure(self._read(path, STRUCTURE_PROMPT))

    def inspect(self, path, request, structure):
        box = request.get("box") or structure.get("regions", {}).get(request["region"])
        hint = json.dumps({"region": request["region"], "unverified_series_hint": request["series"]}, ensure_ascii=False)
        prompt = STRUCTURE_PROMPT + "\nFocus request: " + hint + (
            "\nThe hint is NOT evidence: read the actual pixels, correct misspellings. "
            "If cropped, report only visible labels and set both completeness flags false.")
        return {"structure": validate_structure(self._read(path, prompt, box)), "full_image": box is None}

    def read_values(self, path, lookup, structure):
        from vinumqa.nlp_module.dsl_operators import DSL_OPERATORS
        signature = DSL_OPERATORS[lookup["operator"]]["signature"]
        prompt = '''Read the chart points needed by this lookup; do NOT compute the final answer or an aggregate.
Return JSON: {"complete":false,"points":[{"series":"exact name","x_label":"exact category","y_label":"none","value":null,"raw_value":"","basis":"printed/estimated/unreadable"}]}.
value is a JSON number in the chart's displayed unit, or null if unreadable. Preserve
signs. Mark printed only if a numeric DATA label is actually printed beside the point,
not an axis tick. For an aggregate, include every underlying point in the requested
scope; complete=false when hidden/unlabelled points cannot be recovered. For chart_total,
include each required component, not an already added total. Never extrapolate dates.
The lookup labels are a request, not evidence. Return only JSON.
The three lookup arguments omit the first image_id argument from the signature.
''' + "Signature: " + signature + "\nLookup: " + json.dumps(lookup, ensure_ascii=False)
        return self._read(path, prompt)

    def close(self):
        if self.backend is not None:
            self.backend.close()
            self.backend = None
