"""Cheap image-complexity heuristic; token caps do not change image resolution."""
def initial_token_budget(image):
    from PIL import ImageFilter
    gray = image.convert("L")
    gray.thumbnail((512, 512))
    edges = gray.filter(ImageFilter.FIND_EDGES)
    histogram = edges.histogram()
    density = sum(histogram[40:]) / (gray.width * gray.height)
    # Dense text/grid charts generally require more output than sparse charts.
    if density > .20: return 4096
    if density > .09: return 2048
    return 1024

MAX_NEW_TOKENS = 16384

def budget_schedule(initial, maximum=MAX_NEW_TOKENS):
    if initial <= 0 or maximum < initial: raise ValueError("Invalid token budget")
    while True:
        yield initial
        if initial == maximum: break
        initial = min(initial * 2, maximum)

def reached_eos(last_token, eos_ids):
    if eos_ids is None: return False
    if isinstance(eos_ids, int): eos_ids = [eos_ids]
    return int(last_token) in eos_ids
