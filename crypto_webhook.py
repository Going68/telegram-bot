from flask import Flask, request
import os
from database import update_plan
from telegram import Bot
import asyncio

app = Flask(__name__)

# الإعدادات الأساسية
SECRET_KEY = "mysecret123"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# --- 1. مسار النبض (Keep-Alive) لضمان عدم نوم البوت ---
@app.route("/health")
def health():
    return "✅ Bot is alive and running!", 200

# --- 2. مسار استقبال الأموال من CryptoBot ---
@app.route("/crypto-webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data or data.get("status") != "paid":
        return "ignored", 200

    payload = data.get("payload")
    if payload:
        try:
            # التحليل: user_id:plan:days:secret
            user_id, plan, days, secret = payload.split(":")

            if secret != SECRET_KEY:
                return "unauthorized", 403

            # تحديث الخطة في قاعدة البيانات
            update_plan(int(user_id), plan, int(days))

            # إرسال إشعار للمستخدم والأدمن
            async def notify():
                async with bot:
                    await bot.send_message(chat_id=int(user_id), text=f"🎉 مبروك! تم تفعيل اشتراكك في الخطة ({plan}) لمدة {days} يوم.")
                    await bot.send_message(chat_id=ADMIN_ID, text=f"💰 دفع جديد!\nالمستخدم: {user_id}\nالخطة: {plan}\nالمدة: {days} يوم")
            
            asyncio.run(notify())
            return "ok", 200
        except Exception as e:
            print("Webhook Error:", e)

    return "ok", 200

if __name__ == "__main__":
    # تشغيل السيرفر على المنفذ 8000
    app.run(host="0.0.0.0", port=8000)
