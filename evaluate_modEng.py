import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

# Import script kamu untuk build data ulang
# (Kita butuh X_test dan y_test yang sama dengan saat training)
from model_engine import build_country_dataset 

# --- 1. PERSIAPAN DATA (Re-Build untuk Test) ---
print("[PROCESS] Re-building test data for evaluation...")
df_usa = build_country_dataset('USA', 0)
df_uk  = build_country_dataset('UK', 1)
df_aus = build_country_dataset('Australia', 2)
df_oth = build_country_dataset('Other', 3)

master_df = pd.concat([df_usa, df_uk, df_aus, df_oth], ignore_index=True)

X = master_df[['Country_Code', 'Inflation_Rate', 'Year_Index']]
y = master_df[['Tuition_Growth', 'Rent_Growth', 'Living_Growth', 'Insurance_Growth']]

# Split harus sama persis dengan train_model (random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 2. LOAD MODEL ---
print("[PROCESS] Loading model...")
try:
    rf_model = joblib.load('budget_predictor_model.pkl')
except FileNotFoundError:
    print("❌ Model belum ada! Jalankan train_model.py dulu.")
    exit()

# --- 3. MULAI PENGECEKAN ---
preds = rf_model.predict(X_test)

# A. CEK METRICS (ANGKA)
print("\n" + "="*40)
print("📊 1. EVALUASI METRICS (AKURASI)")
print("="*40)

# R-Squared (Seberapa baik model menjelaskan variasi data. Mendekati 1 = Sempurna)
r2 = r2_score(y_test, preds)
mae = mean_absolute_error(y_test, preds)

print(f"Global R-Squared Score : {r2:.4f} (Mendekati 1.0 makin bagus)")
print(f"Mean Absolute Error    : {mae:.2f}% (Rata-rata meleset cuma segini)")

if r2 > 0.7:
    print("✅ Kesimpulan: Model SANGAT BAGUS (Strong fit).")
elif r2 > 0.5:
    print("⚠️ Kesimpulan: Model CUKUP OKE (Moderate fit).")
else:
    print("❌ Kesimpulan: Model KURANG AKURAT (Underfitting). Perbanyak data!")

# B. CEK FEATURE IMPORTANCE (KENAPA MODEL MEMPREDIKSI ITU?)
print("\n" + "="*40)
print("🧠 2. FEATURE IMPORTANCE (LOGIKA ML)")
print("="*40)
# Random Forest bisa memberi tahu fitur mana yang paling penting
importances = rf_model.feature_importances_
feature_names = ['Country', 'Inflation (Macro)', 'Year (Time)']

# Buat DataFrame biar rapi
fi_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
fi_df = fi_df.sort_values(by='Importance', ascending=False)

print(fi_df)
print("\n💡 Insight: Fitur dengan skor tertinggi adalah penentu utama kenaikan harga.")

# C. VISUALISASI (Opsional jika punya matplotlib)
try:
    plt.figure(figsize=(10, 5))
    sns.barplot(x='Importance', y='Feature', data=fi_df, palette='viridis')
    plt.title('Apa Faktor Paling Berpengaruh pada Kenaikan Biaya?')
    plt.xlabel('Tingkat Kepentingan (0-1)')
    plt.tight_layout()
    plt.show()
    print("📈 Grafik Feature Importance ditampilkan.")
except Exception:
    pass

# D. REALITY CHECK (SAMPEL DATA)
print("\n" + "="*40)
print("👀 3. REALITY CHECK (ASLI vs PREDIKSI)")
print("="*40)
# Kita ambil 5 data acak dari hasil tes
sample_idx = np.random.choice(len(y_test), 5)
real_sample = y_test.iloc[sample_idx]
pred_sample = preds[sample_idx]

comparison = pd.DataFrame({
    'Tuition Real (%)': real_sample['Tuition_Growth'].values,
    'Tuition Pred (%)': pred_sample[:, 0], # Kolom 0 itu Tuition
    'Rent Real (%)': real_sample['Rent_Growth'].values,
    'Rent Pred (%)': pred_sample[:, 1]     # Kolom 1 itu Rent
})

print(comparison)