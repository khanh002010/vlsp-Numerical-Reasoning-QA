"""Conservative pixel geometry for separated, solid, upright bars.

No OCR reference, years, image IDs or generated coordinates are used here.
Unsupported charts deliberately fail instead of inventing label positions.
"""
import numpy as np
from PIL import Image


def bar_label_boxes(path):
    with Image.open(path) as image:
        rgb=np.asarray(image.convert('RGB')).astype(np.int16)
    h,w=rgb.shape[:2]
    # Colored bar interiors; exclude gray grid, black text and white background.
    mask=(rgb.max(2)-rgb.min(2)>60) & (rgb.max(2)<250)
    counts=mask.sum(0)
    active=counts>max(12,h*.10)
    edges=np.diff(np.r_[False,active,False].astype(int))
    runs=list(zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)))
    bars=[]
    for left,right in runs:
        if not 3<=right-left<=w*.08: continue
        rows=np.flatnonzero(mask[:,left:right].mean(1)>.8)
        if len(rows)<h*.10: continue
        top,bottom=int(rows[0]),int(rows[-1])
        if len(rows)/(bottom-top+1)<.95: continue
        bars.append((left,right,top,bottom))
    if len(bars)<3: raise ValueError('No reliable separated upright bars found')
    bottoms=np.array([b[3] for b in bars])
    if bottoms.max()-bottoms.min()>max(3,h*.01):
        raise ValueError('Bars do not share a baseline')
    baseline=int(np.median(bottoms))
    if not .45*h<baseline<.96*h: raise ValueError('No usable label band below bars')
    centers=np.array([(b[0]+b[1])/2 for b in bars])
    gaps=np.diff(centers)
    if gaps.min()<5 or gaps.max()>gaps.min()*1.35:
        raise ValueError('Irregular bar spacing; column crops would be ambiguous')
    # Interior colors must agree: this recovery is not for grouped/stacked bars.
    colors=np.array([np.median(rgb[t:b+1,l:r],axis=(0,1)) for l,r,t,b in bars])
    if np.max(np.abs(colors-np.median(colors,axis=0)))>25:
        raise ValueError('Multiple bar colors; single-series recovery is unsafe')
    boundaries=np.r_[max(0,centers[0]-gaps[0]/2), (centers[:-1]+centers[1:])/2,
                     min(w,centers[-1]+gaps[-1]/2)]
    return [[float(boundaries[i]/w), min(1,(baseline+2)/h),
             float(boundaries[i+1]/w),1.] for i in range(len(bars))]


def read_bar_labels(reader,path,series):
    from vinumqa.cv_module.reviewed_reader import checked_read,axis_groups
    boxes=bar_label_boxes(path)
    reader.last_generation['bar_label_boxes']=boxes
    labels=[]
    def validate(v):
        if not isinstance(v,dict) or v.get('readable') is not True:
            raise ValueError('Column label not fully readable')
        lines=v.get('lines')
        if not isinstance(lines,list) or not lines or any(not isinstance(s,str) or not s.strip() for s in lines):
            raise ValueError('Column label needs its visible text lines')
        axis_groups({'labels':[' '.join(lines)],'complete':False},series)
    for i,box in enumerate(boxes):
        value=checked_read(reader,path,
            'This crop contains the label under ONE bar. Transcribe its printed lines only. '
            'Return {"lines":[],"readable":false}. Set readable=true only if the entire label is visible. '
            'Copy the year and any printed occurrence qualifier on the next line. '
            'If no qualifier is printed, return just the year. Never infer a year or occurrence. '
            'Do not include neighboring text or chart values.',
            validator=validate,phase=f'bar_label_{i}',budgets=(128,),box=box)
        labels.append(' '.join(s.strip() for s in value['lines']))
    labels=axis_groups({'labels':labels,'complete':False},series)
    return labels,False
