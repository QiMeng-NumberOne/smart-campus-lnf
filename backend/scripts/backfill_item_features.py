"""
把已有物品写入 CLIP 特征表。请先安装好 cn_clip 并执行 alter_item_feature_table.py。

用法（在 backend 目录、已激活 conda 环境）:
  python scripts/backfill_item_features.py

说明：需要能从本机读取到图片文件（backend/uploads 下存在对应文件），或
临时启动后端使 image_url 可访问；否则该物品会 skip。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.item import Item
from app.services.clip_service import ClipService


def main():
    db = SessionLocal()
    try:
        ids = [
            r[0]
            for r in db.query(Item.id).filter(Item.is_deleted == 0).order_by(Item.id.asc()).all()
        ]
        print(f"total items: {len(ids)}")
        ok_n = 0
        dbg_once = os.environ.get("CLIP_BACKFILL_DEBUG", "")
        for iid in ids:
            ok = ClipService.refresh_item_features(db, iid)
            if ok:
                ok_n += 1
            print(f"  item {iid}: {'OK' if ok else 'skip/fail'}")
            if dbg_once and not ok and dbg_once == "1":
                from app.models.item import ItemImage

                img = db.query(ItemImage).filter(ItemImage.item_id == iid).first()
                print("    first_image:", getattr(img, "image_url", None))
                dbg_once = "0"
        if ok_n == 0 and ids:
            print("提示: 全部失败通常是 uploads 无文件或图片 URL 无法访问。设置环境变量 CLIP_BACKFILL_DEBUG=1 可打印首条图片 URL。")
        print(f"indexed: {ok_n}/{len(ids)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
