import os
import sys
from streamlit.web import cli as stcli

# Vercel'in aradığı o kutsal nesne: app
def app(environ, start_response):
    sys.argv = ["streamlit", "run", "yapay.py", "--server.port", "8000", "--server.address", "0.0.0.0"]
    stcli.main()
