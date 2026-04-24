import pymysql


def add_column_if_missing(cur, table_name, column_name, ddl):
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",
        ("lostfound_db", table_name, column_name),
    )
    if cur.fetchone()[0] == 0:
        cur.execute(ddl)


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

    # item_image 新增 AI 字段
    add_column_if_missing(cur, "item_image", "ai_class", "ALTER TABLE item_image ADD COLUMN ai_class VARCHAR(64) NULL")
    add_column_if_missing(cur, "item_image", "ai_confidence", "ALTER TABLE item_image ADD COLUMN ai_confidence FLOAT NULL")
    add_column_if_missing(cur, "item_image", "ai_bbox_json", "ALTER TABLE item_image ADD COLUMN ai_bbox_json TEXT NULL")
    add_column_if_missing(cur, "item_image", "ai_model_version", "ALTER TABLE item_image ADD COLUMN ai_model_version VARCHAR(64) NULL")
    add_column_if_missing(cur, "item_image", "ai_updated_at", "ALTER TABLE item_image ADD COLUMN ai_updated_at DATETIME NULL")

    # recognition_log 增强观测字段
    add_column_if_missing(cur, "recognition_log", "model_version", "ALTER TABLE recognition_log ADD COLUMN model_version VARCHAR(64) NULL")
    add_column_if_missing(cur, "recognition_log", "status", "ALTER TABLE recognition_log ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'success'")
    add_column_if_missing(cur, "recognition_log", "error", "ALTER TABLE recognition_log ADD COLUMN error TEXT NULL")

    print("AI table fields ready")
    conn.close()


if __name__ == "__main__":
    run()
