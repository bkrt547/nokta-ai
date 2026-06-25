import streamlit as st
import json
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# İnternet üzerinden çalışan yapay zeka kütüphanesi
try:
    from groq import Groq
except ImportError:
    os.system("pip install groq")
    from groq import Groq

# Sayfa Ayarları
st.set_page_config(page_title="Nokta AI Ultimate Cloud", page_icon="🎯", layout="wide")

VERITABANI_DOSYASI = "kullanicilar.json"
HAFIZA_DOSYASI = "yapay_zekahafiza.json"

# --- 🔐 GÜVENLİK AYARLARI (STREAMLIT CLOUD İÇİN) ---
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    GÖNDERİCİ_MAİL = st.secrets["GENDERICI_MAIL"]
    GÖNDERİCİ_ŞİFRE = st.secrets["GENDERICI_SIFRE"]
else:
    GROQ_KEY = ""
    GÖNDERİCİ_MAİL = "noktaaioffical@gmail.com"
    GÖNDERİCİ_ŞİFRE = "pxpxynxaxkictlew"

# Yapay Zeka Bulut Motorunu Başlat
try:
    client = Groq(api_key=GROQ_KEY)
except:
    client = None

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
            return json.load(f)
    return {}

def kullanici_kaydet(k_adi, sifre, gercek_isim, e_posta, dogum_tarihi):
    veriler = kullanicilari_yukle()
    temiz_eposta = e_posta.lower().strip()
    if k_adi in veriler: return "kullanici_var"
    veriler[k_adi] = {
        "sifre": sifre, 
        "isim": gercek_isim, 
        "eposta": temiz_eposta, 
        "dogum_tarihi": str(dogum_tarihi),
        "dogum_gunu_kutlandi_yil": ""
    }
    with open(VERITABANI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)
    return "basarili"

# --- 🎂 OTOMATİK DOĞUM GÜNÜ KONTROL MOTORU ---
def otomatik_dogum_gunu_kontrol():
    veriler = kullanicilari_yukle()
    bugun = datetime.today().strftime('%m-%d')
    bu_yil = str(datetime.today().year)
    
    guncelleme_var = False
    for k_adi, bilgi in veriler.items():
        if "dogum_tarihi" in bilgi and bilgi["dogum_tarihi"]:
            try:
                dt = datetime.strptime(bilgi["dogum_tarihi"], "%Y-%m-%d")
                if dt.strftime('%m-%d') == bugun:
                    if bilgi.get("dogum_gunu_kutlandi_yil") != bu_yil:
                        icerik = f"Merhaba {bilgi['isim']},\n\n🎂 Bugün senin doğum günün! Nokta AI ailesi olarak yeni yaşını kutlar, sevdiklerinle birlikte sağlıklı, mutlu ve yapay zeka dolu harika bir yıl dileriz! 🎉🎈"
                        if gercek_mail_gonder(bilgi["eposta"], "🎂 İyi ki Doğdun! - Nokta AI", icerik):
                            bilgi["dogum_gunu_kutlandi_yil"] = bu_yil
                            guncelleme_var = True
            except:
                pass
                
    if guncelleme_var:
        with open(VERITABANI_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, ensure_ascii=False, indent=4)

# --- SESSION STATES ---
if "mesajlar" not in st.session_state: st.session_state.mesajlar = []
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "dogrulama_kodu" not in st.session_state: st.session_state.dogrulama_kodu = None
if "gecici_kayit" not in st.session_state: st.session_state.gecici_kayit = {}
if "sifre_unuttum_modu" not in st.session_state: st.session_state.sifre_unuttum_modu = False
if "sifre_kodu" not in st.session_state: st.session_state.sifre_kodu = None
if "is_admin" not in st.session_state: st.session_state.is_admin = False

# Doğum günlerini kontrol et
otomatik_dogum_gunu_kontrol()

