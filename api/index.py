import os
import sys

# Streamlit'i Vercel içinde başlatacak sihirli tetikleyici
from streamlit.web import cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "yapay.py", "--server.port", "8000", "--server.address", "0.0.0.0"]
    sys.exit(stcli.main())
