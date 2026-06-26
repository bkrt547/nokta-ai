import streamlit as st
import json
import os
import random
import base64
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq

# Sayfa Ayarları
st.set_page_config(page_title="Nokta AI Ultimate Otomatik", page_icon="🎨", layout="wide")

VERITABANI_DOSYASI = "kullanicilar.json"

# --- 🔑 API BAĞLANTILARI ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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
        "💬 Yeni Sohbet": []
    }

if "ek_egitim_notu" not in st.session_state:
    st.session_state.ek_egitim_notu = "Nokta AI kararlı modda çalışıyor."

# SESSION STATES
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = ""
if "secilen_konu" not in st.session_state: st.session_state.secilen_konu = "💬 Yeni Sohbet"
if "dogrulama_kodu" not in st.session_state: st.session_state.dogrulama_kodu = None
if "gecici_kayit" not in st.session_state: st.session_state.gecici_kayit = {}

# --- 🖼️ GÖRÜNTÜ ÇEVİRİCİ ---
def goruntuyu_base64_yap(yuklenen_dosya):
    if yuklenen_dosya is not None:
        return base64.b64encode(yuklenen_dosya.getvalue()).decode("utf-8")
    return None

# --- 🤖 OTOMATİK BAŞLIK ÜRETME MOTORU ---
def otomatik_baslik_uret(kullanici_ilk_mesaji):
    if not GROQ_API_KEY:
        return f"Sohbet_{random.randint(100,999)}"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = (
            f"Sana bir kullanıcının yapay zekaya yazdığı ilk mesajı vereceğim. Bu mesaja bakarak sol menüde listelenmek üzere "
            f"en fazla 3-5 kelimelik, çok şık ve Türkçe bir sohbet başlığı üret. Sadece başlığı yaz, başka hiçbir açıklama ekleme.\n"
            f"Kullanıcı Mesajı: {kullanici_ilk_mesaji}"
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=20
        )
        return completion.choices[0].message.content.strip().replace('"', '').replace("'", "")
    except:
        return f"Sohbet_{random.randint(100,999)}"

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.giris_yapildi:
    st.markdown("<h1 style='text-align: center;'>🎯 NOKTA AI ULTIMATE ART</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa;'>Kurucu: Berat</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

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
            
            if st.button("Kaydet ve Üye Yap", use_container_width=True):
                if yeni_isim and yeni_eposta and yeni_k_adi and yeni_sifre:
                    kullanicilar = kullanicilari_yukle()
                    if yeni_k_adi in kullanicilar or yeni_k_adi == "admin":
                        st.warning("Bu kullanıcı adı kapılmış şef!")
                    else:
                        kullanici_kaydet(yeni_k_adi, yeni_sifre, yeni_isim, yeni_eposta)
                        st.success("Hesap başarıyla açıldı! Giriş yapabilirsiniz.")
                        st.rerun()
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
        if st.button("➕ Yeni Sohbet Başlat", use_container_width=True, type="primary"):
            st.session_state.konu_hafizalari["💬 Yeni Sohbet"] = []
            st.session_state.secilen_konu = "💬 Yeni Sohbet"
            st.rerun()

        st.write("---")
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

# --- 🔥 GÜÇLÜ VE HATASIZ GROQ SOHBET MOTORU (KURUCUYA ÖZEL) ---
def groq_sohbet_motoru(kullanici_mesaji, base64_goruntu=None):
    if not GROQ_API_KEY: return "Hata: GROQ_API_KEY Render panellerinde eksik şef!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        system_instruction = (
            f"Senin adın Nokta AI Ultimate. Sen Berat tarafından geliştirilmiş harika bir yapay zekasın. "
            f"Berat bir ilkokul öğrencisidir ve bu platformun dahi mucididir. Ona hep 'Şef' veya 'Kurucum' de. "
            f"Şu anki aktif oda başlığı: {st.session_state.secilen_konu}. Kurucunun ek eğitim talimatı: {st.session_state.ek_egitim_notu}. "
            f"Kısa, enerjik, çok zeki, dürüst ve net Türkçe cevaplar ver."
        )
        groq_messages = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.konu_hafizalari[st.session_state.secilen_konu]:
            if m.get("type") != "image":
                groq_messages.append({"role": m["role"], "content": m["content"]})
        groq_messages.append({"role": "user", "content": kullanici_mesaji})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=groq_messages,
            temperature=0.6,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e: return f"Bağlantı Hatası: {e}"

# --- 📉 VERİMSİZ VE KISITLI MİSAFİR MOTORU (ZİYARETÇİYE ÖZEL) 📉 ---
def misafir_sohbet_motoru(kullanici_mesaji):
    if not GROQ_API_KEY: return "Sistem yoğun."
    try:
        client = Groq(api_key=GROQ_API_KEY)
        # Bilerek hafızasız, kısıtlı ve basit talimat veriyoruz şef
        system_instruction = "Sen kısıtlı bir misafir yapay zekasısın. Sorulara çok kısa, basit, derin analize girmeden ve kısıtlı modda olduğunu belirterek cevap ver."
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Daha küçük, daha verimsiz ve basit model!
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": kullanici_mesaji}
            ],
            temperature=0.4,
            max_tokens=150,
        )
        return completion.choices[0].message.content
    except: return "Şu an yanıt verilemiyor."

