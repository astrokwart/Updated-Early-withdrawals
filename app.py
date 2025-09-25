import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

# Upload deposit and withdrawal files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_first_sheet(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    return pd.read_excel(file, sheet_name=first_sheet)

if deposit_file and withdrawal_file:
    try:
        deposits_raw = load_first_sheet(deposit_file)
        withdrawals_raw = load_first_sheet(withdrawal_file)

        # Debug: Show column names
        st.write("Deposit file columns:", deposits_raw.columns.tolist())
        st.write("Withdrawal file columns:", withdrawals_raw.columns.tolist())

        # Stop here for now, just to inspect
        st.stop()

    except Exception as e:
        st.error(f"Error reading files: {e}")
