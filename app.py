import streamlit as st
import pandas as pd
import joblib
import datetime
import data_prep as dp

# --- CONFIG ---
st.set_page_config(page_title="EduCost Predictor", layout="wide")
st.title("Education Budget Forecaster")
st.markdown("Estimate your future study costs using Machine Learning (Random Forest).")

# --- LOAD MODEL (Cached) ---
@st.cache_resource
def load_model():
    try:
        return joblib.load('budget_predictor_model.pkl')
    except:
        return None

model = load_model()

if not model:
    st.error("Model not found! Please run `model_engine.py` first to generate the .pkl file.")
    st.stop()

COUNTRY_MAP = {'USA': 0, 'UK': 1, 'Australia': 2, 'Other': 3}

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Study Plan")
    
    # 1. Country Selection
    countries = sorted(dp.df_main['Country'].unique())
    country = st.selectbox("Destination Country", countries)
    
    # 2. University Selection (Filtered by Country)
    univs = sorted(dp.df_main[dp.df_main['Country'] == country]['University'].unique())
    university = st.selectbox("University", univs)
    
    # 3. Program Selection (Filtered by University)
    programs = sorted(dp.df_main[
        (dp.df_main['Country'] == country) & 
        (dp.df_main['University'] == university)
    ]['Program'].unique())
    program = st.selectbox("Program", programs)
    
    # 4. Level Selection (Filtered by Program)
    levels = sorted(dp.df_main[
        (dp.df_main['Country'] == country) & 
        (dp.df_main['University'] == university) &
        (dp.df_main['Program'] == program)
    ]['Level'].unique())
    level = st.selectbox("Degree Level", levels)
    
    # 5. Year Input
    current_year = datetime.datetime.now().year
    start_year = st.number_input("Target Start Year", min_value=current_year, value=current_year+5)
    
    predict_btn = st.button("Calculate Forecast", type="primary")

# --- MAIN LOGIC ---
if predict_btn:
    # Get Data Row
    row = dp.df_main[
        (dp.df_main['Country'] == country) & 
        (dp.df_main['University'] == university) &
        (dp.df_main['Program'] == program) &
        (dp.df_main['Level'] == level)
    ].iloc[0]
    
    # Predict Rates
    c_code = COUNTRY_MAP.get(country, 3)
    curr_rate = dp.exchange_rate_growth()
    # Predict rates relative to the start year context
    rates = model.predict([[c_code, 3.0, start_year, curr_rate]])[0] / 100
    r_tui, r_rent, r_liv, r_ins = rates
    
    # Calculate Future Value at Start Year
    # Initial Base Costs
    cur_tuition = row['Tuition_USD'] * 2
    cur_liv_excl_rent = (row['Living_Cost_Index']/100) * 1650
    cur_rent = row['Rent_USD']
    cur_insurance = row['Insurance_USD']
    
    years_gap = start_year - current_year
    
    if years_gap > 0:
        cur_tuition *= ((1 + r_tui) ** years_gap)
        cur_rent *= ((1 + r_rent) ** years_gap)
        cur_liv_excl_rent *= ((1 + r_liv) ** years_gap)
        cur_insurance *= ((1 + r_ins) ** years_gap)
        
    # Generate Table Data
    duration = int(row.get('Duration_Years', 1))
    table_data = []
    
    for i in range(duration):
        year_study = start_year + i
        annual_liv = (cur_rent + cur_liv_excl_rent) * 12
        total = cur_tuition + annual_liv + cur_insurance
        
        table_data.append({
            "Year": year_study,
            "Tuition": cur_tuition,
            "Living Cost": annual_liv,
            "Insurance": cur_insurance,
            "Total Budget": total
        })
        
        # Compound for next year
        cur_tuition *= (1 + r_tui)
        cur_rent *= (1 + r_rent)
        cur_liv_excl_rent *= (1 + r_liv)
        cur_insurance *= (1 + r_ins)
        
    df_result = pd.DataFrame(table_data)
    
    # --- DISPLAY ---
    st.subheader(f"Financial Forecast: {university}")
    st.caption(f"{program} - {level} ({duration} Years)")
    
    # Key Metric Highlight
    total_est = df_result['Total Budget'].sum()
    st.metric("Total Estimated Cost (Full Degree)", f"${total_est:,.2f}")
    
    # Styled Table
    st.dataframe(
        df_result.style.format({
            "Year": "{:.0f}",
            "Tuition": "${:,.2f}",
            "Living Cost": "${:,.2f}",
            "Insurance": "${:,.2f}",
            "Total Budget": "${:,.2f}"
        }),
        use_container_width=True
    )