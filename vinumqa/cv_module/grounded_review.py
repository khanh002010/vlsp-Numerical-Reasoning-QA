"""Region-backed chart reading. Locations are hypotheses until crop text agrees.

No image identifiers, answer programs or audit transcriptions enter these prompts.
"""
import json
import re

from vinumqa.cv_module.structure import validate_box, validate_structure
from vinumqa.cv_module.structure_grounding import key, REVIEW_RECIPE


def observe(reader, path, prompt, validator, phase, budget=1024, box=None):
    from vinumqa.cv_module.reviewed_reader import checked_read
    return checked_read(reader, path, prompt, validator=validator, phase=phase,
                        budgets=(budget,), box=box)


def text(value, field, empty=False):
    s = value.get(field)
    if not isinstance(s, str) or (not empty and not s.strip()):
        raise ValueError('Missing readable ' + field)
    return s.strip()


def boolean(value, field):
    if not isinstance(value.get(field), bool):
        raise ValueError('Missing boolean ' + field)
    return value[field]


def heading(value):
    if not isinstance(value, dict): raise ValueError('Heading must be an object')
    role = value.get('role')
    if role not in {'heading', 'absent'}: raise ValueError('Unit/legend/event is not a heading')
    title = text(value, 'title', empty=True)
    if role == 'absent':
        if title or value.get('box') is not None: raise ValueError('Absent heading must be empty')
    else:
        if not title: raise ValueError('Heading is empty')
        if re.fullmatch(r'\(?\s*(?:%|(?:nghìn\s+)?tỷ\s+(?:đồng|VND)|triệu\s+USD|GW|MW)\s*\)?', title, re.I):
            raise ValueError('Standalone measurement unit is not a chart heading')
        validate_box(value.get('box'))


def crop_text(reader, path, box, phase, instruction=''):
    def valid(v):
        if not isinstance(v, dict) or v.get('readable') is not True:
            raise ValueError('Crop text is clipped or unreadable')
        text(v, 'text')
    return observe(reader, path,
        'Transcribe the printed text in this crop exactly, preserving accents and symbols. '
        'Do not translate, paraphrase, add dates or infer missing words. '
        'Return {"text":"","readable":false}. Use readable=true only for fully visible text. '
        + instruction, valid, phase, 512, box)['text'].strip()


def read_heading(reader, path):
    value = observe(reader, path,
        'Locate the standalone chart heading/banner, including its subtitle if part of the heading. '
        'Unit at an axis, legend names, tick dates and event annotations with arrows are NOT headings. '
        'Do not invent a descriptive title for an untitled chart. Return '
        '{"role":"absent","title":"","box":null}, or role=heading with exact title and '
        'normalized box [left,top,right,bottom] enclosing only that heading. '
        'Include ALL lines of the heading, excluding separate axis-unit text.',
        heading, 'heading_location', 512)
    confirmation = observe(reader, path,
        'Check the full image for a separate chart heading/banner. Exclude axis units, '
        'legend, dates and event annotations. Return {"role":"absent","title":"","box":null} '
        'if none exists; otherwise role=heading, copy the complete heading and give its normalized box. '
        'Do not describe the chart yourself.', heading, 'heading_confirmation', 512)
    if key(value['title']) != key(confirmation['title']) or value['role'] != confirmation['role']:
        raise ValueError('Heading presence/text observations disagree')
    if value['role'] == 'absent': return ''
    actual = crop_text(reader, path, value['box'], 'heading_pixels')
    if key(actual) != key(value['title']):
        raise ValueError('Heading crop disagrees with full-image heading; re-localize')
    return actual


def inventory(v):
    if not isinstance(v, dict): raise ValueError('Series inventory must be an object')
    if v.get('kind') not in {'line','bar','mixed','pie','table'}: raise ValueError('Unknown chart kind')
    boolean(v, 'series_complete')
    items = v.get('series')
    if not isinstance(items, list) or not 1 <= len(items) <= 64:
        raise ValueError('Inventory must include every plotted series and named reference line')
    names = []
    for s in items:
        if not isinstance(s, dict): raise ValueError('Invalid series entry')
        name, raw = text(s, 'name'), text(s, 'raw_text')
        if not isinstance(s.get('color',''),str):raise ValueError('Invalid observed color')
        validate_box(s.get('box'))
        if s.get('source') not in {'legend','direct','title'}: raise ValueError('Invalid series text source')
        if key(name) not in key(raw): raise ValueError('Series name must be verbatim inside raw printed text')
        # The trailing percentage in a direct label is a point annotation, not its name.
        if s['source'] == 'direct' and re.search(r',\s*[+-]?\d+(?:[.,]\d+)?\s*%\s*$', name):
            raise ValueError('Separate endpoint value from direct series name')
        names.append(key(name))
    if len(set(names)) != len(names): raise ValueError('Duplicate series names; inspect separate swatches')


