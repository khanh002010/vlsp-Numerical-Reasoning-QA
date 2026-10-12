"""Independent layout observation, then label reads anchored to image positions."""
import json
import re
from vinumqa.cv_module.structure import validate_structure
from vinumqa.cv_module.structure_grounding import positioned_labels, validate_layout, REVIEW_RECIPE


def checked_read(reader, path, prompt, *, validator, phase, budgets):
    """One fresh visual retry for invalid schema/semantics, retaining both attempts."""
    for attempt in range(2):
        try:
            value = reader._read(path, prompt, budgets=budgets, reset=False,
                                 phase=phase if attempt == 0 else phase + '_retry')
            validator(value)
            return value
        except ValueError as error:
            reader.last_generation.setdefault('review_errors', []).append(
                {'phase': phase, 'attempt': attempt + 1, 'error': str(error)})
            if attempt: raise
            print(f'[Structure] {phase}: re-reading pixels after validation error: {error}', flush=True)
            prompt += ('\nThe previous read failed validation: ' + str(error)[:250] +
                       '\nRead the image again independently. Return ONE JSON OBJECT using the exact '
                       'schema above, never a bare array or a list of strings. Do not invent missing '
                       'coordinates, labels or completeness. No Markdown or explanation.')


def checked_layout(meta):
    layout = validate_layout(meta)
    if 'unknown' in layout.values():
        raise ValueError('Axis roles/orientation not verified; inspect marks and scale positions again')
    if not isinstance(meta.get('title'), str) or not isinstance(meta.get('chart_unit', ''), str):
        raise ValueError('Layout title/unit must be strings')


def validate_metadata(value):
    if not isinstance(value, dict) or not isinstance(value.get('title'), str):
        raise ValueError('Metadata must include a title string')


def validate_axis_roles(value):
    if not isinstance(value, dict) or any(value.get(k) not in {'numerical','time','categorical','none'}
                                        for k in ('x_axis_type','y_axis_type')):
        raise ValueError('Both axis roles must be observed')


def axis_groups(value, series):
    if not isinstance(value, dict) or not isinstance(value.get('complete'), bool):
        raise ValueError('Axis read requires groups and explicit completeness')
    groups = value.get('groups')
    if not isinstance(groups, list) or not groups:
        raise ValueError('No readable category groups')
    names = {' '.join(s['name'].split()).casefold() for s in series}
    labels = []
    for lines in groups:
        if not isinstance(lines, list) or not lines or any(not isinstance(s,str) or not s.strip() for s in lines):
            raise ValueError('Each category needs its own nonempty list of printed lines')
        text = ' '.join(s.strip() for s in lines)
        if len(re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', text)) > 1 or len(re.findall(r'\b(?:19|20)\d{2}\b',text)) > 1:
            raise ValueError('Multiple dates/years merged into one category; separate tick positions')
        if any(' '.join(s.split()).casefold() in names for s in lines):
            raise ValueError('Legend entry mixed into category lines')
        labels.append(text)
    if len(set(labels)) != len(labels):
        raise ValueError('Duplicate categories; re-read qualifiers at each position')
    return labels


def read_axis_labels(reader, path, axis, series):
    prompt = ('Copy ONLY printed ' + axis.upper() + ' category/time labels in visual order. '
        'Return {"groups":[],"complete":false}. Each groups item is a list of printed lines '
        'at ONE tick position. Adjacent dates are separate groups, not lines of one group. '
        'For multiline years copy only the occurrence qualifier printed under that SAME year. '
        'Never invent qualifiers or extend a calendar. Ignore legend, title, values and scale ticks. '
        'No boxes or coordinates. Empty groups means unreadable. complete=false for sparse ticks. '
        'Copy rotated labels individually. Do not interpolate dates.')
    observations = []
    for phase, instruction in [('axis_text_', ''), ('axis_verify_',
            '\nCheck every tick from the first to the last directly in the image; omit no printed tick.')]:
        value = checked_read(reader,path,prompt+instruction,validator=lambda v: axis_groups(v,series),
                             phase=phase+axis,budgets=(2048,))
        observations.append(value)
    reader.last_generation[axis+'_text_observations'] = observations
    first, second = [axis_groups(v,series) for v in observations]
    if first != second:
        raise ValueError('Independent axis transcriptions disagree; visual review required')
    return first, all(v['complete'] for v in observations)


def read_reviewed(reader, path):
    reader.last_generation = {'attempts': [], 'recipe': REVIEW_RECIPE}
    meta = checked_read(reader, path, '''Inspect the FULL chart before transcribing labels. Return only JSON:
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
Orientation describes bar direction, NOT the wide shape of the image or text direction.
Bars rising upward from a baseline are vertical even in a wide landscape image.
Horizontal bars extend sideways: X is the numerical scale and Y contains row names.
Copy all title words, accents and units exactly. Do not translate units or guess them.
chart_unit is only a common unit explicitly printed for ALL series; empty for mixed units.
Do not transcribe labels, numerical data points or programs.''', budgets=(512,), validator=validate_metadata, phase='review_layout')
    roles = checked_read(reader, path,
        'Inspect only the axes of the plotted data, ignoring title and legend. '
        'Return {"x_axis_type":"unknown","y_axis_type":"unknown"}. '
        'Use numerical for a numeric measurement scale, time for dates, categorical for category names, '
        'none for absent axes. Do not describe image orientation. No labels.',
        validator=validate_axis_roles, phase='axis_roles', budgets=(128,))
    meta.update(roles)
    meta['orientation'] = ('vertical' if roles['y_axis_type']=='numerical' else
                           'horizontal' if roles['x_axis_type']=='numerical' else
                           'none' if set(roles.values())=={'none'} else 'matrix')
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
    title_read = checked_read(reader,path,
        'Read ONLY the standalone chart heading, not colored legend entries. '
        'Return {"title":""}. If no separate heading is printed, title must be empty. '
        'Never concatenate legend names into a title. Preserve the full printed heading and unit.',
        validator=validate_metadata,phase='title_only',budgets=(256,))
    chart['title'] = title_read['title'].strip()
    for entry in chart['series']:
        unit = entry.get('unit','').strip()
        if unit.startswith('(') and unit.endswith(')'):
            entry['unit'] = unit[1:-1].strip()
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
        labels, complete = read_axis_labels(reader, path, axis, chart['series'])
        chart[axis + '_labels'] = labels
        if axis == 'x':
            chart['x_labels_complete'] = complete
            chart['x_order_known'] = True
    reader.last_generation['layout_observation'] = meta
    return validate_structure(chart)
