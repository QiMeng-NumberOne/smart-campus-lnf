import pymysql


def add_column_if_missing(cur, column_name, ddl):
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='item' AND COLUMN_NAME=%s",
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

    add_column_if_missing(cur, "is_deleted", "ALTER TABLE item ADD COLUMN is_deleted TINYINT NOT NULL DEFAULT 0")
    add_column_if_missing(cur, "expires_at", "ALTER TABLE item ADD COLUMN expires_at DATETIME NULL")
    add_column_if_missing(cur, "closed_at", "ALTER TABLE item ADD COLUMN closed_at DATETIME NULL")
    cur.execute("UPDATE item SET is_deleted=0 WHERE is_deleted IS NULL")
    cur.execute("UPDATE item SET expires_at=DATE_ADD(created_at, INTERVAL 28 DAY) WHERE expires_at IS NULL")
    print("item lifecycle columns ready")
    conn.close()


if __name__ == "__main__":
    run()
