import os
import random
import shutil
from pathlib import Path

# 获取当前脚本所在目录的上一级目录 (yolo_model)
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= 配置区 =================
# 目标数据集路径 (datasets)
TARGET_BASE_DIR = BASE_DIR / 'datasets'
IMG_TRAIN_DIR = TARGET_BASE_DIR / 'images' / 'train'
IMG_VAL_DIR = TARGET_BASE_DIR / 'images' / 'val'
LBL_TRAIN_DIR = TARGET_BASE_DIR / 'labels' / 'train'
LBL_VAL_DIR = TARGET_BASE_DIR / 'labels' / 'val'

VAL_RATIO = 0.2  # 20% 验证集

# 🌟 【核心魔法区】: 在这里定义你的数据集来源、新编号、以及文件前缀
DATA_SOURCES = [
    {
        'source_dir': BASE_DIR / 'origindata' / 'keys.yolov11' / 'train',
        'new_class_id': 0,        # 钥匙统统改成 0 号
        'prefix': 'key_'          # 文件名加前缀 key_
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'id_card.yolov11' / 'train',
        'new_class_id': 1,       
        'prefix': 'idcard_'     
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'glasses.yolov11' / 'train',
        'new_class_id': 2,        
        'prefix': 'glasses_'     
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'phone.yolov11' / 'train',
        'new_class_id': 3,     
        'prefix': 'phone_'     
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'headphone.yolov11' / 'train',
        'new_class_id': 4,      
        'prefix': 'headphone_'    
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'flashdrive.yolov11' / 'train',
        'new_class_id': 5,       
        'prefix': 'flashdrive_'      
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'umbrella.yolov11' / 'train',
        'new_class_id': 6,      
        'prefix': 'umbrella_'     
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'waterbottle.yolov11' / 'train',
        'new_class_id': 7,       
        'prefix': 'waterbottle_'     
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'bag.yolov11' / 'train',
        'new_class_id': 8,       
        'prefix': 'bag_'      
    },
    {
        'source_dir': BASE_DIR / 'origindata' / 'book.yolov11' / 'train',
        'new_class_id': 9,       
        'prefix': 'book_'     
    }
]
# ==========================================

def create_target_dirs():
    """清理旧数据并重建干净的文件夹，防止有幽灵数据残留"""
    if TARGET_BASE_DIR.exists():
        shutil.rmtree(TARGET_BASE_DIR)
    for d in [IMG_TRAIN_DIR, IMG_VAL_DIR, LBL_TRAIN_DIR, LBL_VAL_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def process_and_split():
    print("🚀 开始多类别数据集整合、重编号与分割...")
    create_target_dirs()

    total_images_processed = 0

    for data in DATA_SOURCES:
        source_path = data['source_dir']
        class_id = data['new_class_id']
        prefix = data['prefix']
        
        source_img_dir = source_path / 'images'
        source_lbl_dir = source_path / 'labels'
        
        if not source_img_dir.exists():
            print(f"⚠️ 跳过: 找不到路径 {source_img_dir}")
            continue
            
        images = list(source_img_dir.glob('*.*'))
        images = [img for img in images if img.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        
        if not images:
            print(f"⚠️ 跳过: {source_img_dir} 里没有图片")
            continue
            
        random.shuffle(images)
        val_count = int(len(images) * VAL_RATIO)
        val_images = set(images[:val_count])
        
        print(f"\n📦 正在处理 [{prefix}] 数据集... 发现 {len(images)} 张图片")
        
        success_count = 0
        
        for img_path in images:
            lbl_path = source_lbl_dir / (img_path.stem + '.txt')
            
            if lbl_path.exists():
                is_val = img_path in val_images
                target_img_dir = IMG_VAL_DIR if is_val else IMG_TRAIN_DIR
                target_lbl_dir = LBL_VAL_DIR if is_val else LBL_TRAIN_DIR
                
                # 给文件改名，防止覆盖 (例如：1.jpg 变成 key_1.jpg)
                new_img_name = f"{prefix}{img_path.name}"
                new_lbl_name = f"{prefix}{lbl_path.name}"
                
                # 1. 复制图片
                shutil.copy(str(img_path), str(target_img_dir / new_img_name))
                
                # 2. 🧙‍♂️ 核心：打开 txt 文件，把里面开头的数字强行换成 class_id
                with open(lbl_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                new_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        parts[0] = str(class_id)  # 篡改编号！
                        new_lines.append(" ".join(parts) + "\n")
                        
                # 把修改后的内容写入新的 txt 里
                with open(target_lbl_dir / new_lbl_name, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                    
                success_count += 1
                total_images_processed += 1
                
        print(f"  ✅ [{prefix}] 处理完成！成功转移并篡改了 {success_count} 张标签。")
        
    print(f"\n🎉 全部搞定！共计处理 {total_images_processed} 张完美数据！可以开始训练了！")

if __name__ == '__main__':
    process_and_split()