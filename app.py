import streamlit as st
import pandas as pd

st.title("Early Withdrawal Report Tool")

try:
    deposit_file = st.file_uploader("Upload Deposit File", type=["xlsx"])
    withdrawal_file = st.file_uploader("Upload Withdrawal File", type=["xlsx"])

    if deposit_file and withdrawal_file:
        try:
            # Read files, skipping first 5 rows
            deposits = pd.read_excel(deposit_file, skiprows=5)
            withdrawals = pd.read_excel(withdrawal_file, skiprows=5)

            st.subheader("Deposit File Preview")
            st.dataframe(deposits.head())

            st.subheader("Withdrawal File Preview")
            st.dataframe(withdrawals.head())

            # --- Ensure date columns are datetime ---
            deposits["Date"] = pd.to_datetime(deposits["Date"], errors="coerce")
            withdrawals["Date"] = pd.to_datetime(withdrawals["Date"], errors="coerce")

            # --- Merge deposits and withdrawals on Account No + Amount ---
            merged = pd.merge(
                deposits,
                withdrawals,
                on=["Account No", "Amount"],
                how="left",
                suffixes=("_dep", "_withd")
            )

            # --- Calculate difference in days ---
            merged["Days Held"] = (merged["Date_withd"] - merged["Date_dep"]).dt.days

            # --- Early withdrawals (<14 days) ---
            early_withdrawals = merged[merged["Days Held"] < 14]

            st.subheader("Early Withdrawals Report")
            st.dataframe(early_withdrawals)

            # --- Download option ---
            st.download_button(
                "Download Early Withdrawals as Excel",
                early_withdrawals.to_excel(index=False, engine="openpyxl"),
                file_name="early_withdrawals.xlsx"
            )

        except Exception as e:
            st.error(f"Error processing files: {e}")

except Exception as e:
    st.error(f"Unexpected error: {e}")
