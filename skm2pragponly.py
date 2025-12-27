
import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection
from io import BytesIO
from datetime import datetime, timedelta


def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
@st.cache_data(ttl=30)
def load_sheet():
    """Read Google Sheet (cached for 60 seconds)."""
    return conn.read(worksheet=url)

url = "JanganSentuhOtomatisDesember2025"
urlp = "percobaan"

if "submitted" not in st.session_state:
    st.session_state.submitted = False


conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(worksheet=url)
name= load_sheet()




dff = pd.DataFrame(name)
CSV_FILE = "submissions.csv"
ADMIN_PASSWORD = "pragp99"

st.set_page_config(page_title="PraGP Sukamulya 2",
                   page_icon="✨",
                   layout="wide")

st.markdown(
        """
        <div class="transparent-container">
            <h1>✨ PraGP SKM 2</h1>
            <h4>
            يٰٓاَيُّهَا الَّذِيْنَ اٰمَنُوْٓا اِنْ تَنْصُرُوا اللّٰهَ يَنْصُرْكُمْ وَيُثَبِّتْ اَقْدَامَكُمْ <br><br> 💡"Wahai orang-orang yang beriman, jika kamu menolong (agama) Allah, niscaya Dia akan menolongmu dan meneguhkan kedudukanmu" QS 47 ayat 7 <br><br>INFO:<br>Absensi ini khusus untuk SKM 2 saja ya..<br>(skm 1 dan 3 tidak perlu absen disini ok)
    </h4>
    
        """,
        unsafe_allow_html=True
    )
now = datetime.now() - timedelta(hours=-7)


formatted_now = now.strftime("%A, %d %B %Y - %H:%M:%S")
st.markdown(f"### 🗺️ {formatted_now}")
selected_date = now.day


if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()




name_list = name.iloc[1:28, 1].dropna().astype(str).tolist()  
name_list.insert(0, "-")


selected_name = st.selectbox("Pilih Nama:", name_list)
status_map = {"Hadir": "H", "Ijin": "I", "Sakit": "S"}
selected_status = st.selectbox("Pilih Status:", ["-", "Hadir", "Ijin", "Sakit"])

user_input = ""
if selected_status == "Ijin":
    user_input = st.text_input("Ketik alasan: (contoh: ijin kerja)")
elif selected_status == "Sakit":
    user_input = st.text_input("Ketik alasan: (contoh: sakit demam)")
elif selected_status == "Hadir":
    user_input = "Hadir" 


if st.button("Submit Kehadiran"):

    st.cache_data.clear()
    name = load_sheet()
    
    if selected_name == "-":
        st.warning("⚠️ Silakan pilih nama terlebih dahulu.")
    elif selected_status == "-":
        st.warning("⚠️ Pilih status kehadiran.")
    elif selected_status in ["Ijin", "Sakit"] and user_input.strip() == "":
        st.warning("⚠️ Alasan tidak boleh kosong.")
    else:
       
        st.session_state.submitted = True
      
        name_row = name.index[name.iloc[:, 1] == selected_name].tolist()

        if not name_row:
            st.error("Nama tidak ditemukan dalam daftar.")
        else:
            row_idx = name_row[0]
            col_idx = 3 + (selected_date - 1)  
            # kolom tanggal cek sheet nya pls
            name.iat[row_idx, col_idx] = status_map[selected_status]
            conn.update(worksheet=url, data=name)
     
            

         
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
            else:
                df = pd.DataFrame(columns=["Text"])

            new_row = pd.DataFrame({"Text": [f"{selected_name}: {user_input}"]})
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)

           
            if selected_status == "Hadir":
                st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga kehadiran hari ini membawa kebarokahan dan ilmu yang bermanfaat.")
            elif selected_status == "Ijin":
                st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga Allah paring kelonggaran waktu untuk hadir di pertemuan selanjutnya.")
            elif selected_status == "Sakit":
                st.success(f"✅ جَزَاكُمُ اللهُ خَيْرًا {selected_name} - Semoga Allah paring kesembuhan dan kesehatan yang barokah.")


if st.session_state.submitted:
    st.session_state.submitted = False
            
if os.path.exists(CSV_FILE):
    st.subheader("Kehadiran hari ini:")
    df_display = pd.read_csv(CSV_FILE)
   
    def censor_from_second_word(text):
        words = str(text).split()
        if len(words) > 1:
            censored = [words[0]] + ["*" * len(w) for w in words[1:]]
            return " ".join(censored)
        else:
            return text

    df_display["Absen"] = df_display["Text"].apply(censor_from_second_word)
    st.dataframe(df_display[["Absen"]])
    



st.markdown("---")
st.subheader("Khusus Admin")
admin_password = st.text_input("Masukan password untuk menggunakan fitur:", type="password")


if admin_password == ADMIN_PASSWORD:
    with st.expander("🧹 Clear data alasan"):
        if st.button("Clear Data"):
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
                st.success("✅ All data cleared successfully!")
                st.rerun()
            else:
                st.info("No data file found to clear.")
    with st.expander("🚀 Absen"):
        col1, col2 ,col3= st.columns(3)
        with col1:
            csv = dff.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ absen report",
                data=csv,
                file_name="absen report.csv",
                mime="text/csv")
        with col2:
            if st.button("⬇️ liat absen"):
                st.dataframe(dff, use_container_width=True, height=600)
        with col3:
            st.download_button(
                label="⬇️ alasan ijin/sakit",
                data=df_display.to_csv(index=False).encode('utf-8'),
                file_name="alasan ijin/sakit.csv",
                mime="text/csv")
    
else:
    if admin_password != "":
        st.error("❌ Incorrect password.")




































































































































































