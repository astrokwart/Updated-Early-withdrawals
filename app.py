import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool - Debug Mode")

deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_clean_file(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    df = pd.read_excel(file, sheet_name=first_sheet, header=4)
    return df

if deposit_file and withdrawal_file:
    try:
        deposits = load_clean_file(deposit_file)
        withdrawals = load_clean_file(withdrawal_file)

        st.subheader("Deposit Columns")
        st.write(list(deposits.columns))

        st.subheader("Withdrawal Columns")
        st.write(list(withdrawals.columns))

        st.info("Please copy the exact column names for Date, Account Number, Credit Amt, Debit Amt, etc.")

    except Exception as e:
        st.error(f"Error reading files: {e}")
