import pandas as pd
import streamlit as st
from io import BytesIO

st.title("📊 Early Withdrawal Report Generator")

# Upload files
deposit_file = st.file_uploader("Upload Deposit File (Excel)", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File (Excel)", type=["xlsx"])

if deposit_file and withdrawal_file:
    # === Step 1: Read first sheet from both files ===
    deposits = pd.read_excel(deposit_file, sheet_name=0)
    withdrawals = pd.read_excel(withdrawal_file, sheet_name=0)

    # === Step 2: Normalize column names ===
    deposits.columns = deposits.columns.str.strip().str.lower()
    withdrawals.columns = withdrawals.columns.str.strip().str.lower()

    # === Step 3: Ensure date columns are datetime ===
    deposits['deposit date'] = pd.to_datetime(deposits['deposit date'])
    withdrawals['withdrawal date'] = pd.to_datetime(withdrawals['withdrawal date'])

    # === Step 4: Working days calculator ===
    def working_days(start, end):
        if pd.isna(end):
            return None
        return len(pd.bdate_range(start, end)) - 1  # exclude deposit day itself

    # === Step 5: Merge deposits & withdrawals ===
    merged = pd.merge(
        deposits,
        withdrawals,
        on="account number",
        suffixes=("_dep", "_withd"),
        how="left"
    )

    merged['working days held'] = merged.apply(
        lambda row: working_days(row['deposit date'], row['withdrawal date']),
        axis=1
    )

    # === Step 6: Flag early withdrawals ===
    merged['early withdrawal'] = merged['working days held'].apply(
        lambda x: True if x is not None and x < 14 else False
    )

    # === Step 7: Show preview ===
    st.subheader("Preview of Processed Data")
    st.dataframe(merged.head(20))

    # === Step 8: Prepare for download ===
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        merged.to_excel(writer, index=False, sheet_name="Report")

    st.download_button(
        label="📥 Download Early Withdrawal Report",
        data=output.getvalue(),
        file_name="Early_Withdrawal_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
