import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

# Upload deposit and withdrawal files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_first_sheet(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]   # take first sheet automatically
    return pd.read_excel(file, sheet_name=first_sheet)

if deposit_file and withdrawal_file:
    try:
        deposits = load_first_sheet(deposit_file)
        withdrawals = load_first_sheet(withdrawal_file)

        st.subheader("Preview: Deposits")
        st.dataframe(deposits.head())

        st.subheader("Preview: Withdrawals")
        st.dataframe(withdrawals.head())

        # Save raw cleaned outputs (placeholders for now)
        output_file = "Processed_Report.xlsx"
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            deposits.to_excel(writer, sheet_name="Deposits", index=False)
            withdrawals.to_excel(writer, sheet_name="Withdrawals", index=False)

        with open(output_file, "rb") as f:
            st.download_button("Download Processed Report", f, file_name=output_file)

    except Exception as e:
        st.error(f"Error reading files: {e}")
