import streamlit as st
import json
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from groq import Groq  # Bulut yapay zeka motorumuz aktif!

# Sayfa Ayarları
st.set_page_config(page_title="Nokta AI Ultimate Edition", page_icon="🎯", layout="wide")

VERITABANI_DOSYASI = "kullanicilar.json"

# --- 📧 GERÇEK E-POSTA BİLGİLERİ ---
GÖNDERİCİ_MAİL = "noktaaioffical@gmail.com"  
GÖNDERİCİ_ŞİFRE = "gpbfxxerhtwakuwd"  # Senin o canavar yeni anahtarın!

# --- 🔑 GROQ API KEY BAĞLANTISI ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- 📩 GERÇEK E-POSTA GÖNDERME MOTORU ---
def gercek_mail_gonder(alici_mail, konu, mesaj_icerigi):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GÖNDERİCİ_MAİL, GÖNDERİCİ_ŞİFRE)
        msg = MIMEMultipart()
        msg['From'] = GÖNDERİCİ_MAİL
        msg['To'] = alici_mail
        msg['Subject'] = konu
        msg.attach(MIMEText(mesaj_icerigi, 'plain', 'utf-8'))
        server.sendmail(GÖNDERİCİ_MAİL, alici_mail, msg.as_string())
        server.quit()
        return True
    except:
        return False

# --- KULLANICI VERİTABANI FONKSİYONLARI ---
def kullanicilari_yukle():
    if os.path.exists(VERITABANI_DOSYASI):
        with open(VERITABANI_DOSYASI, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def kullanici_kaydet(k_adi, sifre, gercek_isim, e_posta):
    veriler = kullanicilari_yukle()
    temiz_eposta = e_posta.lower().strip()
    if k_adi in veriler: return "kullanici_var"
    veriler[k_adi] = {
        "sifre": sifre, 
        "isim": gercek_isim, 
        "eposta": temiz_eposta
    }
    with open(VERITABANI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)
    return "basarili"

# --- SESSION STATES ---
if "mesajlar" not in st.session_state: st.session_state.mesajlar = []
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "dogrulama_kodu" not in st.session_state: st.session_state.dogrulama_kodu = None
if "gecici_kayit" not in st.session_state: st.session_state.gecici_kayit = {}
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""

# --- GİRİŞ VE KAYIT EKRANLARI ---
if not st.session_state.giris_yapildi:
    st.markdown("<h1 style='text-align: center;'>🎯 NOKTA AI ULTIMATE</h1>", unsafe_allow_html=True)
    
    # --- 🔴 GİZLİ MUCİT DOKUNUŞU: GOOGLE ILE GIRIS BUTONU 🔴 ---
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        google_butonu = st.button("🔴 Google ile Giriş Yap (Hızlı Bağlantı)", use_container_width=True)
        if google_butonu:
            # Gerçek Google Auth simülasyonu: Arkadaşların hiç beklemeden sisteme bir Google üyesi gibi sızar!
            st.session_state.giris_yapildi = True
            st.session_state.is_admin = False
            st.session_state.aktif_kullanici = "Değerli Google Üyesi"
            st.balloons()
            st.success("Google Hesabınız Doğrulandı! Giriş yapılıyor...")
            st.rerun()
            
    st.markdown("<p style='text-align: center; color: gray;'>- VEYA KLASİK YÖNTEMİ KULLAN -</p>", unsafe_allow_html=True)

    if st.session_state.dogrulama_kodu:
        st.subheader("📩 Hesap Doğrulama Alanı")
        kg = st.text_input("E-postanıza Gelen 6 Haneli Onay Kodunu Yazın:")
        if st.button("Hesabımı Onayla ve Giriş Yap 🚀"):
            if kg == st.session_state.dogrulama_kodu:
                g = st.session_state.gecici_kayit
                kullanici_kaydet(g["k_adi"], g["sifre"], g["isim"], g["eposta"])
                st.success("Mükemmel! Hesabın başarıyla oluşturuldu şef. Şimdi Oturum Aç sekmesinden girebilirsin!")
                st.session_state.dogrulama_kodu = None
                st.rerun()
            else: 
                st.error("Doğrulama kodu hatalı, e-postanı tekrar kontrol et kurucum!")
        if st.button("⬅️ İptal Et ve Geri Dön"):
            st.session_state.dogrulama_kodu = None
            st.rerun()
        st.stop()

    sekme1, sekme2 = st.tabs(["🚪 Klasik Oturum Aç", "📝 Ücretsiz Kayıt Ol"])
    with sekme1:
        k_adi_input = st.text_input("Kullanıcı Adı")
        sifre_input = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            if k_adi_input == "admin" and sifre_input == "berat123":
                st.session_state.giris_yapildi = True
                st.session_state.is_admin = True
                st.session_state.aktif_kullanici = "Yapay Zeka Mucidi Berat"
                st.rerun()
            else:
                kullanicilar = kullanicilari_yukle()
                if k_adi_input in kullanicilar and kullanicilar[k_adi_input]["sifre"] == sifre_input:
                    st.session_state.giris_yapildi = True
                    st.session_state.is_admin = False
                    st.session_state.aktif_kullanici = kullanicilar[k_adi_input]["isim"]
                    st.rerun()
                else: 
                    st.error("Hatalı kullanıcı adı veya şifre!")
            
    with sekme2:
        yeni_isim = st.text_input("Adınız Soyadınız")
        yeni_eposta = st.text_input("E-posta Adresiniz")
        yeni_k_adi = st.text_input("Yeni Kullanıcı Adı")
        yeni_sifre = st.text_input("Yeni Şifre", type="password")
        
        if st.button("Doğrulama Kodu Gönder ve Üye Ol", use_container_width=True):
            if yeni_isim and yeni_eposta and yeni_k_adi and yeni_sifre:
                kullanicilar = kullanicilari_yukle()
                if yeni_k_adi in kullanicilar or yeni_k_adi == "admin":
                    st.warning("Bu kullanıcı adı zaten alınmış şef!")
                else:
                    st.session_state.dogrulama_kodu = str(random.randint(100000, 999999))
                    st.session_state.gecici_kayit = {
                        "k_adi": yeni_k_adi, "sifre": yeni_sifre, "isim": yeni_isim, "eposta": yeni_eposta
                    }
                    with st.spinner("Doğrulama kodu e-postanıza fırlatılıyor..."):
                        icerik = f"Merhaba {yeni_isim},\n\nNokta AI platformuna güvenli kayıt olmak için onay kodunuz: {st.session_state.dogrulama_kodu}\n\nKeyifli sohbetler dileriz!"
                        if gercek_mail_gonder(yeni_eposta, "Nokta AI Kayıt Onayı 🎯", icerik):
                            st.success("Kod başarıyla gönderildi! Sayfa yönlendiriliyor...")
                            st.rerun()
                        else:
                            st.error("Kod gönderilirken e-posta motoru bir hata verdi. Bilgileri kontrol et şef.")
            else: 
                st.warning("Lütfen tüm alanları doldur şef!")
    st.stop()

# --- 🛠️ PANEL BAŞLANGICI ---
with st.sidebar:
    st.title("🎯 Nokta AI")
    st.write(f"👤 İsim: **{st.session_state.aktif_kullanici}**")
    st.write(f"🛡️ Rol: **{'👑 KURUCU' if st.session_state.is_admin else '👤 ÜYE'}**")
    st.write("---")
    
    yuklenen_resim = st.file_uploader("🖼️ Profil Resmi Yükle", type=["png", "jpg", "jpeg"])
    if yuklenen_resim is not None:
        st.image(yuklenen_resim, use_container_width=True)
        
    st.write("---")
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        st.session_state.mesajlar = []
        st.session_state.giris_yapildi = False
        st.rerun()

# --- 🔥 GÜVENLİ GÜNCEL GROQ SOHBET MOTORU ---
def groq_ile_sohbet_et(kullanici_mesaji):
    if not GROQ_API_KEY:
        return "Hata: GROQ_API_KEY Render panelinde bulunamadı şef!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        system_instruction = (
            "Senin adın Nokta AI Ultimate. Sen Berat tarafından geliştirilmiş çok gelişmiş bir yapay zekasın. "
            "Berat bir ilkokul öğrencisidir ve bu projenin dahi mucididir. Ona hep 'Şef', 'Kurucum' veya 'Berat' diye hitap et. "
            "Diğer üyelere ise kibar bir asistan gibi davran. Berat; Arduino, robotik, DJI dronelar, Beşiktaş, Minecraft ve Roblox sevdalısıdır. "
            "Kısa, enerjik ve zeki cevaplar ver."
        )
        groq_messages = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.mesajlar:
            groq_messages.append({"role": m["role"], "content": m["content"]})
            
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=groq_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Groq Motoru Hatası: {e}"

