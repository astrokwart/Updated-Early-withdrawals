import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_clean_file(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    df = pd.read_excel(file, sheet_name=first_sheet, header=4)
    return df

def process_files(deposits, withdrawals):
    # Normalize column names (strip spaces, lowercase)
    deposits.columns = deposits.columns.str.strip().str.lower()
    withdrawals.columns = withdrawals.columns.str.strip().str.lower()

    # Map expected columns
    date_col = "date"
    acct_col = "account number"
    credit_col = "credit amt"
    debit_col = "debit amt"

    # Convert dates
    deposits[date_col] = pd.to_datetime(deposits[date_col], errors="coerce")
    withdrawals[date_col] = pd.to_datetime(withdrawals[date_col], errors="coerce")

    # Select useful columns
    deposits = deposits[[date_col, acct_col, credit_col]].dropna()
    withdrawals = withdrawals[[date_col, acct_col, debit_col]].dropna()

    # Rename for clarity
    deposits.rename(columns={date_col: "Deposit Date", credit_col: "Deposit Amt"}, inplace=True)
    withdrawals.rename(columns={date_col: "Withdrawal Date", debit_col: "Withdrawal Amt"}, inplace=True)

    # Merge deposits & withdrawals
    merged = pd.merge(deposits, withdrawals, on=acct_col, how="inner")

    # Calculate days held
    merged["Days Held"] = (merged["Withdrawal Date"] - merged["Deposit Date"]).dt.days
    merged["Early Withdrawal"] = merged["Days Held"] < 14

    # Separate reports
    early_withdrawals = merged[merged["Early Withdrawal"]]
    valid_deposits = merged[~merged["Early Withdrawal"]]

    # Save report
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
