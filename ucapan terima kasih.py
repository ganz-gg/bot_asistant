import streamlit as st
from googleapiclient.discovery import build
import time

# --- SETUP TAMPILAN ---
st.set_page_config(page_title="AI Assistant Streamer", page_icon="🎙️")
st.title("🎙️ AI Assistant YouTuber")
st.write("Hubungkan Live Stream kamu dengan Asisten AI!")

# --- AMBIL API KEY DARI SECRETS ---
if "YOUTUBE_API_KEY" in st.secrets:
    api_key = st.secrets["YOUTUBE_API_KEY"]
else:
    st.error("❌ API Key tidak ditemukan di Secrets Streamlit Cloud!")
    api_key = st.sidebar.text_input("Masukkan API Key Manual (Untuk Tes Local):", type="password")

# --- FUNGSI SUARA ---
def bunyikan_ai(teks):
    js_code = f"""<script>
        var msg = new SpeechSynthesisUtterance('{teks}');
        msg.lang = 'id-ID';
        window.speechSynthesis.speak(msg);
    </script>"""
    st.components.v1.html(js_code, height=0)

# --- INPUT ---
col_a, col_b = st.columns(2)
link_live = col_a.text_input("🔗 Link Live Video", placeholder="Paste link dari Browser atau Tombol Bagikan")
user_handle = col_b.text_input("👤 Handle Channel", placeholder="@BoloGamer")

if st.button("🔥 AKTIFKAN ASISTEN AI"):
    if not link_live or not user_handle:
        st.warning("Isi Link Live dan Handle dulu ya, Bolo!")
    elif not api_key:
        st.error("API Key belum diisi!")
    else:
        try:
            # --- PEMBERSIH LINK (BIAR GAK ERROR LAGI) ---
            v_id = ""
            if "v=" in link_live:
                v_id = link_live.split("v=")[1].split("&")[0]
            elif "youtu.be/" in link_live:
                v_id = link_live.split("youtu.be/")[1].split("?")[0]
            elif "live/" in link_live:
                v_id = link_live.split("live/")[1].split("?")[0]
            else:
                v_id = link_live 

            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Cek ke YouTube
            v_req = youtube.videos().list(part="snippet,statistics", id=v_id).execute()
            
            if not v_req['items']:
                st.error(f"❌ Video ID '{v_id}' gak ketemu! Pastikan linknya bener, Bolo.")
            else:
                data_video = v_req['items'][0]
                owner_ch_id = data_video['snippet']['channelId']
                
                st.success(f"✅ Terhubung ke: {data_video['snippet']['title']}")
                bunyikan_ai(f"Halo streamer {user_handle}, asisten A I sudah standby!")
                
                # Ambil Data Awal
                ch_info = youtube.channels().list(part="statistics", id=owner_ch_id).execute()
                sub_lama = int(ch_info['items'][0]['statistics']['subscriberCount'])
                like_lama = int(data_video['statistics'].get('likeCount', 0))

                m1, m2 = st.columns(2)
                met_sub = m1.metric("Subscriber", sub_lama)
                met_like = m2.metric("Likes", like_lama)

                # --- LOOPING MONITOR ---
                while True:
                    time.sleep(25)
                    v_up = youtube.videos().list(part="statistics", id=v_id).execute()
                    c_up = youtube.channels().list(part="statistics", id=owner_ch_id).execute()
                    
                    sub_baru = int(c_up['items'][0]['statistics']['subscriberCount'])
                    like_baru = int(v_up['items'][0]['statistics'].get('likeCount', 0))

                    met_sub.metric("Subscriber", sub_baru, sub_baru - sub_lama)
                    met_like.metric("Likes", like_baru, like_baru - like_lama)

                    if sub_baru > sub_lama:
                        bunyikan_ai("Wih, ada subrek baru masuk! Makasih ya Bolo!")
                        sub_lama = sub_baru
                    if like_baru > like_lama:
                        bunyikan_ai("Mantap, like-nya nambah! Makasih jempolnya Bolo!")
                        like_lama = like_baru

        except Exception as e:
            st.error(f"Gagal koneksi: {e}")
