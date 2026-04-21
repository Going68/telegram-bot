from flask import Flask, request
import requests

app = Flask(__name__)

# الرابط الدقيق لهوجينج فيس (تأكد من كتابته هكذا تماماً)
HF_URL = "https://vhfg874-my-bot-master.hf.space/webhook"

@app.route('/')
def home():
    return "Proxy is Alive!", 200

@app.route('/bridge', methods=['POST'])
def bridge():
    try:
        # استلام البيانات من تيليجرام
        data = request.get_json()
        
        # إرسالها لهوجينج فيس مع رأس بيانات (Header) صحيح
        response = requests.post(
            HF_URL, 
            json=data, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ تم التمرير لـ HF، رد السيرفر: {response.status_code}")
        return "ok", 200
    except Exception as e:
        print(f"❌ فشل التمرير: {e}")
        return "ok", 200 # نرد بـ ok لتيليجرام دائماً

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
