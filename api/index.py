import os
import sys
import subprocess

# Vercel'in köşe bucak aradığı o "app" nesnesini tanımlıyoruz
def app(environ, start_response):
    # Streamlit'i arka planda bir alt işlem (subprocess) olarak tetikliyoruz
    cmd = [
        "streamlit", "run", "yapay.py", 
        "--server.port", "8000", 
        "--server.address", "0.0.0.0", 
        "--server.headless", "true"
    ]
    
    # Sunucuyu arka planda ayağa kaldırıyoruz
    subprocess.Popen(cmd)
    
    # Vercel'e "Her şey yolunda, sunucu başladı" yanıtı dönüyoruz
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, response_headers)
    return [b"Nokta AI Vercel Motoru Basariyla Tetiklendi! Siteniz hazirlaniyor..."]
