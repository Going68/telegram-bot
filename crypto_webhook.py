from flask import Flask, request
import os
from database import update_plan
from telegram import Bot
import asyncio

app = Flask(__name__)
SECRET_KEY = "mysecret123"
ADMIN_ID = int(os.getenv("ADMIN_ID"))
bot = Bot(token=os.getenv("BOT_TOKEN"))

@app.route("/crypto-webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and data.get("status") == "paid":
        payload = data.get("payload")
        if payload:
            try:
                user_id, plan, days, secret = payload.split(":")
                if secret == SECRET_KEY:
                    update_plan(int(user_id), plan, int(days))
                    
                    # إشعار للمستخدم
                    asyncio.run(bot.send_message(chat_id=int(user_id), text=f"🎉 تم تفعيل اشتراكك {plan} لمدة {days} يوم بنجاح!"))
                    
                    # إشعار للأدمن (أنت)
                    asyncio.run(bot.send_message(chat_id=ADMIN_ID, text=f"💰 اشتراك جديد!\nالمستخدم: {user_id}\nالخطة: {plan}\nالمدة: {days} يوم"))
            except Exception as e:
                print("Webhook error:", e)
    return "ok"
