import pandas as pd
import joblib
import datetime
import data_prep as dp

# Load Model
try:
    model = joblib.load('budget_predictor_model.pkl')
except:
    model = None
    print("[ERROR] Model not found. Run model_engine.py first.")

COUNTRY_MAP = {'USA': 0, 'UK': 1, 'Australia': 2, 'Other': 3}

def predict_scenario(country, university, program, level, start_year):
    if not model: return
    
    # 1. Baseline Data (Filter by Country, Univ, Program, Level)
    data = dp.df_main[
        (dp.df_main['Country'] == country) & 
        (dp.df_main['University'] == university) &
        (dp.df_main['Program'] == program) &
        (dp.df_main['Level'] == level)
    ]
    
    if data.empty:
        print(f"Dataset not found for {program} ({level}) at {university}, {country}.")
        return

    current_year = datetime.datetime.now().year
    
    if start_year < current_year:
        print("Start year cannot be in the past.")
        return

    # 2. Predict Growth Rates (AI)
    c_code = COUNTRY_MAP.get(country, 3)
    curr_rate = dp.exchange_rate_growth()
    rates = model.predict([[c_code, 3.0, start_year, curr_rate]])[0] / 100
    r_tui, r_rent, r_liv, r_ins = rates

    print(f"\n{'='*95}")
    print(f"ANALYSIS REPORT: {university} ({country})")
    print(f"Program: {program} | Level: {level}")
    print(f"Timeline: {current_year} -> {start_year}")
    print(f"{'='*95}")

    for _, row in data.iterrows():
        # Get Program Duration
        duration_years = int(row.get('Duration_Years', 1))
        
        # Initial Values (Base Year)
        current_tuition = row['Tuition_USD'] * 2
        base_liv_idx = 1650 
        current_liv_excl_rent = (row['Living_Cost_Index'] / 100) * base_liv_idx
        current_rent = row['Rent_USD']
        current_insurance = row['Insurance_USD']

        # Calculate Future Value at Start Year (Compound Interest from Now -> Start Year)
        years_gap = start_year - current_year
        if years_gap > 0:
            current_tuition *= ((1 + r_tui) ** years_gap)
            current_rent *= ((1 + r_rent) ** years_gap)
            current_liv_excl_rent *= ((1 + r_liv) ** years_gap)
            current_insurance *= ((1 + r_ins) ** years_gap)

        # Table Header
        print(f"Duration: {duration_years} Years")
        print(f"{'-'*95}")
        print(f"{'Year':<6} | {'Annual Tuition':<18} | {'Annual Living Cost':<20} | {'Annual Insurance':<18} | {'Total Budget':<15}")
        print(f"{'-'*95}")

        # Loop for the DURATION of the study (Start Year -> End of Program)
        for i in range(duration_years):
            year_study = start_year + i
            
            annual_living_cost = (current_rent + current_liv_excl_rent) * 12
            total_budget = current_tuition + annual_living_cost + current_insurance
            
            print(f"{year_study:<6} | ${current_tuition:,.2f}{'':<8} | ${annual_living_cost:,.2f}{'':<10} | ${current_insurance:,.2f}{'':<8} | ${total_budget:,.2f}")
            
            # Apply Growth for NEXT year
            current_tuition *= (1 + r_tui)
            current_rent *= (1 + r_rent)
            current_liv_excl_rent *= (1 + r_liv)
            current_insurance *= (1 + r_ins)

        print(f"{'-'*95}")

def run_app():
    print("\n--- INPUT RENCANA STUDI ---")
    try:
        u_country = input("Masukkan Negara Tujuan (USA/UK/Australia/Other): ").strip()
        u_univ = input("Masukkan Nama Universitas (sesuai data): ").strip()
        u_program = input("Masukkan Nama Program (misal Computer Science): ").strip()
        u_level = input("Masukkan Level Studi (Bachelor/Master/PhD): ").strip()
        u_year_str = input("Rencana Tahun Keberangkatan (misal 2030): ").strip()
        
        if not u_year_str.isdigit():
            print("Error: Tahun harus berupa angka.")
        else:
            u_year = int(u_year_str)
            predict_scenario(u_country, u_univ, u_program, u_level, u_year)
            
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")

if __name__ == "__main__":
    run_app()