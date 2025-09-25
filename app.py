import pandas as pd
import streamlit as st

st.title("Early Withdrawal Processing Tool")

# Upload deposit and withdrawal files
deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

# Helper function to split Description column
def split_description(desc, remove_prefix=""):
    if pd.isna(desc):
        return None, None
    if "-" in str(desc):
        parts = desc.split("-")
        name = parts[0].replace(remove_prefix, "").strip()
        acc = parts[1].strip()
        return name, acc
    return desc, None

def load_first_sheet(file):
    xls = pd.ExcelFile(file)
    first_sheet = xls.sheet_names[0]
    return pd.read_excel(file, sheet_name=first_sheet)

if deposit_file and withdrawal_file:
    try:
        # Load raw data
        deposits_raw = load_first_sheet(deposit_file)
        withdrawals_raw = load_first_sheet(withdrawal_file)

        # --- Clean Deposits ---
        deposits = deposits_raw[deposits_raw['Credit Amt'] > 0].copy()
        deposits[['customer name', 'Account number']] = deposits['Description'].apply(
            lambda x: pd.Series(split_description(x, remove_prefix="DEPOSIT BY"))
        )
        clean_deposits = pd.DataFrame({
            "deposit Date": deposits['Value Date'],
            "customer name": deposits['customer name'],
            "Account number": deposits['Account number'],
            "Amount": deposits['Credit Amt']
        })

        # --- Clean Withdrawals ---
        withdrawals = withdrawals_raw[withdrawals_raw['Debit Amt'] > 0].copy()
        withdrawals[['customer name', 'Account number']] = withdrawals['Description'].apply(
            lambda x: pd.Series(split_description(x))
        )
        clean_withdrawals = pd.DataFrame({
            "withdrawal Date": withdrawals['Value Date'],
            "customer name": withdrawals['customer name'],
            "Account number": withdrawals['Account number'],
            "Amount": withdrawals['Debit Amt']
        })

        # --- Save into one Excel file ---
        output_file = "Processed_Report.xlsx"
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            clean_deposits.to_excel(writer, sheet_name="Deposits", index=False)
            clean_withdrawals.to_excel(writer, sheet_name="Withdrawals", index=False)

        st.success("Files processed successfully!")
        st.subheader("Deposits Preview")
        st.dataframe(clean_deposits.head())

        st.subheader("Withdrawals Preview")
        st.dataframe(clean_withdrawals.head())

        with open(output_file, "rb") as f:
            st.download_button("Download Processed Report", f, file_name=output_file)

    except Exception as e:
        st.error(f"Error processing files: {e}")