# --- GİRİŞ VE KAYIT EKRANLARI ---
if not st.session_state.giris_yapildi:
    st.markdown("<h1 style='text-align: center;'>🎯 NOKTA AI ULTIMATE CLOUD</h1>", unsafe_allow_html=True)
    
    if st.session_state.sifre_unuttum_modu:
        st.subheader("🔑 Şifre Sıfırlama Merkezi")
        unuttum_eposta = st.text_input("Kayıtlı E-posta Adresiniz")
        if st.button("Sıfırlama Kodu Gönder") and unuttum_eposta:
            st.session_state.sifre_kodu = str(random.randint(100000, 999999))
            gercek_mail_gonder(unuttum_eposta, "Şifre Kodu", f"Kodunuz: {st.session_state.sifre_kodu}")
            st.success("Kod e-postanıza fırlatıldı!")
        if st.session_state.sifre_kodu:
            gk = st.text_input("6 Haneli Kurtarma Kodu")
            ys = st.text_input("Yeni Şifre", type="password")
            if st.button("Şifreyi Güncelle"):
                if gk == st.session_state.sifre_kodu and ys:
                    veriler = kullanicilari_yukle()
                    for k, v in veriler.items():
                        if v.get("eposta") == unuttum_eposta.lower().strip():
                            veriler[k]["sifre"] = ys
                    with open(VERITABANI_DOSYASI, "w", encoding="utf-8") as f:
                        json.dump(veriler, f, ensure_ascii=False, indent=4)
                    st.success("Şifreniz başarıyla güncellendi!")
                    st.session_state.sifre_unuttum_modu = False
                    st.rerun()
        if st.button("⬅️ Geri Dön"): st.session_state.sifre_unuttum_modu = False; st.rerun()
        st.stop()

    if st.session_state.dogrulama_kodu:
        st.subheader("📩 Hesap Doğrulama Alanı")
        kg = st.text_input("E-postanıza Gelen 6 Haneli Kodu Yazın")
        if st.button("Hesabımı Onayla"):
            if kg == st.session_state.dogrulama_kodu:
                g = st.session_state.gecici_kayit
                kullanici_kaydet(g["k_adi"], g["sifre"], g["isim"], g["eposta"], g["dogum_tarihi"])
                st.success("Mükemmel! Hesabınız başarıyla oluşturuldu.")
                st.session_state.dogrulama_kodu = None
                st.rerun()
            else: st.error("Doğrulama kodu hatalı!")
        st.stop()

    sekme1, sekme2 = st.tabs(["🚪 Oturum Aç", "📝 Ücretsiz Kayıt Ol"])
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
                else: st.error("Hatalı kullanıcı adı veya şifre!")
        if st.button("Şifremi Unuttum"): st.session_state.sifre_unuttum_modu = True; st.rerun()
            
    with sekme2:
        yeni_isim = st.text_input("Adınız")
        yeni_eposta = st.text_input("E-posta Adresiniz")
        yeni_k_adi = st.text_input("Yeni Kullanıcı Adı")
        yeni_sifre = st.text_input("Yeni Şifre", type="password")
        yeni_dogum = st.date_input("Doğum Tarihiniz", min_value=datetime(1950, 1, 1), max_value=datetime.today())
        
        if st.button("Doğrulama Kodu Gönder ve Ücretsiz Üye Ol", use_container_width=True):
            if yeni_isim and yeni_eposta and yeni_k_adi and yeni_sifre:
                st.session_state.dogrulama_kodu = str(random.randint(100000, 999999))
                st.session_state.gecici_kayit = {
                    "k_adi": yeni_k_adi, "sifre": yeni_sifre, "isim": yeni_isim, "eposta": yeni_eposta, "dogum_tarihi": str(yeni_dogum)
                }
                with st.spinner("Doğrulama kodu e-postanıza gönderiliyor..."):
                    icerik = f"Merhaba {yeni_isim},\n\nNokta AI platformuna kayıt olmak için kodunuz: {st.session_state.dogrulama_kodu}"
                    gercek_mail_gonder(yeni_eposta, "Nokta AI Kayıt Onayı", icerik)
                    st.rerun()
            else: st.warning("Lütfen tüm alanları doldur şef!")
    st.stop()

