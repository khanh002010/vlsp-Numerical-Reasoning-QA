"""GPU adapter for bounded structure reads and optional numerical evidence reads."""
import json
from pathlib import Path
from PIL import Image
from vinumqa.cv_module.structure import STRUCTURE_PROMPT, STRUCTURE_RETRY_PROMPT, json_object, validate_box
from vinumqa.cv_module.structure_output import parse_structure_output, json_repetition_reason
from vinumqa.cv_module.structure_parts import validate_part, normalize_locator_box


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
            attempt = {"budget": budget, "phase": phase, "box": box, "prompt": prompt,
                       **{k: result[k] for k in ("text", "tokens", "eos", "seconds", "stop_reason")}}
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
             'axis must be left, right or none; for pie use none. '
             'Do not invent a title: if no title is printed, use an empty string. Do not translate names. '
             'Join ALL lines of each legend entry. Distinguish neighboring colored entries. '
             'Never repeat a name across different colors or invent suffixes. '
             'If there is no legend, use a printed series title only when unambiguous. '
             'If a series name is unreadable, return series_complete=false and explain in uncertain.'),
            ("x_axis", {"x_labels": [], "x_labels_complete": False},
             'Read ONLY X category/time labels, in visual order. Copy visible text exactly. '
             'For grouped categories include the visible parent with each child to distinguish them. '
             'Never invent dates, omit duplicate positions, or add artificial numbering. '
             'Read rotated labels individually. Do not enumerate a calendar or continue a quarter cycle. '
             'For quarter/year tiers, copy each printed quarter together with its printed year. '
             'Sparse ticks or unreadable labels mean x_labels_complete=false.'),
            ("y_axis", {"y_axis_type": "unknown", "y_labels": []},
             'Read ONLY categorical Y labels (horizontal bar row names). '
             'First choose y_axis_type: numerical, categorical, none, unknown. '
             'A legend beside colored marks is NOT a Y axis. A percent sign is a UNIT, not a category. '
             'For a numerical Y axis return y_labels: [] -- percentages, parentheses, minus signs '
             'and numerical scale ticks are NOT category labels. '
             'For horizontal bars copy full row names, not bar values. Do not list data points.'),
        ]
        merged = {"regions": {}, "uncertain": []}
        for phase, template, instruction in fields:
            prompt = ('Read the actual image. Return ONLY compact JSON, no Markdown. '
                      'Do not guess unreadable text. Template: '
                      + json.dumps({**template, "uncertain": []}) + '\n' + instruction + focus)
            value = self._read_part(path, phase, prompt, box)
            merged["uncertain"].extend(value.pop("uncertain"))
            merged.update(value)
        merged["uncertain"] = list(dict.fromkeys(merged["uncertain"]))
        result, repairs = parse_structure_output(json.dumps(merged, ensure_ascii=False))
        self.last_generation["focused_repairs"] = repairs
        self.last_generation["recovery_version"] = "localized-fields-v3"
        return result

    def _read_part(self, path, phase, prompt, box=None):
        try:
            value = self._read(path, prompt, box, budgets=(1024,),
                               reset=False, phase="focused_" + phase)
            result, repairs = validate_part(phase, value)
        except ValueError as error:
            self.last_generation.setdefault("part_errors", {})[phase] = str(error)
            if phase == "y_axis":
                # Classification is a separate visual observation. Do not ask a
                # numerical-axis classifier to transcribe a category list at all.
                try:
                    axis = self._read(path,
                        'Is the vertical Y axis a numerical scale, category names, or absent? '
                        'Percentages and negative numbers are numerical. Ignore the legend. '
                        'Return ONE JSON field: {"y_axis_type":"numerical"}, '
                        'or categorical, none, unknown. No labels or explanation.',
                        box, budgets=(128,), reset=False, phase="classify_y_axis")
                    axis_type = axis.get("y_axis_type")
                    if axis_type in {"numerical", "none"}:
                        self.last_generation["y_axis_classification"] = axis_type
                        return {"y_labels": [], "uncertain": [
                            "Y categories omitted after separate visual classification: " + axis_type]}
                except ValueError as classification_error:
                    self.last_generation["y_axis_classification_error"] = str(classification_error)
            # Locate from pixels, never assume the legend is at the top or the
            # X axis at the bottom (negative bars often cross in mid-image).
            locator = ('Locate the ' + phase + ' in the FULL image. Return ONLY JSON '
                       '{"box":[left,top,right,bottom]}. Coordinates normalized 0..1. '
                       'Include all visible labels, rotated text and parent/year tiers. '
                       'For legend include all colored keys and their complete names. '
                       'For y_axis include the plotted area and left/right scales so axis type is visible. '
                       'Do not transcribe text. If uncertain return {"box":null}.')
            try:
                located = self._read(path, locator, budgets=(256,), reset=False, phase="locate_" + phase)
                crop = normalize_locator_box(located.get("box"))
            except ValueError as location_error:
                self.last_generation.setdefault("locator_errors", {})[phase] = str(location_error)
                # Small-model coordinates often degenerate into nested objects or
                # long scene descriptions. One coarse choice needs no coordinates.
                coarse = self._read(path,
                    'Where are the ' + phase + ' labels in the FULL image? '
                    'Return only {"region":"top"} or {"region":"middle"} '
                    'or {"region":"bottom"} or {"region":"full"}. '
                    'Choose full if labels span multiple regions or you are unsure. '
                    'No coordinates, transcription or explanation.',
                    budgets=(128,), reset=False, phase="locate_coarse_" + phase)
                regions = {"top": [0, 0, 1, 0.55], "middle": [0, 0.2, 1, 0.8],
                           "bottom": [0, 0.45, 1, 1], "full": [0, 0, 1, 1]}
                region = coarse.get("region")
                if not isinstance(region, str) or region not in regions:
                    raise ValueError("Locator could not identify a valid coarse region")
                crop = regions[region]
                self.last_generation.setdefault("coarse_regions", {})[phase] = region
            # Inspection requests may already be cropped; keep the new crop inside
            # the authorized observation so it cannot be mistaken for full coverage.
            if box is not None:
                crop = validate_box([max(crop[0], box[0]), max(crop[1], box[1]),
                                     min(crop[2], box[2]), min(crop[3], box[3])])
            print(f"[Structure] re-read {phase} crop={crop}: {error}", flush=True)
            value = self._read(path, prompt + '\nThis is a crop: report only visible text. '
                               'Set completeness flags false. Close JSON after the last printed label. '
                               'Previous validation error: ' + str(error)[:200], crop,
                               budgets=(2048,), reset=False, phase="crop_" + phase)
            result, repairs = validate_part(phase, value)
            if phase == "legend":
                result["series_complete"] = False
            elif phase == "x_axis":
                result["x_labels_complete"] = False
                result["x_order_known"] = False
            result["uncertain"].append("Recovered " + phase + " from a crop; global coverage unverified")
        self.last_generation.setdefault("part_repairs", {})[phase] = repairs
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
