import pymysql


def add_column_if_missing(cur, column_name: str, ddl: str):
    cur.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME='user' AND COLUMN_NAME=%s
        """,
        ("lostfound_db", column_name),
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
    add_column_if_missing(
        cur,
        "match_notification_enabled",
        "ALTER TABLE user ADD COLUMN match_notification_enabled TINYINT NOT NULL DEFAULT 0",
    )
    add_column_if_missing(
        cur,
        "wechat_subscribe_at",
        "ALTER TABLE user ADD COLUMN wechat_subscribe_at DATETIME NULL",
    )
    print("user subscribe fields ready")
    conn.close()


if __name__ == "__main__":
    run()