def bindings(v, names):
    if not isinstance(v, dict): raise ValueError('Scale evidence must be an object')
    scales = v.get('scales')
    if not isinstance(scales, dict): raise ValueError('Missing scale locations')
    for side in ('left','right'):
        if scales.get(side) is not None: validate_box(scales.get(side))
    rows = v.get('series')
    if not isinstance(rows, list) or any(not isinstance(s,dict) for s in rows) or [s.get('name') for s in rows] != names:
        raise ValueError('Scale bindings must preserve exact inventory names and order')
    for s in rows:
        axis = s.get('axis')
        if axis not in {'left','right','none'}: raise ValueError('Invalid scale side')
        if axis != 'none' and scales.get(axis) is None:
            raise ValueError('Series assigned to a nonexistent scale')
        if axis == 'none' and any(scales.get(side) is not None for side in ('left','right')):
            raise ValueError('Series scale binding unresolved despite visible measurement scales')
        unit = text(s, 'unit', empty=True)
        if re.fullmatch(r'[+−-]?\d[\d.,\s]*(?:%|x)?', unit):
            raise ValueError('A numerical tick or point value is not a unit')
        text(s, 'evidence', empty=(axis == 'none' and not unit))


def read_series(reader, path):
    v = observe(reader, path,
        'Inventory ALL plotted quantities, including the main curve, every colored/hatch legend key, '
        'and named threshold/reference lines (+1 Std, Avg., etc.). Do not take axis categories or '
        'a standalone unit as a series. A plot can have a title-named main quantity AND named references. '
        'Return {"kind":"line","series_complete":false,"series":['
        '{"name":"","raw_text":"","color":"","source":"legend","box":[0,0,1,1]}]}. '
        'source is legend, direct (text beside a curve), or title (only if heading identifies that '
        'otherwise unnamed plotted quantity). raw_text is the exact printed label; name preserves '
        'its words but excludes a trailing endpoint value. Never translate China/US or expand abbreviations. '
        'Color is the visibly associated swatch/curve color, empty if uncertain; do not invent hex codes. '
        'Each normalized box encloses the text of ONE entry, all its lines, without neighbors. '
        'series_complete=true only if no plotted quantity/reference is missing.',
        inventory, 'series_inventory', 2048)
    for i, s in enumerate(v['series']):
        actual = crop_text(reader, path, s['box'], f'series_pixels_{i}',
                           'Copy the full label, including any point-value suffix, but ignore the colored swatch.')
        if key(actual) != key(s['raw_text']):
            raise ValueError('Series crop disagrees with inventory: ' + s['name'])
    names = [s['name'] for s in v['series']]
    b = observe(reader, path,
        'Inspect actual scale positions and follow each plotted series to its scale. '
        'Text printed at the right end of a line does NOT imply a right axis. '
        'If only a left scale exists, every measured series uses left. Pie uses none. '
        'Keep units separate from values: % is a unit, 100%/150%/59% are not. '
        'Do not invent a unit if absent. For horizontal plots left/right mean the vertical '
        'measurement scales only; use none when the numerical scale is horizontal. '
        'Return {"scales":{"left":null,"right":null},"series":['
        '{"name":"","axis":"none","unit":"","evidence":""}]}. '
        'For each existing vertical numerical scale supply its normalized box. '
        'Evidence must describe the visible scale/unit/legend association. '
        'Return exactly these names in this order: ' + json.dumps(names, ensure_ascii=False),
        lambda x: bindings(x, names), 'scale_binding', 2048)
    scale_checks={}
    for side,box in b['scales'].items():
        if side not in {'left','right'} or box is None:continue
        def scale_check(c):
            if not isinstance(c,dict) or c.get('numeric_scale_visible') is not True:
                raise ValueError('Proposed scale crop does not show a numerical scale')
            text(c,'unit',empty=True)
            if re.fullmatch(r'[+−-]?\d[\d.,\s]*(?:%|x)?',c['unit']):
                raise ValueError('Scale crop unit contains a tick value')
        check=observe(reader,path,
            'Inspect this proposed numerical scale crop. Return '
            '{"numeric_scale_visible":false,"unit":""}. Set true only for actual numeric '
            'scale ticks, not legend text or point annotations. Unit is the printed unit only '
            '(e.g. %), never a tick number. Leave unit empty if not printed in this crop.',
            scale_check,'scale_pixels_'+side,256,box)
        scale_checks[side]=check
        unit=check['unit'].strip().strip('()').strip()
        if unit:
            for binding in b['series']:
                if binding['axis']==side and key(binding['unit'].strip().strip('()'))!=key(unit):
                    raise ValueError('Series unit disagrees with its scale crop: '+binding['name'])
    def check_inventory(c):
        if not isinstance(c,dict): raise ValueError('Inventory check must be an object')
        if c.get('missing') != [] or c.get('extra') != [] or c.get('bindings_correct') is not True:
            raise ValueError('Inventory/scale check found missing, extra or misbound series: '+json.dumps(c,ensure_ascii=False))
    observe(reader,path,
        'Compare this candidate inventory to the FULL image. Look specifically for omitted main curves, '
        'hatch legend keys, named thresholds, units/axis text accidentally listed as series, and '
        'left/right swaps. Check percent curves against percent scales, not text position. '
        'Return {"missing":[],"extra":[],"bindings_correct":true}. List exact missing/extra '
        'printed names and set bindings_correct=false when a unit or scale is wrong. Candidate: '+
        json.dumps(b['series'],ensure_ascii=False),check_inventory,'inventory_coverage',1024)
    v['bindings'] = b
    v['scale_checks'] = scale_checks
    return v


