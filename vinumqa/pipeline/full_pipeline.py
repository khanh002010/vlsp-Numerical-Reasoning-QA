"""Structure-first CV/NLP orchestration with bounded requests and exclusive GPU ownership."""
from vinumqa.data.context import build_inline_context
from vinumqa.cv_module.structure import validate_request
from vinumqa.cv_module.structure_store import ChartStructureStore
from vinumqa.nlp_module.inference.evidence_validation import validate_evidence
from vinumqa.utils.dsl_parser import parse_program, execute_program


class ViNumQAPipeline:
    def __init__(self, cv_model_id="Qwen/Qwen2-VL-2B-Instruct",
                 nlp_model_id="Qwen/Qwen2.5-7B-Instruct", nlp_lora_weights=None,
                 use_reflection=True, structure_store="prepared/chart_structures.json",
                 max_cv_requests=2, store=None, nlp_factory=None):
        if max_cv_requests < 0: raise ValueError("max_cv_requests must be nonnegative")
        self.store = store if store is not None else ChartStructureStore(structure_store, cv_model_id)
        self.max_cv_requests = max_cv_requests
        self.nlp_pipeline = None
        self.use_reflection = use_reflection
        if nlp_factory is None:
            def nlp_factory():
                from vinumqa.nlp_module.pipeline import NLPPipeline
                return NLPPipeline(nlp_model_id, nlp_lora_weights, use_reflection=False)
        self.nlp_factory = nlp_factory

    def _close_nlp(self):
        if self.nlp_pipeline is not None:
            self.nlp_pipeline.close()
            self.nlp_pipeline = None

    def _nlp(self):
        self.store.close()
        if self.nlp_pipeline is None: self.nlp_pipeline = self.nlp_factory()
        return self.nlp_pipeline

    def close(self):
        self._close_nlp()
        self.store.close()

    def run(self, text_segments, tables_dict, image_dict, question,
            execute=False, allow_estimates=False, table_resolvers=None):
        # A cache hit never loads a vision model or unloads an already loaded NLP.
        if any(not self.store.record(path) or self.store.record(path)["status"] != "ok"
               for path in image_dict.values()):
            self._close_nlp()
        try:
            charts = {key: self.store.get(path) for key, path in image_dict.items()}
        finally:
            self.store.close()
        history, feedback, requested = [], "", set()
        cv_count, correction_count = 0, 0
        max_corrections = 1 if self.use_reflection else 0
        sources = set(image_dict) | set(tables_dict)
        result = {"program": "", "valid": False}
        for _ in range(self.max_cv_requests + max_corrections + 1):
            context = build_inline_context(text_segments, tables_dict, image_dict, None, chart_structures=charts)
            nlp_context = context + ("\n\n### Validation feedback\n" + feedback if feedback else "")
            result = self._nlp().process(nlp_context, "", ", ".join(image_dict), question)
            if result.get("error"):
                result["valid"] = False
                break
            request = result.get("cv_request")
            if request is None:
                check = validate_evidence(result.get("program", ""), charts, sources,
                                          evidence=result.get("extracted_values", ""))
                history.append({"program": result.get("program", ""), "validation": check})
                if check["valid"]:
                    result.update(valid=True, validation_error="", evidence_validation=check)
                    break
                result.update(valid=False, validation_error="; ".join(check["errors"]))
                feedback = result["validation_error"]
                request = next((r for r in check["cv_requests"] if str(r) not in requested), None)
            if request is not None and cv_count < self.max_cv_requests:
                try:
                    request = validate_request(request, image_dict)
                    if str(request) in requested: raise ValueError("This inspection was already requested")
                    requested.add(str(request))
                    cv_count += 1
                    path = image_dict[request["image_id"]]
                    if not self.store.has_request(path, "inspect", request): self._close_nlp()
                    try:
                        charts[request["image_id"]] = self.store.inspect(path, request)
                    finally:
                        self.store.close()
                    history.append({"cv_request": request, "status": "read"})
                    feedback += "\nUpdated image structure is now in context. Re-read the labels; do not repeat the request."
                except Exception as error:
                    feedback += "\nCV inspection unavailable: " + str(error)
                    history.append({"cv_request": request, "error": str(error)})
                continue
            if correction_count < max_corrections:
                correction_count += 1
                feedback += "\nNo further CV calls available. Correct the program using verified labels, or report missing evidence."
                continue
            result.update(valid=False, error="Program validation or CV request budget exhausted")
            break
        else:
            result.update(valid=False, error="Bounded generation loop exhausted")
        result["structure_trace"] = history
        result["cv_requests_used"] = cv_count
        answer = None
        if execute and result.get("valid"):
            # The original program remains intact even if numeric extraction fails.
            self._close_nlp()
            from vinumqa.cv_module.chart_lookup import resolve_chart
            resolvers = {key: (lambda op, a, b, c, path=path:
                         resolve_chart(self.store, path, op, a, b, c, allow_estimates))
                         for key, path in image_dict.items()}
            try:
                steps = parse_program(result["program"])
                values = execute_program(steps, tables=table_resolvers, charts=resolvers)
                answer = values[steps[-1].step_id]
            except Exception as error:
                result["execution_error"] = str(error)
            finally:
                self.store.close()
        return {"inline_context": context, "chart_structures": charts,
                "reasoning_result": result, "answer": answer}
