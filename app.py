import pandas as pd

def process_files(deposit_file, withdrawal_file, output_file="Early_Withdrawal_Report.xlsx"):
    # Read only the first sheet from each file
    deposits = pd.read_excel(deposit_file, sheet_name=0)
    withdrawals = pd.read_excel(withdrawal_file, sheet_name=0)

    # Normalize column names
    deposits.columns = deposits.columns.str.strip().str.lower()
    withdrawals.columns = withdrawals.columns.str.strip().str.lower()

    # Ensure dates are datetime
    deposits['deposit date'] = pd.to_datetime(deposits['deposit date'])
    withdrawals['withdrawal date'] = pd.to_datetime(withdrawals['withdrawal date'])

    # Working days calculator
    def working_days(start, end):
        if pd.isna(end):
            return None
        return len(pd.bdate_range(start, end)) - 1  # exclude deposit day itself

    # Merge deposits with withdrawals
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

    # Flag early withdrawals
    merged['early withdrawal'] = merged['working days held'].apply(
        lambda x: True if x is not None and x < 14 else False
    )

    # Save final report
    merged.to_excel(output_file, index=False)
    return output_file
