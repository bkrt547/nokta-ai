import streamlit as st
import json
import os
import random
import base64
import smtplib
import urllib.parse  # Resim komutlarını internet diline çevirmek için
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq

# Sayfa Ayarları
st.set_page_config(page_title="Nokta AI Ultimate Art", page_icon="🎨", layout="wide")

VERITABANI_DOSYASI = "kullanicilar.json"

# --- 📧 GERÇEK E-POSTA BİLGİLERİ ---
GÖNDERİCİ_MAİL = "noktaaioffical@gmail.com"  
GÖNDERİCİ_ŞİFRE = "gpbfxxerhtwakuwd"  

# --- 🔑 API BAĞLANTILARI ---
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

# --- 🧠 DİNAMİK SOHBET ODALARI HAFIZASI ---
if "konu_hafizalari" not in st.session_state:
    st.session_state.konu_hafizalari = {
        "💬 Genel Sohbet": []
    }

if "ek_egitim_notu" not in st.session_state:
    st.session_state.ek_egitim_notu = "Nokta AI kararlı modda çalışıyor."

# SESSION STATES
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "secilen_konu" not in st.session_state: st.session_state.secilen_konu = "💬 Genel Sohbet"
if "dogrulama_kodu" not in st.session_state: st.session_state.dogrulama_kodu = None
if "gecici_kayit" not in st.session_state: st.session_state.gecici_kayit = {}