# --- 🛠️ PANEL BAŞLANGICI ---
with st.sidebar:
    st.title("🎯 Nokta AI")
    st.write(f"👤 İsim: **{st.session_state.aktif_kullanici}**")
    st.write(f"🛡️ Rol: **{'👑 KURUCU' if st.session_state.is_admin else '👤 ÜYE'}**")
    st.write("---")
    
    yuklenen_resim = st.file_uploader("🖼️ Profil Resmi veya Görsel Yükle", type=["png", "jpg", "jpeg"])
    if yuklenen_resim is not None:
        st.image(yuklenen_resim, caption="Yüklediğin Görsel!", use_container_width=True)
        
    st.write("---")
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        st.session_state.mesajlar = []
        st.session_state.giris_yapildi = False
        st.rerun()

# --- 👑 MOD 1: ADMIN PANELİ ---
if st.session_state.is_admin:
    st.title("👑 Nokta AI Yönetim Merkez")
    sekme_chat, sekme_kullanicilar, sekme_toplu_mail = st.tabs(["💬 Nokta AI Bulut Motoru", "📊 Kullanıcı Listesi", "📣 TÜM ÜYELERE MAİL AT"])
    
    with sekme_toplu_mail:
        st.subheader("📬 Kayıtlı İnsanların Maillerine Buradan Mail At")
        mail_konusu = st.text_input("E-posta Konusu")
        mail_mesaji = st.text_area("Gönderilecek Mesaj İçeriği")
        
        if st.button("🚀 TOPLU MAİLİ ŞİMDİ FIRLAT", use_container_width=True):
            if mail_konusu and mail_mesaji:
                tum_uyeler = kullanicilari_yukle()
                gonderilen_sayi = 0
                for u_adi, u_bilgi in tum_uyeler.items():
                    if "eposta" in u_bilgi:
                        if gercek_mail_gonder(u_bilgi["eposta"], mail_konusu, mail_mesaji):
                            gonderilen_sayi += 1
                st.success(f"🔥 Başarılı! Toplam {gonderilen_sayi} kişiye mail uçuruldu!")
            else: st.warning("Lütfen alanları doldur Kurucum!")

    with sekme_kullanicilar:
        st.subheader("👥 Platformdaki Kayıtlı Kişiler")
        tum_uyeler = kullanicilari_yukle()
        if tum_uyeler:
            for k, v in tum_uyeler.items():
                st.info(f"👤 **Kullanıcı:** {k} | **İsim:** {v['isim']} | **E-posta:** {v['eposta']} | **Doğum Tarihi:** {v.get('dogum_tarihi','--')}")
        else: st.write("Sistemde henüz üye yok.")

    with sekme_chat:
        for m in st.session_state.mesajlar:
            with st.chat_message(m["role"]): st.write(m["content"])
        if ks := st.chat_input("NOKTA AI'a Sor..."):
            with st.chat_message("user"): st.write(ks)
            st.session_state.mesajlar.append({'role': 'user', 'content': ks})
            
            if client:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.mesajlar],
                        model="llama3-8b-8192",
                    )
                    cevap = chat_completion.choices[0].message.content
                except:
                    cevap = "Bulut motorunda yoğunluk var, lütfen tekrar dene."
            else:
                cevap = "API Anahtarı eksik!"
                
            with st.chat_message("assistant"): st.write(cevap)
            st.session_state.mesajlar.append({'role': 'assistant', 'content': cevap})
            st.rerun()

# --- 👤 MOD 2: NORMAL KULLANICI PANELİ ---
else:
    st.title("💬 Nokta AI Sohbet Odası")
    st.info("🚀 7/24 Kesintisiz Bulut Sistemi Aktif!")

    for m in st.session_state.mesajlar:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if ks := st.chat_input("NOKTA AI'a Sor..."):
        with st.chat_message("user"): st.write(ks)
        st.session_state.mesajlar.append({'role': 'user', 'content': ks})
        
        with st.chat_message("assistant"):
            with st.spinner("Nokta AI Düşünüyor..."):
                if client:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.mesajlar],
                            model="llama3-8b-8192",
                        )
                        cevap = chat_completion.choices[0].message.content
                    except:
                        cevap = "Sistem şu an yoğun, saniyeler içinde tekrar yaz şef!"
                else:
                    cevap = "Zeka motoru şu an uykuda."
                    
        with st.chat_message("assistant"): st.write(cevap)
        st.session_state.mesajlar.append({'role': 'assistant', 'content': cevap})
        st.rerun()
