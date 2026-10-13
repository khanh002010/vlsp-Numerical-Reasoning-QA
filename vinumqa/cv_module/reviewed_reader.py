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
    from vinumqa.cv_module.grounded_review import read_chart
    return read_chart(reader, path)