# --- 🖼️ GÖRÜNTÜ ÇEVİRİCİ ---
def goruntuyu_base64_yap(yuklenen_dosya):
    if yuklenen_dosya is not None:
        return base64.b64encode(yuklenen_dosya.getvalue()).decode("utf-8")
    return None

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.giris_yapildi:
    st.markdown("<h1 style='text-align: center;'>🎯 NOKTA AI ULTIMATE ART</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa;'>Kurucu: Berat</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.dogrulama_kodu:
        st.subheader("📩 Üye Onay Paneli")
        kg = st.text_input("E-postaya gelen 6 haneli kodu yazın:")
        if st.button("Onayla ve Üye Yap 🚀"):
            if kg == st.session_state.dogrulama_kodu:
                g = st.session_state.gecici_kayit
                kullanici_kaydet(g["k_adi"], g["sifre"], g["isim"], g["eposta"])
                st.success("Hesap başarıyla açıldı! Giriş yapabilirsiniz.")
                st.session_state.dogrulama_kodu = None
                st.rerun()
            else: 
                st.error("Kod hatalı şef!")
        if st.button("⬅️ İptal Et"):
            st.session_state.dogrulama_kodu = None
            st.rerun()
        st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        hizli_gecis = st.button("🚀 Oturum Açmadan Devam Et", use_container_width=True)
        if hizli_gecis:
            st.session_state.giris_yapildi = True
            st.session_state.is_admin = False
            st.session_state.aktif_kullanici = "Ziyaretçi"
            st.rerun()
            
        st.markdown("<hr style='border-color: #444;'>", unsafe_allow_html=True)
        
        sekme1, sekme2 = st.tabs(["🚪 Klasik Oturum Aç", "📝 Ücretsiz Kayıt Ol"])
        
        with sekme1:
            k_adi_input = st.text_input("Kullanıcı Adı / Kurucu Kodu")
            sifre_input = st.text_input("Şifre", type="password")
            if st.button("Oturum Aç", use_container_width=True):
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
                        st.error("Kullanıcı adı veya şifre hatalı!")
                        
        with sekme2:
            yeni_isim = st.text_input("Ad Soyad")
            yeni_eposta = st.text_input("E-posta")
            yeni_k_adi = st.text_input("Kullanıcı Adı Seçin")
            yeni_sifre = st.text_input("Şifre Seçin", type="password")
            
            if st.button("Doğrulama Kodu Gönder ve Kaydet", use_container_width=True):
                if yeni_isim and yeni_eposta and yeni_k_adi and yeni_sifre:
                    kullanicilar = kullanicilari_yukle()
                    if yeni_k_adi in kullanicilar or yeni_k_adi == "admin":
                        st.warning("Bu kullanıcı adı kapılmış şef!")
                    else:
                        st.session_state.dogrulama_kodu = str(random.randint(100000, 999999))
                        st.session_state.gecici_kayit = {
                            "k_adi": yeni_k_adi, "sifre": yeni_sifre, "isim": yeni_isim, "eposta": yeni_eposta
                        }
                        with st.spinner("Kod fırlatılıyor..."):
                            icerik = f"Merhaba {yeni_isim},\n\nNokta AI onay kodunuz: {st.session_state.dogrulama_kodu}"
                            if gercek_mail_gonder(yeni_eposta, "Nokta AI Onay Kodu 🎯", icerik):
                                st.success("Kod gönderildi!")
                                st.rerun()
                            else:
                                st.error("E-posta hatası oluştu.")
                else: 
                    st.warning("Tüm alanları doldur kurucum!")
    st.stop()

# --- 🛠️ PANEL İÇİ YAN MENÜ MANTIĞI ---
with st.sidebar:
    st.title("🎯 Nokta AI")
    st.write(f"👤 İsim: **{st.session_state.aktif_kullanici}**")
    st.write(f"🛡️ Rol: **{'👑 KURUCU' if st.session_state.is_admin else '👤 ÜYE / ZİYARETÇİ'}**")
    st.write("---")
    
    if st.session_state.is_admin:
        st.markdown("### ➕ Yeni Sohbet Başlat")
        yeni_oda_ismi = st.text_input("Başlık Yazın (Örn: Drone Çizimleri):")
        if st.button("🚀 Listeye Ekle", use_container_width=True):
            if yeni_oda_ismi and yeni_oda_ismi not in st.session_state.konu_hafizalari:
                st.session_state.konu_hafizalari[yeni_oda_ismi] = []
                st.session_state.secilen_konu = yeni_oda_ismi
                st.rerun()

        st.write("---")
        
        # 🔴 FOTOĞRAFTAKİ GİBİ ALT ALTA LİSTELEME ALANI
        st.markdown("<p style='font-weight: bold; color: #888;'>Son Kullanılanlar</p>", unsafe_allow_html=True)
        konu_listesi = list(st.session_state.konu_hafizalari.keys())
        for oda in konu_listesi:
            if oda == st.session_state.secilen_konu:
                if st.button(f"➡️ {oda}", key=f"btn_{oda}", use_container_width=True, type="primary"):
                    st.session_state.secilen_konu = oda
                    st.rerun()
            else:
                if st.button(f"{oda}", key=f"btn_{oda}", use_container_width=True):
                    st.session_state.secilen_konu = oda
                    st.rerun()
            
        st.write("---")
        st.markdown("### 📸 Resim İnceleme")
        sohbet_görüntüsü = st.file_uploader("Resim bırakın:", type=["png", "jpg", "jpeg"])
        if sohbet_görüntüsü is not None:
            st.image(sohbet_görüntüsü, use_container_width=True)
        st.write("---")
    else:
        st.warning("🔒 Sohbet odaları sadece kurucuya özeldir!")
        sohbet_görüntüsü = None

    if st.button("🚪 Çıkış Yap / Ana Sayfa", use_container_width=True):
        st.session_state.giris_yapildi = False
        st.session_state.is_admin = False
        st.rerun()

# --- 🔥 GÜÇLÜ GROQ SOHBET MOTORU (RESİM OKUMALI) ---
def groq_sohbet_motoru(kullanici_mesaji, base64_goruntu=None):
    if not GROQ_API_KEY:
        return "Hata: GROQ_API_KEY Render panellerinde eksik şef!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_instruction = (
            f"Senin adın Nokta AI Ultimate. Sen Berat tarafından geliştirilmiş harika bir yapay zekasın. "
            f"Berat bir ilkokul öğrencisidir ve bu platformun dahi mucididir. Ona hep 'Şef' veya 'Kurucum' de. "
            f"Şu anki konuşulan aktif oda konusu: {st.session_state.secilen_konu}. "
            f"Kurucunun ek eğitim talimatı: {st.session_state.ek_egitim_notu}. "
            f"Kısa, enerjik, çok zeki, dürüst ve net Türkçe cevaplar ver."
        )
        
        groq_messages = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.konu_hafizalari[st.session_state.secilen_konu]:
            if m.get("type") != "image":  # Resim yollarını metin geçmişine karıştırma şef
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

# --- 🎨 LIGHTWEIGHT JET RESİM ÜRETME MOTORU (RENDER DOSTU) 🎨 ---
def bulut_resim_ciz_motoru(prompt):
    try:
        with st.spinner(f"🎨 Nokta AI Bulut Motoru '{prompt}' resmini çiziyor..."):
            # Prompt içindeki Türkçe karakterleri ve boşlukları internet diline güvenli bir şekilde kodluyoruz şef
            temiz_prompt = urllib.parse.quote(prompt)
            # Rastgele bir seed ekliyoruz ki her çizim benzersiz ve harika olsun
            rastgele_seed = random.randint(1, 999999)
            # Saniyeler içinde yüksek kaliteli resim üreten Flux sunucu bağlantısı!
            resim_url = f"https://image.pollinations.ai/prompt/{temiz_prompt}?width=1024&height=1024&seed={rastgele_seed}&model=flux"
            return resim_url, None
    except Exception as e:
        return None, f"Resim Çizme Hatası: {e}"

