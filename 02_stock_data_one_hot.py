import pandas as pd
import os

# Configuration - adjust only these entries
CONFIG = {
    "input_folder": "01_Raw Data\yFinance API",
    "input_file": "stock_data.xlsx",
    "columns_to_keep": ['Date', 'Open', 'Close'],
    "sheet_names": ['DAX_EUR', 'MDAX_EUR', 'SDAX_EUR'],
    "output_folder": "02_Preprocessing\Stock_Preprocessed",
    "excel_filename": "stock_data_combined_onehot.xlsx"
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load and combine all sheets
combined_data = []
for sheet in CONFIG["sheet_names"]:
    df_sheet = pd.read_excel(f"{CONFIG['input_folder']}/{CONFIG['input_file']}", sheet_name=sheet)
    df_sheet = df_sheet[CONFIG["columns_to_keep"]]
    df_sheet['Index'] = sheet.replace('_EUR', '')
    combined_data.append(df_sheet)

# Combine and one-hot encode
df = pd.concat(combined_data, ignore_index=True)
df_onehot = pd.get_dummies(df, columns=['Index'], prefix='Index', dtype=float)

# Save to Excel
os.makedirs(CONFIG["output_folder"], exist_ok=True)
df_onehot.to_excel(f"{CONFIG['output_folder']}/{CONFIG['excel_filename']}", index=False)

# Display results
print(f"Dimensions: {df_onehot.shape[0]} rows × {df_onehot.shape[1]} columns")
print(f"Columns kept: {', '.join(CONFIG['columns_to_keep'])}")
print(f"One-Hot Encoded Columns: {[col for col in df_onehot.columns if 'Index_' in col]}")
print(f"Sheets combined: {len(CONFIG['sheet_names'])} ({', '.join([name.replace('_EUR', '') for name in CONFIG['sheet_names']])})")
print(df_onehot.head(-10))

print("\nColumn data types:")
for col in df_onehot.columns:
    print(f"   • {col}: {df_onehot[col].dtype}")

print(f"\n✅ File saved: {CONFIG['output_folder']}/{CONFIG['excel_filename']}")
