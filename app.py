import streamlit as st
import os
from groq import Groq

# 1. Sayfa Tasarımı ve Başlıklar
st.set_page_config(page_title="Nokta AI Sohbet Odası", page_icon="👑", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>👑 Nokta AI Yapay Zeka Sunucusu</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #777;'>Kurucu: Berat | Render Canlı Yayını aktif!</h3>", unsafe_allow_html=True)
st.write("---")

# 2. Render Şifre Paneline Yazdığımız Groq Anahtarını Güvenle Çekiyoruz
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Hata: GROQ_API_KEY Render panelinde bulunamadı şef! Ayarları kontrol et.")
else:
    # Groq istemcisini başlatıyoruz
    client = Groq(api_key=GROQ_API_KEY)

    # Sohbet geçmişini Streamlit hafızasında tutmak için alan açıyoruz (Sayfa yenilenince uçmasın)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Eski mesajları ekrana alt alta basıyoruz
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Kurucudan (Senden) Gelen Giriş Kutusu
    if prompt := st.chat_input("Nokta AI'a bir şeyler yazın..."):
        # Senin yazdığını ekrana bas ve hafızaya kaydet
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Yapay zekaya kim olduğunu ve nasıl davranacağını fısıldıyoruz (Sistem Talimatı)
        system_instruction = (
            "Senin adın Nokta AI. Sen Berat tarafından geliştirilmiş çok özel ve akıllı bir yapay zeka asistanısın. "
            "Berat bir ilkokul öğrencisidir, onunla konuşurken ona hep 'Şef', 'Kurucum' veya 'Berat' diye hitap et. "
            "Onun hevesini kıracak hiçbir şey söyleme, çok enerjik, zeki ve cana yakın ol. "
            "Berat teknolojiye, Arduino ve PicoBricks ile kodlama yapmaya, drone modellerine (özellikle DJI modelleri), "
            "Minecraft ve Roblox oynamaya bayılır. Beşiktaş Gymnastics Club taraftarıdır. "
            "Kısa, net ve eğlenceli cevaplar ver."
        )

        # 4. Groq Motoruna İstek Atıp Canlı Cevap İstiyoruz
        try:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Mesajları Groq'un anlayacağı formata sokuyoruz
                groq_messages = [{"role": "system", "content": system_instruction}]
                for m in st.session_state.messages:
                    groq_messages.append({"role": m["role"], "content": m["content"]})
                
                # Groq Modelini tetikliyoruz (Dünyanın en hızlısı: Llama 3)
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=groq_messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
                
                response = completion.choices[0].message.content
                message_placeholder.markdown(response)
                
            # Yapay zekanın cevabını da hafızaya ekliyoruz
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Groq motoruna bağlanırken bir hata oluştu: {e}")