def axis_plan(v, axis):
    if not isinstance(v, dict): raise ValueError('Axis plan must be an object')
    if v.get('role') not in {'time','categorical','numerical','none'}:
        raise ValueError('Invalid axis role')
    boolean(v, 'all_visible_located'); boolean(v, 'all_data_labelled')
    groups = v.get('groups')
    if not isinstance(groups, list) or len(groups) > 128: raise ValueError('Invalid axis groups')
    if v['role'] in {'none','numerical'}:
        if groups: raise ValueError('Measurement scale is not a category axis')
        return
    if not groups or not v['all_visible_located']: raise ValueError('Axis label locations incomplete')
    dim = 0 if axis == 'x' else 1
    positions = []
    if any(not isinstance(g,dict) or 'parent_box' not in g for g in groups):
        raise ValueError('Each group requires parent_box (null if no parent)')
    parented = any(g.get('parent_box') is not None for g in groups)
    for g in groups:
        if not isinstance(g,dict): raise ValueError('Axis group must be an object')
        if g.get('parent_box') is not None: validate_box(g['parent_box'])
        if parented and g.get('parent_box') is None:
            raise ValueError('Mixed parented and unparented groups; check duplicate first tier')
        boxes = g.get('boxes')
        if not isinstance(boxes, list) or not boxes: raise ValueError('Empty tick group')
        for box in boxes:
            box = validate_box(box)
            center = (box[dim]+box[dim+2])/2
            positions.append(center)
    if len(positions)>128: raise ValueError('Too many axis labels in one observation')
    ordered=sorted(positions)
    if any(b-a < .002 for a,b in zip(ordered,ordered[1:])):
        raise ValueError('Duplicate tick positions; do not copy child ticks twice')


