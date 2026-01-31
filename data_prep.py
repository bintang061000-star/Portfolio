import pandas as pd
import yfinance as yf

def load_dataset(file_name):
    return pd.read_csv(f"datasets/{file_name}.csv")

df_main = load_dataset("New International_Education_Costs")

df_us = load_dataset("US_Avg_Tuition")
df_uk = load_dataset("UK_Avg_Tuition")
df_au = load_dataset("Aus_Avg_Tuition")
df_other = load_dataset("Other_Avg_Tuition")

df_Growth_LivCost_US = load_dataset("Growth_LivCost_US")
df_Growth_LivCost_UK = load_dataset("Growth_LivCost_UK")
df_Growth_LivCost_Aus = load_dataset("Growth_LivCost_Aus")
df_Growth_LivCost_Other = load_dataset("Growth_LivCost_Other")

df_Growth_Insurance_US = load_dataset("Growth_Insurance_US")
df_Growth_Insurance_UK = load_dataset("Growth_Insurance_UK")
df_Growth_Insurance_Aus = load_dataset("Growth_Insurance_Aus")
df_Growth_Insurance_Other = load_dataset("Growth_Insurance_Other")

df_Growth_Rent_US = load_dataset("Growth_Rent_US")
df_Growth_Rent_UK = load_dataset("Growth_Rent_UK")
df_Growth_Rent_Aus = load_dataset("Growth_Rent_Aus")
df_Growth_Rent_Other = load_dataset("Growth_Rent_Other")

df_InfUS = load_dataset("US_Inflation")
df_InfUK = load_dataset("UK_Inflation")
df_InfAus = load_dataset("Aus_Inflation")
df_InfGlobal = load_dataset("Other_Inflation")

df_work = pd.DataFrame(df_main)

def update_data(df):
    update_typo = {
        'MIT' : 'Boston',
        'Massachusetts' : 'MIT'
    }

    update_level = {
        'Bachelor' : 'Bachelor',
        'Master' : 'Master',
        'PhD' : 'PhD'
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
    df['Monthly_Living_Cost'] = fix_livCost
    return df

def get_avgInf_Series(df, target_col):
    inflation = df[target_col].pct_change() * 100
    inflation = inflation.dropna()
    return inflation

def exchange_rate_growth():
    try:
        data_kurs = yf.Ticker("IDR=X").history(period="10y")
        if data_kurs.empty:
            return 0.0
        kurs_tahunan = data_kurs['Close'].resample('YE').mean()
        growth_kurs = kurs_tahunan.pct_change() * 100
        rerata_kenaikan_kurs = growth_kurs.mean()
        if pd.isna(rerata_kenaikan_kurs):
            return 0.0
        return round(rerata_kenaikan_kurs, 2)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return 0.0

def get_current_exchange_rate():
    try:
        data_kurs = yf.Ticker("IDR=X").history(period="1d")
        if not data_kurs.empty:
            return data_kurs['Close'].iloc[-1]
        return 16000.0
    except Exception as e:
        print(f"Error fetching current exchange rate: {e}")
        return 16000.0
