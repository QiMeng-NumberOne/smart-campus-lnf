from datetime import datetime, timedelta

import pymysql
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

    phone = "18800000000"
    cur.execute("SELECT id FROM user WHERE phone=%s", (phone,))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        cur.execute(
            "INSERT INTO user (username,password_hash,phone,student_id,role,status) VALUES (%s,%s,%s,%s,1,1)",
            ("微信用户", pwd_context.hash("123456"), phone, "20260001"),
        )
        user_id = cur.lastrowid

    samples = [
        ("黑色双肩包", "在图书馆丢失，内含教材", "图书馆", 1, 7),
        ("白色耳机盒", "在食堂拾到，可联系认领", "第一食堂", 2, 8),
        ("校园卡", "教学楼附近拾到一张校园卡", "教学楼A区", 2, 5),
        ("钥匙串", "蓝色钥匙扣，可能在操场丢失", "操场看台", 1, 1),
    ]
    now = datetime.now()
    created_ids = []
    for idx, (title, desc, location, item_type, item_type_id) in enumerate(samples):
        cur.execute(
            """
            INSERT INTO item (user_id,item_type,item_type_id,title,description,status,location_detail,lost_found_time,contact_info,view_count)
            VALUES (%s,%s,%s,%s,%s,1,%s,%s,%s,0)
            """,
            (
                user_id,
                item_type,
                item_type_id,
                title,
                desc,
                location,
                (now - timedelta(days=idx)).strftime("%Y-%m-%d %H:%M:%S"),
                "vx_test_001",
            ),
        )
        item_id = cur.lastrowid
        created_ids.append(item_id)
        cur.execute(
            "INSERT INTO item_image (item_id,image_url,sort_order) VALUES (%s,%s,0)",
            (item_id, "http://127.0.0.1:8090/uploads/demo-item.jpg"),
        )

    # 插入消息样例
    for item_id in created_ids[:2]:
        cur.execute(
            "INSERT INTO message (from_user_id,to_user_id,item_id,content,is_read) VALUES (%s,%s,%s,%s,0)",
            (user_id, user_id, item_id, f"关于物品#{item_id}，有新的线索，请查看。"),
        )

    print(f"Seed completed. user_id={user_id}, items={len(created_ids)}")
    conn.close()


if __name__ == "__main__":
    run()
