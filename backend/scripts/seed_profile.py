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
        "UPDATE user SET grade=%s, college=%s, major=%s WHERE phone=%s",
        ("2022", "计算机与信息科学学院 软件学院", "软件工程", "18800000000"),
    )
    cur.execute("SELECT username, grade, college, major FROM user WHERE phone=%s", ("18800000000",))
    print(cur.fetchone())
    conn.close()


if __name__ == "__main__":
    run()
