"""
若数据库由旧脚本初始化且缺少 behavior_log 表，执行本脚本创建（与 docs/03_database/schema.sql 一致）。

用法:
  python scripts/ensure_behavior_log.py
"""

import pymysql


def run():
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
        WHERE table_schema = DATABASE() AND table_name = 'behavior_log'
        """
    )
    if cur.fetchone()[0] > 0:
        print("behavior_log: already exists, skip")
        conn.close()
        return
    cur.execute(
        """
        CREATE TABLE `behavior_log` (
            `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID',
            `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID',
            `item_id` BIGINT UNSIGNED NOT NULL COMMENT '物品ID',
            `behavior_type` VARCHAR(32) NOT NULL COMMENT '行为类型',
            `extra` JSON DEFAULT NULL COMMENT '扩展信息',
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            KEY `idx_user` (`user_id`),
            KEY `idx_item` (`item_id`),
            KEY `idx_behavior` (`behavior_type`),
            KEY `idx_created` (`created_at`),
            CONSTRAINT `fk_behavior_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL,
            CONSTRAINT `fk_behavior_item` FOREIGN KEY (`item_id`) REFERENCES `item` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户行为日志表'
        """
    )
    print("behavior_log: created")
    conn.close()


if __name__ == "__main__":
    run()
