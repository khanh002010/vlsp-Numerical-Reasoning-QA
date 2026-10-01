import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Cấu hình tiếng Việt cho Matplotlib
plt.rcParams['font.family'] = 'sans-serif'

# Paths
data_path = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\train\train.json"
out_dir = Path(r"C:\Users\USER\.gemini\antigravity-ide\brain\51c01346-4495-4380-91d2-3a4633691feb\scratch")
out_dir.mkdir(parents=True, exist_ok=True)

print("Reading JSON data...")
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Analyzing text length...")
text_lengths = []
for item in data:
    length = sum(len(str(p).split()) for p in item.get('text', []))
    text_lengths.append(length)

plt.figure(figsize=(10, 5))
sns.histplot(text_lengths, bins=50, kde=True, color='skyblue')
plt.title('Phan bo do dai van ban (So luong tu)')
plt.xlabel('So tu')
plt.ylabel('Tan suat')
plt.savefig(out_dir / 'text_length.png')
plt.close()

print("Analyzing media counts...")
img_counts = [len(item.get('images', {})) for item in data]
tbl_counts = [len(item.get('tables', {})) for item in data]

fig, ax = plt.subplots(1, 2, figsize=(12, 5))
sns.countplot(x=img_counts, ax=ax[0], palette='viridis')
ax[0].set_title('So luong Hinh Anh tren moi cau hoi')
ax[0].set_xlabel('So anh')

sns.countplot(x=tbl_counts, ax=ax[1], palette='magma')
ax[1].set_title('So luong Bang (HTML) tren moi cau hoi')
ax[1].set_xlabel('So bang')
plt.savefig(out_dir / 'media_counts.png')
plt.close()

print("Analyzing program structure...")
ops_count = {}
steps_count = []
pattern = r'([a-z_]+)\('
for item in data:
    program = item.get('qa', {}).get('program', '')
    if program:
        ops = re.findall(pattern, program)
        steps_count.append(len(ops))
        for op in ops:
            ops_count[op] = ops_count.get(op, 0) + 1

sorted_ops = dict(sorted(ops_count.items(), key=lambda item: item[1], reverse=True))

plt.figure(figsize=(12, 6))
sns.barplot(x=list(sorted_ops.values()), y=list(sorted_ops.keys()), palette='rocket')
plt.title('Tan suat su dung cac Toan tu (Operators)')
plt.xlabel('So lan xuat hien')
plt.ylabel('Ham toan hoc')
plt.tight_layout()
plt.savefig(out_dir / 'operators.png')
plt.close()

plt.figure(figsize=(10, 5))
sns.histplot(steps_count, bins=range(0, max(steps_count)+2), kde=False, discrete=True, color='coral')
plt.title('Phan bo so buoc giai (So luong ham trong 1 cau hoi)')
plt.xlabel('So buoc')
plt.ylabel('Tan suat')
plt.savefig(out_dir / 'steps_count.png')
plt.close()

summary = {
    "total_samples": len(data),
    "max_text_words": max(text_lengths),
    "avg_text_words": round(sum(text_lengths)/len(text_lengths), 1),
    "max_images": max(img_counts),
    "max_tables": max(tbl_counts),
    "unique_operators": len(ops_count)
}
with open(out_dir / 'summary.json', 'w') as f:
    json.dump(summary, f)

print("Done! Charts have been saved to the scratch directory.")
