import sys
import os

def main():
    cmd = f'"{sys.executable}" -m streamlit run app.py'
    os.system(cmd)

if __name__ == "__main__":
    main()
