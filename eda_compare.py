import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from PIL import Image
import pandas as pd
import numpy as np

# Cấu hình tiếng Việt cho Matplotlib
plt.rcParams['font.family'] = 'sans-serif'

# Paths
train_json_path = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\train\train.json"
train_img_dir = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\train\train_images"

test_json_path = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\public_test\public_test.json"
test_img_dir = r"d:\VS CODE\vlsp Numerical Reasoning QA\data\public_test\public_test_images"

out_dir = Path(r"C:\Users\USER\.gemini\antigravity-ide\brain\51c01346-4495-4380-91d2-3a4633691feb\scratch")
out_dir.mkdir(parents=True, exist_ok=True)

print("Reading JSON data...")
with open(train_json_path, 'r', encoding='utf-8') as f:
    train_data = json.load(f)
with open(test_json_path, 'r', encoding='utf-8') as f:
    test_data = json.load(f)

# --- 1. Basic Stats Comparison ---
def get_stats(data, split_name):
    records = []
    for item in data:
        text_len = sum(len(str(p).split()) for p in item.get('text', []))
        img_count = len(item.get('images', {}))
        tbl_count = len(item.get('tables', {}))
        records.append({
            'Split': split_name,
            'Text Length': text_len,
            'Images': img_count,
            'Tables': tbl_count
        })
    return records

df_stats = pd.DataFrame(get_stats(train_data, 'Train') + get_stats(test_data, 'Public Test'))

print("Plotting Text Length Comparison...")
plt.figure(figsize=(10, 5))
sns.histplot(data=df_stats, x='Text Length', hue='Split', element='step', common_norm=False, stat='density')
plt.title('So sanh Do dai Van ban (Train vs Public Test)')
plt.savefig(out_dir / 'compare_text_length.png')
plt.close()

print("Plotting Media Counts Comparison...")
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
sns.countplot(data=df_stats, x='Images', hue='Split', ax=ax[0])
ax[0].set_title('So luong Anh tren moi cau hoi')
sns.countplot(data=df_stats, x='Tables', hue='Split', ax=ax[1])
ax[1].set_title('So luong Bang HTML tren moi cau hoi')
plt.savefig(out_dir / 'compare_media_counts.png')
plt.close()

# --- 2. Image EDA (Resolution, Aspect Ratio) ---
print("Analyzing Images...")
def analyze_images(data, img_dir_path, split_name):
    records = []
    for item in data:
        images = item.get('images', {})
        for img_key, img_filename in images.items():
            img_path = os.path.join(img_dir_path, img_filename)
            if os.path.exists(img_path):
                try:
                    with Image.open(img_path) as img:
                        w, h = img.size
                        res = w * h
                        ratio = w / h if h > 0 else 1
                        
                        # Phân loại hình dáng (Shape)
                        if ratio > 1.2: shape = 'Landscape (Ngang)'
                        elif ratio < 0.8: shape = 'Portrait (Doc)'
                        else: shape = 'Square (Vuong)'
                        
                        records.append({
                            'Split': split_name,
                            'Width': w,
                            'Height': h,
                            'Resolution': res,
                            'Aspect Ratio': ratio,
                            'Shape': shape
                        })
                except Exception as e:
                    pass
    return records

img_records = analyze_images(train_data, train_img_dir, 'Train') + analyze_images(test_data, test_img_dir, 'Public Test')
df_img = pd.DataFrame(img_records)

if not df_img.empty:
    print("Plotting Image EDA...")
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    
    # Biểu đồ 1: Phân bố Shape (Landscape/Square/Portrait)
    sns.countplot(data=df_img, x='Shape', hue='Split', ax=ax[0])
    ax[0].set_title('Phan loai Hinh dang Anh (Aspect Ratio)')
    
    # Biểu đồ 2: Phân bố Độ phân giải (Quality proxy)
    sns.kdeplot(data=df_img, x='Resolution', hue='Split', fill=True, ax=ax[1], common_norm=False)
    ax[1].set_title('Phan bo Do phan giai Anh (Chat luong)')
    ax[1].set_xlabel('Resolution (Width x Height)')
    
    plt.savefig(out_dir / 'compare_image_eda.png')
    plt.close()

    # Lưu thêm summary để báo cáo
    summary = {
        "train_img_count": len(df_img[df_img['Split'] == 'Train']),
        "test_img_count": len(df_img[df_img['Split'] == 'Public Test']),
        "train_avg_res": int(df_img[df_img['Split'] == 'Train']['Resolution'].mean()),
        "test_avg_res": int(df_img[df_img['Split'] == 'Public Test']['Resolution'].mean()),
        "shape_dist": df_img['Shape'].value_counts().to_dict()
    }
    with open(out_dir / 'compare_summary.json', 'w') as f:
        json.dump(summary, f)

print("Done! Charts have been saved.")
