from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- الرابط الدقيق والمضمون لهوجينج فيس ---
# ملاحظة: تم تجميع الرابط لضمان عدم حدوث نقص
HF_DOMAIN = "vhfg874-my-bot-master.hf.space"
HF_URL = f"https://{HF_DOMAIN}/webhook"

@app.route('/')
def home():
    return "✅ Render Proxy is Online and Ready!", 200

@app.route('/bridge', methods=['POST'])
def bridge():
    """استلام الرسالة من تيليجرام وقذفها لـ Hugging Face"""
    try:
        # استلام بيانات الرسالة (Update)
        data = request.get_json()
        
        # تمرير الرسالة فوراً
        response = requests.post(
            HF_URL, 
            json=data, 
            headers={"Content-Type": "application/json"},
            timeout=15  # وقت انتظار كافٍ لاستيقاظ السبيس
        )
        
        print(f"🚀 Forwarded to HF. Status: {response.status_code}")
        return "ok", 200
    except Exception as e:
        print(f"⚠️ Error during forwarding: {e}")
        return "ok", 200 # نرد بـ ok دائماً لتيليجرام لضمان الاستمرارية

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
