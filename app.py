import streamlit as st
import pandas as pd
import joblib
import datetime
import data_prep as dp
import update_dataPrep as udp

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
    
    # 1. Country Selection - Use udp.df_adjust for consistent data source
    countries = sorted(udp.df_adjust['Country'].unique())
    country = st.selectbox("Destination Country", countries)
    
    # 2. University Selection (Filtered by Country)
    univs = sorted(udp.df_adjust[udp.df_adjust['Country'] == country]['University'].unique())
    university = st.selectbox("University", univs)
    
    # 3. Program Selection (Filtered by University)
    programs = sorted(udp.df_adjust[
        (udp.df_adjust['Country'] == country) & 
        (udp.df_adjust['University'] == university)
    ]['Program'].unique())
    program = st.selectbox("Program", programs)
    
    # 4. Level Selection (Filtered by Program)
    levels = sorted(udp.df_adjust[
        (udp.df_adjust['Country'] == country) & 
        (udp.df_adjust['University'] == university) &
        (udp.df_adjust['Program'] == program)
    ]['Level'].unique())
    level = st.selectbox("Degree Level", levels)
    
    # 5. Year Input
    current_year = datetime.datetime.now().year
    start_year = st.number_input("Target Start Year", min_value=current_year, value=current_year+5)
    
    predict_btn = st.button("Calculate Forecast", type="primary")

# --- MAIN LOGIC ---
if predict_btn:
    # Get Data Row from treated dataframe
    row = udp.df_adjust[
        (udp.df_adjust['Country'] == country) & 
        (udp.df_adjust['University'] == university) &
        (udp.df_adjust['Program'] == program) &
        (udp.df_adjust['Level'] == level)
    ].iloc[0]
    
    # Predict Rates
    c_code = COUNTRY_MAP.get(country, 3)
    curr_rate = dp.exchange_rate_growth()
    current_idr_rate = dp.get_current_exchange_rate()
    
    # Predict rates relative to the start year context
    rates = model.predict([[c_code, 3.0, start_year, curr_rate]])[0] / 100
    r_tui, r_rent, r_liv, r_ins = rates
    
    # IDR Growth factor
    idr_growth_factor = curr_rate / 100
    
    # Calculate Future Value at Start Year
    # Initial Base Costs (From pre-calculated columns)
    cur_tuition = row['Tuition_Yearly']
    cur_rent = row['Rent_USD']
    cur_liv_excl_rent = row['Monthly_Living_Cost'] - row['Rent_USD']
    cur_insurance = row['Insurance_USD']
    
    # Project Exchange Rate to Start Year
    projected_idr_rate = current_idr_rate
    
    years_gap = start_year - current_year
    
    if years_gap > 0:
        cur_tuition *= ((1 + r_tui) ** years_gap)
        cur_rent *= ((1 + r_rent) ** years_gap)
        cur_liv_excl_rent *= ((1 + r_liv) ** years_gap)
        cur_insurance *= ((1 + r_ins) ** years_gap)
        projected_idr_rate *= ((1 + idr_growth_factor) ** years_gap)
        
    # Generate Table Data
    duration = int(row.get('Duration_Years', 1))
    table_data = []
    
    for i in range(duration):
        year_study = start_year + i
        annual_liv = (cur_rent + cur_liv_excl_rent) * 12
        total_usd = cur_tuition + annual_liv + cur_insurance
        total_idr = total_usd * projected_idr_rate
        
        table_data.append({
            "Year": year_study,
            "Tuition (USD)": cur_tuition,
            "Living Cost (USD)": annual_liv,
            "Insurance (USD)": cur_insurance,
            "Total Budget (USD)": total_usd,
            "Total Budget (IDR)": total_idr
        })
        
        # Compound for next year
        cur_tuition *= (1 + r_tui)
        cur_rent *= (1 + r_rent)
        cur_liv_excl_rent *= (1 + r_liv)
        cur_insurance *= (1 + r_ins)
        projected_idr_rate *= (1 + idr_growth_factor)
        
    df_result = pd.DataFrame(table_data)
    
    # --- DISPLAY ---
    st.subheader(f"Financial Forecast: {university}")
    st.caption(f"{program} - {level} ({duration} Years)")
    st.markdown(f"**Current Exchange Rate:** 1 USD = Rp {current_idr_rate:,.2f} | **Avg Growth:** {curr_rate}%")
    
    # Key Metric Highlight
    total_est_usd = df_result['Total Budget (USD)'].sum()
    total_est_idr = df_result['Total Budget (IDR)'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Estimated Cost (USD)", f"${total_est_usd:,.2f}")
    with col2:
        st.metric("Total Estimated Cost (IDR)", f"Rp {total_est_idr:,.2f}")
    
    # Styled Table
    st.dataframe(
        df_result.style.format({
            "Year": "{:.0f}",
            "Tuition (USD)": "${:,.2f}",
            "Living Cost (USD)": "${:,.2f}",
            "Insurance (USD)": "${:,.2f}",
            "Total Budget (USD)": "${:,.2f}",
            "Total Budget (IDR)": "Rp {:,.2f}"
        }),
        use_container_width=True
    )