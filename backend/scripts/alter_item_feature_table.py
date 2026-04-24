"""
创建 / 对齐 item_feature 表（与 Navicat 常见结构一致：feature_vector 为 JSON）。

若你库里已是旧版脚本建的 BLOB 表且为空，可安全执行本脚本（会 DROP 后重建）。
若表内有要保留的数据，请先备份。

用法:
  python scripts/alter_item_feature_table.py
"""

import os
import pymysql


def run():
    force = os.environ.get("ITEM_FEATURE_RECREATE", "").strip() == "1"
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="lostfound_db",
        charset="utf8mb4",
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = 'item_feature'
        """
    )
    exists = cur.fetchone()[0] > 0
    ddl = """
        CREATE TABLE item_feature (
            id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            item_id BIGINT UNSIGNED NOT NULL,
            image_id BIGINT UNSIGNED NULL,
            feature_type TINYINT NOT NULL DEFAULT 0 COMMENT '0=CLIP bundle in feature_vector JSON',
            feature_vector JSON NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_item_feature_item_type (item_id, feature_type),
            KEY idx_item_feature_item (item_id),
            CONSTRAINT fk_item_feature_item FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    if exists and force:
        cur.execute("DROP TABLE IF EXISTS item_feature")
        cur.execute(ddl)
        print("item_feature: dropped and recreated (JSON schema)")
    elif not exists:
        cur.execute(ddl)
        print("item_feature: created (JSON schema)")
    else:
        cur.execute(
            """
            SELECT COLUMN_NAME FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = 'item_feature'
            """
        )
        cols = {r[0] for r in cur.fetchall()}
        if "feature_vector" in cols and "feature_type" in cols:
            print("item_feature: already compatible, skip")
        else:
            print(
                "item_feature: exists but columns mismatch. "
                "Backup data then run: set ITEM_FEATURE_RECREATE=1 and run this script again."
            )
    conn.close()


if __name__ == "__main__":
    run()
