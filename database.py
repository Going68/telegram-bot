import sqlite3
import time

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجدول
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    balance INTEGER DEFAULT 0,
    ads_claim INTEGER DEFAULT 0,
    expire_at INTEGER DEFAULT 0
)
""")

conn.commit()

# ===== جلب المستخدم =====
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return get_user(user_id)

    return {
        "user_id": user[0],
        "plan": user[1],
        "balance": user[2],
        "ads_claim": user[3],
        "expire_at": user[4]
    }

# ===== تحديث الخطة =====
def update_plan(user_id, plan, days=30):
    expire = int(time.time()) + (days * 86400)

    cursor.execute("""
    UPDATE users
    SET plan=?, expire_at=?
    WHERE user_id=?
    """, (plan, expire, user_id))

    conn.commit()

# ===== رصيد =====
def add_balance(user_id, amount):
    cursor.execute("""
    UPDATE users
    SET balance = balance + ?
    WHERE user_id=?
    """, (amount, user_id))

    conn.commit()

# ===== إعادة تعيين يومي =====
def reset_daily(user):
    import datetime

    today = datetime.date.today()

    if "last_reset" not in user:
        return

    # بسيط الآن (تقدر تطوره لاحقًا)