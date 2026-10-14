"""Package the pilot into a single Kaggle cell, including the runner source."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
runner=(root/'vinumqa/cv_module/hybrid_pilot.py').read_text(encoding='utf-8')
cell='''import os
import sys
import subprocess
from pathlib import Path

REPO = Path('/kaggle/working/vlsp-Numerical-Reasoning-QA')
OUT = Path('/kaggle/working/ocr_pilot10_paddle_qwen_v1')
assert REPO.is_dir(), 'Clone repo vao /kaggle/working/vlsp-Numerical-Reasoning-QA truoc.'
assert (REPO/'reports/ocr_pilot10/pixel_references.json').is_file()
OUT.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONUNBUFFERED='1', CUDA_VISIBLE_DEVICES='0')
subprocess.run([sys.executable, '-c',
    'import torch; from transformers.utils import is_bitsandbytes_available; '
    'assert torch.cuda.is_available(), "Enable Kaggle GPU"; '
    'assert is_bitsandbytes_available(), "bitsandbytes unavailable"'], check=True, env=env)

# Isolate Paddle packages from the working Qwen/PyTorch environment.
VENV = Path('/kaggle/working/paddle_ocr_cpu_env')
if not (VENV/'bin/python').exists():
    subprocess.run([sys.executable, '-m', 'venv', str(VENV)], check=True)
PPY = str(VENV/'bin/python')
subprocess.run([PPY, '-m', 'pip', 'install', 'paddlepaddle', 'paddleocr>=3,<4', 'Pillow'], check=True)
'''
cell+='\nRUNNER = '+repr(runner)+'\n'
cell+='''
common = ['--images', str(REPO/'data/public_test/public_test_images'),
          '--reference', str(REPO/'reports/ocr_pilot10/pixel_references.json'),
          '--output-dir', str(OUT)]
print('PHASE 1: PP-OCRv5 Vietnamese on CPU', flush=True)
subprocess.run([PPY, '-u', '-c', RUNNER, '--phase', 'ocr', *common],
               cwd=REPO, env=env, check=True)
print('PHASE 2: Qwen2.5-VL-7B NF4 on GPU', flush=True)
subprocess.run([sys.executable, '-u', '-c', RUNNER, '--phase', 'structure', *common],
               cwd=REPO, env=env, check=True)
print('Download entire output folder:', OUT, flush=True)
'''
notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},
          'cells':[{'cell_type':'code','id':'paddle-qwen-pilot','execution_count':None,'metadata':{},'outputs':[],'source':cell.splitlines(True)}]}
target=Path(__file__).parent/'paddle_qwen_one_cell.ipynb'
target.write_text(json.dumps(notebook,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(target)
