"""GPU adapter for bounded structure reads and optional numerical evidence reads."""
import json
from pathlib import Path
from PIL import Image
from vinumqa.cv_module.structure import STRUCTURE_PROMPT, STRUCTURE_RETRY_PROMPT, json_object, validate_box
from vinumqa.cv_module.structure_output import parse_structure_output, json_repetition_reason


class ChartStructureReader:
    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct"):
        from vinumqa.cv_module.chart_to_table.extract_table import ChartToTableExtractor
        self.backend = ChartToTableExtractor(model_id=model_id)
        self.backend.generation_config.max_time = 120
        self.backend.repetition_check = json_repetition_reason
        self.last_generation = {}

    def _read(self, path, prompt, box=None, *, structure=False, budgets=(1024, 2048), reset=True, phase="primary"):
        if reset: self.last_generation = {"attempts": []}
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
        for budget in budgets:
            print(f"[Structure] {Path(path).name}: budget={budget}, crop={box is not None}, phase={phase}", flush=True)
            result = self.backend.generate_once(inputs, budget)
            attempt = {"budget": budget, "phase": phase, **{k: result[k] for k in ("text", "tokens", "eos", "seconds", "stop_reason")}}
            self.last_generation["attempts"].append(attempt)
            print(f"[Structure] tokens={result['tokens']}, stop={result['stop_reason']}, seconds={result['seconds']}", flush=True)
            reason = json_repetition_reason(result["text"])
            if result["stop_reason"] == "repetition" or reason:
                attempt["quality_error"] = reason or "Repetitive structure output"
                raise ValueError(attempt["quality_error"])
            if result["eos"]:
                try:
                    if structure:
                        value, attempt["repairs"] = parse_structure_output(result["text"])
                        return value
                    return json_object(result["text"])
                except ValueError as error:
                    attempt["quality_error"] = str(error)
                    raise
            if len(result["token_ids"]) < budget: break  # Time limit; do not start another long retry.
        raise ValueError("Structure read incomplete at the bounded token/time limit")

    def _structure(self, path, focus="", box=None):
        try:
            return self._read(path, STRUCTURE_PROMPT + focus, box, structure=True)
        except ValueError as error:
            self.last_generation["retry_reason"] = str(error)
            # One different, compact prompt. Never continue a failed/truncated JSON.
            prompt = STRUCTURE_RETRY_PROMPT + focus + "\nValidation error: " + str(error)[:250]
            try:
                return self._read(path, prompt, box, structure=True, budgets=(2048,), reset=False, phase="retry")
            except ValueError as retry_error:
                print(f"[Structure] focused recovery: {retry_error}", flush=True)
                return self._read_parts(path, focus, box)

    def _read_parts(self, path, focus="", box=None):
        """Reduce generation length by reading independent fields from actual pixels.

        Never salvage a truncated JSON or invent names to pass the validator.
        Every part must finish, and the combined structure must pass validation.
        """
        fields = [
            ("legend", {"title": "", "kind": "unknown", "series": [], "series_complete": False},
             'Read ONLY title and legend. Choose kind: line, bar, pie, mixed, table, unknown. '
             'Each series: {"name":"exact full visible name","color":"","axis":"none","unit":""}. '
             'Join ALL lines of each legend entry. Distinguish neighboring colored entries. '
             'Never repeat a name across different colors or invent suffixes. '
             'If there is no legend, use a printed series title only when unambiguous. '
             'If a series name is unreadable, return series_complete=false and explain in uncertain.'),
            ("x_axis", {"x_labels": [], "x_labels_complete": False},
             'Read ONLY X category/time labels, in visual order. Copy visible text exactly. '
             'For grouped categories include the visible parent with each child to distinguish them. '
             'Never invent dates, omit duplicate positions, or add artificial numbering. '
             'Sparse ticks or unreadable labels mean x_labels_complete=false.'),
            ("y_axis", {"y_labels": []},
             'Read ONLY categorical Y labels (horizontal bar row names). '
             'For a numerical Y axis return y_labels: [] -- percentages, parentheses, minus signs '
             'and numerical scale ticks are NOT category labels. '
             'For horizontal bars copy full row names, not bar values. Do not list data points.'),
        ]
        merged = {"regions": {}, "uncertain": []}
        for phase, template, instruction in fields:
            prompt = ('Read the actual image. Return ONLY compact JSON, no Markdown. '
                      'Do not guess unreadable text. Template: '
                      + json.dumps({**template, "uncertain": []}) + '\n' + instruction + focus)
            value = self._read(path, prompt, box, budgets=(1024, 2048),
                               reset=False, phase="focused_" + phase)
            for key in template:
                if key not in value:
                    if key.endswith("_complete"):
                        value[key] = False
                    else:
                        raise ValueError("Focused read missing " + key)
                merged[key] = value[key]
            uncertain = value.get("uncertain", [])
            if not isinstance(uncertain, list) or any(not isinstance(v, str) for v in uncertain):
                raise ValueError("Focused uncertainty must be a string list")
            merged["uncertain"].extend(v for v in uncertain if v.strip())
        merged["uncertain"] = list(dict.fromkeys(merged["uncertain"]))
        result, repairs = parse_structure_output(json.dumps(merged, ensure_ascii=False))
        self.last_generation["focused_repairs"] = repairs
        self.last_generation["recovery_version"] = "focused-fields-v1"
        return result

    def read_structure(self, path):
        return self._structure(path)

    def inspect(self, path, request, structure):
        box = request.get("box") or structure.get("regions", {}).get(request["region"])
        hint = json.dumps({"region": request["region"], "unverified_series_hint": request["series"]}, ensure_ascii=False)
        focus = "\nFocus request: " + hint + (
            "\nThe hint is NOT evidence: read the actual pixels, correct misspellings. "
            "If cropped, report only visible labels and set both completeness flags false.")
        return {"structure": self._structure(path, focus, box), "full_image": box is None}

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
