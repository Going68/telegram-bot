import sqlite3, time

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    balance INTEGER DEFAULT 700,
    last_reset INTEGER,
    ads_claim INTEGER DEFAULT 0,
    expire_date INTEGER
)
""")
conn.commit()

PLANS = {"free":700,"iron":2000,"silver":5000,"gold":16000}

def get_user(uid):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    u = cursor.fetchone()
    if not u:
        cursor.execute(
            "INSERT INTO users (user_id,last_reset) VALUES (?,?)",
            (uid,int(time.time()))
        )
        conn.commit()
        return get_user(uid)
    return {
        "user_id":u[0],
        "plan":u[1],
        "balance":u[2],
        "last_reset":u[3],
        "ads_claim":u[4],
        "expire_date":u[5]
    }

def reset_daily(u):
    now = int(time.time())
    if now - (u["last_reset"] or 0) >= 86400:
        cursor.execute(
            "UPDATE users SET balance=?, last_reset=?, ads_claim=0 WHERE user_id=?",
            (PLANS[u["plan"]], now, u["user_id"])
        )
        conn.commit()

def add_balance(uid, amt):
    cursor.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amt,uid))
    conn.commit()

def update_plan(uid, plan, days=30):
    exp = int(time.time()) + days*86400
    cursor.execute("UPDATE users SET plan=?, expire_date=? WHERE user_id=?", (plan,exp,uid))
    conn.commit()

def check_expired(uid):
    u = get_user(uid)
    if u["expire_date"] and u["expire_date"] < int(time.time()):
        cursor.execute("UPDATE users SET plan='free', expire_date=NULL WHERE user_id=?", (uid,))
        conn.commit()
        return True
    return False