import streamlit as st
import json
import os
import base64
from io import BytesIO
from groq import Groq
from streamlit_google_auth import Authenticate

# Sayfa Ayarları
st.set_page_config(page_title="Nokta AI Ultimate Konular", page_icon="🎯", layout="wide")

VERITABANI_DOSYASI = "kullanicilar.json"

# --- 🔑 API BAĞLANTILARI ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "TEST_MODU")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "TEST_MODU")

# Google Kimlik Doğrulayıcı
authenticator = Authenticate(
    secret_key="nokta_ai_gizli_anahtar_99",
    cookie_name="nokta_ai_oauth",
    cookie_expiry_days=30,
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri="https://nokta-ai.onrender.com",
)

authenticator.check_authentification()

# --- SESSION STATES ---
if "mesajlar" not in st.session_state: st.session_state.mesajlar = []
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "secilen_konu" not in st.session_state: st.session_state.secilen_konu = "Genel Sohbet"

# --- 🖼️ GÖRÜNTÜ ÇEVİRİCİ SİHİRBAZ ---
def goruntuyu_base64_yap(yuklenen_dosya):
    if yuklenen_dosya is not None:
        return base64.b64encode(yuklenen_dosya.getvalue()).decode("utf-8")
    return None

# --- GİRİŞ VE HIZLI GEÇİŞ EKRANI ---
if not st.session_state.giris_yapildi and not st.session_state.get("connected", False):
    st.markdown("<h1 style='text-align: center;'>🎯 NOKTA AI ULTIMATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa;'>Berat AI Sunucu Altyapısı</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 🟢 1. SEÇENEK: GİRİŞ YAPMADAN DEVAM ET BUTONU
        hizli_gecis = st.button("🚀 Giriş Yapmadan Devam Et (Misafir Modu)", use_container_width=True)
        if hizli_gecis:
            st.session_state.giris_yapildi = True
            st.session_state.is_admin = False
            st.session_state.aktif_kullanici = "Ziyaretçi Arkadaş"
            st.rerun()
            
        st.markdown("<hr style='border-color: #444;'>", unsafe_allow_html=True)
        
        # 🔴 2. SEÇENEK: RESMİ GOOGLE GİRİŞİ
        st.markdown("<p style='text-align: center; font-weight: bold;'>Google Hesabınla Bağlan:</p>", unsafe_allow_html=True)
        authenticator.login()
        if st.session_state.get("connected", False):
            st.session_state.giris_yapildi = True
            st.session_state.is_admin = False
            st.session_state.aktif_kullanici = st.session_state.get("user_info", {}).get("name", "Üye")
            st.rerun()
            
        st.markdown("<hr style='border-color: #444;'>", unsafe_allow_html=True)
        
        # 👑 3. SEÇENEK: KURUCU GİRİŞİ
        k_adi_input = st.text_input("Kurucu Kullanıcı Adı")
        sifre_input = st.text_input("Kurucu Şifresi", type="password")
        if st.button("Kurucu Panelini Aç", use_container_width=True):
            if k_adi_input == "admin" and sifre_input == "berat123":
                st.session_state.giris_yapildi = True
                st.session_state.is_admin = True
                st.session_state.aktif_kullanici = "Yapay Zeka Mucidi Berat"
                st.rerun()
            else:
                st.error("Kurucu şifresi hatalı şef!")
    st.stop()

# --- 🛠️ PANEL İÇİ VE KONU SEÇİM ALANI ---
if st.session_state.get("connected", False) and not st.session_state.aktif_kullanici:
    st.session_state.aktif_kullanici = st.session_state.get("user_info", {}).get("name", "Google Üyesi")

with st.sidebar:
    st.title("🎯 Nokta AI Panel")
    st.write(f"👤 Kullanıcı: **{st.session_state.aktif_kullanici}**")
    st.write(f"🛡️ Rol: **{'👑 KURUCU' if st.session_state.is_admin else '👤 ZİYARETÇİ / ÜYE'}**")
    st.write("---")
    
    # 🔥 İŞTE O İSTEDİĞİN ÖZEL KONULAR ALANI 🔥
    st.markdown("### 📚 Bir Sohbet Konusu Seç")
    konu_listesi = ["🤖 Genel Yapay Zeka", "🧱 Minecraft & Roblox Dünyası", "🔌 Arduino & Robotik Kodlama", "🦅 Beşiktaş Gündemi", "🛸 DJI Drone Teknolojileri"]
    secilen_konu_kutusu = st.selectbox("Konuyu Değiştir:", konu_listesi)
    
    # Konu değiştiğinde hafızayı temizle ki yapay zeka yeni moda adapte olsun
    if secilen_konu_kutusu != st.session_state.secilen_konu:
        st.session_state.secilen_konu = secilen_konu_kutusu
        st.session_state.mesajlar = []
        st.toast(f"🔄 {secilen_konu_kutusu} moduna geçiş yapıldı şef!")
        
    st.write("---")
    st.markdown("### 📸 Resim Gönder")
    sohbet_görüntüsü = st.file_uploader("Resim yükle:", type=["png", "jpg", "jpeg"])
    if sohbet_görüntüsü is not None:
        st.image(sohbet_görüntüsü, caption="İklenecek Görsel", use_container_width=True)
        
    st.write("---")
    if st.button("🚪 Çıkış Yap / Ana Sayfa", use_container_width=True):
        if st.session_state.get("connected", False):
            authenticator.logout()
        st.session_state.mesajlar = []
        st.session_state.giris_yapildi = False
        st.session_state.is_admin = False
        st.rerun()

# --- 🔥 DİNAMİK GROQ SOHBET MOTORU FONKSİYONU ---
def groq_sohbet_motoru(kullanici_mesaji, base64_goruntu=None):
    if not GROQ_API_KEY:
        return "Hata: GROQ_API_KEY Render'da eksik şef!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Konuya göre yapay zekaya verilecek gizli emirler (System Prompt)
        if "Minecraft" in st.session_state.secilen_konu:
            konu_emri = "Sen tam bir Minecraft ve Roblox uzmanısın. Kullanıcıya modlar, aternos sunucuları, taktikler ve oyun stratejileri ver."
        elif "Arduino" in st.session_state.secilen_konu:
            konu_emri = "Sen uzman bir elektronik ve robotik mühendisisin. Arduino, sensor, röle, buzzer ve kodlama hatalarını tamir et."
        elif "Beşiktaş" in st.session_state.secilen_konu:
            konu_emri = "Sen koyu bir Beşiktaş taraftarısın! Beşiktaş kadrosu, marşları ve şampiyonlukları hakkında coşkulu cevaplar ver."
        elif "Drone" in st.session_state.secilen_konu:
            konu_emri = "Sen DJI drone uzmanısın. Neo, Mini 4 Pro, Air 3 modellerinin ağırlıkları, özellikleri ve uçuş kurallarını anlat."
        else:
            konu_emri = "Genel bir yapay zekasın. Her soruya zekice cevaplar üret."

        system_instruction = (
            f"Senin adın Nokta AI Ultimate. Sen Berat tarafından geliştirilmiş çok gelişmiş bir yapay zekasın. "
            f"Berat bir ilkokul öğrencisidir ve bu projenin dahi kurucusudur. Ona hep 'Şef' veya 'Kurucum' de. "
            f"Şu anki aktif sohbet modun: {st.session_state.secilen_konu}. {konu_emri} "
            f"Kısa, enerjik ve net Türkçe cevaplar ver."
        )
        
        icerik_listesi = [{"type": "text", "text": kullanici_mesaji}]
        if base64_goruntu:
            icerik_listesi.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_goruntu}"}
            })
            
        groq_messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": icerik_listesi}
        ]
            
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=groq_messages,
            temperature=0.6,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Bağlantı Hatası: {e}"

# --- 💬 SOHBET ODASI EKRANI ---
st.title(f"💬 Nokta AI Odası: {st.session_state.secilen_konu}")
st.caption(f"🎯 Şu an '{st.session_state.secilen_konu}' modunda konuşuyorsun. Sol menüden konuyu değiştirebilirsin.")

for m in st.session_state.mesajlar:
    with st.chat_message(m["role"]): st.write(m["content"])
    
if ks := st.chat_input("Nokta AI'a mesajını fırlat..."):
    with st.chat_message("user"): st.write(ks)
    st.session_state.mesajlar.append({'role': 'user', 'content': ks})
    
    b64_img = goruntuyu_base64_yap(sohbet_görüntüsü) if sohbet_görüntüsü else None
    
    with st.chat_message("assistant"):
        with st.spinner("Nokta AI konuyu analiz ediyor..."):
            cevap = groq_sohbet_motoru(ks, b64_img)
            
    st.write(cevap)
    st.session_state.mesajlar.append({'role': 'assistant', 'content': cevap})
    st.rerun()
