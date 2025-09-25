import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

# Upload deposit and withdrawal files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_first_sheet(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    return pd.read_excel(file, sheet_name=first_sheet, header=None)  # load raw, no headers

if deposit_file and withdrawal_file:
    try:
        deposits_raw = load_first_sheet(deposit_file)
        withdrawals_raw = load_first_sheet(withdrawal_file)

        # Show first 15 rows so we can locate real headers
        st.subheader("Deposit File Preview")
        st.dataframe(deposits_raw.head(15))

        st.subheader("Withdrawal File Preview")
        st.dataframe(withdrawals_raw.head(15))

        st.info("Check the preview above and tell me which row number contains the actual column headers (e.g., Date, Credit Amt, Debit Amt, Balance).")

    except Exception as e:
        st.error(f"Error reading files: {e}")
