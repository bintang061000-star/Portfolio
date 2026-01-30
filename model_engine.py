import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import data_prep as dp

def load_data():
    datasets = [('US', 0), ('UK', 1), ('Aus', 2), ('Other', 3)]
    dfs = []
    
    for nation, code in datasets:
        try:
            folder = "datasets"
            df_tui = pd.read_csv(f"{folder}/{nation}_Avg_Tuition.csv")
            df_rent = pd.read_csv(f"{folder}/Growth_Rent_{nation}.csv")
            df_liv = pd.read_csv(f"{folder}/Growth_LivCost_{nation}.csv")
            df_ins = pd.read_csv(f"{folder}/Growth_Insurance_{nation}.csv")
            df_inf = pd.read_csv(f"{folder}/{nation}_Inflation.csv")

            merged = df_tui.merge(df_rent, on='Year', suffixes=('_tui', '_rent')) \
                           .merge(df_liv, on='Year') \
                           .merge(df_ins, on='Year', suffixes=('_liv', '_ins')) \
                           .merge(df_inf, on='Year')

            merged = merged.rename(columns={
                'Growth_tui': 'y_tuition', 'Growth_rent': 'y_rent',
                'Growth_liv': 'y_living', 'Growth_ins': 'y_insur',
                'Growth': 'x_inflation'
            })
            merged['Country_Code'] = code
            dfs.append(merged)
        except Exception:
            continue

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

if __name__ == "__main__":
    df = load_data()
    
    if not df.empty:
        df['x_currency'] = dp.exchange_rate_growth()
        
        X = df[['Country_Code', 'x_inflation', 'Year', 'x_currency']]
        y = df[['y_tuition', 'y_rent', 'y_living', 'y_insur']]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        pred = model.predict(X_test)
        
        print(f"MAE: {mean_absolute_error(y_test, pred):.2f}%")
        print(f"R2 Score: {r2_score(y_test, pred):.4f}")
        
        joblib.dump(model, 'budget_predictor_model.pkl')