# --- 👑 GERÇEK KURUCU EKRANI VE PANELLERİ ---
if st.session_state.is_admin:
    st.title("👑 Nokta AI Kurucu Yönetim Merkezi")
    
    sekme_chat, sekme_rapor, sekme_egitme = st.tabs(["💬 Sohbet & Resim Odaları", "📊 Üye Sayısı & Rapor", "🧠 Yapay Zeka Eğitme"])
    
    with sekme_rapor:
        st.subheader("📊 Platform Raporu")
        tum_uyeler = kullanicilari_yukle()
        c1, c2 = st.columns(2)
        c1.metric(label="👥 Toplam Üye Sayısı", value=f"{len(tum_uyeler)} Kişi")
        c2.metric(label="🔵 Resim Motoru Durumu", value="🟢 Sınırsız Bulut Flux Aktif")
        st.write("---")
        st.markdown("#### 👥 Üye Listesi")
        if tum_uyeler:
            for k, v in tum_uyeler.items():
                st.info(f"👤 **Kullanıcı:** {k} | **İsim:** {v['isim']}")
        else: 
            st.write("Sistemde henüz üye yok şef.")

    with sekme_egitme:
        st.subheader("🧠 Nokta AI Zeka Motorunu Eğit")
        yeni_talimat = st.text_area("Yapay Zekaya Verilecek Gizli Emir:", value=st.session_state.ek_egitim_notu)
        if st.button("🧠 Zeka Motorunu Güncelle", use_container_width=True):
            st.session_state.ek_egitim_notu = yeni_talimat
            st.success("🔥 Harika! Yapay zeka bu yeni emirlerle eğitildi kurucum!")

    with sekme_chat:
        st.subheader(f"💬 Aktif Sohbet Odası: {st.session_state.secilen_konu}")
        
        for m in st.session_state.konu_hafizalari[st.session_state.secilen_konu]:
            with st.chat_message(m["role"]):
                if m.get("type") == "image":
                    st.image(m["content"], caption="Nokta AI Tarafından Çizilen Sanat!", use_container_width=True)
                else:
                    st.write(m["content"])
            
        if ks := st.chat_input("Nokta AI'a sor veya 'çiz' komutu fırlat...", key="admin_chat_box"):
            with st.chat_message("user"): st.write(ks)
            st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'user', 'content': ks})
            
            b64_img = goruntuyu_base64_yap(sohbet_görüntüsü) if sohbet_görüntüsü else None
            
            # 🎨 RESİM ÇİZME MANTIĞI ACTIVATED!
            if any(kelime in ks.lower() for kelime in ["çiz", "oluştur", "resmini yap"]):
                aranan_cizim = ks.lower().replace("çiz", "").replace("oluştur", "").replace("resmini yap", "").strip()
                resim_linki, hata = bulut_resim_ciz_motoru(aranan_cizim)
                
                with st.chat_message("assistant"):
                    if hata:
                        st.error(hata)
                    else:
                        st.image(resim_linki, caption="Hayalindeki Çizim Saniyeler İçinde Hazır Kurucum!", use_container_width=True)
                        st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'assistant', 'content': resim_linki, 'type': 'image'})
                st.rerun()
                
            else: # Sadece normal mesajlaşma
                with st.spinner("Groq Motoru Düşünüyor..."):
                    cevap = groq_sohbet_motoru(ks, b64_img)
                    
                with st.chat_message("assistant"): st.write(cevap)
                st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'assistant', 'content': cevap, 'type': 'text'})
                st.rerun()

# --- 👤 NORMAL MİSAFİR EKRANI ---
else:
    st.title("🎯 Nokta AI Ziyaretçi Kanalı")
    st.info("👋 Merhaba! Sohbet odaları sadece kurucuya özeldir.")
    st.caption("Genel test mesajı:")
    
    if "misafir_mesajlar" not in st.session_state:
        st.session_state.misafir_mesajlar = []
        
    for m in st.session_state.misafir_mesajlar:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if ks := st.chat_input("Genel test mesajı yazın...", key="guest_chat_box"):
        with st.chat_message("user"): st.write(ks)
        st.session_state.misafir_mesajlar.append({'role': 'user', 'content': ks})
        
        with st.chat_message("assistant"):
            st.write("Merhaba! Ben Nokta AI. Sohbet odalarına kurucu girişiyle ulaşılabilir şef!")
            st.session_state.misafir_mesajlar.append({'role': 'assistant', 'content': "Misafir modu yanıtı."})
        st.rerun()