# --- 🎨 BULUT RESİM OLUŞTURMA MOTORU ---
def bulut_resim_ciz_motoru(prompt):
    try:
        with st.spinner(f"🎨 Nokta AI Bulut Motoru '{prompt}' resmini çiziyor..."):
            temiz_prompt = urllib.parse.quote(prompt)
            rastgele_seed = random.randint(1, 999999)
            resim_url = f"https://image.pollinations.ai/prompt/{temiz_prompt}?width=1024&height=1024&seed={rastgele_seed}&model=flux"
            return resim_url, None
    except Exception as e: return None, f"Resim Çizme Hatası: {e}"

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
        if tum_uyeler:
            for k, v in tum_uyeler.items(): st.info(f"👤 **Kullanıcı:** {k} | **İsim:** {v['isim']}")

    with sekme_egitme:
        st.subheader("🧠 Nokta AI Zeka Motorunu Eğit")
        yeni_talimat = st.text_area("Yapay Zekaya Verilecek Gizli Emir:", value=st.session_state.ek_egitim_notu)
        if st.button("🧠 Zeka Motorunu Güncelle", use_container_width=True):
            st.session_state.ek_egitim_notu = yeni_talimat
            st.success("🔥 Harika! Yapay zeka bu yeni emirlerle eğitildi kurucum!")

    with sekme_chat:
        st.subheader(f"💬 Aktif Sohbet: {st.session_state.secilen_konu}")
        for m in st.session_state.konu_hafizalari[st.session_state.secilen_konu]:
            with st.chat_message(m["role"]):
                if m.get("type") == "image": st.image(m["content"], caption="Nokta AI Çizimi!", use_container_width=True)
                else: st.write(m["content"])
            
        if ks := st.chat_input("Nokta AI'a sor, konuyu analiz edip yanda başlık açsın...", key="admin_chat_box"):
            if st.session_state.secilen_konu == "💬 Yeni Sohbet":
                with st.spinner("🧠 Konu analiz ediliyor..."):
                    yeni_baslik = otomatik_baslik_uret(ks)
                st.session_state.konu_hafizalari[yeni_baslik] = st.session_state.konu_hafizalari.pop("💬 Yeni Sohbet")
                st.session_state.secilen_konu = yeni_baslik
            
            with st.chat_message("user"): st.write(ks)
            st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'user', 'content': ks})
            b64_img = goruntuyu_base64_yap(sohbet_görüntüsü) if sohbet_görüntüsü else None
            
            if any(kelime in ks.lower() for kelime in ["çiz", "oluştur", "resmini yap"]):
                aranan_cizim = ks.lower().replace("çiz", "").replace("oluştur", "").replace("resmini yap", "").strip()
                resim_linki, hata = bulut_resim_ciz_motoru(aranan_cizim)
                with st.chat_message("assistant"):
                    if hata: st.error(hata)
                    else:
                        st.image(resim_linki, use_container_width=True)
                        st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'assistant', 'content': resim_linki, 'type': 'image'})
                st.rerun()
            else:
                with st.spinner("Nokta AI Yanıtlıyor..."): cevap = groq_sohbet_motoru(ks, b64_img)
                with st.chat_message("assistant"): st.write(cevap)
                st.session_state.konu_hafizalari[st.session_state.secilen_konu].append({'role': 'assistant', 'content': cevap, 'type': 'text'})
                st.rerun()

# --- 👤 NORMAL MİSAFİR EKRANI (ŞİMDİ GERÇEK AMA VERİMSİZ SOHBET MOTORU AKTİF) ---
else:
    st.title("🎯 Nokta AI Ziyaretçi Kanalı")
    st.info("👋 Hoş geldin! Şu an Oturum Açmadan bağlandın. Özel odalar kapalıdır ama temel yapay zekayı test edebilirsin:")
    
    if "misafir_mesajlar" not in st.session_state:
        st.session_state.misafir_mesajlar = []
        
    for m in st.session_state.misafir_mesajlar:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if ks := st.chat_input("Genel kısıtlı test mesajı yazın...", key="guest_chat_box"):
        with st.chat_message("user"): st.write(ks)
        st.session_state.misafir_mesajlar.append({'role': 'user', 'content': ks})
        
        with st.chat_message("assistant"):
            with st.spinner("Kısıtlı motor yanıtlıyor..."):
                cevap_misafir = misafir_sohbet_motoru(ks)
            st.write(cevap_misafir)
            st.session_state.misafir_mesajlar.append({'role': 'assistant', 'content': cevap_misafir})
        st.rerun()
