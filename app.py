from flask import Flask, request
import requests
import os

app = Flask(__name__)

# رابط الويبهوك الخاص بك في هوجينج فيس
HF_URL = "https://hf.space"

@app.route('/')
def home():
    return "✅ Render Proxy is Online!", 200

@app.route('/bridge', methods=['POST'])
def bridge():
    """استلام الرسالة وتمريرها فوراً"""
    try:
        data = request.get_json()
        # تمرير الطلب لهوجينج فيس مع وقت انتظار 10 ثوانٍ
        requests.post(HF_URL, json=data, timeout=10)
        return "ok", 200
    except Exception as e:
        print(f"⚠️ Error forwarding: {e}")
        return "ok", 200 # نرد بـ ok دائماً لكي لا يغضب تيليجرام

if __name__ == "__main__":
    # ريندر يطلب التشغيل على المنفذ الذي يحدده هو
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
