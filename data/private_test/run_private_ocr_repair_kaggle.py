"""Paste this Python file into a Kaggle cell after syncing code and input files."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
SOURCE = REPO / 'data/private_test/private_chart_structures.json'
QUEUE = REPO / 'data/private_test/private_ocr_repair_queue.json'
OUTPUT = Path('/kaggle/working/private_ocr_repair_v4')

for path in [SOURCE, QUEUE, REPO/'vinumqa/cv_module/grounded_review.py']:
    if not path.is_file():
        raise FileNotFoundError(f'Can dong bo file len Kaggle: {path}')

# Use a new Python process to avoid reusing old modules loaded in the notebook.
subprocess.run([
    sys.executable, '-u', '-c',
    'from vinumqa.cv_module.structure_grounding import REVIEW_RECIPE; '
    'print("Reader:", REVIEW_RECIPE, flush=True); '
    'assert REVIEW_RECIPE == "region-evidence-v4", "Can dong bo reader v4 truoc khi chay"',
], cwd=REPO, check=True)

queue = json.loads(QUEUE.read_text(encoding='utf-8'))
assert queue['images'] and all(r['split'] == 'private_test' for r in queue['images'])
print(f"Doc lai {len(queue['images'])} anh private; source duoc giu nguyen.", flush=True)
subprocess.run([
    sys.executable, '-u', '-m', 'vinumqa.cv_module.repair_audited',
    '--source', str(SOURCE), '--queue', str(QUEUE),
    '--data-root', str(REPO/'data'), '--output-dir', str(OUTPUT),
    '--max-minutes', '90',
], cwd=REPO, check=True)

merged = json.loads((OUTPUT/'chart_structures.json').read_text(encoding='utf-8'))
retried = json.loads((OUTPUT/'retried_chart_structures.json').read_text(encoding='utf-8'))
print('Ket qua merged:', dict(Counter(r['status'] for r in merged['images'].values())))
print('Ket qua doc lai:', dict(Counter(r['status'] for r in retried['images'].values())))
print('Chua thu:', len(queue['images']) - len(retried['images']))
print('File ket qua:', OUTPUT/'chart_structures.json')
print('Can doi chieu anh goc; status=ok khong chung minh OCR dung.')
