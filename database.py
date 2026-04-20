import sqlite3
import time
import datetime

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول بنظام الاستهلاك اليومي والترقية
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    balance_used INTEGER DEFAULT 0,
    last_reset TEXT,
    expire_at INTEGER DEFAULT 0
)
""")
conn.commit()

# مخزن الإعلانات المؤقت في الذاكرة (يحذف عند إعادة تشغيل السيرفر أو بعد 24 ساعة)
current_ads = {
    "reward_link": None,
    "reward_expiry": 0,
    "interstitial_link": None,
    "interstitial_expiry": 0
}

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, last_reset) VALUES (?, ?)", 
                       (user_id, str(datetime.date.today())))
        conn.commit()
        return get_user(user_id)

    user_data = {
        "user_id": user[0],
        "plan": user[1],
        "balance_used": user[2],
        "last_reset": user[3],
        "expire_at": user[4]
    }
    
    # 1. التحقق من انتهاء الاشتراك
    if user_data["expire_at"] != 0 and time.time() > user_data["expire_at"]:
        update_plan(user_id, 'free', 0)
        user_data["plan"] = 'free'

    # 2. إعادة تعيين الاستهلاك اليومي (تصفير الرصيد المستخدم عند بداية يوم جديد)
    today = str(datetime.date.today())
    if user_data["last_reset"] != today:
        cursor.execute("UPDATE users SET balance_used=0, last_reset=? WHERE user_id=?", (today, user_id))
        conn.commit()
        user_data["balance_used"] = 0

    return user_data

def update_plan(user_id, plan, days=30):
    expire = int(time.time()) + (int(days) * 86400) if int(days) > 0 else 0
    cursor.execute("UPDATE users SET plan=?, expire_at=? WHERE user_id=?", (plan, expire, user_id))
    conn.commit()

def log_consumption(user_id, mb_used):
    cursor.execute("UPDATE users SET balance_used = balance_used + ? WHERE user_id=?", (mb_used, user_id))
    conn.commit()

def add_balance(user_id, amount):
    # وظيفة لزيادة الرصيد (عبر تقليل المستهلك)
    cursor.execute("UPDATE users SET balance_used = balance_used - ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def get_stats():
    cursor.execute("SELECT plan, COUNT(*) FROM users GROUP BY plan")
    return cursor.fetchall()

# --- نظام الإعلانات ---
def set_ad(ad_type, link):
    current_ads[ad_type] = link
    current_ads[f"{ad_type}_expiry"] = time.time() + 86400

def get_active_ad(ad_type):
    if current_ads[ad_type] and time.time() > current_ads[f"{ad_type}_expiry"]:
        current_ads[ad_type] = None
    return current_ads[ad_type]
