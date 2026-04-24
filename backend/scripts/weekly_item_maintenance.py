from datetime import datetime
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
    cur = conn.cursor(pymysql.cursors.DictCursor)
    now = datetime.now()
    week_tag = now.strftime("%Y-%W")

    cur.execute("SELECT * FROM item WHERE is_deleted=0 AND status=1")
    rows = cur.fetchall()
    remind_count = 0
    close_count = 0

    for item in rows:
        item_id = item["id"]
        user_id = item["user_id"]
        title = item["title"]
        expires_at = item["expires_at"]
        item_type = item["item_type"]
        status_text = "寻物是否已找回" if item_type == 1 else "招领是否已认领"
        remind_msg = f"[系统提醒周报 {week_tag}] 请确认“{title}”的状态：{status_text}"

        # 每周提醒（同一周只发一次）
        cur.execute(
            "SELECT COUNT(*) c FROM message WHERE item_id=%s AND to_user_id=%s AND content=%s",
            (item_id, user_id, remind_msg),
        )
        if cur.fetchone()["c"] == 0:
            cur.execute(
                "INSERT INTO message (from_user_id,to_user_id,item_id,content,is_read) VALUES (%s,%s,%s,%s,0)",
                (user_id, user_id, item_id, remind_msg),
            )
            remind_count += 1

        # 超过四周自动关闭
        if expires_at and expires_at < now:
            cur.execute("UPDATE item SET status=3, closed_at=%s WHERE id=%s", (now, item_id))
            close_count += 1

    print(f"weekly maintenance done: remind={remind_count}, auto_closed={close_count}")
    conn.close()


if __name__ == "__main__":
    run()
