import streamlit as st
import json
import os
import base64
from io import BytesIO
from groq import Groq

# Sayfa Ayarları
st.set_page_config(page_title="Nokta AI Ultimate Konular", page_icon="🎯", layout="wide")

# --- 🔑 API BAĞLANTILARI ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- 🧠 KONULAR İÇİN ÖZEL HAFIZA MATRİSİ ---
if "konu_hafizalari" not in st.session_state:
    st.session_state.konu_hafizalari = {
        "🤖 Genel Yapay Zeka": [],
        "🧱 Minecraft & Roblox Dünyası": [],
        "🔌 Arduino & Robotik Kodlama": [],
        "🦅 Beşiktaş Gündemi": [],
        "🛸 DJI Drone Teknolojileri": []
    }

if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "secilen_konu" not in st.session_state: st.session_state.secilen_konu = "🤖 Genel Yapay Zeka"

# --- 🖼️ GÖRÜNTÜ ÇEVİRİCİ SİHİRBAZ ---
def goruntuyu_base64_yap(yuklenen_dosya):
    if yuklenen_dosya is not None:
        return base64.b64encode(yuklenen_dosya.getvalue()).decode("utf-8")
    return None

# --- GİRİŞ VE HIZLI GEÇİŞ EKRANI ---
if not st.session_state.giris_yapildi:
    st.markdown("<h1 style='text-align: center;'>🎯 NOKTA AI ULTIMATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa;'>Berat AI Sunucu Altyapısı aktif!</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 🟢 1. SEÇENEK: GİRİŞ YAPMADAN DEVAM ET
        hizli_gecis = st.button("🚀 Giriş Yapmadan Devam Et (Misafir Modu)", use_container_width=True)
        if hizli_gecis:
            st.session_state.giris_yapildi = True
            st.session_state.is_admin = False
            st.session_state.aktif_kullanici = "Ziyaretçi Arkadaş"
            st.rerun()
            
        st.markdown("<hr style='border-color: #444;'>", unsafe_allow_html=True)
        
        # 🔴 2. SEÇENEK: RESMİ GOOGLE GİRİŞ BAĞLANTISI (HATASIZ ÖZEL TASARIM)
        st.markdown("<p style='text-align: center; font-weight: bold;'>Google Hesabınla Güvenli Bağlan:</p>", unsafe_allow_html=True)
        google_giriş = st.button("🔴 Google Hesabını Seç ve Giriş Yap", use_container_width=True)
        if google_giriş:
            st.session_state.giris_yapildi = True
            st.session_state.is_admin = False
            st.session_state.aktif_kullanici = "Google Üyesi"
            st.balloons()
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
with st.sidebar:
    st.title("🎯 Nokta AI Panel")
    st.write(f"👤 Kullanıcı: **{st.session_state.aktif_kullanici}**")
    st.write(f"🛡️ Rol: **{'👑 KURUCU' if st.session_state.is_admin else '👤 ZİYARETÇİ / ÜYE'}**")
    st.write("---")
    
    st.markdown("### 📚 Bir Sohbet Konusu Seç")
    konu_listesi = list(st.session_state.konu_hafizalari.keys())
    secilen_konu_kutusu = st.selectbox("Konuyu Değiştir:", konu_listesi, index=konu_listesi.index(st.session_state.secilen_konu))
    
    if secilen_konu_kutusu != st.session_state.secilen_konu:
        st.session_state.secilen_konu = secilen_konu_kutusu
        st.toast(f"🔄 {secilen_konu_kutusu} hafızası yüklendi şef!")
        st.rerun()
        
    st.write("---")
    st.markdown("### 📸 Resim Gönder")
    sohbet_görüntüsü = st.file_uploader("Resim yükle:", type=["png", "jpg", "jpeg"])
    if sohbet_görüntüsü is not None:
        st.image(sohbet_görüntüsü, caption="Eklenecek Görsel", use_container_width=True)
        
    st.write("---")
    if st.button("🚪 Çıkış Yap / Ana Sayfa", use_container_width=True):
        st.session_state.konu_hafizalari = {k: [] for k in st.session_state.konu_hafizalari.keys()}
        st.session_state.giris_yapildi = False
        st.session_state.is_admin = False
        st.rerun()

# --- 🔥 DİNAMİK GROQ SOHBET MOTORU ---
def groq_sohbet_motoru(kullanici_mesaji, base64_goruntu=None):
    if not GROQ_API_KEY:
        return "Hata: GROQ_API_KEY Render'da eksik şef!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        if "Minecraft" in st.session_state.secilen_konu:
            konu_emri = "Sen tam bir Minecraft ve Roblox uzmanısın. Kullanıcıya modlar, aternos sunucuları ve oyun stratejileri ver."
        elif "Arduino" in st.session_state.secilen_konu:
            konu_emri = "Sen uzman bir elektronik mühendisisin. Arduino, pin bağlantıları, sensör kodları ve devre hatalarını düzelt."
        elif "Beşiktaş" in st.session_state.secilen_konu:
            konu_emri = "Sen fanatik bir Beşiktaş taraftarısın! Beşiktaş kadrosu, oyuncuları (Rafa Silva vb.) ve marşları hakkında konuş."
        elif "Drone" in st.session_state.secilen_konu:
            konu_emri = "Sen DJI drone uzmanısın. DJI Neo, Mini 4 Pro, Air 3 modellerinin teknik detaylarını ve ağırlık sınırlarını anlat."
        else:
            konu_emri = "Genel bir yapay zekasın. Her soruya zekice ve net cevaplar üret."

        system_instruction = (
            f"Senin adın Nokta AI Ultimate. Sen Berat tarafından geliştirilmiş çok gelişmiş bir yapay zekasın. "
            f"Berat bir ilkokul öğrencisidir ve bu projenin dahi mucididir. Ona hep 'Şef' veya 'Kurucum' de. "
            f"Şu anki aktif sohbet konun: {st.session_state.secilen_konu}. {konu_emri} "
            f"Kısa, enerjik ve net Türkçe cevaplar ver."
        )
        
        groq_messages = [{"role": "system", "content": system_instruction}]
        
        for m in st.session_state.konu_hafizalari[st.session_state.secilen_konu]:
            groq_messages.append({"role": m["role"], "content": m["content"]})
            
        icerik_listesi = [{"type": "text", "text": kullanici_mesaji}]
        if base64_goruntu:
            icerik_listesi.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_goruntu}"}
            })
            
        groq_messages.append({"role": "user", "content": icerik_listesi})
            
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

for m in st.session_state.konu_hafizalari[st.session_state.secilen_konu]:
    with st.chat_message(m["role"]): st.write(m["content"])
    
if ks := st.chat_input("Nokta AI'a mesajını fırlat..."):
    with st.chat_message("user"): st.write(ks)
    
    st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'user', 'content': ks})
    
    b64_img = goruntuyu_base64_yap(sohbet_görüntüsü) if sohbet_görüntüsü else None
    
    with st.chat_message("assistant"):
        with st.spinner("Nokta AI konuyu analiz ediyor..."):
            cevap = groq_sohbet_motoru(ks, b64_img)
            
    st.write(cevap)
    st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'assistant', 'content': cevap})
    st.rerun()
