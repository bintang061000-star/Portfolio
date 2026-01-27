import datetime
import update_dataPrep as udp  # Untuk ambil Rates Inflasi
import data_prep as dp  # PENTING: Untuk ambil Data Kampus (df)

def main():
    print("=== SIMULASI BIAYA KULIAH BY KAMPUS ===")
    
    # 1. LOAD DATA INFLASI (Memory)
    rates_memory = udp.update_tuiInf()
    
    # 2. INPUT NAMA UNIVERSITAS
    # Tips: Tampilkan dulu daftar kampus yg tersedia (opsional, biar user tau)
    # print("Kampus tersedia:", dp.df['University'].unique()) 
    
    input_univ = input("Masukkan Nama Universitas (Sesuai Data): ")
    
    # --- LOGIKA PENCARIAN DATA (FILTERING) ---
    # Kita cari baris di tabel 'dp.df_main' yang kolom University-nya sama dengan input user
    data_kampus = dp.df_main[dp.df_main['University'] == input_univ]

    # Cek: Apakah kampusnya ketemu?
    if data_kampus.empty:
        print(f"\n[ERROR] Maaf, universitas '{input_univ}' tidak ditemukan di database.")
        print("Pastikan penulisan huruf besar/kecil sesuai.")
        return # Berhenti jika data tidak ada
    else:
        # Jika ketemu, ambil datanya (Values[0] artinya ambil data pertama yg ketemu)
        biaya_sekarang = data_kampus['Tuition_USD'].values[0]
        negara_otomatis = data_kampus['Country'].values[0]
        
        print(f"\n[SUKSES] Data Ditemukan!")
        print(f"Lokasi: {negara_otomatis}")
        print(f"Biaya Saat Ini: ${biaya_sekarang:,.2f}")

    # 3. INPUT SISA (Tahun Rencana)
    rencana_tahun = int(input("\nRencana kuliah berapa tahun lagi? (misal: 5): "))

    # 4. AMBIL RATE OTOMATIS (Berdasarkan Negara Otomatis tadi)
    # Kita pakai 'negara_otomatis', bukan input manual lagi
    rate_inflasi = rates_memory.get(negara_otomatis, 3.0) 

    print(f"\n[INFO] Menggunakan laju inflasi: {rate_inflasi}% ({negara_otomatis})")
    
    # --- MULAI HITUNGAN ---
    print("-" * 50)
    print(f"{'Tahun':<10} | {'Status':<15} | {'Estimasi Biaya (USD)':<20}")
    print("-" * 50)

    tahun_ini = datetime.datetime.now().year
    biaya_progresif = biaya_sekarang

    # Tampilkan Tahun Ini
    print(f"{tahun_ini:<10} | {'Sekarang':<15} | ${biaya_progresif:,.2f}")

    for i in range(1, rencana_tahun + 1):
        tahun_target = tahun_ini + i
        biaya_progresif = biaya_progresif * (1 + rate_inflasi/100)
        print(f"{tahun_target:<10} | {'+ ' + str(i) + ' Tahun':<15} | ${biaya_progresif:,.2f}")

    print("-" * 50)
    print(f"KESIMPULAN: Jika kuliah di {input_univ} ({negara_otomatis}) tahun {tahun_ini + rencana_tahun},")
    print(f"Siapkan dana sekitar ${biaya_progresif:,.2f}")

if __name__ == "__main__":
    main()