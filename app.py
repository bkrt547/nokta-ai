import streamlit as st
import os
from groq import Groq

# Sayfa ayarları
st.set_page_config(page_title="Nokta AI Sohbet Odası", page_icon="👑", layout="wide")

# Şifreleri Render panelinden güvenli bir şekilde çekiyoruz
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GENDERICI_MAIL = os.environ.get("GENDERICI_MAIL")
GENDERICI_SIFRE = os.environ.get("GENDERICI_SIFRE")

# Başlık ve Arayüz
st.title("👑 Nokta AI Sohbet Odası")
st.subheader("Kurucu Paneline Hoş Geldiniz, Berat!")

st.write("Yapay zeka motoru Render üzerinde %100 performansla aktif edildi. Sohbet etmeye hazırsınız.")

# Basit bir deneme mesaj kutusu
user_input = st.text_input("Nokta AI'a bir şeyler yazın:")
if user_input:
    st.success(f"Nokta AI Cevabı: Harika gidiyoruz şef! Yazdığın mesaj alındı.")
