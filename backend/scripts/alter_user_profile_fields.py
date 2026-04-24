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
    cur.execute("ALTER TABLE user ADD COLUMN grade VARCHAR(16) NULL")
    cur.execute("ALTER TABLE user ADD COLUMN college VARCHAR(128) NULL")
    cur.execute("ALTER TABLE user ADD COLUMN major VARCHAR(128) NULL")
    print("Added columns: grade, college, major")
    conn.close()


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        # Repeat-run safe
        print(f"Skip or failed: {e}")
