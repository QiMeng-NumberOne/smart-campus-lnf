import pathlib

import pymysql


def run():
    root = pathlib.Path(__file__).resolve().parents[1]
    schema_path = root.parent / "docs" / "03_database" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        charset="utf8mb4",
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS lostfound_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.select_db("lostfound_db")

    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        cur.execute(stmt)

    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print(f"Initialized database with {len(tables)} tables.")
    conn.close()


if __name__ == "__main__":
    run()
