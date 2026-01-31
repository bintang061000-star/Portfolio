import pandas as pd
import joblib
import datetime
import data_prep as dp
import update_dataPrep as udp

try:
    model = joblib.load('budget_predictor_model.pkl')
except:
    model = None
    print("[ERROR] Model not found. Run model_engine.py first.")

COUNTRY_MAP = {'USA': 0, 'UK': 1, 'Australia': 2, 'Other': 3}

def predict_scenario(country, university, program, level, start_year):
    if not model: return
    
    # 1. Baseline Data (Filter by Country, Univ, Program, Level)
    data = udp.df_adjust[
        (udp.df_adjust['Country'] == country) & 
        (udp.df_adjust['University'] == university) &
        (udp.df_adjust['Program'] == program) &
        (udp.df_adjust['Level'] == level)
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
    current_idr_rate = dp.get_current_exchange_rate()
    rates = model.predict([[c_code, 3.0, start_year, curr_rate]])[0] / 100
    r_tui, r_rent, r_liv, r_ins = rates
    
    # IDR Growth factor (using the historical avg growth rate)
    idr_growth_factor = curr_rate / 100

    print(f"\n{'='*95}")
    print(f"ANALYSIS REPORT: {university} ({country})")
    print(f"Program: {program} | Level: {level}")
    print(f"Timeline: {current_year} -> {start_year}")
    print(f"Current Exchange Rate: 1 USD = {current_idr_rate:,.2f} IDR (Growth: {curr_rate}%)")
    print(f"{'='*95}")

    for _, row in data.iterrows():
        # Get Program Duration
        duration_years = int(row.get('Duration_Years', 1))
        
        # Initial Values (Base Year)
        current_tuition = row['Tuition_Yearly']
        current_rent = row['Rent_USD']
        current_liv_excl_rent = row['Monthly_Living_Cost'] - row['Rent_USD']
        current_insurance = row['Insurance_USD']
        
        # Project Exchange Rate to Start Year
        projected_idr_rate = current_idr_rate

        # Calculate Future Value at Start Year (Compound Interest from Now -> Start Year)
        years_gap = start_year - current_year
        if years_gap > 0:
            current_tuition *= ((1 + r_tui) ** years_gap)
            current_rent *= ((1 + r_rent) ** years_gap)
            current_liv_excl_rent *= ((1 + r_liv) ** years_gap)
            current_insurance *= ((1 + r_ins) ** years_gap)
            projected_idr_rate *= ((1 + idr_growth_factor) ** years_gap)

        # Table Header
        print(f"Duration: {duration_years} Years")
        print(f"{'-'*130}") # Extended for IDR column
        print(f"{'Year':<6} | {'Annual Tuition':<18} | {'Annual Living Cost':<20} | {'Annual Insurance':<18} | {'Total Budget (USD)':<20} | {'Total Budget (IDR)':<25}")
        print(f"{'-'*130}")

        # Loop for the DURATION of the study (Start Year -> End of Program)
        for i in range(duration_years):
            year_study = start_year + i
            
            annual_living_cost = (current_rent + current_liv_excl_rent) * 12
            total_budget_usd = current_tuition + annual_living_cost + current_insurance
            total_budget_idr = total_budget_usd * projected_idr_rate
            
            print(f"{year_study:<6} | ${current_tuition:,.2f}{'':<8} | ${annual_living_cost:,.2f}{'':<10} | ${current_insurance:,.2f}{'':<8} | ${total_budget_usd:,.2f}{'':<8} | Rp {total_budget_idr:,.2f}")
            
            # Apply Growth for NEXT year
            current_tuition *= (1 + r_tui)
            current_rent *= (1 + r_rent)
            current_liv_excl_rent *= (1 + r_liv)
            current_insurance *= (1 + r_ins)
            projected_idr_rate *= (1 + idr_growth_factor)

        print(f"{'-'*130}")

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