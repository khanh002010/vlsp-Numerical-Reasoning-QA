"""Independent layout observation, then label reads anchored to image positions."""
import json
from vinumqa.cv_module.structure import validate_box, validate_structure
from vinumqa.cv_module.structure_grounding import positioned_labels, validate_layout, REVIEW_RECIPE


def read_reviewed(reader, path):
    reader.last_generation = {'attempts': [], 'recipe': REVIEW_RECIPE}
    meta = reader._read(path, '''Inspect the FULL chart before transcribing labels. Return only JSON:
{"title":"exact printed title or empty", "kind":"unknown", "series_source":"unknown",
 "chart_unit":"exact printed common unit or empty",
 "orientation":"unknown", "x_axis_type":"unknown", "y_axis_type":"unknown"}.
kind: line/bar/pie/mixed/table/unknown. series_source: legend/title/unknown; title only
when ONE plotted series has no legend and its title names that series.
orientation: vertical (upright bars or ordinary line plot), horizontal (bars extend
left/right), matrix, none (pie), unknown. Each axis type: numerical/categorical/time/none/unknown.
Look at the PLOTTED MARKS and numerical scale positions, NOT the legend. A legend
below the chart is not an axis. Rotated/multiline text below upright bars belongs to X.
For a vertical bar/line plot with a numerical Y scale use y_axis_type=numerical.
Copy all title words, accents and units exactly. Do not translate units or guess them.
chart_unit is only a common unit explicitly printed for ALL series; empty for mixed units.
Do not transcribe labels, numerical data points or programs.''', budgets=(512,), reset=False, phase='review_layout')
    layout = validate_layout(meta)
    if layout['y_axis_type'] == 'unknown' or layout['x_axis_type'] == 'unknown':
        raise ValueError('Axis roles not verified; inspect the full image before accepting labels')
    if not isinstance(meta.get('title'), str) or not isinstance(meta.get('chart_unit', ''), str):
        raise ValueError('Layout title/unit must be strings')
    legend = reader._read_part(path, 'legend', '''Read the full title and each colored legend entry separately.
Return ONLY JSON: {"title":"", "kind":"unknown", "series":[], "series_complete":false,"uncertain":[]}.
Each series: {"name":"exact visible name","color":"","axis":"none","unit":""}.
Copy the complete printed title, even when it is in a heading/banner above the plot.
Join multiline legend text inside its OWN entry. Do not confuse legend with X/Y labels.
Copy units exactly in their original language; leave empty if absent. Do not invent color codes.
For a single series without a legend use the full printed title, not a guessed short name.
kind: line/bar/pie/mixed/table/unknown; axis: left/right/none. No numeric data values.''')
    chart = {**legend, 'title': meta['title'].strip(), 'kind': meta.get('kind', legend['kind']),
             'layout': layout, 'series_source': meta.get('series_source', 'unknown'),
             'x_labels': [], 'y_labels': [], 'x_labels_complete': False,
             'x_order_known': False, 'regions': {}}
    if chart['series_source'] == 'title' and len(chart['series']) == 1 and chart['title']:
        # The separate observation explicitly identifies title as the sole series name.
        chart['series'][0]['name'] = chart['title']
    if meta.get('chart_unit') and all(s.get('axis', 'none') != 'right' for s in chart['series']):
        for s in chart['series']:
            if not s.get('unit'): s['unit'] = meta['chart_unit'].strip()
    for axis in ('x', 'y'):
        axis_type = layout[axis + '_axis_type']
        if axis_type not in {'categorical', 'time'}:
            continue  # Numeric ticks never become category labels.
        value = reader._read(path, '''Read ONLY the ''' + axis.upper() + ''' category/time tick labels.
Return compact JSON: {"items":[{"box":[0.1,0.8,0.2,0.95],"lines":["exact first line","exact second line"]}],"complete":false}.
The box is the TEXT LABEL bounds, normalized 0..1 relative to this full image.
One item per plotted category/tick position; all its printed lines belong in that ONE item.
For year + occurrence labels, keep year and (Lần ...) under the SAME column/mark.
Never move a child line into an adjacent year. Never omit duplicate years: distinguish
them by their own printed qualifiers. Do not merge neighboring category positions.
For rotated labels, one item contains the full rotated label. Copy printed ticks only,
never interpolate dates. complete=true only if labels enumerate every category;
use false for sparse time ticks. No legend names, numeric data labels or scale ticks.
The template numbers are examples, not coordinates to copy.''', budgets=(4096,), reset=False, phase='positioned_' + axis)
        labels, items = positioned_labels(value, axis)
        # Verify multiline labels at their own column/row; do not ask the model
        # to reassign qualifiers while looking at every neighboring label.
        for item in items:
            if len(item['lines']) <= 1: continue
            l, t, r, b = item['box']
            crop = validate_box([max(0, l-.003), max(0, t-.008), min(1, r+.003), min(1, b+.008)])
            checked = reader._read(path, 'This crop is ONE axis label at ONE category position. '
                'Transcribe ALL its printed lines in reading order. Do not add a year, occurrence or neighboring label. '
                'Return ONLY {"lines":["exact printed line"],"readable":true}; '
                'if cut/unreadable return {"lines":[],"readable":false}.', crop,
                budgets=(256,), reset=False, phase='verify_multiline_' + axis)
            lines = checked.get('lines')
            if checked.get('readable') is not True or not isinstance(lines, list) or not lines or any(not isinstance(s,str) or not s.strip() for s in lines):
                raise ValueError('Multiline label not readable in its own crop')
            item['lines'] = lines
        labels, items = positioned_labels({'items': items, 'complete': value['complete']}, axis)
        chart[axis + '_labels'] = labels
        if axis == 'x':
            chart['x_labels_complete'] = value['complete']
            chart['x_order_known'] = True
        reader.last_generation[axis + '_label_observations'] = items
    reader.last_generation['layout_observation'] = meta
    return validate_structure(chart)
