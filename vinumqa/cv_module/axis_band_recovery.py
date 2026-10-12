"""Read lower axis tiers independently, preserving ambiguity in the source."""
from collections import Counter


def parse_band(value):
    if not isinstance(value,dict) or value.get('readable') is not True:
        raise ValueError('Axis band is not fully readable')
    groups=value.get('groups')
    if not isinstance(groups,list) or not groups or len(groups)>128:
        raise ValueError('Invalid or unbounded axis groups')
    labels=[]
    for group in groups:
        if not isinstance(group,dict) or not isinstance(group.get('parent'),str):
            raise ValueError('Each group requires its printed parent, empty if absent')
        ticks=group.get('ticks')
        if not isinstance(ticks,list) or not ticks or any(not isinstance(t,str) or not t.strip() for t in ticks):
            raise ValueError('Each group requires visible ticks')
        parent=group['parent'].strip()
        labels.extend(t.strip()+(' '+parent if parent else '') for t in ticks)
    if len(labels)>128: raise ValueError('Unbounded tick sequence')
    return labels


def recover_axis_band(reader,path,chart):
    from vinumqa.cv_module.reviewed_reader import checked_read
    # Preserve full width and all lower-tier text. No generated coordinates.
    box=[0,.65,1,1]
    prompt=('Read only the X-axis text in this lower chart crop. Return '
        '{"groups":[{"parent":"","ticks":[]}],"readable":true}. '
        'Group ticks using ONLY visible divider lines and printed lower parent labels. '
        'For quarters, parent is the printed year beneath that group; ticks are its printed quarters. '
        'If no parent is printed, use empty parent and copy each visible tick in order, including '
        'literal repeated labels. STOP at the last visible tick. Never extend a calendar. '
        'Ignore plot values, legend and footer. Do not guess missing years. '
        'Set readable=false if any label is clipped or unclear.')
    reads=[]
    for phase in ('axis_band','axis_band_verify'):
        try:
            value=checked_read(reader,path,prompt,validator=parse_band,phase=phase,budgets=(1024,),box=box)
        except ValueError:
            return recover_rotated_ticks(reader,path,chart)
        reads.append(value)
    reader.last_generation['axis_band_observations']=reads
    labels=parse_band(reads[0])
    if labels!=parse_band(reads[1]):raise ValueError('Independent axis band reads disagree')
    counts=Counter(labels)
    if any(n>1 for n in counts.values()):
        chart['x_tick_labels']=labels
        chart['uncertain'].append('Source repeats X tick labels; individual positions cannot be resolved by label alone')
        chart['x_order_known']=False
        return [],False
    return labels,False


def rotated_tick_boxes(path):
    """Conservative fallback for tall, evenly spaced dark ticks in the lower band."""
    import numpy as np
    from PIL import Image
    with Image.open(path) as image: rgb=np.asarray(image.convert('RGB'))
    h,w=rgb.shape[:2];top=int(.70*h);bottom=int(.84*h)
    dark=rgb[top:bottom].max(2)<150
    active=dark.sum(0)>max(8,(bottom-top)*.13)
    edges=np.diff(np.r_[False,active,False].astype(int))
    runs=[]
    for l,r in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
        if runs and l-runs[-1][1]<=3:runs[-1][1]=int(r)
        else:runs.append([int(l),int(r)])
    runs=[(l,r) for l,r in runs if 5<=r-l<=w*.035 and
          np.count_nonzero(dark[:,l:r].any(1))>(bottom-top)*.50]
    if len(runs)<6:raise ValueError('No reliable rotated tick regions')
    centers=np.array([(l+r)/2 for l,r in runs]);gaps=np.diff(centers)
    if gaps.max()>gaps.min()*1.3:raise ValueError('Rotated tick spacing is ambiguous')
    return [[max(0,(l-4)/w),max(0,(top-3)/h),min(1,(r+4)/w),min(1,(bottom+3)/h)] for l,r in runs]


def recover_rotated_ticks(reader,path,chart):
    from vinumqa.cv_module.reviewed_reader import checked_read
    boxes=rotated_tick_boxes(path)
    reader.last_generation['rotated_tick_boxes']=boxes
    labels=[]
    def validate(v):
        if not isinstance(v,dict) or not isinstance(v.get('label'),str) or not v['label'].strip():
            raise ValueError('Unreadable individual rotated tick')
        if v.get('readable') is False:raise ValueError('Clipped individual rotated tick')
    for i,box in enumerate(boxes):
        observations=[]
        for j in range(2):
            v=checked_read(reader,path,'Read the ONE rotated axis label in this crop. '
                'Copy exactly what is printed, even if its date seems unusual. '
                'Return {"label":""}. No calendar continuation or inferred year.',
                validator=validate,phase=f'rotated_tick_{i}_{j}',budgets=(64,),box=box)
            observations.append(v['label'].strip())
        if observations[0]!=observations[1]:raise ValueError('Rotated tick observations disagree')
        labels.append(observations[0])
    if len(set(labels))<len(labels):
        chart['x_tick_labels']=labels
        chart['uncertain'].append('Literal repeated X ticks observed individually; positional grounding required')
        chart['x_order_known']=False
        return [],False
    return labels,False


def recover_title_series(reader,path,chart):
    from vinumqa.cv_module.reviewed_reader import checked_read
    def validate(value):
        if not isinstance(value,dict) or value.get('legend_present') is not False or value.get('single_quantity') is not True:
            raise ValueError('No-legend single-quantity chart has not been confirmed')
    for phase in ('confirm_no_legend','confirm_no_legend_verify'):
        checked_read(reader,path,
            'Inspect whether there is a legend: a separate colored swatch or line sample with a name. '
            'Colored bars themselves and year labels under bars are NOT a legend. '
            'Does this chart plot a single named quantity over time, possibly highlighting a forecast bar? '
            'Return {"legend_present":true,"single_quantity":false}; choose values from the image.',
            validator=validate,phase=phase,budgets=(128,))
    if not chart['title']:raise ValueError('Single quantity has no visible title')
    chart['series']=[{'name':chart['title'],'color':'','axis':'none','unit':''}]
    chart['series_source']='title'
    chart['series_complete']=True
