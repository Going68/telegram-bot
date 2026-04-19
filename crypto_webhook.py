from flask import Flask, request
import os
from database import update_plan

from telegram import Bot

app = Flask(__name__)

SECRET_KEY = "mysecret123"
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

@app.route("/crypto-webhook", methods=["POST"])
def webhook():
    data = request.json

    if not data:
        return "no data"

    if data.get("status") == "paid":

        payload = data.get("payload")

        if payload:
            try:
                user_id, plan, days, secret = payload.split(":")

                if secret != SECRET_KEY:
                    return "unauthorized"

                update_plan(int(user_id), plan, int(days))

                # إرسال إشعار للمستخدم
                bot.send_message(
                    chat_id=int(user_id),
                    text=f"🎉 تم تفعيل اشتراكك {plan} بنجاح!"
                )

                print(f"✅ تم ترقية {user_id} إلى {plan}")

            except Exception as e:
                print("Webhook error:", e)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)