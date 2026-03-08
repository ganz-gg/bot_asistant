if st.button("🔥 AKTIFKAN ASISTEN AI"):
    if not link_live or not user_handle:
        st.warning("Isi Link Live dan Handle dulu ya, Bolo!")
    else:
        try:
            # --- LOGIKA PEMBERSIH LINK (BIAR GAK ERROR LAGI) ---
            v_id = ""
            if "v=" in link_live:
                v_id = link_live.split("v=")[1].split("&")[0]
            elif "youtu.be/" in link_live:
                v_id = link_live.split("youtu.be/")[1].split("?")[0]
            elif "live/" in link_live:
                v_id = link_live.split("live/")[1].split("?")[0]
            else:
                v_id = link_live # Anggap user masukin ID-nya langsung

            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Cek ke YouTube
            v_req = youtube.videos().list(part="snippet,statistics", id=v_id).execute()
            
            if not v_req['items']:
                st.error(f"❌ Video ID '{v_id}' gak ketemu! Pastikan linknya bener, Bolo.")
                st.stop()
            
            # ... Sisa kode ke bawah sama (Cek status live, ambil subrek, dll) ...
            data_video = v_req['items'][0]
            owner_ch_id = data_video['snippet']['channelId']
            
            st.success(f"✅ Terhubung ke: {data_video['snippet']['title']}")
            bunyikan_ai(f"Halo streamer {user_handle}, asisten A I sudah standby!")
            
            # (Lanjutin kode looping kamu di sini)
