import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

# Upload deposit and withdrawal files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_clean_file(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    # Start reading from row 5 (index=4)
    df = pd.read_excel(file, sheet_name=first_sheet, header=4)
    return df

if deposit_file and withdrawal_file:
    try:
        deposits = load_clean_file(deposit_file)
        withdrawals = load_clean_file(withdrawal_file)

        st.subheader("Deposit File (Cleaned Preview)")
        st.dataframe(deposits.head())

        st.subheader("Withdrawal File (Cleaned Preview)")
        st.dataframe(withdrawals.head())

        st.success("Files loaded and headers fixed. Ready for processing!")

    except Exception as e:
        st.error(f"Error processing files: {e}")
