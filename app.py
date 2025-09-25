import pandas as pd

# === Step 1: Load the raw Excel file ===
file_path = "ESUSU_ACCT_STMT.xlsx"   # replace with your actual file
df = pd.read_excel(file_path, sheet_name="Sheet1")

# === Helper function to split Description into Name + Account Number ===
def split_description(desc, remove_prefix=""):
    if pd.isna(desc):
        return None, None
    if "-" in str(desc):
        parts = desc.split("-")
        name = parts[0].replace(remove_prefix, "").strip()
        acc = parts[1].strip()
        return name, acc
    return desc, None

# === Step 2: Extract Withdrawals ===
withdrawals = df[df['Debit Amt'] > 0].copy()
withdrawals[['customer name', 'Account number']] = withdrawals['Description'].apply(
    lambda x: pd.Series(split_description(x))
)
clean_withdrawals = pd.DataFrame({
    "withdrawal Date": withdrawals['Value Date'],
    "customer name": withdrawals['customer name'],
    "Account number": withdrawals['Account number'],
    "Amount": withdrawals['Debit Amt']
})

# === Step 3: Extract Deposits ===
deposits = df[df['Credit Amt'] > 0].copy()
deposits[['customer name', 'Account number']] = deposits['Description'].apply(
    lambda x: pd.Series(split_description(x, remove_prefix="DEPOSIT BY"))
)
clean_deposits = pd.DataFrame({
    "deposit Date": deposits['Value Date'],
    "customer name": deposits['customer name'],
    "Account number": deposits['Account number'],
    "Amount": deposits['Credit Amt']
})

# === Step 4: Save into one Excel file with two sheets ===
output_file = "Processed_Report.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    clean_deposits.to_excel(writer, sheet_name="Deposits", index=False)
    clean_withdrawals.to_excel(writer, sheet_name="Withdrawals", index=False)

print(f"Processed report saved as: {output_file}")
