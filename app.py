import os
import sys
import subprocess
from flask import Flask

# 1. Vercel'in köşe bucak aradığı o "app" nesnesini Flask ile yaratıyoruz!
app = Flask(__name__)

# 2. Vercel bu dosyayı tetiklediğinde Streamlit'i arka planda gizlice başlatıyoruz
try:
    cmd = [
        "streamlit", "run", "app.py", 
        "--server.port", "8000", 
        "--server.address", "0.0.0.0", 
        "--server.headless", "true"
    ]
    subprocess.Popen(cmd)
except Exception as e:
    print(f"Streamlit baslatilamadı: {e}")

# 3. Vercel ana sayfaya istek attığında ona "çalışıyorum" mesajı veriyoruz
@app.route('/')
def home():
    return "Nokta AI Vercel Uzerinde Flask/Streamlit Koprusuyle Aktif! Siteniz port 8000 uzerinde hazirlaniyor..."

@app.route('/<path:path>')
def catch_all(path):
    return f"{path} rotası Flask koprusunde."

if __name__ == "__main__":
    app.run(port=5000)
