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
        "UPDATE item_image SET image_url=REPLACE(image_url, %s, %s)",
        ("http://10.135.119.64:8090", "http://127.0.0.1:8090"),
    )
    cur.execute(
        "UPDATE item_image SET image_url=%s WHERE image_url LIKE %s",
        ("http://127.0.0.1:8090/uploads/demo-item.jpg", "%demo-item.jpg%"),
    )
    cur.execute("SELECT id, image_url FROM item_image ORDER BY id")
    print(cur.fetchall())
    conn.close()


if __name__ == "__main__":
    run()
