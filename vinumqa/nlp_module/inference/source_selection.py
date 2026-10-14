"""Short, untrusted source plans; actual programs still require evidence validation."""
import json
from vinumqa.cv_module.structure import json_object

VERSION = 'source-plan-v1'


def selection_prompt(context, question, images):
    return '''Select evidence for the question. Do not calculate an answer or write a program.
Return only JSON: {"task":"short mathematical task", "sources":[{"id":"Image 1 or Table 1 or Text", "series":"exact visible name or empty", "labels":["required period/category"], "quote":"short verbatim evidence from context"}]}.
Choose the correct report, period, units and series. Preserve forecast/half-year/quarter qualifiers.
Do not turn comparison of numerical magnitudes into a different question. Use Text for prose evidence.
For missing chart evidence you may instead return {"cv_request":{"image_id":"Image 1","kind":"inspect","region":"legend","series":""}}.
Available images: ''' + images + '\n### Context\n' + context + '\n### Question\n' + question + '\n### Source selection\n'


def parse_selection(text):
    return json_object(text)


def validate_selection(plan, sample, charts, context):
    errors = []
    if not isinstance(plan, dict): return ['Source plan must be an object']
    if not isinstance(plan.get('task'), str) or not plan['task'].strip(): errors.append('Missing mathematical task')
    sources = plan.get('sources')
    if not isinstance(sources, list) or not sources or len(sources) > 12:
        return errors + ['Source plan requires 1 to 12 evidence entries']
    known = set(sample.get('images', {})) | set(sample.get('tables', {})) | {'Text'}
    normalized_context = ' '.join(context.split())
    for source in sources:
        if not isinstance(source, dict):
            errors.append('Invalid source entry'); continue
        name = source.get('id')
        if not isinstance(name, str) or name not in known:
            errors.append(f'Unknown source: {name}'); continue
        quote = source.get('quote')
        if not isinstance(quote, str) or not quote.strip() or ' '.join(quote.split()) not in normalized_context:
            errors.append(f'{name}: evidence quote is not verbatim')
        labels = source.get('labels')
        if not isinstance(labels, list) or any(not isinstance(x, str) or not x.strip() for x in labels):
            errors.append(f'{name}: invalid requested labels')
        series = source.get('series')
        if not isinstance(series, str): errors.append(f'{name}: invalid series')
        elif name in sample.get('images', {}):
            chart = charts.get(name)
            if chart is None: errors.append(f'{name}: missing chart structure')
            elif series not in {s['name'] for s in chart.get('series', [])}:
                errors.append(f'{name}: series absent from this image: {series}')
    return errors


def plan_feedback(plan, errors):
    if errors:
        return '\n### Source selection failed checks\n' + json.dumps(errors, ensure_ascii=False) + '\nSelect evidence again from the full original context while generating the program. Never invent missing facts.\n'
    return '\n### Proposed source plan (not ground truth)\n' + json.dumps(plan, ensure_ascii=False) + '\nVerify this plan against the question and original context; correct it if necessary. Keep chart_* operations.\n'
