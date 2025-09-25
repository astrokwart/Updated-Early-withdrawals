import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

# Upload deposit and withdrawal files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

if deposit_file and withdrawal_file:
    # Read uploaded Excel files
    try:
        deposits = pd.read_excel(deposit_file, sheet_name="Sheet1")
        withdrawals = pd.read_excel(withdrawal_file, sheet_name="Sheet1")

        st.subheader("Preview: Deposits")
        st.dataframe(deposits.head())

        st.subheader("Preview: Withdrawals")
        st.dataframe(withdrawals.head())

        # --- Example: simple merge (you’ll define exact rules later) ---
        merged = pd.merge(withdrawals, deposits, on="Account Number", how="left")

        st.subheader("Processed Data")
        st.dataframe(merged.head())

        # Save output
        output_file = "Processed_Report.xlsx"
        merged.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("Download Processed Report", f, file_name=output_file)

    except Exception as e:
        st.error(f"Error reading files: {e}")