def read_axis(reader, path, axis):
    plan = observe(reader, path,
        'Locate every PRINTED ' + axis.upper() + ' label at its actual tick/category position. '
        'Return {"role":"none","all_visible_located":false,"all_data_labelled":false,"groups":['
        '{"parent_box":null,"boxes":[]}]}. role: time/categorical/numerical/none. '
        'For numerical measurement scales or absent axes return groups=[]. '
        'Years written as 23,24,25,26 below a time series are time ticks, NOT a measurement scale. '
        'For time/categories boxes are normalized [left,top,right,bottom], ONE box for the full '
        'text of each printed tick. Include rotated text and multiline categories. '
        'For callouts use the category column order, not text height. Do not merge adjacent regions. '
        'For shared years below months/quarters create one group per printed year, parent_box '
        'around its year ONLY and boxes around each child month/quarter ONLY. Include ALL year '
        'groups (not just the first). Never include a second copy of unqualified child ticks. '
        'For a single label with an occurrence qualifier include both lines in its one box. '
        'Never generate intermediate ticks or infer years. all_data_labelled=false for sparse '
        'time ticks. Do not transcribe label text in this step.',
        lambda x: axis_plan(x, axis), 'locate_ticks_'+axis, 4096)
    if plan['role'] in {'numerical','none'}:
        def role_check(v):
            if not isinstance(v,dict) or v.get('role') != plan['role']:
                raise ValueError('Axis role disagrees; time/category labels must not be dropped')
        observe(reader,path,'Inspect the '+axis.upper()+' axis independently. Return {"role":"none"}; '
                'choose time, categorical, numerical or none. Two-digit years beneath a line plot '
                'are time; rows beside horizontal bars are categories. Numeric measurements alone '
                'are numerical. Do not confuse legend with axis.',role_check,'confirm_role_'+axis,128)
        return plan, [], []
    dim=0 if axis=='x' else 1
    labels=[]
    for j,g in enumerate(plan['groups']):
        parent = ''
        if g['parent_box'] is not None:
            parent=crop_text(reader,path,g['parent_box'],f'parent_{axis}_{j}',
                             'Read ONLY the shared parent year/text, not child ticks.')
        for k,box in enumerate(g['boxes']):
            label=crop_text(reader,path,box,f'tick_{axis}_{j}_{k}',
                            'Read ONE tick/category only. Do not include neighboring labels or plot values.')
            if parent and key(parent) in key(label):
                raise ValueError('Child crop includes parent text; separate the two tiers before joining')
            labels.append(((box[dim]+box[dim+2])/2, label+(' '+parent if parent else '')))
    labels.sort()
    result=[s for _,s in labels]
    # A different full-image task checks coverage/count and spatial order, with no
    # previous transcription supplied: agreement is not guaranteed by echoing it.
    def coverage(v):
        if not isinstance(v,dict) or not isinstance(v.get('labels'),list):
            raise ValueError('Coverage requires labels')
        if any(not isinstance(x,str) or not x.strip() for x in v['labels']):
            raise ValueError('Coverage contains unreadable label')
    check=observe(reader,path,
        'Read ALL printed '+axis.upper()+' category/time ticks in spatial order. '
        'Return {"labels":[]}. Include each parent year after its child month/quarter; '
        'retain every year group. Do not repeat the first unqualified child group. '
        'Keep literal duplicate ticks if no parent exists. Do not translate, infer or extend dates. '
        'For callout categories sort by their data columns, not label height.',
        coverage,'coverage_'+axis,2048)
    if [key(s) for s in check['labels']] != [key(s) for s in result]:
        raise ValueError('Crop labels/count/order disagree with full-axis coverage: '+axis)
    repeated=len({key(s) for s in result})!=len(result)
    if repeated and axis!='x': raise ValueError('Repeated Y categories require positional disambiguation')
    if repeated: return plan, [], result
    return plan,result,[]


def read_chart(reader,path):
    reader.last_generation={'attempts':[], 'recipe':REVIEW_RECIPE}
    # Re-localize once on crop disagreement; never accept the unchecked candidate.
    def stage(fn, name):
        for attempt in range(2):
            try: return fn()
            except ValueError as e:
                reader.last_generation.setdefault('stage_errors',[]).append({'stage':name,'error':str(e)})
                if attempt: raise
                print('[Structure] Re-localizing '+name+': '+str(e),flush=True)
    title=stage(lambda:read_heading(reader,path),'heading')
    inv=stage(lambda:read_series(reader,path),'series')
    x,xlabels,xticks=stage(lambda:read_axis(reader,path,'x'),'x_axis')
    y,ylabels,_=stage(lambda:read_axis(reader,path,'y'),'y_axis')
    orientation=('none' if inv['kind']=='pie' else 'matrix' if inv['kind']=='table' else
                 'horizontal' if x['role']=='numerical' and y['role'] in {'categorical','time'} else 'vertical')
    series=[{'name':s['name'],'color':s.get('color',''),'axis':b['axis'],'unit':b['unit']}
            for s,b in zip(inv['series'],inv['bindings']['series'])]
    source=('title' if len(series)==1 and inv['series'][0]['source']=='title' and key(title)==key(series[0]['name'])
            else 'legend' if any(s['source']=='legend' for s in inv['series']) else 'unknown')
    result=dict(title=title,kind=inv['kind'],series=series,series_source=source,
                x_labels=xlabels,y_labels=ylabels,x_labels_complete=bool(xlabels) and x['all_data_labelled'],
                x_order_known=bool(xlabels),series_complete=inv['series_complete'],regions={},uncertain=[],
                layout={'orientation':orientation,'x_axis_type':x['role'],'y_axis_type':y['role']})
    if xticks:
        result['x_tick_labels']=xticks
        result['uncertain'].append('Literal repeated X ticks: positional grounding required; do not infer years')
    if not inv['series_complete']:result['uncertain'].append('Series inventory coverage remains uncertain')
    reader.last_generation['field_evidence']={'inventory':inv,'x_plan':x,'y_plan':y}
    # Passing these checks records cross-view agreement, NOT human accuracy verification.
    reader.last_generation['quality_status']='cross_view_checked_not_human_verified'
    return validate_structure(result)
