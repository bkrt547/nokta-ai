import os
import sys
from streamlit.web import cli as stcli

# Vercel'in köşe bucak aradığı o "app" nesnesini burada tanımlıyoruz
def app(environ, start_response):
    # Streamlit'i arka planda tetikleyen ana mekanizma
    sys.argv = ["streamlit", "run", "yapay.py", "--server.port", "8000", "--server.address", "0.0.0.0"]
    stcli.main()
