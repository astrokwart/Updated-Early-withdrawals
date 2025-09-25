import pandas as pd
import streamlit as st
from datetime import timedelta

st.title("Early Withdrawal Processing Tool")

# Upload files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_clean_file(file):
    """Load Excel file starting from row 5 (index=4)."""
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    df = pd.read_excel(file, sheet_name=first_sheet, header=4)
    return df

def process_files(deposits, withdrawals):
    # Convert dates
    deposits["Date"] = pd.to_datetime(deposits["Date"], errors="coerce")
    withdrawals["Date"] = pd.to_datetime(withdrawals["Date"], errors="coerce")

    # Keep only useful columns
    deposits = deposits[["Date", "Account Number", "Credit Amt"]].dropna()
    withdrawals = withdrawals[["Date", "Account Number", "Debit Amt"]].dropna()

    # Rename for clarity
    deposits.rename(columns={"Date": "Deposit Date", "Credit Amt": "Deposit Amt"}, inplace=True)
    withdrawals.rename(columns={"Date": "Withdrawal Date", "Debit Amt": "Withdrawal Amt"}, inplace=True)

    # Merge deposits & withdrawals by Account Number
    merged = pd.merge(deposits, withdrawals, on="Account Number", how="inner")

    # Check if withdrawal matches deposit within 14 days
    merged["Days Held"] = (merged["Withdrawal Date"] - merged["Deposit Date"]).dt.days
    merged["Early Withdrawal"] = merged["Days Held"] < 14
    merged["Matched Amount"] = merged.apply(
        lambda row: row["Deposit Amt"] if row["Deposit Amt"] == row["Withdrawal Amt"] else 0,
        axis=1
    )

    # Separate reports
    early_withdrawals = merged[merged["Early Withdrawal"]]
    valid_deposits = merged[~merged["Early Withdrawal"]]

    # Save to Excel
    with pd.ExcelWriter("Processed_Report.xlsx") as writer:
        deposits.to_excel(writer, sheet_name="Deposits", index=False)
        withdrawals.to_excel(writer, sheet_name="Withdrawals", index=False)
        early_withdrawals.to_excel(writer, sheet_name="Early Withdrawals", index=False)
        valid_deposits.to_excel(writer, sheet_name="Valid Deposits", index=False)

    return early_withdrawals, valid_deposits

if deposit_file and withdrawal_file:
    try:
        deposits = load_clean_file(deposit_file)
        withdrawals = load_clean_file(withdrawal_file)

        st.subheader("Deposit File Preview")
        st.dataframe(deposits.head())

        st.subheader("Withdrawal File Preview")
        st.dataframe(withdrawals.head())

        if st.button("Process Files"):
            early_withdrawals, valid_deposits = process_files(deposits, withdrawals)

            st.success("✅ Processing complete! File saved as Processed_Report.xlsx")
            st.subheader("Early Withdrawals (Preview)")
            st.dataframe(early_withdrawals.head())

            st.subheader("Valid Deposits (Preview)")
            st.dataframe(valid_deposits.head())

    except Exception as e:
        st.error(f"Error processing files: {e}")
