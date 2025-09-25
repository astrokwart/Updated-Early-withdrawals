import streamlit as st
import pandas as pd
from pandas.tseries.offsets import BDay

# === Streamlit App Title ===
st.title("Early Withdrawal Report")

# === Step 1: Allow user to upload Excel data ===
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read the uploaded file into a DataFrame
    df = pd.read_excel(uploaded_file, sheet_name="Sheet1")

    # === Step 1.5: Automatically sort the data ===
    df = df.sort_values(by='Deposit Date', ascending=True)

    # === Step 2: Ensure date columns are datetime ===
    df['Deposit Date'] = pd.to_datetime(df['Deposit Date'])
    df['Withdrawal Date'] = pd.to_datetime(df['Withdrawal Date'], errors='coerce')

    # === Step 3: Calculate working days ===
    def working_days(start, end):
        if pd.isna(end):
            return None
        return len(pd.bdate_range(start, end)) - 1

    df['Working Days Held'] = df.apply(
        lambda row: working_days(row['Deposit Date'], row['Withdrawal Date']),
        axis=1
    )

    # === Step 4: Flag early withdrawals ===
    df['Early Withdrawal'] = df['Working Days Held'].apply(
        lambda x: True if x is not None and x < 14 else False
    )

    # === Step 5: Display report ===
    st.header("Processed Data")
    st.dataframe(df)

    # === Step 6: Create a download button ===
    output = df.to_excel(index=False, engine='xlsxwriter')
    st.download_button(
        label="Download Report as Excel",
        data=output,
        file_name='early_withdrawal_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )