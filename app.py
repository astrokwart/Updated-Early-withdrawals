import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

def load_clean_file(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    df = pd.read_excel(file, sheet_name=first_sheet, header=4)
    df.columns = df.columns.str.strip().str.lower()
    return df.fillna("")   # Replace NaN with blank strings for Streamlit display

def find_column(columns, keywords):
    """Find the first matching column given keywords."""
    for col in columns:
        for kw in keywords:
            if kw in col:
                return col
    return None

def process_files(deposits, withdrawals):
    # Detect columns dynamically
    date_col_d = find_column(deposits.columns, ["date"])
    acct_col_d = find_column(deposits.columns, ["account"])
    credit_col = find_column(deposits.columns, ["credit"])
    
    date_col_w = find_column(withdrawals.columns, ["date"])
    acct_col_w = find_column(withdrawals.columns, ["account"])
    debit_col = find_column(withdrawals.columns, ["debit"])

    detected = {
        "Deposit Date": date_col_d,
        "Deposit Account": acct_col_d,
        "Deposit Credit": credit_col,
        "Withdrawal Date": date_col_w,
        "Withdrawal Account": acct_col_w,
        "Withdrawal Debit": debit_col,
    }

    # Show detected columns to confirm
    st.write("📌 Auto-detected columns:", detected)

    if not all(detected.values()):
        raise ValueError("❌ Could not auto-detect all required columns. Please check headers.")

    # Convert dates
    deposits[date_col_d] = pd.to_datetime(deposits[date_col_d], errors="coerce")
    withdrawals[date_col_w] = pd.to_datetime(withdrawals[date_col_w], errors="coerce")

    # Keep only relevant cols
    deposits = deposits[[date_col_d, acct_col_d, credit_col]]
    withdrawals = withdrawals[[date_col_w, acct_col_w, debit_col]]

    # Rename
    deposits.rename(columns={date_col_d: "Deposit Date", credit_col: "Deposit Amt", acct_col_d: "Account Number"}, inplace=True)
    withdrawals.rename(columns={date_col_w: "Withdrawal Date", debit_col: "Withdrawal Amt", acct_col_w: "Account Number"}, inplace=True)

    # Merge
    merged = pd.merge(deposits, withdrawals, on="Account Number", how="inner")

    # Calculate holding days
    merged["Days Held"] = (merged["Withdrawal Date"] - merged["Deposit Date"]).dt.days
    merged["Early Withdrawal"] = merged["Days Held"] < 14

    # Split reports
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
        st.dataframe(deposits.head(10))

        st.subheader("Withdrawal File Preview")
        st.dataframe(withdrawals.head(10))

        if st.button("Process Files"):
            early_withdrawals, valid_deposits = process_files(deposits, withdrawals)

            st.success("✅ Processing complete! File saved as Processed_Report.xlsx")
            st.subheader("Early Withdrawals (Preview)")
            st.dataframe(early_withdrawals.head())
            st.subheader("Valid Deposits (Preview)")
            st.dataframe(valid_deposits.head())

    except Exception
