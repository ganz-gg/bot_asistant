import streamlit as st
from googleapiclient.discovery import build
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Streamer Assistant", page_icon="🎙️", layout="wide")

# --- SISTEM KEAMANAN (SECRETS) ---
# Di Streamlit Cloud, isi di menu Settings > Secrets: YOUTUBE_API_KEY = "KODE_KAMU"
if "YOUTUBE_API_KEY" in st.secrets:
    api_key = st.secrets["YOUTUBE_API_KEY"]
else:
    st.sidebar.warning("⚠️ API Key tidak ditemukan di Secrets.")
    api_key = st.sidebar.text_input("Masukkan API Key Manual (Untuk Tes Local):", type="password")

# --- INPUT USER ---
st.sidebar.header("⚙️ Pengaturan Channel")
handle_input = st.sidebar.text_input("Handle YouTube (Contoh: @BoloGamer)", value="@")

# --- FUNGSI SUARA (BROWSER BASED) ---
def panggil_suara_ai(teks):
    # Menggunakan Web Speech API agar suara keluar di browser streamer
    js_code = f"""
        <script>
        var msg = new SpeechSynthesisUtterance('{teks}');
        msg.lang = 'id-ID';
        msg.volume = 1.0;
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

# --- TAMPILAN UTAMA ---
st.title("🎙️ AI Assistant Live Streamer")
st.info("Asisten ini akan memantau Subrek & Like secara otomatis dan merespon dengan suara.")

if st.sidebar.button("Mulai Patroli 🚀"):
    if not api_key:
        st.error("Waduh, API Key-nya kosong, Bolo!")
    elif len(handle_input) < 2:
        st.error("Handle channel-nya diisi dulu ya!")
    else:
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # 1. Cari ID Channel
            search_ch = youtube.search().list(q=handle_input, type="channel", part="id").execute()
            if not search_ch['items']:
                st.error("Channel gak ketemu. Cek lagi handlenya!")
                st.stop()
            
            channel_id = search_ch['items'][0]['id']['channelId']
            
            # 2. Cari Video yang lagi LIVE
            search_live = youtube.search().list(
                channelId=channel_id,
                type="video",
                eventType="live",
                part="id"
            ).execute()
            
            if not search_live['items']:
                st.warning("Kamu belum Live nih. Klik 'Mulai Streaming' dulu di YouTube!")
                st.stop()
            
            video_id = search_live['items'][0]['id']['videoId']
            
            st.success(f"✅ Berhasil Terkoneksi! Lagi mantau: {handle_input}")
            panggil_suara_ai("Sistem asisten A I sudah aktif. Selamat streaming Bolo!")

            # Ambil Data Awal
            ch_info = youtube.channels().list(part="statistics", id=channel_id).execute()
            v_info = youtube.videos().list(part="statistics", id=video_id).execute()
            
            sub_lama = int(ch_info['items'][0]['statistics']['subscriberCount'])
            like_lama = int(v_info['items'][0]['statistics'].get('likeCount', 0))

            # Tempat update angka & log
            col1, col2 = st.columns(2)
            stat_sub = col1.metric("Subscriber", sub_lama)
            stat_like = col2.metric("Likes", like_lama)
            log_box = st.expander("Log Aktivitas", expanded=True)

            # --- LOOPING MONITOR ---
            while True:
                time.sleep(20) # Cek tiap 20 detik (Aman dari limit)
                
                ch_up = youtube.channels().list(part="statistics", id=channel_id).execute()
                v_up = youtube.videos().list(part="statistics", id=video_id).execute()
                
                sub_baru = int(ch_up['items'][0]['statistics']['subscriberCount'])
                like_baru = int(v_up['items'][0]['statistics'].get('likeCount', 0))

                # Update tampilan angka
                stat_sub.metric("Subscriber", sub_baru, sub_baru - sub_lama)
                stat_like.metric("Likes", like_baru, like_baru - like_lama)

                if sub_baru > sub_lama:
                    msg = f"Wih, ada subrek baru! Makasih banyak ya Bolo!"
                    log_box.write(f"🔔 {msg}")
                    panggil_suara_ai(msg)
                    sub_lama = sub_baru

                if like_baru > like_lama:
                    msg = f"Mantap jempolnya! Makasih like-nya Bolo!"
                    log_box.write(f"👍 {msg}")
                    panggil_suara_ai(msg)
                    like_lama = like_baru

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
