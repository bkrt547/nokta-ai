import os
import sys
import subprocess
from flask import Flask, Response

app = Flask(__name__)

# Vercel projeyi başlattığı an Streamlit'i arka planda headless (arayüzsüz sunucu) olarak tetikliyoruz
try:
    # Eğer önceden kalma bir süreç varsa çakışmasın diye portu ve ayarları netleştiriyoruz
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"]
    
    cmd = ["streamlit", "run", "app.py", "--server.headless", "true"]
    # Süreci arka planda tamamen bağımsız başlatıyoruz
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    print(f"Streamlit köprüsü başlatılamadı: {e}")

@app.route('/')
def home():
    # Vercel ana sayfaya gelindiğinde, arka planda dönen Streamlit arayüzünü Flask üzerinden ekrana basacak köprü
    return """
    <html>
        <head>
            <title>Nokta AI Sohbet Odası</title>
            <style>body, html {margin: 0; padding: 0; height: 100%; overflow: hidden;}</style>
        </head>
        <body>
            <iframe src="http://localhost:8501" width="100%" height="100%" style="border:none;"></iframe>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(port=5000)
