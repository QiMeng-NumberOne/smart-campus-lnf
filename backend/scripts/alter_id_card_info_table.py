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
        """
        CREATE TABLE IF NOT EXISTS id_card_info (
            id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            item_id BIGINT UNSIGNED NOT NULL UNIQUE,
            name_plain VARCHAR(64) NOT NULL,
            id_no_enc VARCHAR(1024) NULL,
            id_no_last4 VARCHAR(8) NULL,
            address_enc VARCHAR(2048) NULL,
            source VARCHAR(16) DEFAULT 'manual',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            KEY idx_name_plain (name_plain),
            CONSTRAINT fk_id_card_item FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    print("id_card_info table ready")
    conn.close()


if __name__ == "__main__":
    run()