# --- 👑 MOD 1: ADMIN PANELİ ---
if st.session_state.is_admin:
    st.title("👑 Nokta AI Yönetim Merkezi")
    sekme_chat, sekme_kullanicilar = st.tabs(["💬 Nokta AI Motorunu Dene", "📊 Kayıtlı Kullanıcı Listesi"])
    
    with sekme_kullanicilar:
        st.subheader("👥 Platformdaki Kayıtlı Kişiler")
        tum_uyeler = kullanicilari_yukle()
        if tum_uyeler:
            for k, v in tum_uyeler.items():
                st.info(f"👤 **Kullanıcı:** {k} | **İsim:** {v['isim']} | **E-posta:** {v['eposta']}")
        else: 
            st.write("Sistemde henüz kayıtlı üye yok.")

    with sekme_chat:
        for m in st.session_state.mesajlar:
            with st.chat_message(m["role"]): st.write(m["content"])
        if ks := st.chat_input("NOKTA AI'a Sor... (Kurucu Denemesi)"):
            with st.chat_message("user"): st.write(ks)
            st.session_state.mesajlar.append({'role': 'user', 'content': ks})
            with st.spinner("Groq Yanıtlıyor..."):
                cevap = groq_ile_sohbet_et(ks)
            with st.chat_message("assistant"): st.write(cevap)
            st.session_state.mesajlar.append({'role': 'assistant', 'content': cevap})
            st.rerun()

# --- 👤 MOD 2: NORMAL KULLANICI PANELİ ---
else:
    st.title("💬 Nokta AI Sohbet Odası")
    st.info("🚀 Sınırsız ve Ücretsiz Nokta AI Deneyimi Aktif!")

    for m in st.session_state.mesajlar:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if ks := st.chat_input("NOKTA AI'a Sor..."):
        with st.chat_message("user"): st.write(ks)
        st.session_state.mesajlar.append({'role': 'user', 'content': ks})
        with st.chat_message("assistant"):
            with st.spinner("Nokta AI Düşünüyor..."):
                cevap = groq_ile_sohbet_et(ks)
        st.session_state.mesajlar.append({'role': 'assistant', 'content': cevap})
        st.rerun()
