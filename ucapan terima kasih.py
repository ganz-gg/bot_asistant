import streamlit as st
from googleapiclient.discovery import build
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Assistant YouTuber", page_icon="🎙️")

# --- AMBIL API KEY DARI BRANKAS (SECRETS) ---
# Kamu harus isi YOUTUBE_API_KEY di settingan Secrets Streamlit Cloud!
try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("⚠️ Error: API Key tidak ditemukan di brankas Secrets!")
    st.stop()

# --- FUNGSI SUARA (BROWSER BASED) ---
def panggil_suara_ai(teks):
    js_code = f"""
        <script>
        var msg = new SpeechSynthesisUtterance('{teks}');
        msg.lang = 'id-ID';
        window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

# --- TAMPILAN WEBSITE ---
st.title("🎙️ AI Assistant Streamer")
st.write("Cukup masukkan handle YouTube-mu, dan AI akan otomatis menyapa saat ada Subrek/Like!")

# Input buat orang lain (User)
handle_input = st.text_input("Masukkan Handle YouTube (Contoh: @BoloGamer)", placeholder="@")

if st.button("Aktifkan Asisten AI 🚀"):
    if len(handle_input) < 2:
        st.warning("Masukkan handle yang bener dulu, Bolo!")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # 1. Cari ID Channel User
            search_ch = youtube.search().list(q=handle_input, type="channel", part="id").execute()
            if not search_ch['items']:
                st.error("Channel tidak ditemukan!")
                st.stop()
            
            channel_id = search_ch['items'][0]['id']['channelId']
            
            # 2. Cari Video yang lagi LIVE
            search_live = youtube.search().list(
                channelId=channel_id, type="video", eventType="live", part="id"
            ).execute()
            
            if not search_live['items']:
                st.warning("Channel ini lagi gak Live. Mulai Live dulu di YouTube baru klik tombol ini!")
                st.stop()
            
            video_id = search_live['items'][0]['id']['videoId']
            
            st.success(f"✅ Terhubung ke @{handle_input}! AI sedang berjaga...")
            panggil_suara_ai(f"Halo streamer {handle_input}, asisten A I sudah mulai berjaga. Selamat streaming!")

            # Ambil Data Awal
            ch_info = youtube.channels().list(part="statistics", id=channel_id).execute()
            v_info = youtube.videos().list(part="statistics", id=video_id).execute()
            
            sub_lama = int(ch_info['items'][0]['statistics']['subscriberCount'])
            like_lama = int(v_info['items'][0]['statistics'].get('likeCount', 0))

            # Tampilan Dashboard Real-time
            col1, col2 = st.columns(2)
            metrik_sub = col1.metric("Subscriber", sub_lama)
            metrik_like = col2.metric("Likes", like_lama)
            
            # --- LOOPING MONITOR ---
            while True:
                time.sleep(25) # Jeda agak lama biar API Key kamu gak cepet habis (Limit Google)
                
                ch_up = youtube.channels().list(part="statistics", id=channel_id).execute()
                v_up = youtube.videos().list(part="statistics", id=video_id).execute()
                
                sub_baru = int(ch_up['items'][0]['statistics']['subscriberCount'])
                like_baru = int(v_up['items'][0]['statistics'].get('likeCount', 0))

                # Update Angka di Layar
                metrik_sub.metric("Subscriber", sub_baru, sub_baru - sub_lama)
                metrik_like.metric("Likes", like_baru, like_baru - like_lama)

                if sub_baru > sub_lama:
                    msg = "Wih, ada subrek baru! Makasih banyak ya Bolo!"
                    panggil_suara_ai(msg)
                    sub_lama = sub_baru

                if like_baru > like_lama:
                    msg = "Mantap jempolnya! Makasih like-nya Bolo!"
                    panggil_suara_ai(msg)
                    like_lama = like_baru

        except Exception as e:
            st.error(f"Terjadi masalah: {e}")
