"""Independent layout observation, then label reads anchored to image positions."""
import json
import re
from vinumqa.cv_module.structure import validate_structure
from vinumqa.cv_module.structure_grounding import positioned_labels, validate_layout, REVIEW_RECIPE


def checked_read(reader, path, prompt, *, validator, phase, budgets, box=None):
    """One fresh visual retry for invalid schema/semantics, retaining both attempts."""
    for attempt in range(2):
        try:
            value = reader._read(path, prompt, box, budgets=budgets, reset=False,
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
    if isinstance(value, dict):
        for field in ('x_axis_type', 'y_axis_type'):
            if value.get(field) == 'numeric':
                value[field] = 'numerical'
    if not isinstance(value, dict) or any(value.get(k) not in {'numerical','time','categorical','none'}
                                        for k in ('x_axis_type','y_axis_type')):
        raise ValueError('Both axis roles must be observed')


def axis_groups(value, series):
    if isinstance(value,dict) and value.get('source_ambiguous') is True:
        raise ValueError('Source axis has repeated labels without a visible parent; cannot invent unique dates')
    if not isinstance(value, dict) or not isinstance(value.get('complete'), bool):
        raise ValueError('Axis read requires groups and explicit completeness')
    if 'labels' in value:
        if not isinstance(value['labels'], list) or any(not isinstance(s,str) for s in value['labels']):
            raise ValueError('labels must be a flat list of strings, one string per tick')
        groups = [[s] for s in value['labels']]
    else:
        groups = value.get('groups')
    if not isinstance(groups, list) or not groups:
        raise ValueError('No readable category groups')
    names = {' '.join(s['name'].split()).casefold() for s in series}
    labels = []
    for lines in groups:
        if not isinstance(lines, list) or not lines or any(not isinstance(s,str) or not s.strip() for s in lines):
            raise ValueError('Each category needs its own nonempty list of printed lines')
        # A group made entirely of full dates is a serialization grouping,
        # not a multiline label. Preserve every date and its observed order.
        if all(re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', s.strip()) for s in lines):
            labels.extend(s.strip() for s in lines)
            continue
        if len(lines) > 1:
            raise ValueError('Ambiguous grouped text; return flat labels with one complete string per tick')
        text = ' '.join(s.strip() for s in lines)
        if re.fullmatch(r'\(?\s*Lần\s+\d+\s*\)?', text, re.I):
            raise ValueError('Occurrence qualifier has no parent year; re-read that column')
        if len(re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', text)) > 1 or len(re.findall(r'\b(?:19|20)\d{2}\b',text)) > 1:
            raise ValueError('Multiple dates/years merged into one category; separate tick positions')
        if any(' '.join(s.split()).casefold() in names for s in lines):
            raise ValueError('Legend entry mixed into category lines')
        labels.append(text)
    if len(set(labels)) != len(labels):
        raise ValueError('Duplicate categories; re-read qualifiers at each position')
    return labels


def merge_axis_windows(windows):
    merged = list(windows[0])
    for labels in windows[1:]:
        matches = [n for n in range(1,min(len(merged),len(labels))+1) if merged[-n:]==labels[:n]]
        if not matches:
            raise ValueError('Axis crops have no exact shared boundary labels; cannot safely merge')
        merged.extend(labels[max(matches):])
    if len(set(merged)) != len(merged):
        raise ValueError('Duplicate labels across axis crops')
    return merged


def corroborated_candidate(candidates, windows):
    """Accept an existing transcription only when crop evidence covers every label.

    Never form a union, sort dates, or infer missing labels. All crop labels must
    appear in the candidate in the same order, with no conflicting extra labels.
    """
    accepted=[]
    for candidate in candidates:
        if not candidate or len(set(candidate)) != len(candidate): continue
        positions={label:i for i,label in enumerate(candidate)}
        if any(any(label not in positions for label in window) or
               any(positions[a]>=positions[b] for a,b in zip(window,window[1:]))
               for window in windows): continue
        if set(candidate) != {label for window in windows for label in window}: continue
        if candidate not in accepted: accepted.append(candidate)
    if len(accepted) != 1:
        raise ValueError('Crop evidence does not uniquely support a full axis transcription')
    return accepted[0]


def read_axis_windows(reader,path,axis,series,prompt,candidates=()):
    windows=[]
    # Fixed overlapping windows keep the entire orthogonal dimension, including
    # all printed lines; coordinates come from code, never generated by the model.
    for index,(lo,hi) in enumerate(((0,.45),(.25,.75),(.55,1))):
        box=[lo,0,hi,1] if axis=='x' else [0,lo,1,hi]
        value=checked_read(reader,path,prompt+
            '\nThis is a partial chart crop. Copy only fully visible labels. Exclude clipped boundary text. '
            'Keep repeated years when their printed qualifiers differ. Do not infer missing years or qualifiers.',
            validator=lambda v:axis_groups(v,series),phase=f'axis_crop_{axis}_{index}',budgets=(2048,),box=box)
        windows.append(axis_groups(value,series))
    reader.last_generation[axis+'_crop_labels']=windows
    try:
        labels=merge_axis_windows(windows)
    except ValueError:
        labels=corroborated_candidate(candidates,windows)
        reader.last_generation[axis+'_recovery']='full transcription corroborated by ordered crop evidence'
    return labels, False  # Coverage does not prove complete chart data.


def read_axis_labels(reader, path, axis, series):
    prompt = ('Copy ONLY printed ' + axis.upper() + ' category/time labels in visual order. '
        'Return {"labels":[],"complete":false}. labels is a FLAT array of strings. '
        'Each string is ONE complete tick label; join only printed lines belonging to that tick. '
        'Adjacent dates and neighboring industry names MUST be separate strings. No nested lists. '
        'For multiline years copy only the occurrence qualifier printed under that SAME year. '
        'For repeated quarters inspect the lower printed year row and attach its year to each child quarter. '
        'If identical dates genuinely repeat in the source with no visible distinguishing parent, '
        'return {"labels":[],"complete":false,"source_ambiguous":true}; never invent year increments. '
        'Never invent qualifiers or extend a calendar. Ignore legend, title, values and scale ticks. '
        'No boxes or coordinates. Empty labels means unreadable. complete=false for sparse ticks. '
        'Copy rotated labels individually. Do not interpolate dates.')
    observations = []
    for phase, instruction in [('axis_text_', ''), ('axis_verify_',
            '\nCheck every tick from the first to the last directly in the image; omit no printed tick.')]:
        try:
            value = checked_read(reader,path,prompt+instruction,validator=lambda v: axis_groups(v,series),
                                 phase=phase+axis,budgets=(2048,))
        except ValueError as error:
            reader.last_generation[axis+'_text_observations']=observations
            reader.last_generation[axis+'_crop_trigger']=str(error)
            if 'Source axis has repeated labels' in str(error):
                raise
            if 'Legend entry mixed' in str(error):
                raise  # Repair the series observation, not the category labels.
            recent_text=' '.join(a.get('text','') for a in reader.last_generation.get('attempts',[])[-2:])
            if axis=='x' and 'Duplicate categories' in str(error) and re.search(r'\b[1-4]Q\b|\bQ[1-4]\b',recent_text):
                tiered=checked_read(reader,path,
                    'Inspect ALL rows of X-axis text, including the lower parent-year row and divider lines. '
                    'Return {"labels":[],"complete":false}. One string per tick. '
                    'If quarters repeat under a printed year spanning several ticks, attach that printed '
                    'year to EACH child, e.g. quarter followed by year. Copy only the year visibly spanning '
                    'that group. Do not infer years from chronology or position. '
                    'If the source itself repeats dates with no distinguishing parent label, return '
                    '{"labels":[],"complete":false,"source_ambiguous":true}. '
                    'Do not repeat a calendar to fill space.',
                    validator=lambda v:axis_groups(v,series),phase='axis_parent_year',budgets=(1024,))
                observations.append(tiered)
                # Independent confirmation with the same parent-row instruction.
                confirm=checked_read(reader,path,
                    'Transcribe X ticks with their printed parent-year group. Read the bottom row and '
                    'group dividers. Return {"labels":[],"complete":false}, one string per tick, '
                    'quarter then printed year. Never invent missing years.',
                    validator=lambda v:axis_groups(v,series),phase='axis_parent_year_verify',budgets=(1024,))
                if axis_groups(tiered,series)==axis_groups(confirm,series):
                    reader.last_generation['x_parent_observations']=[tiered,confirm]
                    return axis_groups(tiered,series),False
            return read_axis_windows(reader,path,axis,series,prompt,
                                     [axis_groups(v,series) for v in observations])
        observations.append(value)
    reader.last_generation[axis+'_text_observations'] = observations
    first, second = [axis_groups(v,series) for v in observations]
    if first != second:
        return read_axis_windows(reader,path,axis,series,prompt,[first,second])
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
                           'none' if set(roles.values())=={'none'} else
                           'vertical' if roles['x_axis_type'] in {'time','categorical'} and roles['y_axis_type']=='none' and meta.get('kind') in {'bar','line','mixed'} else
                           'horizontal' if roles['y_axis_type'] in {'time','categorical'} and roles['x_axis_type']=='none' and meta.get('kind')=='bar' else
                           'matrix' if meta.get('kind')=='table' else 'unknown')
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
    if chart['title'] and chart['series_source']=='legend' and any(
            chart['title'].casefold()==s['name'].strip().casefold() for s in chart['series']):
        def heading_check(v):
            validate_metadata(v)
            if not isinstance(v.get('separate_heading'),bool):
                raise ValueError('Must confirm whether a separate heading is visible')
            if not v['separate_heading'] and v['title'].strip():
                raise ValueError('No standalone heading means empty title')
        title_read=checked_read(reader,path,
            'Check for a standalone heading separate from the legend. Colored line/square swatches '
            'identify legend entries, not headings. Return {"separate_heading":false,"title":""}. '
            'Set true only if a separate heading is visibly printed, and transcribe that heading.',
            validator=heading_check,phase='verify_heading',budgets=(256,))
        chart['title']=title_read['title'].strip()
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
        try:
            labels, complete = read_axis_labels(reader, path, axis, chart['series'])
        except ValueError as error:
            if 'Legend entry mixed' in str(error):
                repaired=reader._read_part(path,'legend',
                    'Re-read the actual legend: colored swatches/line samples beside text. '
                    'Company names or years printed under bars are X categories, NOT series. '
                    'Look below the X labels for a second band of multiline legend entries. '
                    'Join all lines belonging to EACH colored swatch. If no legend exists and a '
                    'single quantity is plotted, use the exact printed chart title as its series name. '
                    'Return {"title":"","kind":"unknown","series":[],"series_complete":false,"uncertain":[]}. '
                    'Each series has name, color, axis (left/right/none), unit. No guessed names.')
                chart['series']=repaired['series']
                chart['series_complete']=repaired['series_complete']
                chart['uncertain']=list(dict.fromkeys(chart.get('uncertain',[])+repaired.get('uncertain',[])))
                # Re-observe categories with repaired series; still reject collisions.
                try:
                    labels,complete=read_axis_labels(reader,path,axis,chart['series'])
                except ValueError as legend_error:
                    if 'Legend entry mixed' not in str(legend_error):raise
                    from vinumqa.cv_module.axis_band_recovery import recover_title_series
                    recover_title_series(reader,path,chart)
                    labels,complete=read_axis_labels(reader,path,axis,chart['series'])
                chart[axis+'_labels']=labels
                if axis=='x':
                    chart['x_labels_complete']=complete
                    chart['x_order_known']=True
                continue
            if axis=='x' and chart['kind']=='line':
                from vinumqa.cv_module.axis_band_recovery import recover_axis_band
                labels,complete=recover_axis_band(reader,path,chart)
                chart['x_labels']=labels
                chart['x_labels_complete']=complete
                chart['x_order_known']=bool(labels)
                continue
            if axis!='x' or chart['kind']!='bar' or layout['orientation']!='vertical' or len(chart['series'])!=1:
                raise
            from vinumqa.cv_module.bar_label_regions import read_bar_labels
            reader.last_generation['bar_recovery_trigger']=str(error)
            print('[Structure] Recovering labels below pixel-detected bars',flush=True)
            labels, complete = read_bar_labels(reader,path,chart['series'])
        chart[axis + '_labels'] = labels
        if axis == 'x':
            chart['x_labels_complete'] = complete
            chart['x_order_known'] = True
    reader.last_generation['layout_observation'] = meta
    return validate_structure(chart)
