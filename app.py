import streamlit as st
import pandas as pd
from pandas.tseries.offsets import BDay

# === Streamlit App Title ===
st.title("Early Withdrawal Report")

# === Step 1: Allow users to upload Excel data ===
st.markdown("Please upload your **deposits** and **withdrawals** Excel files.")
deposits_file = st.file_uploader("Upload Deposits File", type="xlsx")
withdrawals_file = st.file_uploader("Upload Withdrawals File", type="xlsx")

# The main logic runs only if both files have been uploaded
if deposits_file is not None and withdrawals_file is not None:
    try:
        # === Step 2: Read and prepare the data ===
        # Read deposits data
        df_deposits = pd.read_excel(deposits_file, sheet_name="Sheet1")

        # Read withdrawals data
        df_withdrawals = pd.read_excel(withdrawals_file, sheet_name="Sheet1")

        # === Define Column Names (EDIT THESE TO MATCH YOUR FILES) ===
        ACCOUNT_ID = 'Account ID'  # Placeholder for the column linking deposits and withdrawals
        DEPOSIT_DATE = 'Deposit Date'
        WITHDRAWAL_DATE = 'Withdrawal Date'

        # Ensure the linking column exists in both files
        if ACCOUNT_ID not in df_deposits.columns or ACCOUNT_ID not in df_withdrawals.columns:
            st.error(f"Error: The '{ACCOUNT_ID}' column was not found in one or both of your files.")
        else:
            # === Step 3: Sort and clean data ===
            df_deposits[DEPOSIT_DATE] = pd.to_datetime(df_deposits[DEPOSIT_DATE])
            df_withdrawals[WITHDRAWAL_DATE] = pd.to_datetime(df_withdrawals[WITHDRAWAL_DATE])

            # Sort both dataframes by their respective dates
            df_deposits.sort_values(by=DEPOSIT_DATE, ascending=True, inplace=True)
            df_withdrawals.sort_values(by=WITHDRAWAL_DATE, ascending=True, inplace=True)

            # === Step 4: Merge data to match deposits with subsequent withdrawals ===
            # This performs a complex merge to find the first withdrawal after a deposit
            # Note: This is a simplified approach and may need adjustment for complex cases.

            # Create a temporary 'key' for merging
            df_deposits['merge_key'] = df_deposits[DEPOSIT_DATE].apply(lambda x: x.date())
            df_withdrawals['merge_key'] = df_withdrawals[WITHDRAWAL_DATE].apply(lambda x: x.date())

            df = pd.merge(
                df_deposits,
                df_withdrawals,
                how='left',
                on=ACCOUNT_ID,
                suffixes=('_deposit', '_withdrawal')
            )

            # Filter to only keep withdrawals that happen AFTER the deposit
            df = df[df[WITHDRAWAL_DATE] >= df[DEPOSIT_DATE]]

            # Keep only the first valid withdrawal after each deposit
            df = df.sort_values(by=WITHDRAWAL_DATE).drop_duplicates(
                subset=[ACCOUNT_ID, DEPOSIT_DATE], keep='first'
            )

            # === Step 5: Calculate working days ===
            def working_days(start, end):
                if pd.isna(end):
                    return None
                return len(pd.bdate_range(start, end)) - 1  # Exclude deposit day itself

            df['Working Days Held'] = df.apply(
                lambda row: working_days(row[DEPOSIT_DATE], row[WITHDRAWAL_DATE]),
                axis=1
            )

            # === Step 6: Flag early withdrawals ===
            df['Early Withdrawal'] = df['Working Days Held'].apply(
                lambda x: True if x is not None and x < 14 else False
            )

            # === Step 7: Display report ===
            st.header("Processed Report")
            st.dataframe(df)

            # === Step 8: Create a download button ===
            output = df.to_excel(index=False, engine='xlsxwriter')
            st.download_button(
                label="Download Report as Excel",
                data=output,
                file_name='early_withdrawal_report.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    except Exception as e:
        st.error(f"An error occurred: {e}. Please ensure your Excel files have the correct sheet names and column headers.")
