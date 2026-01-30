import sys
import os
import subprocess
import model_engine
import data_prep
import update_dataPrep

def main():
    print("===========================================")
    print("   EDUCATION BUDGET PREDICTOR PIPELINE     ")
    print("===========================================\n")

    # 1. Train the Model
    print(">>> [Step 1/2] Training & Saving Model...")
    try:
        model_engine.train_model()
        print("    [OK] Model trained and saved successfully.")
    except Exception as e:
        print(f"    [ERROR] Failed to train model: {e}")
        return

    # 2. Launch Streamlit App
    print("\n>>> [Step 2/2] Launching Streamlit Interface...")
    print("    Redirecting to your web browser...")
    print("    (Press Ctrl+C here to stop the server)\n")
    
    # Execute 'streamlit run app.py'
    # using os.system for direct shell interaction
    print("    Starting Streamlit server...")
    print("    If the browser does not open, please visit: http://localhost:8501")
    
    cmd = f'"{sys.executable}" -m streamlit run app.py'
    os.system(cmd)

if __name__ == "__main__":
    main()
