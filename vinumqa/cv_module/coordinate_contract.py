"""Convert only explicitly declared coordinates; never guess a box's units."""
from copy import deepcopy
from vinumqa.cv_module.structure import validate_box

PROMPT = '''
Coordinate contract: return a single JSON object. Add coordinate_system="normalized_1000"
when returning boxes. In that system x and y range from 0 to 1000 relative to the
ENTIRE image supplied in this call. Example: [100,200,900,300]. Locate actual text;
never copy a full-image placeholder for an individual label.
Alternatively declare coordinate_system="normalized_1" for coordinates 0..1.
Pixel coordinates require coordinate_system="pixels" AND coordinate_size=[width,height]
of the exact image coordinate frame you used. Never mix coordinate systems.
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
