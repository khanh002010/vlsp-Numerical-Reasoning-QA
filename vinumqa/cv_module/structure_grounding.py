"""Pixel-observation checks and conservative, reproducible series aliases."""
import re
import unicodedata

REVIEW_RECIPE = 'region-evidence-v5-explicit-coordinates'


def key(value):
    return ' '.join(unicodedata.normalize('NFC', value).split()).casefold()


def validate_layout(value):
    if not isinstance(value, dict):
        raise ValueError('Layout must be an object')
    orientation = value.get('orientation')
    if orientation not in {'vertical', 'horizontal', 'matrix', 'none', 'unknown'}:
        raise ValueError('Missing/invalid plot orientation')
    result = {'orientation': orientation}
    for field in ('x_axis_type', 'y_axis_type'):
        if value.get(field) not in {'numerical', 'categorical', 'time', 'none', 'unknown'}:
            raise ValueError('Missing/invalid ' + field)
        result[field] = value[field]
    if orientation == 'vertical' and result['y_axis_type'] == 'categorical':
        raise ValueError('Vertical bars cannot use legend entries as categorical Y rows')
    if orientation == 'horizontal' and result['x_axis_type'] == 'categorical':
        raise ValueError('Horizontal bars cannot use row names as X categories')
    return result


def positioned_labels(value, axis):
    """Join lines ONLY inside one observed label box; never deduplicate positions."""
    from vinumqa.cv_module.structure import validate_box
    if axis not in {'x', 'y'} or not isinstance(value, dict):
        raise ValueError('Invalid positioned label observation')
    items = value.get('items')
    if not isinstance(items, list) or not isinstance(value.get('complete'), bool):
        raise ValueError('Positioned labels need items and a completeness flag')
    result = []
    for item in items:
        if not isinstance(item, dict): raise ValueError('Malformed label item')
        box = validate_box(item.get('box'))
        lines = item.get('lines')
        if not isinstance(lines, list) or not lines or any(not isinstance(s, str) or not s.strip() for s in lines):
            raise ValueError('Each label box needs its exact nonempty text lines')
        result.append({'box': box, 'lines': [s.strip() for s in lines]})
    dim = 0 if axis == 'x' else 1
    result.sort(key=lambda r: r['box'][dim] + r['box'][dim+2])
    for a, b in zip(result, result[1:]):
        center_a = (a['box'][dim] + a['box'][dim+2]) / 2
        center_b = (b['box'][dim] + b['box'][dim+2]) / 2
        if center_b - center_a < 0.002:
            raise ValueError('Overlapping label positions: re-read parent/child lines in one box')
    labels = [' '.join(r['lines']) for r in result]
    if len({key(s) for s in labels}) != len(labels):
        raise ValueError('Repeated labels at different positions; missing multiline qualifiers')
    return labels, result


def title_alias(title):
    """Strip ONLY a trailing printed period/unit suffix, never a metric modifier."""
    text = title.strip()
    units = r'(?:VND/kWh|VNĐ/kWh|VND|VNĐ|USD|%|nghìn tỷ|tỷ đồng|triệu đồng)'
    text = re.sub(r'\s*\(' + units + r'\)\s*$', '', text, flags=re.I).strip()
    text = re.sub(r'\s+từ\s+(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\s*$', '', text, flags=re.I).strip()
    return text if text and text != title.strip() else None


def derived_series_aliases(chart):
    """A title-derived alias is allowed only for a verified single-series title."""
    series = chart.get('series', [])
    if chart.get('series_source') != 'title' or len(series) != 1:
        return []
    title = chart.get('title', '')
    if not title or key(series[0]['name']) != key(title):
        return []
    alias = title_alias(title)
    if not alias: return []
    return [{'alias': alias, 'target': series[0]['name'], 'basis': 'single-series-title-suffix', 'evidence': title}]


def resolve_series(label, chart):
    names = [s['name'] for s in chart['series']]
    matches = [n for n in names if key(n) == key(label)]
    if len(matches) == 1: return matches[0]
    matches = {a['target'] for a in derived_series_aliases(chart) if key(a['alias']) == key(label)}
    return next(iter(matches)) if len(matches) == 1 else None


def check_axis_labels(chart):
    """Require another observation on conflicting roles; don't erase by similarity."""
    layout = chart.get('layout')
    if not layout: return
    validate_layout(layout)
    ys = chart.get('y_labels', [])
    if layout['y_axis_type'] in {'numerical', 'none'} and ys:
        raise ValueError('Numerical/absent Y axis cannot have categorical y_labels')
    if layout['y_axis_type'] in {'categorical', 'time'}:
        names = {key(s['name']) for s in chart.get('series', [])}
        if ys and names and {key(y) for y in ys} == names:
            raise ValueError('Y labels duplicate the legend; require a separate axis observation')
        if ys and {key(y) for y in ys} == {key(x) for x in chart.get('x_labels', [])} and layout['orientation'] != 'matrix':
            raise ValueError('X and Y categories are identical in a non-matrix plot')
