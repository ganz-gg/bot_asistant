import streamlit as st
from googleapiclient.discovery import build
import time

# --- SETUP HALAMAN ---
st.set_page_config(page_title="AI Streamer Assistant", page_icon="🎙️")
st.title("🎙️ AI Assistant YouTuber")
st.subheader("Bikin Live Stream makin rame pake suara AI!")

# --- AMBIL API KEY (Bisa dari Secrets atau Input) ---
# Jika di Streamlit Cloud, setting di Secrets dengan nama YOUTUBE_API_KEY
if "YOUTUBE_API_KEY" in st.secrets:
    api_key = st.secrets["YOUTUBE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan YouTube API Key", type="password")

handle_input = st.sidebar.text_input("Handle Channel (Contoh: @BoloGamer)", value="@")

# --- FUNGSI SUARA (JavaScript agar bunyi di Browser) ---
def bunyikan_ai(teks):
    js_code = f"""
        <script>
        var msg = new SpeechSynthesisUtterance('{teks}');
        msg.lang = 'id-ID';
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

# --- LOGIKA UTAMA ---
if st.sidebar.button("Mulai Patroli 🚀"):
    if not api_key or len(handle_input) < 2:
        st.error("Isi API Key dan Handle Channel dulu, Bolo!")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # 1. Cari ID Channel & Cek Status Live
            search_ch = youtube.search().list(q=handle_input, type="channel", part="id").execute()
            channel_id = search_ch['items'][0]['id']['channelId']
            
            st.info(f"Memantau Channel: {handle_input}")
            
            # Cari Video yang lagi LIVE sekarang
            search_live = youtube.search().list(
                channelId=channel_id,
                type="video",
                eventType="live",
                part="id"
            ).execute()
            
            if not search_live['items']:
                st.warning("Channelmu lagi gak Live nih. Pastikan sudah klik 'Start Stream' di YouTube!")
                st.stop()
            
            video_id = search_live['items'][0]['id']['videoId']
            st.success(f"Dapet! Lagi mantau Video ID: {video_id}")
            bunyikan_ai("Sistem asisten A I sudah aktif. Selamat streaming Bolo!")

            # Simpan data awal
            ch_info = youtube.channels().list(part="statistics", id=channel_id).execute()
            v_info = youtube.videos().list(part="statistics", id=video_id).execute()
            
            sub_lama = int(ch_info['items'][0]['statistics']['subscriberCount'])
            like_lama = int(v_info['items'][0]['statistics'].get('likeCount', 0))

            log_placeholder = st.empty()
            
            # --- LOOPING MONITOR ---
            while True:
                # Update Data
                ch_up = youtube.channels().list(part="statistics", id=channel_id).execute()
                v_up = youtube.videos().list(part="statistics", id=video_id).execute()
                
                sub_baru = int(ch_up['items'][0]['statistics']['subscriberCount'])
                like_baru = int(v_up['items'][0]['statistics'].get('likeCount', 0))

                if sub_baru > sub_lama:
                    msg = "Wih, ada subrek baru! Makasih banyak ya Bolo!"
                    st.toast(msg, icon="🔥")
                    bunyikan_ai(msg)
                    sub_lama = sub_baru

                if like_baru > like_lama:
                    msg = "Mantap jempolnya! Makasih like-nya Bolo!"
                    st.toast(msg, icon="👍")
                    bunyikan_ai(msg)
                    like_lama = like_baru

                # Tampilan Log Simple
                log_placeholder.write(f"📊 Subs: {sub_baru} | ❤️ Likes: {like_baru} (Update tiap 20 detik)")
                
                time.sleep(20)

        except Exception as e:
            st.error(f"Aduh ada masalah teknis: {e}")