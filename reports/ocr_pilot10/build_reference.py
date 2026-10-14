"""Six pixel transcriptions plus the four existing reviewed difficult images."""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def build():
    original = json.loads((ROOT / 'reports/public_accuracy_v2/pixel_references.json').read_text(encoding='utf-8'))
    extra = {
        'b850d918-b62a-4516-bf95-35c7e781fc15.png': {
            'title': 'TTCK Việt Nam tương quan ngược so với TTCK Mỹ',
            'series': ['VNIndex', 'DJIA (Mỹ)', 'S&P 500 (Mỹ)'],
            'x_labels': ['31/12/2021', '31/1/2022', '28/2/2022', '31/3/2022', '30/4/2022', '31/5/2022', '30/6/2022', '31/7/2022', '31/8/2022', '30/9/2022', '31/10/2022'],
            'units': {'VNIndex': '%', 'DJIA (Mỹ)': '%', 'S&P 500 (Mỹ)': '%'}},
        '85387fdd-d4a9-42bb-8bf4-2eae607a948c.png': {
            'title': 'Dòng tiền tiếp tục suy yếu trên TTCK',
            'series': ['VN30', 'VNMidcap', 'VNSmallcap', 'VNIndex'],
            'x_labels': ['T1/2021', 'T3/2021', 'T5/2021', 'T7/2021', 'T9/2021', 'T11/2021', 'T1/2022', 'T3/2022', 'T5/2022', 'T7/2022', 'T9/2022'],
            'units': {s: '' for s in ['VN30', 'VNMidcap', 'VNSmallcap', 'VNIndex']}},
        '1bd23f2d-2018-468c-bfba-e4eac7fe7811.png': {
            'title': '', 'series': ['Cổ phiếu', 'Trái phiếu', 'Tiền tệ'],
            'x_labels': [f'{m}-{y}' for y in ['21', '22', '23'] for m in ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov'] if not (y == '23' and m == 'Nov')],
            'units': {'Cổ phiếu': '', 'Trái phiếu': '', 'Tiền tệ': ''},
            'note': 'Title is cropped off; do not reconstruct it from context.'},
        'b371f5a9-42a2-4ec2-a554-db6e217429a1.png': {
            'title': 'Nhóm cổ phiếu bán ròng/mua ròng nhiều nhất',
            'series': ['GTGD ròng NĐTNN'],
            'x_labels': 'HPG PVD DGC DVS PNJ VNM VRE POW GMD HDB KDH STB NVL VND FUEVFVND NLG SSI VJC VHM BSR'.split(),
            'units': {'GTGD ròng NĐTNN': ''},
            'note': 'Transcribe visible DVS; do not replace it using ticker knowledge.'},
        'c57ab530-2070-4b0e-af3b-d51bcf61ea8b.png': {
            'title': 'Khối ngoại tiếp tục bán ròng, chủ yếu qua kênh thỏa thuận',
            'series': ['Giá trị mua/bán ròng', 'NĐTNN Mua', 'NĐTNN Bán'],
            'x_labels': [f'{day}/10/2022' for day in range(1, 32, 2)],
            'units': {'Giá trị mua/bán ròng': '', 'NĐTNN Mua': '', 'NĐTNN Bán': ''}},
        '17c9541d-b1e6-41dc-8fd0-d3b09ee84710.png': {
            'title': 'Cổ phiếu tác động tiêu cực nhất lên thị trường trong tháng 10',
            'series': ['Index', '% +/-'],
            'x_labels': 'HPG NVL TCB VHM GVR MSN MWG MBB KBC STB'.split(),
            'units': {'Index': '', '% +/-': '%'}}
    }
    image_dir = ROOT / 'data/public_test/public_test_images'
    pool = sorted(p for p in image_dir.glob('*.png') if p.name not in original['images'])
    selected = random.Random(20261014).sample(pool, 6)
    assert {p.name for p in selected} == set(extra), 'Image pool changed; review selection explicitly'
    refs = dict(original['images'])
    for p in selected:
        refs[p.name] = dict(extra[p.name], y_labels=[])
    result = {'scope': '10-image screening pilot: four previously tuned difficult images + six random public images (seed 20261014). Labels transcribed from pixels, not programs. Not a dataset accuracy estimate. y_labels means categorical Y labels, NOT numeric axis ticks. Numerical values and numeric-axis ticks are not scored.',
              'selection': {'seed': 20261014, 'fixed_difficult': list(original['images']), 'random_extra': [p.name for p in selected]},
              'sha256': {name: hashlib.sha256((image_dir/name).read_bytes()).hexdigest() for name in refs},
              'images': refs}
    (Path(__file__).parent/'pixel_references.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    build()
