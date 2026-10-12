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
        value=checked_read(reader,path,prompt,validator=parse_band,phase=phase,budgets=(1024,),box=box)
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
