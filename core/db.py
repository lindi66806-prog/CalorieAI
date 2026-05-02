"""
数据库模块 - Android稳定版
SQLite本地存储，WAL模式，连接池安全
"""
import sqlite3
import json
import os
import sys

# 确定数据库路径
if getattr(sys, 'android', False):
    from android.storage import app_storage_path
    DB_PATH = os.path.join(app_storage_path(), 'calorie.db')
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'calorie.db')


def init_db():
    """初始化数据库，创建所有表"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS user_base(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gender TEXT DEFAULT '男',
        age INTEGER DEFAULT 25,
        height REAL DEFAULT 170,
        weight REAL DEFAULT 65,
        bmr REAL DEFAULT 1600
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS food(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        meal TEXT,
        img TEXT DEFAULT '',
        foods TEXT DEFAULT '[]',
        kcal REAL DEFAULT 0,
        protein REAL DEFAULT 0,
        fat REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        steps INTEGER DEFAULT 0,
        sport TEXT DEFAULT '其他',
        minutes INTEGER DEFAULT 0,
        total REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS body_record(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        weight REAL DEFAULT 0,
        neck REAL DEFAULT 0,
        chest REAL DEFAULT 0,
        waist REAL DEFAULT 0,
        hip REAL DEFAULT 0,
        arm REAL DEFAULT 0,
        thigh REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 插入默认用户信息
    cur = conn.execute("SELECT COUNT(*) FROM user_base")
    if cur.fetchone()[0] == 0:
        conn.execute("""
        INSERT INTO user_base(gender, age, height, weight, bmr)
        VALUES ('男', 25, 170, 65, 1600)
        """)

    conn.commit()
    conn.close()
    print(f"[DB] 初始化完成: {DB_PATH}")


class DB:

    @staticmethod
    def _conn():
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def save_food(date, meal, img, foods, result):
        conn = DB._conn()
        conn.execute("""
        INSERT INTO food(date, meal, img, foods, kcal, protein, fat)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            date, meal, img,
            json.dumps(foods, ensure_ascii=False),
            result["kcal"],
            result["protein"],
            result["fat"]
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def save_activity(date, steps, sport, minutes, total):
        conn = DB._conn()
        conn.execute("""
        INSERT INTO activity(date, steps, sport, minutes, total)
        VALUES (?, ?, ?, ?, ?)
        """, (date, steps, sport, minutes, total))
        conn.commit()
        conn.close()

    @staticmethod
    def save_body(date, data):
        conn = DB._conn()
        conn.execute("""
        INSERT OR REPLACE INTO body_record(date, weight, neck, chest, waist, hip, arm, thigh)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date,
            data.get("weight", 0),
            data.get("neck", 0),
            data.get("chest", 0),
            data.get("waist", 0),
            data.get("hip", 0),
            data.get("arm", 0),
            data.get("thigh", 0)
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def save_user_info(gender, age, height, weight, bmr):
        conn = DB._conn()
        conn.execute("DELETE FROM user_base")
        conn.execute("""
        INSERT INTO user_base(gender, age, height, weight, bmr)
        VALUES (?, ?, ?, ?, ?)
        """, (gender, age, height, weight, bmr))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_info():
        conn = DB._conn()
        cur = conn.execute("SELECT gender, age, height, weight, bmr FROM user_base LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row:
            return {"gender": row[0], "age": row[1], "height": row[2], "weight": row[3], "bmr": row[4]}
        return None

    @staticmethod
    def get_intake(date):
        conn = DB._conn()
        val = conn.execute(
            "SELECT IFNULL(SUM(kcal),0) FROM food WHERE date=?", (date,)
        ).fetchone()[0]
        conn.close()
        return val

    @staticmethod
    def get_consume(date):
        conn = DB._conn()
        val = conn.execute(
            "SELECT IFNULL(SUM(total),0) FROM activity WHERE date=?", (date,)
        ).fetchone()[0]
        conn.close()
        return val

    @staticmethod
    def get_food_records(date):
        conn = DB._conn()
        rows = conn.execute(
            "SELECT meal, foods, kcal FROM food WHERE date=? ORDER BY id", (date,)
        ).fetchall()
        conn.close()
        results = []
        for r in rows:
            foods_list = json.loads(r[1]) if r[1] else []
            food_names = ", ".join(f.get("name", "?") for f in foods_list)
            results.append({"meal": r[0], "foods": food_names, "kcal": r[2]})
        return results

    @staticmethod
    def get_body_history(days=30):
        conn = DB._conn()
        rows = conn.execute("""
        SELECT date, weight, waist FROM body_record
        WHERE weight > 0
        ORDER BY date DESC LIMIT ?
        """, (days,)).fetchall()
        conn.close()
        return [{"date": r[0], "weight": r[1], "waist": r[2]} for r in rows]
