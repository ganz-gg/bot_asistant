import streamlit as st
from googleapiclient.discovery import build
import time

# --- SETUP TAMPILAN ---
st.set_page_config(page_title="AI Assistant Streamer", page_icon="🎙️")
st.title("🎙️ AI Assistant YouTuber")
st.write("Hubungkan Live Stream kamu dengan Asisten AI!")

# --- AMBIL API KEY DARI SECRETS ---
try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except:
    st.error("❌ API Key tidak ditemukan di Secrets!")
    st.stop()

# --- FUNGSI SUARA ---
def bunyikan_ai(teks):
    js_code = f"""<script>
        var msg = new SpeechSynthesisUtterance('{teks}');
        msg.lang = 'id-ID';
        window.speechSynthesis.speak(msg);
    </script>"""
    st.components.v1.html(js_code, height=0)

# --- INPUT 2 KOLOM ---
col_a, col_b = st.columns(2)
link_live = col_a.text_input("🔗 Link Live Video", placeholder="https://www.youtube.com/watch?v=...")
user_handle = col_b.text_input("👤 Handle Channel", placeholder="@BoloGamer")

if st.button("🔥 AKTIFKAN ASISTEN AI"):
    if not link_live or not user_handle:
        st.warning("Isi Link Live dan Handle dulu ya, Bolo!")
    else:
        try:
            # Ambil ID Video dari Link
            if "v=" in link_live:
                v_id = link_live.split("v=")[1].split("&")[0]
            else:
                v_id = link_live.split("/")[-1]

            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # 1. Cek Detail Video & Channel ID Pemiliknya
            v_req = youtube.videos().list(part="snippet,statistics", id=v_id).execute()
            
            if not v_req['items']:
                st.error("Video tidak ditemukan! Cek linknya lagi.")
                st.stop()
            
            data_video = v_req['items'][0]
            owner_ch_id = data_video['snippet']['channelId']
            status_live = data_video['snippet'].get('liveBroadcastContent', 'none')

            # 2. Verifikasi: Apakah video ini lagi LIVE?
            if status_live != "live":
                st.warning(f"Video ini statusnya: {status_live}. Harus lagi LIVE baru bisa dipantau!")
                st.stop()

            st.success(f"✅ Terhubung! Memantau Live: {data_video['snippet']['title']}")
            bunyikan_ai(f"Halo streamer {user_handle}, asisten A I sudah mendeteksi siaran langsung anda. Selamat streaming!")

            # Ambil Data Awal
            s_lama = int(youtube.channels().list(part="statistics", id=owner_ch_id).execute()['items'][0]['statistics']['subscriberCount'])
            l_lama = int(data_video['statistics'].get('likeCount', 0))

            m1, m2 = st.columns(2)
            met_sub = m1.metric("Subscriber", s_lama)
            met_like = m2.metric("Likes", l_lama)

            # --- LOOPING MONITOR ---
            while True:
                time.sleep(25)
                v_up = youtube.videos().list(part="statistics", id=v_id).execute()
                c_up = youtube.channels().list(part="statistics", id=owner_ch_id).execute()
                
                s_baru = int(c_up['items'][0]['statistics']['subscriberCount'])
                l_baru = int(v_up['items'][0]['statistics'].get('likeCount', 0))

                met_sub.metric("Subscriber", s_baru, s_baru - s_lama)
                met_like.metric("Likes", l_baru, l_baru - l_lama)

                if s_baru > s_lama:
                    bunyikan_ai("Wih, ada subrek baru masuk! Makasih ya Bolo!")
                    s_lama = s_baru
                if l_baru > l_lama:
                    bunyikan_ai("Mantap, like-nya nambah! Makasih jempolnya Bolo!")
                    l_lama = l_baru

        except Exception as e:
            st.error(f"Gagal koneksi: {e}")
