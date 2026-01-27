import streamlit as st
import pandas as pd
import datetime
import data_prep as dp  # Data Frame Utama
import update_dataPrep as udp  # Logic Inflasi

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="EduCost Predictor", layout="wide")

st.title("🎓 Kalkulator Inflasi Biaya Pendidikan")
st.markdown("Simulasi kenaikan biaya kuliah di luar negeri berdasarkan data historis inflasi.")

# --- 2. SIDEBAR (UNTUK INPUT USER) ---
with st.sidebar:
    st.header("Parameter Simulasi")
    
    # A. Load Data Inflasi (Disimpan di Cache biar cepat)
    # Kita pakai st.cache_data supaya tidak hitung ulang terus menerus
    @st.cache_data
    def load_inflation():
        return udp.update_tuiInf()

    rates_memory = load_inflation()
    
    # B. Input Kampus (Dropdown, bukan ketik manual!)
    # Ambil daftar unik universitas dari dataframe
    list_kampus = sorted(dp.df_main['University'].unique())
    pilihan_kampus = st.selectbox("Pilih Universitas:", list_kampus)
    
    # C. Input Tahun Rencana (Slider)
    rencana_tahun = st.slider("Rencana Kuliah (Berapa tahun lagi?)", 1, 10, 5)

# --- 3. LOGIKA UTAMA (MAIN ENGINE) ---

# Cari data kampus yang dipilih user
# Filter baris yang University-nya sama dengan pilihan user
data_kampus_terpilih = dp.df_main[dp.df_main['University'] == pilihan_kampus].iloc[0]

# Ambil informasi penting dari data tersebut
negara_asal = data_kampus_terpilih['Country']
biaya_saat_ini = data_kampus_terpilih['Tuition_USD']

# Ambil Rate Inflasi dari Memory (Logic .get yang kita bahas tadi)
rate_inflasi = rates_memory.get(negara_asal, 3.0) # Default 3.0 jika negara unknown

# --- 4. TAMPILKAN INFO UTAMA (METRICS) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Lokasi Kampus", negara_asal)

with col2:
    st.metric("Biaya Saat Ini (USD)", f"${biaya_saat_ini:,.0f}")

with col3:
    # Tampilkan Rate Inflasi (Merah artinya naik)
    st.metric("Laju Inflasi Historis", f"{rate_inflasi}%", delta=f"{rate_inflasi}%")

st.divider()

# --- 5. KALKULASI LOOPING (LOGIKA MASA DEPAN) ---
# Kita simpan hasilnya dalam bentuk List of Dictionary agar mudah jadi Tabel/Grafik
hasil_prediksi = []

tahun_sekarang = datetime.datetime.now().year
biaya_progresif = biaya_saat_ini

# Masukkan data tahun ini (Tahun ke-0)
hasil_prediksi.append({
    "Tahun": tahun_sekarang,
    "Status": "Sekarang",
    "Estimasi Biaya (USD)": round(biaya_progresif, 2)
})

# Loop untuk tahun-tahun berikutnya
for i in range(1, rencana_tahun + 1):
    tahun_target = tahun_sekarang + i
    
    # RUMUS COMPOUNDING
    biaya_progresif = biaya_progresif * (1 + rate_inflasi/100)
    
    hasil_prediksi.append({
        "Tahun": tahun_target,
        "Status": f"+ {i} Tahun",
        "Estimasi Biaya (USD)": round(biaya_progresif, 2)
    })

# Ubah List menjadi DataFrame (Tabel Pandas) supaya bisa divisualisasikan
df_hasil = pd.DataFrame(hasil_prediksi)

# --- 6. VISUALISASI HASIL (TABEL & GRAFIK) ---
col_kiri, col_kanan = st.columns([1, 2]) # Kolom kanan lebih lebar buat grafik

with col_kiri:
    st.subheader("Tabel Rincian")
    # Tampilkan tabel data
    st.dataframe(df_hasil.style.format({"Estimasi Biaya (USD)": "${:,.2f}"}))

with col_kanan:
    st.subheader("Tren Kenaikan Biaya")
    # Tampilkan Grafik Garis
    st.line_chart(df_hasil, x="Tahun", y="Estimasi Biaya (USD)")

# --- 7. KESIMPULAN (MSG BOX) ---
biaya_akhir = df_hasil.iloc[-1]['Estimasi Biaya (USD)']
kenaikan_total = biaya_akhir - biaya_saat_ini

st.warning(f"""
**Kesimpulan:**
Jika kamu berencana kuliah di **{pilihan_kampus}** pada tahun **{tahun_sekarang + rencana_tahun}**, 
kamu perlu menyiapkan dana sekitar **${biaya_akhir:,.2f}**.
Biaya ini naik sebesar **${kenaikan_total:,.2f}** dari harga sekarang akibat inflasi pendidikan.
""")