"""Convert only explicitly declared coordinates; never guess a box's units."""
from copy import deepcopy
from vinumqa.cv_module.structure import validate_box

PROMPT = '''
For this call use ONLY coordinate_system="normalized_1": four decimal fractions
[left,top,right,bottom], each between 0 and 1 relative to the whole supplied image.
Example: [0.10,0.20,0.90,0.30]. Never output pixels or numbers such as 100 or 900.
A box is a flat list of four numbers, not [[...]]. Do not use the full image as
the box of an individual label. Return one JSON object with all required fields.
'''


def normalize_observation(value):
    if not isinstance(value, dict): raise ValueError('Expected one observation object')
    result = deepcopy(value)
    system = result.get('coordinate_system', 'normalized_1')
    size = result.get('coordinate_size')

    def box(b):
        if b is None: return None
        if system == 'normalized_1': return validate_box(b)
        if system == 'normalized_1000': sx = sy = 1000
        elif system == 'pixels':
            if not isinstance(size, list) or len(size) != 2 or any(
                    isinstance(x, bool) or not isinstance(x, (int, float)) or x <= 0 for x in size):
                raise ValueError('Pixel boxes require explicit positive coordinate_size')
            sx, sy = size
        else: raise ValueError('Unknown coordinate system')
        if not isinstance(b, (list, tuple)) or len(b) != 4 or any(
                isinstance(x, bool) or not isinstance(x, (int, float)) for x in b):
            raise ValueError('Box requires four numerical coordinates')
        return validate_box([b[0]/sx, b[1]/sy, b[2]/sx, b[3]/sy])

    def visit(node):
        if isinstance(node, list):
            for item in node: visit(item)
        elif isinstance(node, dict):
            for k, v in list(node.items()):
                if k in {'box', 'parent_box'}: node[k] = box(v)
                elif k == 'boxes' and isinstance(v, list): node[k] = [box(b) for b in v]
                elif k == 'scales' and isinstance(v, dict):
                    node[k] = {side: box(b) for side, b in v.items()}
                else: visit(v)
    visit(result)
    result['coordinate_system'] = 'normalized_1'
    return result
