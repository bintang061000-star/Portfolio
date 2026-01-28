import pandas as pd
import yfinance as yf

df_main = pd.read_csv("New International_Education_Costs.csv")
df_us = pd.read_csv("US_Avg_Tuition.csv")
df_uk = pd.read_csv("UK_Avg_Tuition.csv")
df_au = pd.read_csv("Aus_Avg_Tuition.csv")

df_work = pd.DataFrame(df_main)

def update_data(df):
    update_typo = {
        'MIT' : 'Boston',
        'Massachusetts' : 'MIT'
    }

    update_level = {
        'Bachelor' : 1,
        'Master' : 2,
        'PhD' : 3
    }

        # Update Living Cost Index
    update_liv_cost = {
        #Australia
        'Brisbane': 69.13,
        'Canberra': 69.18,
        'Melbourne': 72.62,
        'Sydney': 74.45,

        #Austria
        'Vienna': 72.95,

        #Belgium
        'Brussels': 72.15,

        #Canada
        'Montreal': 66.42,
        'Sherbrooke': 58.37,

        #China
        'Beijing': 51.57,

        #Egypt
        'Cairo': 35.10,

        #France
        'Lille': 68.37,
        'Lyon': 73.23,
        'Nice': 74.07,
        'Paris': 79.45,
        'Toulouse': 69.70,

        #Germany
        'Berlin': 67.67,
        'Hamburg': 70.27,
        'Munich': 71.17,

        #Greece
        'Athens': 62.13,

        #Netherlands
        'Amsterdam': 75.97,

        #New Zeeland
        'Auckland': 76.27,

        #Singapore
        'Singapore': 82.02,

        #South Korea'
        'Busan': 69.60,
        'Daejeon': 72.90,
        'Seoul': 82.37,

        #Spain
        'Barcelona': 69.87,

        #Switzerland
        'Basel': 96.80,
        'Lugano': 96.70,

        #UK
        'Bristol': 70.26,
        'Cambridge': 74.10,
        'Edinburgh': 69.70,
        'Leeds': 65.32,
        'London': 78.44,
        'Manchester': 67.34,

        #USA
        'Austin': 70.38,
        'Boston': 82.32,
        'Madison': 70.35
    }
    df['City'] = df['City'].replace(update_typo)
    df['University'] = df['University'].replace(update_typo)
    df['Level'] = df['Level'].map(update_level).fillna(df['Level'])
    df['Living_Cost_Index'] = df['City'].map(update_liv_cost).fillna(df['Living_Cost_Index'])
    return df

def append_yeCost(df):
    df['Rent_Yearly'] = df['Rent_USD'] * 12
    df['Tuition_Yearly'] = df['Tuition_USD'] * 2
    return df

def exact_livCost (df):
    baseline = 1650
    livCost_exclRent = df['Living_Cost_Index'] / 100 * baseline
    fix_livCost = livCost_exclRent + df['Rent_USD']
    df['Exact_Living_Cost'] = fix_livCost
    return df

def get_avgInfTui(df):
    inflation = df['Avg_Tuition'].pct_change() * 100
    return round(inflation.mean(), 2)

# def main ():
#     try:
#         # 1. Coba Load Semua Data
#         print("Sedang memuat data...")
#         df_main = pd.read_csv("New International_Education_Costs.csv")
#         df_us = pd.read_csv("US_Avg_Tuition.csv")
#         df_uk = pd.read_csv("UK_Avg_Tuition.csv")
#         df_au = pd.read_csv("Aus_Avg_Tuition.csv")
        
#         print("Sukses memuat semua data!")
        
#         # Kembalikan data agar bisa dipakai fungsi lain
#         return df_main, df_us, df_uk, df_au

#     except FileNotFoundError as e:
#         # 2. Khusus Error kalau File Tidak Ada
#         print(f"\n[ERROR FATAL] File tidak ditemukan: {e}")
#         print("Pastikan nama file benar dan ada di folder yang sama.")
#         sys.exit() # Matikan program karena percuma jalan tanpa data

#     except Exception as e:
#         # 3. Error Lainnya (Misal: Format CSV rusak, Pandas belum install, dll)
#         print(f"\n[ERROR TIDAK TERDUGA]: {e}")
#         sys.exit()

# class InflationEngine:
#     # 1. Pintu Masuk (Terima Data Mentah)
#     def __init__(self, df_main, df_us, df_uk, df_au):
#         self.univ_map = dict(zip(df_main['University'], df_main['Country']))
        
#         # 2. EKSEKUSI DI SINI (Di dalam __init__)
#         # Kita panggil method '_hitung_growth' (blender yang sama) berulang kali
#         self.rates = {
#             'USA': self._hitung_growth(df_us),       # Panggil untuk US
#             'UK': self._hitung_growth(df_uk),        # Panggil untuk UK
#             'Australia': self._hitung_growth(df_au)  # Panggil untuk Aus
#         }
        
#         # Hitung rata-rata untuk default
#         self.default_rate = round(sum(self.rates.values()) / 3, 2)

#     # 3. METHOD UNIVERSAL (Si Blender)
#     # Ini adalah fungsi efisien yang kamu tanyakan tadi.
#     # Kita taruh di dalam class sebagai 'Private Method' (pake underscore _)
#     def _hitung_growth(self, df):
#         # Logika satu baris yang efisien
#         return round(df['Avg_Tuition'].pct_change().mean() * 100, 2)

#     # 4. Method Prediksi (Output ke User)
#     def get_prediction(self, university_name, current_cost, years):
#         country = self.univ_map.get(university_name, 'Unknown')
#         rate = self.rates.get(country, self.default_rate)
        
#         future_cost = current_cost * ((1 + rate/100) ** years)
#         return future_cost, rate
