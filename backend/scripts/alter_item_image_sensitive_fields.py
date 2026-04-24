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

    add_column_if_missing(cur, "item_image", "raw_image_url", "ALTER TABLE item_image ADD COLUMN raw_image_url VARCHAR(512) NULL")
    add_column_if_missing(cur, "item_image", "masked_image_url", "ALTER TABLE item_image ADD COLUMN masked_image_url VARCHAR(512) NULL")
    add_column_if_missing(cur, "item_image", "is_sensitive", "ALTER TABLE item_image ADD COLUMN is_sensitive TINYINT NOT NULL DEFAULT 0")
    print("item_image sensitive fields ready")
    conn.close()


if __name__ == "__main__":
    run()
