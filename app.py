import pandas as pd

# === Step 1: File paths (replace with your filenames) ===
deposit_file = "Deposits.xlsx"
withdrawal_file = "Withdrawals.xlsx"

# === Step 2: Always pick the first sheet from each file ===
deposits = pd.read_excel(deposit_file, sheet_name=0)    # First sheet only
withdrawals = pd.read_excel(withdrawal_file, sheet_name=0)  # First sheet only

# === Step 3: Normalize column names ===
deposits.columns = deposits.columns.str.strip().str.lower()
withdrawals.columns = withdrawals.columns.str.strip().str.lower()

# === Step 4: Ensure dates are datetime ===
deposits['deposit date'] = pd.to_datetime(deposits['deposit date'])
withdrawals['withdrawal date'] = pd.to_datetime(withdrawals['withdrawal date'])

# === Step 5: Function to calculate working days ===
def working_days(start, end):
    if pd.isna(end):
        return None
    return len(pd.bdate_range(start, end)) - 1  # exclude deposit day itself

# === Step 6: Merge deposits with withdrawals ===
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

# === Step 7: Flag early withdrawals ===
merged['early withdrawal'] = merged['working days held'].apply(
    lambda x: True if x is not None and x < 14 else False
)

# === Step 8: Save report ===
output_file = "Early_Withdrawal_Report.xlsx"
merged.to_excel(output_file, index=False)

print(f"✅ Report generated: {output_file}")
